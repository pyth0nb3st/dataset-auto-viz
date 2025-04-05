import os
from importlib import reload
from pathlib import Path
from pprint import pprint

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from GeneralAgent import Agent

import app.agentlib.prompts as prompts
import app.agentlib.skills as skills
from app.agentlib.agents import (
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


def token_callback(token):
    with open("output.log", "a") as f:
        if token:
            print(token, end="", flush=True)
            f.write(token)
        else:
            print("\n\n", end="", flush=True)
            f.write("\n\n")


@app.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Analyze image
        result = image_to_text_agent.user_input(
            [{"image": file_path, "text": "生成给定图片的描述"}]
        )

        # Clean up
        os.remove(file_path)

        return JSONResponse(content={"description": result})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/analyze-dataset")
def analyze_dataset(
    workspace: str, language: str, request: Request, file: UploadFile = File(...)
):
    workspace_path = settings.WORKSPACE_DIR / workspace
    plan_agent = create_visual_plan_agent(
        quasar_alpha,
        workspace=workspace_path,
        output_callback=token_callback,
        functions=[dataset_glance],
    )
    plot_agent = create_plot_agent(
        quasar_alpha, workspace=workspace_path, output_callback=token_callback
    )
    image_to_text_agent = create_image_to_text_agent(
        gemini_2_0_flash, language, output_callback=token_callback
    )
    data_analysis_report_agent = create_data_analysis_report_agent(
        quasar_alpha, language, workspace=workspace_path, output_callback=token_callback
    )

    try:
        # Save uploaded file temporarily
        file_path = settings.UPLOAD_DIR / workspace / file.filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)

        # Analyze dataset
        result = plan_agent.user_input(
            f"{file_path} 看一下这个数据集，只有最后一行的变量会被返回，不要做异常处理"
        )
        tasks = plan_agent.run(
            "生成一个数据可视化的计划，说明一下每一步使用什么图片类型，横纵坐标数据，图片标题，图片大小，每一步都要生成一张图片，需要有plot和带有subplots的plot各几张",
            "a variable represents a list[str] for tasks",
            display=True,
        )

        pprint(tasks)

        # Generate visualizations
        visualization_paths = []
        for task in tasks:
            img_path = plot_agent.run(
                f"{task} \n\n dataset path: {file_path} \n\n"
                + prompts.create_workspace_prompt(workspace),
                "only the last line of variable will be return, remember use #run code to run the code, return the image path as string in last line",
                display=True,
            )
            try:
                Path(img_path).exists()
                visualization_paths.append(img_path)
            except Exception as e:
                print(e)

        # Clean up
        os.remove(file_path)

        descriptions = []
        for path in visualization_paths:
            relative_path = Path(path).relative_to(settings.STATIC_DIR)
            url = f"{request.url.scheme}://{request.url.netloc}/static/{relative_path}"
            description = image_to_text_agent.run(
                [{"image": path, "text": f"生成给定图片的描述, using {language}"}]
            )
            descriptions.append({"url": url, "description": description})

        data_analysis_report = data_analysis_report_agent.run(
            f"based on the url and description mapping: \n{descriptions}.\nGenerate a data analysis report, and save it as a html file"
            + prompts.create_workspace_prompt(workspace),
            "only return the html file path as string, only the last line of variable will be return, remember use #run code to run the code",
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
                "visualizations": [str(path) for path in visualization_paths],
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
