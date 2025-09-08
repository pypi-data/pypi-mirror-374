"""
Next task command implementation for Taskinator.
"""

import json
import os
from typing import Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

# Define color constants
PRIORITY_COLORS = {
    "high": "red",
    "medium": "yellow",
    "low": "green",
}

STATUS_COLORS = {
    "done": "green",
    "in-progress": "blue",
    "pending": "yellow",
    "blocked": "red",
    "deferred": "magenta",
    "cancelled": "dim",
}


def get_status_with_color(status: str) -> Text:
    """
    Get a colored status string.

    Args:
        status (str): Status string

    Returns:
        Text: Colored status string
    """
    color = STATUS_COLORS.get(status, "white")
    indicator = {
        "done": "✓",
        "in-progress": "►",
        "pending": "○",
        "blocked": "!",
        "deferred": "⏱",
        "cancelled": "✗",
    }.get(status, "?")

    return Text(f"{indicator} {status}", style=color)


def find_next_task(tasks_path: str) -> None:
    """
    Find and display the next task to work on.

    This is a standalone implementation that doesn't rely on any other functions
    to avoid circular dependencies.

    Args:
        tasks_path (str): Path to the tasks.json file
    """
    try:
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

        # Create a lookup dictionary for tasks by ID
        task_lookup = {str(task["id"]): task for task in tasks}

        # Find tasks that are ready to work on (all dependencies are done)
        ready_tasks = []

        for task in tasks:
            # Skip tasks that are already done or cancelled
            if task.get("status") in ["done", "cancelled"]:
                continue

            # Check if all dependencies are done
            all_deps_done = True
            for dep_id in task.get("dependencies", []):
                dep_task = task_lookup.get(str(dep_id))
                if not dep_task or dep_task.get("status") != "done":
                    all_deps_done = False
                    break

            if all_deps_done:
                ready_tasks.append(task)

        if not ready_tasks:
            console.print("[INFO] No tasks ready to work on", style="yellow")
            return

        # Sort ready tasks by priority and ID
        priority_order = {"high": 0, "medium": 1, "low": 2}
        ready_tasks.sort(
            key=lambda t: (
                priority_order.get(t.get("priority", "medium"), 3),
                int(t["id"]) if str(t["id"]).isdigit() else t["id"],
            )
        )

        # Get the next task
        next_task = ready_tasks[0]

        # Format dependencies with status
        dependencies_text = Text("None")
        if next_task.get("dependencies"):
            deps = []
            deps_text = Text()
            first = True

            for dep_id in next_task.get("dependencies", []):
                dep_task = task_lookup.get(str(dep_id))
                if dep_task:
                    if not first:
                        deps_text.append(", ")

                    deps_text.append(str(dep_id))
                    deps_text.append(" (")

                    status = dep_task.get("status", "unknown")
                    status_color = STATUS_COLORS.get(status, "white")
                    status_symbol = "✓" if status == "done" else "○"

                    deps_text.append(status_symbol, style=status_color)
                    deps_text.append(")")

                    first = False

            if not first:  # If we added any dependencies
                dependencies_text = deps_text

        # Create title text
        title_text = Text(
            f"🔥 Next Task to Work On: #{next_task['id']} - {next_task['title']}"
        )

        # Create priority text
        priority = next_task.get("priority", "medium")
        priority_color = PRIORITY_COLORS.get(priority, "white")
        priority_text = Text("Priority: ")
        priority_text.append(priority, style=priority_color)

        # Create status text
        status = next_task.get("status", "pending")
        status_color = STATUS_COLORS.get(status, "white")
        status_indicator = {
            "done": "✓",
            "in-progress": "►",
            "pending": "○",
            "blocked": "!",
            "deferred": "⏱",
            "cancelled": "✗",
        }.get(status, "?")

        status_text = Text("Status: ")
        status_text.append(f"{status_indicator} {status}", style=status_color)

        # Create dependencies text
        deps_label = Text("Dependencies: ")

        # Create description text
        description_text = Text(f"Description: {next_task.get('description', '')}")

        # Create panel content
        panel_content = Text()
        panel_content.append(title_text)
        panel_content.append("\n\n")
        panel_content.append(priority_text)
        panel_content.append("   ")
        panel_content.append(status_text)
        panel_content.append("\n")
        panel_content.append(deps_label)
        panel_content.append(dependencies_text)
        panel_content.append("\n\n")
        panel_content.append(description_text)
        panel_content.append("\n\n")

        # Add subtasks if available
        if next_task.get("subtasks"):
            subtasks_label = Text("Subtasks:\n")
            panel_content.append(subtasks_label)

            for i, subtask in enumerate(next_task.get("subtasks", []), 1):
                subtask_text = Text(f"{i} [")

                status = subtask.get("status", "pending")
                status_color = STATUS_COLORS.get(status, "white")
                status_indicator = {
                    "done": "✓",
                    "in-progress": "►",
                    "pending": "○",
                    "blocked": "!",
                    "deferred": "⏱",
                    "cancelled": "✗",
                }.get(status, "?")

                subtask_text.append(f"{status_indicator} {status}", style=status_color)
                subtask_text.append(f"] {subtask.get('title', '')}")
                subtask_text.append("\n")

                panel_content.append(subtask_text)

            panel_content.append("\n")

        # Add suggested actions
        start_cmd = Text("Start working: ")
        start_cmd.append(
            f"taskinator set-status --id={next_task['id']} --status=in-progress",
            style="cyan",
        )

        view_cmd = Text("View details: ")
        view_cmd.append(f"taskinator show {next_task['id']}", style="cyan")

        panel_content.append(start_cmd)
        panel_content.append("\n")
        panel_content.append(view_cmd)

        # Create the panel
        panel = Panel(
            panel_content,
            title="⚡ RECOMMENDED NEXT TASK ⚡",
            width=100,
            border_style="cyan",
        )

        console.print(panel)

    except Exception as e:
        console.print(f"[ERROR] Error finding next task: {str(e)}", style="bold red")
        raise


def next_command() -> None:
    """
    Display the next task to work on.

    This is a standalone implementation that doesn't rely on any other functions
    to avoid circular dependencies.
    """
    try:
        tasks_path = os.path.join(os.getcwd(), "tasks", "tasks.json")
        find_next_task(tasks_path)
    except Exception as e:
        console.print(f"[ERROR] Error finding next task: {str(e)}", style="bold red")
