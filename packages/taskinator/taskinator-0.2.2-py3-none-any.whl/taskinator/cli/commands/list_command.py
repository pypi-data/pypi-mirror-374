"""
List command implementation for Taskinator.
"""

import json
import math
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import tomli
from rich.box import ROUNDED
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
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

STATUS_INDICATORS = {
    "done": "✓",
    "in-progress": "►",
    "pending": "○",
    "blocked": "!",
    "deferred": "⏱",
    "cancelled": "✗",
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
    indicator = STATUS_INDICATORS.get(status, "?")

    return Text(f"{indicator} {status}", style=color)


def create_progress_bar(percentage: float, width: int = 25) -> str:
    """
    Create a progress bar string.

    Args:
        percentage (float): Percentage of completion (0-100)
        width (int, optional): Width of the progress bar. Defaults to 25.

    Returns:
        str: Progress bar string
    """
    filled = math.floor(percentage * width / 100)
    empty = width - filled
    return "█" * filled + "░" * empty


def get_dependency_metrics(tasks: List[Dict]) -> Dict:
    """
    Calculate dependency metrics for tasks.

    Args:
        tasks (List[Dict]): List of tasks

    Returns:
        Dict: Dictionary of dependency metrics
    """
    task_lookup = {str(task["id"]): task for task in tasks}

    # Count tasks with no dependencies
    no_deps = len([task for task in tasks if not task.get("dependencies")])

    # Count tasks ready to work on
    ready_tasks = []
    for task in tasks:
        if task.get("status") in ["done", "cancelled"]:
            continue

        all_deps_done = True
        for dep_id in task.get("dependencies", []):
            dep_task = task_lookup.get(str(dep_id))
            if not dep_task or dep_task.get("status") != "done":
                all_deps_done = False
                break

        if all_deps_done:
            ready_tasks.append(task)

    ready_count = len(ready_tasks)

    # Count tasks blocked by dependencies
    blocked_count = len(
        [
            task
            for task in tasks
            if task.get("status") not in ["done", "cancelled"]
            and task not in ready_tasks
        ]
    )

    # Find most depended-on task
    dependents = {}
    for task in tasks:
        for dep_id in task.get("dependencies", []):
            dependents[str(dep_id)] = dependents.get(str(dep_id), 0) + 1

    most_depended_id = None
    most_dependents = 0
    for task_id, count in dependents.items():
        if count > most_dependents:
            most_depended_id = task_id
            most_dependents = count

    # Calculate average dependencies per task
    total_deps = sum(len(task.get("dependencies", [])) for task in tasks)
    avg_deps = round(total_deps / len(tasks), 1) if tasks else 0

    return {
        "no_deps": no_deps,
        "ready_count": ready_count,
        "blocked_count": blocked_count,
        "most_depended_id": most_depended_id,
        "most_dependents": most_dependents,
        "avg_deps": avg_deps,
    }


def get_next_task(tasks: List[Dict]) -> Optional[Dict]:
    """
    Get the next task to work on.

    Args:
        tasks (List[Dict]): List of tasks

    Returns:
        Optional[Dict]: Next task or None if no task is ready
    """
    task_lookup = {str(task["id"]): task for task in tasks}

    # Find tasks that are ready to work on
    ready_tasks = []
    for task in tasks:
        if task.get("status") in ["done", "cancelled"]:
            continue

        all_deps_done = True
        for dep_id in task.get("dependencies", []):
            dep_task = task_lookup.get(str(dep_id))
            if not dep_task or dep_task.get("status") != "done":
                all_deps_done = False
                break

        if all_deps_done:
            ready_tasks.append(task)

    if not ready_tasks:
        return None

    # Sort by priority and ID
    priority_order = {"high": 0, "medium": 1, "low": 2}
    ready_tasks.sort(
        key=lambda t: (
            priority_order.get(t.get("priority", "medium"), 3),
            # Safely handle task IDs that might be strings or integers
            # First convert everything to string for consistent comparison
            str(t["id"]),
        )
    )

    return ready_tasks[0]


def list_tasks_standalone(
    tasks_path: str,
    status_filter: Optional[str] = None,
    with_subtasks: bool = False,
    priority: Optional[str] = None,
    with_hierarchy: bool = False,
) -> None:
    """
    List all tasks with their status.

    This is a standalone implementation that doesn't rely on any other functions
    to avoid circular dependencies.

    Args:
        tasks_path (str): Path to the tasks.json file
        status_filter (str, optional): Filter tasks by status. Defaults to None.
        with_subtasks (bool, optional): Whether to include subtasks. Defaults to False.
        priority (str, optional): Filter tasks by priority. Defaults to None.
        with_hierarchy (bool, optional): Whether to display document hierarchy relationships. Defaults to False.
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
        metadata = data.get("metadata", {})
        project_name = metadata.get("project_name", os.path.basename(os.getcwd()))

        # Filter tasks by status if specified
        if status_filter:
            tasks = [t for t in tasks if t.get("status", "pending") == status_filter]

        # Filter tasks by priority if specified
        if priority:
            tasks = [
                t
                for t in tasks
                if t.get("priority", "medium").lower() == priority.lower()
            ]

        # Count tasks by status
        status_counts = {}
        for task in tasks:
            status = task.get("status", "pending")
            status_counts[status] = status_counts.get(status, 0) + 1

        # Count tasks by priority
        priority_counts = {}
        for task in tasks:
            priority_val = task.get("priority", "medium")
            priority_counts[priority_val] = priority_counts.get(priority_val, 0) + 1

        # Get all subtasks if requested
        subtasks = []
        if with_subtasks:
            for task in tasks:
                if "subtasks" in task:
                    subtasks.extend(task["subtasks"])

        # Count subtasks by status
        subtask_status_counts = {}
        for subtask in subtasks:
            status = subtask.get("status", "pending")
            subtask_status_counts[status] = subtask_status_counts.get(status, 0) + 1

        # Calculate dependency metrics
        dependency_metrics = get_dependency_metrics(tasks)

        # Find the next task to work on
        next_task = get_next_task(tasks)

        # Prepare the next task information section based on whether we have a next task
        next_task_info = ""
        if next_task is not None:
            next_task_info = (
                f"[bold]Next Task to Work On:[/bold]\n"
                f"ID: {next_task['id']} - {next_task['title'][:40] + '...' if len(next_task['title']) > 40 else next_task['title']}\n"
                f"Priority: {next_task.get('priority', 'medium')}  "
                f"Dependencies: {', '.join(map(str, next_task.get('dependencies', []))) if next_task.get('dependencies') else 'None'}"
            )
        else:
            next_task_info = f"[bold]Next Task to Work On:[/bold]\nNo tasks ready to work on."

        # Display the dashboard
        console.print(
            Panel(
                f"[bold]Project: {project_name}[/bold]\n\n"
                f"[bold]Task Progress:[/bold]\n"
                f"Total Tasks: {len(tasks)}\n"
                f"Done: {status_counts.get('done', 0)}  "
                f"In Progress: {status_counts.get('in-progress', 0)}  "
                f"Pending: {status_counts.get('pending', 0)}  "
                f"Blocked: {dependency_metrics['blocked_count']}\n\n"
                f"[bold]Priority Breakdown:[/bold]\n"
                f"High: {priority_counts.get('high', 0)}  "
                f"Medium: {priority_counts.get('medium', 0)}  "
                f"Low: {priority_counts.get('low', 0)}\n\n"
                f"[bold]Dependency Status:[/bold]\n"
                f"Tasks with no dependencies: {dependency_metrics['no_deps']}\n"
                f"Tasks ready to work on: {dependency_metrics['ready_count']}\n"
                f"Tasks blocked by dependencies: {dependency_metrics['blocked_count']}\n"
                f"Average dependencies per task: {dependency_metrics['avg_deps']:.1f}\n\n"
                f"{next_task_info}"
                + (
                    f"\n\n[bold]Subtask Progress:[/bold]\n"
                    f"Total Subtasks: {len(subtasks)}\n"
                    f"Done: {subtask_status_counts.get('done', 0)}  "
                    f"In Progress: {subtask_status_counts.get('in-progress', 0)}  "
                    f"Pending: {subtask_status_counts.get('pending', 0)}"
                    if with_subtasks
                    else ""
                ),
                title="[bold]Taskinator Dashboard[/bold]",
                border_style="cyan",
            )
        )

        # Create a table for tasks
        table = Table(title="Tasks", box=ROUNDED, border_style="cyan")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Title", style="white")
        table.add_column("Status", style="green")
        table.add_column("Priority", style="yellow")
        table.add_column("Dependencies", style="magenta")

        # Add document hierarchy column if requested
        if with_hierarchy:
            table.add_column("Source", style="blue")

        # Add rows for each task
        for task in tasks:
            task_id = task.get("id", "")
            title = task.get("title", "")
            status = task.get("status", "pending")
            priority = task.get("priority", "medium")
            dependencies = (
                ", ".join(map(str, task.get("dependencies", [])))
                if task.get("dependencies")
                else "None"
            )

            # Style based on status
            if status == "done":
                status_style = "green"
            elif status == "in-progress":
                status_style = "yellow"
            elif status == "blocked":
                status_style = "red"
            else:
                status_style = "white"

            # Add the row with appropriate columns
            if with_hierarchy:
                source = "N/A"
                if "source" in task:
                    source_type = task["source"].get("type", "").upper()
                    document = task["source"].get("document", "")
                    section = task["source"].get("section", "")
                    source = f"{source_type}: {os.path.basename(document)}"
                    if section:
                        source += f" - {section}"
                table.add_row(
                    str(task_id),
                    title,
                    f"[{status_style}]{status}[/{status_style}]",
                    priority,
                    dependencies,
                    source,
                )
            else:
                table.add_row(
                    str(task_id),
                    title,
                    f"[{status_style}]{status}[/{status_style}]",
                    priority,
                    dependencies,
                )

            # Add subtasks if requested
            if with_subtasks and "subtasks" in task:
                for subtask in task["subtasks"]:
                    subtask_id = subtask.get("id", "")
                    subtask_title = subtask.get("title", "")
                    subtask_status = subtask.get("status", "pending")
                    subtask_priority = subtask.get(
                        "priority", priority
                    )  # Inherit from parent if not specified
                    subtask_dependencies = (
                        ", ".join(map(str, subtask.get("dependencies", [])))
                        if subtask.get("dependencies")
                        else "None"
                    )

                    # Style based on status
                    if subtask_status == "done":
                        subtask_status_style = "green"
                    elif subtask_status == "in-progress":
                        subtask_status_style = "yellow"
                    elif subtask_status == "blocked":
                        subtask_status_style = "red"
                    else:
                        subtask_status_style = "white"

                    # Add the row with appropriate indentation
                    if with_hierarchy:
                        source = "N/A"
                        if "source" in subtask:
                            source_type = subtask["source"].get("type", "").upper()
                            document = subtask["source"].get("document", "")
                            section = subtask["source"].get("section", "")
                            source = f"{source_type}: {os.path.basename(document)}"
                            if section:
                                source += f" - {section}"
                        table.add_row(
                            f"  {subtask_id}",
                            f"  {subtask_title}",
                            f"[{subtask_status_style}]{subtask_status}[/{subtask_status_style}]",
                            subtask_priority,
                            subtask_dependencies,
                            source,
                        )
                    else:
                        table.add_row(
                            f"  {subtask_id}",
                            f"  {subtask_title}",
                            f"[{subtask_status_style}]{subtask_status}[/{subtask_status_style}]",
                            subtask_priority,
                            subtask_dependencies,
                        )

        console.print(table)

        # Display document hierarchy information if requested
        if with_hierarchy:
            document_hierarchy = metadata.get("documentHierarchy", {})
            if document_hierarchy:
                hierarchy_table = Table(
                    title="Document Hierarchy", box=ROUNDED, border_style="blue"
                )
                hierarchy_table.add_column("Type", style="cyan")
                hierarchy_table.add_column("Document", style="white")

                for doc_type, doc_path in document_hierarchy.items():
                    hierarchy_table.add_row(doc_type.upper(), doc_path)

                console.print(hierarchy_table)

        # Display Next Steps section with help text
        console.print(
            Panel(
                "Run [bold cyan]taskinator show <id>[/bold cyan] to view detailed information about a specific task.\n"
                "Run [bold cyan]taskinator set-status --id=<id> --status=<status>[/bold cyan] to update task status.\n"
                "Run [bold cyan]taskinator expand-task --id=<id>[/bold cyan] to break down a task into subtasks.",
                title="[bold]Next Steps[/bold]",
                border_style="cyan",
            )
        )
    except Exception as e:
        console.print(f"[ERROR] Error listing tasks: {str(e)}", style="bold red")
        raise


def list_command(
    status: Optional[str] = None,
    with_subtasks: bool = False,
    priority: Optional[str] = None,
    with_hierarchy: bool = False,
) -> None:
    """
    List all tasks with their status.

    This is a standalone implementation that doesn't rely on any other functions
    to avoid circular dependencies.

    Args:
        status (str, optional): Filter tasks by status. Defaults to None.
        with_subtasks (bool, optional): Whether to include subtasks. Defaults to False.
        priority (str, optional): Filter tasks by priority. Defaults to None.
        with_hierarchy (bool, optional): Whether to display document hierarchy relationships. Defaults to False.
    """
    try:
        tasks_path = os.path.join(os.getcwd(), "tasks", "tasks.json")
        list_tasks_standalone(
            tasks_path, status, with_subtasks, priority, with_hierarchy
        )
    except Exception as e:
        console.print(f"[ERROR] Error listing tasks: {str(e)}", style="bold red")
        raise
