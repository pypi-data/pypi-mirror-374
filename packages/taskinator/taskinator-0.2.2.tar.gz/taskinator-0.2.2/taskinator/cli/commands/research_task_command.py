"""
Research task command implementation for Taskinator.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from rich.box import ROUNDED
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from taskinator.utils.config import get_config_value, check_ai_available

console = Console()


def research_task_command(task_id: str) -> None:
    """
    Generate research for a specific task and save it to the tasks/research directory.

    Args:
        task_id (str): ID of the task to research
    """
    try:
        # Check if AI is available
        if not check_ai_available():
            console.print(
                "[ERROR] AI functionality is not available. Please check your model configuration and credentials.",
                style="bold red",
            )
            return
            
        # Get the tasks file path
        tasks_file_path = get_config_value("tasks_file_path")

        if not os.path.exists(tasks_file_path):
            console.print(
                f"[ERROR] Tasks file {tasks_file_path} does not exist", style="bold red"
            )
            return

        # Read tasks from file
        with open(tasks_file_path, "r") as f:
            data = json.load(f)

        tasks = data.get("tasks", [])

        if not tasks:
            console.print("[ERROR] No tasks found", style="bold red")
            return

        # Find the task by ID
        task = None
        for t in tasks:
            if str(t.get("id", "")) == str(task_id):
                task = t
                break

        if not task:
            console.print(f"[ERROR] Task with ID {task_id} not found", style="bold red")
            return

        # Get task details
        task_title = task.get("title", "")
        task_description = task.get("description", "")
        task_details = task.get("details", "")

        console.print(
            f"[INFO] Generating research for Task #{task_id}: {task_title}...",
            style="blue",
        )

        # Import LiteLLM - should be available since check_ai_available() passed
        import litellm
        from litellm import completion

        # Get model configuration and API key
        from taskinator.utils.config import get_config
        
        config = get_config()
        perplexity_api_key = os.environ.get("PERPLEXITY_API_KEY")
        perplexity_model = os.environ.get("PERPLEXITY_MODEL", "sonar-pro")
        default_model = os.environ.get("MODEL", config.get("MODEL", "anthropic/claude-3-7-sonnet-20250219"))
        use_perplexity = bool(perplexity_api_key)
        
        if not use_perplexity:
            console.print(
                "[WARNING] PERPLEXITY_API_KEY environment variable is not set. Using default AI provider instead.",
                style="yellow",
            )

        # Create the research prompt
        research_prompt = f"""You are conducting a detailed analysis of a software development task to determine its complexity and how it should be broken down into subtasks.

Please research this task thoroughly, considering best practices, industry standards, and potential implementation challenges:

Task ID: {task_id}
Title: {task_title}
Description: {task_description}
Details: {task_details}

Based on your research, provide:
1. Technical approaches and considerations for this task
2. Potential challenges and solutions
3. Similar implementations and best practices
4. Required skills and expertise
5. Estimated complexity and scope

Return your findings in a detailed report that covers this task thoroughly.
"""

        # Configure model parameters
        if use_perplexity:
            console.print("[INFO] Calling Perplexity API for research...", style="blue")
            model_name = f"perplexity/{perplexity_model}"
            model_params = {
                "model": model_name,
                "messages": [{"role": "user", "content": research_prompt}],
                "api_key": perplexity_api_key
            }
        else:
            # Use default model
            console.print(f"[INFO] Using {default_model} for research...", style="blue")
            model_params = {
                "model": default_model,
                "messages": [
                    {"role": "system", "content": "You are a research assistant providing detailed analysis of software development tasks."},
                    {"role": "user", "content": research_prompt}
                ]
            }

        # Make the API call
        research_response = completion(**model_params)

        research_findings = research_response.choices[0].message.content
        console.print(
            f"[SUCCESS] Successfully generated research with {use_perplexity and 'Perplexity AI' or default_model}",
            style="green",
        )

        # Create research directory if it doesn't exist
        tasks_dir = os.path.dirname(tasks_file_path)
        research_dir = os.path.join(tasks_dir, "research")
        os.makedirs(research_dir, exist_ok=True)

        # Save research findings
        task_id_padded = str(task_id).zfill(3)
        task_research_file = os.path.join(research_dir, f"task_{task_id_padded}.txt")

        with open(task_research_file, "w") as f:
            f.write(f"# Research for Task {task_id}: {task_title}\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            f.write(research_findings)

        console.print(
            f"[INFO] Saved research findings to {task_research_file}", style="blue"
        )

        # Display the research findings
        research_panel = Panel(
            Markdown(research_findings),
            title=f"Research Findings for Task #{task_id}",
            width=100,
            border_style="blue",
            box=ROUNDED,
            padding=(1, 2),
        )

        console.print(research_panel)

    except Exception as e:
        console.print(f"[ERROR] Error researching task: {str(e)}", style="bold red")
        import traceback

        console.print(traceback.format_exc(), style="dim")
