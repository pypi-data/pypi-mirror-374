"""
Export plugin for Taskinator.

This plugin adds functionality to export tasks to various formats.
"""

import csv
import json
import os
from typing import Dict, List, Optional

from rich.console import Console

from taskinator.core.task_manager import read_tasks, register_plugin
from taskinator.models.task import Task, TaskCollection

console = Console()


def export_tasks_to_csv(
    tasks_path: str,
    output_path: str,
    options: Optional[Dict] = None,
) -> None:
    """
    Export tasks to a CSV file.

    Args:
        tasks_path (str): Path to the tasks.json file
        output_path (str): Path to the output CSV file
        options (Optional[Dict], optional): Additional options. Defaults to None.
    """
    try:
        # Read tasks
        console.print("[INFO] Reading tasks from {}...".format(tasks_path))
        tasks = read_tasks(tasks_path)

        if not tasks.tasks:
            console.print(
                "[ERROR] No tasks found in {}".format(tasks_path), style="bold red"
            )
            return

        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Write tasks to CSV
        with open(output_path, "w", newline="") as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow(
                [
                    "ID",
                    "Title",
                    "Description",
                    "Status",
                    "Priority",
                    "Dependencies",
                    "Details",
                    "Test Strategy",
                    "Subtasks",
                ]
            )

            # Write tasks
            for task in tasks.tasks:
                writer.writerow(
                    [
                        task.id,
                        task.title,
                        task.description,
                        task.status,
                        task.priority,
                        ",".join(task.dependencies) if task.dependencies else "",
                        task.details or "",
                        task.test_strategy or "",
                        len(task.subtasks),
                    ]
                )

        console.print(f"[SUCCESS] Tasks exported to {output_path}", style="green")
    except Exception as e:
        console.print(
            f"[ERROR] Error exporting tasks to CSV: {str(e)}", style="bold red"
        )
        raise


def export_tasks_to_markdown(
    tasks_path: str,
    output_path: str,
    options: Optional[Dict] = None,
) -> None:
    """
    Export tasks to a Markdown file.

    Args:
        tasks_path (str): Path to the tasks.json file
        output_path (str): Path to the output Markdown file
        options (Optional[Dict], optional): Additional options. Defaults to None.
    """
    try:
        # Read tasks
        console.print("[INFO] Reading tasks from {}...".format(tasks_path))
        tasks = read_tasks(tasks_path)

        if not tasks.tasks:
            console.print(
                "[ERROR] No tasks found in {}".format(tasks_path), style="bold red"
            )
            return

        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Write tasks to Markdown
        with open(output_path, "w") as f:
            # Write header
            f.write("# Task List\n\n")

            # Write tasks
            for task in tasks.tasks:
                f.write(f"## {task.id}: {task.title}\n\n")
                f.write(f"**Status:** {task.status}\n\n")
                f.write(f"**Priority:** {task.priority}\n\n")
                f.write(
                    f"**Dependencies:** {', '.join(task.dependencies) if task.dependencies else 'None'}\n\n"
                )
                f.write(f"**Description:** {task.description}\n\n")

                if task.details:
                    f.write("### Implementation Details\n\n")
                    f.write(f"{task.details}\n\n")

                if task.test_strategy:
                    f.write("### Test Strategy\n\n")
                    f.write(f"{task.test_strategy}\n\n")

                if task.subtasks:
                    f.write("### Subtasks\n\n")
                    for subtask in task.subtasks:
                        f.write(
                            f"- **{subtask.id}:** {subtask.title} ({subtask.status})\n"
                        )
                    f.write("\n")

        console.print(f"[SUCCESS] Tasks exported to {output_path}", style="green")
    except Exception as e:
        console.print(
            f"[ERROR] Error exporting tasks to Markdown: {str(e)}", style="bold red"
        )
        raise


# Register plugins
register_plugin("export_to_csv", export_tasks_to_csv)
register_plugin("export_to_markdown", export_tasks_to_markdown)


# Add CLI command functions
def export_to_csv_command(
    tasks_path: str,
    output_path: str,
    options: Optional[Dict] = None,
) -> None:
    """
    CLI command to export tasks to a CSV file.

    Args:
        tasks_path (str): Path to the tasks.json file
        output_path (str): Path to the output CSV file
        options (Optional[Dict], optional): Additional options. Defaults to None.
    """
    export_tasks_to_csv(tasks_path, output_path, options)


def export_to_markdown_command(
    tasks_path: str,
    output_path: str,
    options: Optional[Dict] = None,
) -> None:
    """
    CLI command to export tasks to a Markdown file.

    Args:
        tasks_path (str): Path to the tasks.json file
        output_path (str): Path to the output Markdown file
        options (Optional[Dict], optional): Additional options. Defaults to None.
    """
    export_tasks_to_markdown(tasks_path, output_path, options)
