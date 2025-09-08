"""
Set status command implementation for Taskinator.
"""

import json
import os
from typing import Dict, List, Optional

from rich.box import ROUNDED, Box
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

# Define color constants
STATUS_COLORS = {
    "done": "green",
    "in-progress": "blue",
    "pending": "yellow",
    "blocked": "red",
    "deferred": "magenta",
    "cancelled": "dim",
}

STATUS_INDICATORS = {
    "done": "✓",
    "in-progress": "►",
    "pending": "○",
    "blocked": "!",
    "deferred": "⏱",
    "cancelled": "✗",
}

VALID_STATUSES = ["done", "in-progress", "pending", "blocked", "deferred", "cancelled"]


def get_status_with_color(status: str) -> Text:
    """
    Get a colored status string.

    Args:
        status (str): Status string

    Returns:
        Text: Colored status string
    """
    color = STATUS_COLORS.get(status, "white")
    indicator = STATUS_INDICATORS.get(status, "?")

    return Text(f"{indicator} {status}", style=color)


def set_status_standalone(tasks_path: str, task_id: str, status: str) -> None:
    """
    Update the status of a task.

    This is a standalone implementation that doesn't rely on any other functions
    to avoid circular dependencies.

    Args:
        tasks_path (str): Path to the tasks.json file
        task_id (str): ID of the task to update
        status (str): New status for the task
    """
    try:
        # Validate status
        if status not in VALID_STATUSES:
            valid_statuses_str = ", ".join(
                [f"[{STATUS_COLORS.get(s, 'white')}]{s}[/]" for s in VALID_STATUSES]
            )
            console.print(
                f"[ERROR] Invalid status: {status}. Valid statuses are: {valid_statuses_str}",
                style="bold red",
            )
            return

        # Read tasks directly from file
        console.print(f"[INFO] Reading tasks from {tasks_path}...")

        if not os.path.exists(tasks_path):
            console.print(
                f"[ERROR] Tasks file {tasks_path} does not exist", style="bold red"
            )
            return

        with open(tasks_path, "r") as f:
            data = json.load(f)

        tasks = data.get("tasks", [])

        if not tasks:
            console.print("[ERROR] No tasks found", style="bold red")
            return

        # Check if this is a subtask ID (format: parent_id.subtask_index)
        if "." in task_id:
            parent_id, subtask_idx = task_id.split(".")

            # Find the parent task
            parent_task = None
            for task in tasks:
                if str(task["id"]) == parent_id:
                    parent_task = task
                    break

            if not parent_task:
                console.print(
                    f"[ERROR] Parent task with ID {parent_id} not found",
                    style="bold red",
                )
                return

            # Find the subtask
            subtasks = parent_task.get("subtasks", [])

            try:
                subtask_idx = int(subtask_idx) - 1  # Convert to 0-based index
                if subtask_idx < 0 or subtask_idx >= len(subtasks):
                    console.print(
                        f"[ERROR] Subtask index {subtask_idx + 1} out of range for task {parent_id}",
                        style="bold red",
                    )
                    return

                old_status = subtasks[subtask_idx].get("status", "pending")
                subtasks[subtask_idx]["status"] = status

                # Create task update panel
                old_status_text = get_status_with_color(old_status)
                new_status_text = get_status_with_color(status)

                panel_content = Text()
                panel_content.append(f"Subtask #{task_id} status updated from ")
                panel_content.append(old_status_text)
                panel_content.append(" to ")
                panel_content.append(new_status_text)

                panel = Panel(
                    panel_content,
                    title="Status Updated",
                    width=80,
                    border_style="green",
                    box=ROUNDED,
                )

                # Write updated tasks back to file
                with open(tasks_path, "w") as f:
                    json.dump(data, f, indent=2)

                console.print(panel)

            except ValueError:
                console.print(
                    f"[ERROR] Invalid subtask index: {subtask_idx + 1}",
                    style="bold red",
                )
                return

        else:
            # Find the task by ID
            task_found = False
            for task in tasks:
                if str(task["id"]) == str(task_id):
                    old_status = task.get("status", "pending")
                    task["status"] = status
                    task_found = True
                    break

            if not task_found:
                console.print(
                    f"[ERROR] Task with ID {task_id} not found", style="bold red"
                )
                return

            # Write updated tasks back to file
            with open(tasks_path, "w") as f:
                json.dump(data, f, indent=2)

            # Create task update panel
            old_status_text = get_status_with_color(old_status)
            new_status_text = get_status_with_color(status)

            panel_content = Text()
            panel_content.append(f"Task #{task_id} status updated from ")
            panel_content.append(old_status_text)
            panel_content.append(" to ")
            panel_content.append(new_status_text)

            panel = Panel(
                panel_content,
                title="Status Updated",
                width=80,
                border_style="green",
                box=ROUNDED,
            )

            console.print(panel)

            # Update task file if it exists
            task_file_path = os.path.join(
                os.path.dirname(tasks_path), f"task_{task_id.zfill(3)}.txt"
            )
            if os.path.exists(task_file_path):
                with open(task_file_path, "r") as f:
                    content = f.read()

                # Update status in the task file
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if line.startswith("# Status:"):
                        lines[i] = f"# Status: {status}"
                        break

                with open(task_file_path, "w") as f:
                    f.write("\n".join(lines))

                console.print(f"[INFO] Updated status in task file: {task_file_path}")

    except Exception as e:
        console.print(f"[ERROR] Error updating task status: {str(e)}", style="bold red")
        raise


def set_status_command(task_id: str, status: str) -> None:
    """
    Update the status of a task.

    This is a standalone implementation that doesn't rely on any other functions
    to avoid circular dependencies.

    Args:
        task_id (str): ID of the task to update
        status (str): New status for the task
    """
    try:
        tasks_path = os.path.join(os.getcwd(), "tasks", "tasks.json")
        set_status_standalone(tasks_path, task_id, status)
    except Exception as e:
        console.print(f"[ERROR] Error updating task status: {str(e)}", style="bold red")
