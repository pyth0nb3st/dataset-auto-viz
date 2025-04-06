from typing import Callable, List, Optional

from GeneralAgent import Agent

from app.agentlib import prompts
from app.agentlib.skills import column_analysis, dataset_glance, install_packages


def create_general_agent(
    model: str,
    role: str = "",
    workspace: Optional[str] = None,
    functions: Optional[List[Callable]] = [],
    token_limit: Optional[int] = 64000,
    output_callback: Optional[Callable] = None,
):
    return Agent(
        model=model,
        role=role,
        functions=functions,
        token_limit=token_limit, 
        workspace=workspace,
        output_callback=output_callback
    )


def create_visual_plan_agent(
    model: str,
    output_callback: Callable = None,
    workspace: Optional[str] = None,
    functions: Optional[List[Callable]] = [
        install_packages,
        dataset_glance,
        column_analysis,
    ],
    token_limit: Optional[int] = 64000,
):
    plot_agent = Agent(
        role=prompts.VISUAL_PLAN_AGENT_PROMPT,
        model=model,
        output_callback=output_callback,
        workspace=workspace,
        functions=functions,
        token_limit=token_limit,
    )
    return plot_agent


def create_image_to_text_agent(
    model: str,
    language: str,
    output_callback: Callable = None,
    workspace: Optional[str] = None,
    token_limit: Optional[int] = 32000,
    disable_python_run: Optional[bool] = True,
):
    image_to_text_agent = Agent(
        role=prompts.create_image_to_text_agent_prompt(language),
        model=model,
        output_callback=output_callback,
        workspace=workspace,
        token_limit=token_limit,
        disable_python_run=disable_python_run,
    )
    return image_to_text_agent


def create_plot_agent(
    model: str,
    output_callback: Callable = None,
    workspace: Optional[str] = None,
    functions: Optional[List[Callable]] = [install_packages],
    token_limit: Optional[int] = 64000,
):
    plot_agent = Agent(
        role=prompts.PLOT_AGENT_PROMPT,
        model=model,
        output_callback=output_callback,
        workspace=workspace,
        functions=functions,
        token_limit=token_limit,
    )
    return plot_agent


def create_data_analysis_report_agent(
    model: str,
    language: str,
    output_callback: Callable = None,
    workspace: Optional[str] = None,
    functions: Optional[List[Callable]] = [install_packages],
    token_limit: Optional[int] = 64000,
):
    data_analysis_report_agent = Agent(
        role=prompts.create_data_analysis_report_agent_prompt(language),
        model=model,
        output_callback=output_callback,
        workspace=workspace,
        functions=functions,
        token_limit=token_limit,
    )
    return data_analysis_report_agent
