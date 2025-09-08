"""
Command implementations for PDD-related functionality.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from rich.console import Console
from rich.panel import Panel

from taskinator.core.task_generation import generate_task_files
from taskinator.core.task_manager import Task, read_tasks, write_tasks
from taskinator.utils.config import get_config_value

console = Console()


def convert_command(
    input_file: str,
    output_file: Optional[str] = None,
    format: str = "markdown",
    output_dir: Optional[str] = None,
) -> None:
    """
    Convert a PDD to SOP documents.

    Args:
        input_file (str): Path to the PDD file
        output_file (Optional[str], optional): Path to the output SOP file. Defaults to None.
        format (str, optional): Output format (markdown, json, yaml). Defaults to "markdown".
        output_dir (Optional[str], optional): Directory to output SOP files. Defaults to None.
    """
    try:
        # Validate input file
        if not os.path.exists(input_file):
            console.print(
                f"[ERROR] Input file {input_file} does not exist", style="bold red"
            )
            return

        # Determine output file or directory
        if not output_file and not output_dir:
            # Default to same directory as input file with .sop.md extension
            input_path = Path(input_file)
            output_dir = input_path.parent
            output_file = os.path.join(output_dir, f"{input_path.stem}.sop.{format}")
        elif output_dir and not output_file:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            # Default to same name as input file with .sop.md extension
            input_path = Path(input_file)
            output_file = os.path.join(output_dir, f"{input_path.stem}.sop.{format}")

        # Read PDD file
        console.print(f"[INFO] Reading PDD from {input_file}...")
        with open(input_file, "r") as f:
            pdd_content = f.read()

        # Parse PDD content
        # This would normally use a proper PDD parser, but for now we'll just do a simple conversion
        sop_content = _convert_pdd_to_sop(pdd_content, format)

        # Write SOP file
        console.print(f"[INFO] Writing SOP to {output_file}...")
        with open(output_file, "w") as f:
            f.write(sop_content)

        console.print(
            Panel(
                f"Successfully converted PDD to SOP:\n"
                f"Input: {input_file}\n"
                f"Output: {output_file}",
                title="",
                style="green",
            )
        )
    except Exception as e:
        console.print(
            f"[ERROR] Error converting PDD to SOP: {str(e)}", style="bold red"
        )


def to_tasks_command(
    input_file: str,
    tasks_file: Optional[str] = None,
    num_tasks: int = 5,
    priority: str = "medium",
) -> None:
    """
    Convert a PDD to tasks.

    Args:
        input_file (str): Path to the PDD file
        tasks_file (Optional[str], optional): Path to the tasks.json file. Defaults to None.
        num_tasks (int, optional): Number of tasks to generate. Defaults to 5.
        priority (str, optional): Priority for the generated tasks. Defaults to "medium".
    """
    try:
        # Validate input file
        if not os.path.exists(input_file):
            console.print(
                f"[ERROR] Input file {input_file} does not exist", style="bold red"
            )
            return

        # Determine tasks file
        if not tasks_file:
            tasks_file = get_config_value("tasks_file_path", "tasks.json")

        # Read PDD file
        console.print(f"[INFO] Reading PDD from {input_file}...")
        with open(input_file, "r") as f:
            pdd_content = f.read()

        # Read existing tasks
        console.print(f"[INFO] Reading tasks from {tasks_file}...")
        tasks = read_tasks(tasks_file)

        # Generate tasks from PDD
        new_tasks = _convert_pdd_to_tasks(pdd_content, num_tasks, priority, input_file)

        # Add new tasks to existing tasks
        for task in new_tasks:
            tasks.tasks.append(task)

        # Write tasks to file
        console.print(f"[INFO] Writing tasks to {tasks_file}...")
        write_tasks(tasks_file, tasks)

        # Generate task files
        console.print("[INFO] Regenerating task files...")
        generate_task_files(tasks_file)

        console.print(
            Panel(
                f"Successfully converted PDD to {len(new_tasks)} tasks:\n"
                f"Input: {input_file}\n"
                f"Tasks: {', '.join([str(task.id) for task in new_tasks])}\n\n"
                f"Next steps:\n"
                f"1. Review the tasks with: taskinator list\n"
                f"2. Start working on the first task with: taskinator set-status --id={new_tasks[0].id} --status=in-progress",
                title="",
                style="green",
            )
        )
    except Exception as e:
        console.print(
            f"[ERROR] Error converting PDD to tasks: {str(e)}", style="bold red"
        )


def _convert_pdd_to_sop(pdd_content: str, format: str) -> str:
    """
    Convert PDD content to SOP content.

    Args:
        pdd_content (str): PDD content
        format (str): Output format

    Returns:
        str: SOP content
    """
    # This would normally use a proper PDD parser and SOP generator
    # For now, we'll just do a simple conversion

    # Extract processes from PDD
    processes = []
    current_process = None

    for line in pdd_content.split("\n"):
        if line.startswith("## "):
            # New process
            if current_process:
                processes.append(current_process)
            current_process = {"name": line[3:].strip(), "steps": [], "description": ""}
        elif line.startswith("### ") and current_process:
            # New step
            current_process["steps"].append(
                {"name": line[4:].strip(), "description": ""}
            )
        elif current_process and current_process["steps"]:
            # Add to current step description
            current_process["steps"][-1]["description"] += line + "\n"
        elif current_process:
            # Add to current process description
            current_process["description"] += line + "\n"

    # Add the last process
    if current_process:
        processes.append(current_process)

    # Generate SOP content
    if format == "markdown":
        sop_content = "# Standard Operating Procedure\n\n"

        for process in processes:
            sop_content += f"## {process['name']}\n\n"
            sop_content += f"{process['description'].strip()}\n\n"

            sop_content += "### Steps\n\n"
            for i, step in enumerate(process["steps"], 1):
                sop_content += f"{i}. **{step['name']}**\n"
                sop_content += f"   {step['description'].strip()}\n\n"

            # Add Mermaid diagram
            sop_content += "### Process Flow\n\n"
            sop_content += "```mermaid\ngraph TD\n"
            for i, step in enumerate(process["steps"], 1):
                sop_content += f"    Step{i}[{step['name']}]\n"
                if i > 1:
                    sop_content += f"    Step{i-1} --> Step{i}\n"
            sop_content += "```\n\n"

    elif format == "json":
        import json

        sop_content = json.dumps(
            {"title": "Standard Operating Procedure", "processes": processes}, indent=2
        )

    elif format == "yaml":
        import yaml

        sop_content = yaml.dump(
            {"title": "Standard Operating Procedure", "processes": processes}
        )

    else:
        raise ValueError(f"Unsupported format: {format}")

    return sop_content


def _convert_pdd_to_tasks(
    pdd_content: str, num_tasks: int, priority: str, pdd_file: str
) -> List[Task]:
    """
    Convert PDD content to tasks.

    Args:
        pdd_content (str): PDD content
        num_tasks (int): Number of tasks to generate
        priority (str): Priority for the generated tasks
        pdd_file (str): Path to the PDD file

    Returns:
        List[Task]: Generated tasks
    """
    # This would normally use a proper PDD parser and task generator
    # For now, we'll just do a simple conversion

    # Extract processes from PDD
    processes = []
    current_process = None

    for line in pdd_content.split("\n"):
        if line.startswith("## "):
            # New process
            if current_process:
                processes.append(current_process)
            current_process = {"name": line[3:].strip(), "description": ""}
        elif current_process:
            # Add to current process description
            current_process["description"] += line + "\n"

    # Add the last process
    if current_process:
        processes.append(current_process)

    # Generate tasks
    tasks = []

    # Limit to num_tasks
    processes = processes[:num_tasks]

    # Get the highest task ID
    from datetime import datetime

    # Start with a base ID if no tasks exist yet
    next_id = 1

    # Try to read existing tasks to get the next ID
    try:
        tasks_file = get_config_value("tasks_file_path", "tasks.json")
        if os.path.exists(tasks_file):
            existing_tasks = read_tasks(tasks_file)
            next_id = existing_tasks.get_next_id()
    except Exception:
        # If there's an error, just use the default ID
        pass

    # Create tasks for each process
    for i, process in enumerate(processes):
        task_id = next_id + i

        # Create the task
        task = Task(
            id=task_id,
            title=process["name"],
            description=f"Implement the {process['name']} process from the PDD.",
            details=process["description"].strip(),
            status="pending",
            priority=priority,
            dependencies=[task_id - 1] if i > 0 else [],
            source={"type": "pdd", "document": pdd_file, "section": process["name"]},
        )

        tasks.append(task)

    return tasks
