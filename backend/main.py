import os
from importlib import reload
from pathlib import Path

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

import app.agentlib.prompts as prompts
import app.agentlib.skills as skills
from app.agentlib.agents import (
    create_general_agent,
    create_data_analysis_report_agent,
    create_image_to_text_agent,
    create_plot_agent,
    create_visual_plan_agent,
)
from app.agentlib.skills import dataset_glance, install_packages
from app.core.config import settings

# Reload modules
reload(skills)
reload(prompts)

# Initialize FastAPI app
app = FastAPI(title="AI Visualization API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the static files directory
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")


# Model configurations
grok_2_1212 = "grok-2-1212"
grok_2_vision_1212 = "grok-2-vision-1212"
gemini_2_0_flash = "gemini-2.0-flash"
gemini_2_5_pro_exp_03_25 = "gemini-2.5-pro-exp-03-25"
gemini_2_0_flash_lite = "gemini-2.0-flash-lite"
deepseek_v3 = "ms/deepseek-v3"
deepseek_v3_0324 = "deepseek/deepseek-chat-v3-0324:free"
quasar_alpha = "openrouter/quasar-alpha"

plan_model = os.getenv("PLAN_MODEL", deepseek_v3)
plot_model = os.getenv("PLOT_MODEL", quasar_alpha)
image_to_text_model = os.getenv("IMAGE_TO_TEXT_MODEL", gemini_2_0_flash_lite)
data_analysis_report_model = os.getenv("DATA_ANALYSIS_REPORT_MODEL", quasar_alpha)


def token_callback(token):
    with open("output.log", "a") as f:
        if token:
            print(token, end="", flush=True)
            f.write(token)
        else:
            print("\n\n", end="", flush=True)
            f.write("\n\n")


@app.post("/analyze-dataset")
def analyze_dataset(
    workspace: str, language: str, request: Request, file: UploadFile = File(...)
):
    workspace_path = settings.WORKSPACE_DIR / workspace
    general_agent = create_general_agent(
        plan_model,
        functions=[dataset_glance],
    )
    plan_agent = create_visual_plan_agent(
        plan_model,
        workspace=workspace_path,
        output_callback=token_callback,
        functions=[dataset_glance],
    )
    plot_agent = create_plot_agent(
        plot_model, workspace=workspace_path, output_callback=token_callback, functions=[install_packages]
    )
    image_to_text_agent = create_image_to_text_agent(
        image_to_text_model, language, output_callback=token_callback
    )
    data_analysis_report_agent = create_data_analysis_report_agent(
        data_analysis_report_model, language, workspace=workspace_path, output_callback=token_callback
    )

    try:
        # Save uploaded file temporarily
        file_path = settings.UPLOAD_DIR / workspace / file.filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)

        # Analyze dataset
        result = general_agent.user_input(
            f"{file_path} 用 dataset_glance 看一下这个数据集，只有最后一行的变量会被返回，不要做异常处理\n" + prompts.create_workspace_prompt(workspace)
        )

        # Use sse return the result

        tasks = plan_agent.run(
            "生成一个数据可视化的计划，说明一下每一步使用什么图片类型，横纵坐标数据，图片标题，图片大小，每一步都要生成一张图片，需要有plot和带有subplots的plot各几张",
            "a variable represents a list[str] for tasks",
            display=True,
        )

        # Use sse return the tasks

        # Generate visualizations
        image_path_url_tuples = []
        for task in tasks:
            img_path = plot_agent.run(
                f"{task} \n\n dataset path: {file_path} \n\n"
                + prompts.create_workspace_prompt(workspace),
                "only the last line of variable will be return, remember use #run code to run the code, return the image path as string in last line",
                display=True,
            )
            try:
                if Path(img_path).exists():
                    relative_path = Path(img_path).absolute().relative_to(settings.STATIC_DIR.absolute())
                    url = f"{request.url.scheme}://{request.url.netloc}/static/{relative_path}"
                    image_path_url_tuples.append((img_path, url))
            except Exception as e:
                print(e)

        # Clean up
        os.remove(file_path)

        descriptions = []
        for path, url in image_path_url_tuples:
            description = image_to_text_agent.run(
                [{"image": path, "text": f"生成给定图片的描述, using {language}"}]
            )
            descriptions.append({"url": url, "description": description})

        data_analysis_report = data_analysis_report_agent.run(
            f"based on the url and description mapping: \n{descriptions}.\nGenerate a data analysis report, and save it as a html file" + prompts.create_workspace_prompt(workspace),
            "html file path as string, remember put the string in last line",
            display=True,
        )

        try:
            Path(data_analysis_report).exists()
            data_analysis_report_url = f"{request.url.scheme}://{request.url.netloc}/static/{Path(data_analysis_report).relative_to(settings.STATIC_DIR)}"
        except Exception as e:
            data_analysis_report_url = None
            print(e)
        return JSONResponse(
            content={
                "analysis": str(result),
                "tasks": [task for task in tasks],
                "image_urls": [url for _, url in image_path_url_tuples],
                "descriptions": [str(description) for description in descriptions],
                "data_analysis_report": (
                    data_analysis_report_url
                    if data_analysis_report_url
                    else str(data_analysis_report)
                ),
            }
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
