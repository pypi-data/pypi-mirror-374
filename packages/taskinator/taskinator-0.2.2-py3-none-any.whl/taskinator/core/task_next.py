"""
Next task functionality for Taskinator.
"""

from typing import Dict, List, Optional, Union

from rich.box import ROUNDED
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from taskinator.core.task_manager import read_tasks
from taskinator.models.task import Task, TaskCollection
from taskinator.utils.ui import (
    create_progress_bar,
    format_dependencies_with_status,
    get_status_with_color,
)

console = Console()


def find_next_task(tasks_path: str) -> Optional[Dict]:
    """
    Find the next task to work on based on dependencies and priority.

    Args:
        tasks_path (str): Path to the tasks.json file

    Returns:
        Optional[Dict]: Next task data if found, None otherwise
    """
    try:
        # Read tasks
        console.print("[INFO] Reading tasks from {}...".format(tasks_path))
        tasks = read_tasks(tasks_path)

        if not tasks.tasks:
            console.print(
                "[ERROR] No tasks found in {}".format(tasks_path), style="bold red"
            )
            return None

        # Find tasks that are ready to work on (all dependencies are done)
        ready_tasks = []

        # Create a lookup dictionary for tasks by ID
        task_lookup = {str(task.id): task for task in tasks.tasks}

        for task in tasks.tasks:
            # Skip tasks that are already done or cancelled
            if task.status in ["done", "cancelled"]:
                continue

            # Check if all dependencies are done
            all_deps_done = True
            for dep_id in task.dependencies:
                # Use the lookup dictionary instead of searching the list each time
                dep_task = task_lookup.get(str(dep_id))
                if not dep_task or dep_task.status != "done":
                    all_deps_done = False
                    break

            if all_deps_done:
                ready_tasks.append(task)

        if not ready_tasks:
            console.print("[INFO] No tasks ready to work on", style="yellow")
            return None

        # Sort ready tasks by priority and ID
        priority_order = {"high": 0, "medium": 1, "low": 2}
        ready_tasks.sort(
            key=lambda t: (
                priority_order.get(t.priority, 3),
                int(t.id) if str(t.id).isdigit() else t.id,
            )
        )

        # Return the first ready task
        next_task = ready_tasks[0]

        # Display the next task
        display_next_task(next_task, tasks)

        return {
            "id": str(next_task.id),
            "title": next_task.title,
            "status": next_task.status,
            "priority": next_task.priority,
            "dependencies": [str(dep) for dep in next_task.dependencies],
            "description": next_task.description,
        }
    except Exception as e:
        console.print(f"[ERROR] Error finding next task: {str(e)}", style="bold red")
        raise


def display_next_task(task: Task, tasks: TaskCollection) -> None:
    """
    Display the next task panel.

    Args:
        task (Task): Task to display
        tasks (TaskCollection): Collection of tasks
    """
    # Create the next task panel
    panel_content = f"""
🔥 Next Task to Work On: #{task.id} - {task.title}

Priority: {task.priority}   Status: {task.status}
Dependencies: {format_dependencies_with_status(task.dependencies, tasks)}

Description: {task.description}

"""

    # Add subtasks if available
    if task.subtasks:
        subtasks_content = "\nSubtasks:\n"
        for i, subtask in enumerate(task.subtasks, 1):
            status_indicator = {
                "done": "✓",
                "in-progress": "►",
                "pending": "○",
                "blocked": "!",
                "deferred": "⏱",
                "cancelled": "✗",
            }.get(subtask.status, "?")
            subtasks_content += (
                f"{i} [{status_indicator} {subtask.status}] {subtask.title}\n"
            )
        panel_content += subtasks_content

    # Add suggested actions
    panel_content += f"""

Start working: taskinator set-status --id={task.id} --status=in-progress
View details: taskinator show {task.id}
"""

    panel = Panel(
        panel_content,
        title="⚡ RECOMMENDED NEXT TASK ⚡",
        width=100,
        border_style="cyan",
    )
    console.print(panel)

    # Display task details
    console.print(Panel(f"Task: #{task.id} - {task.title}", style="bold cyan"))

    # Create a table for task details
    table = Table(show_header=False, box=ROUNDED, width=120)
    table.add_column("Field", style="bold cyan")
    table.add_column("Value")

    # Add task details to the table
    table.add_row("ID:", str(task.id))
    table.add_row("Title:", task.title)
    table.add_row("Status:", get_status_with_color(task.status))

    # Priority
    priority_color = {
        "high": "red",
        "medium": "yellow",
        "low": "green",
    }.get(task.priority, "white")
    table.add_row("Priority:", f"[{priority_color}]{task.priority}[/]")

    # Dependencies
    deps_text = format_dependencies_with_status(task.dependencies, tasks)
    table.add_row("Dependencies:", deps_text)

    # Description
    table.add_row("Description:", task.description)

    console.print(table)

    # Display implementation details if available
    if task.details:
        console.print(
            Panel(
                f"Implementation Details:\n\n{task.details}",
                width=120,
                title="",
            )
        )

    # Display test strategy if available
    if task.test_strategy:
        console.print(
            Panel(
                f"Test Strategy:\n\n{task.test_strategy}",
                width=120,
                title="",
            )
        )

    # Display subtasks if available
    if task.subtasks:
        console.print(Panel("[bold]Subtasks[/]", style="bold cyan"))

        subtask_table = Table(show_header=True, header_style="bold cyan")
        subtask_table.add_column("ID", style="bold cyan")
        subtask_table.add_column("Status", style="bold magenta")
        subtask_table.add_column("Title", style="bold white")
        subtask_table.add_column("Deps", style="dim")

        for subtask in task.subtasks:
            subtask_deps = (
                "None"
                if not subtask.dependencies
                else ", ".join(str(dep) for dep in subtask.dependencies)
            )
            status_color = {
                "done": "green",
                "in-progress": "blue",
                "pending": "yellow",
                "blocked": "red",
                "deferred": "magenta",
                "cancelled": "dim",
            }.get(subtask.status, "white")
            status_indicator = {
                "done": "✓",
                "in-progress": "►",
                "pending": "○",
                "blocked": "!",
                "deferred": "⏱",
                "cancelled": "✗",
            }.get(subtask.status, "?")

            subtask_table.add_row(
                f"{task.id}.{subtask.id}",
                f"[{status_color}]{status_indicator} {subtask.status}[/]",
                subtask.title,
                subtask_deps,
            )

        console.print(subtask_table)

        # Display subtask progress
        done_count = sum(1 for s in task.subtasks if s.status == "done")
        total_count = len(task.subtasks)
        percentage = (done_count / total_count) * 100 if total_count > 0 else 0

        status_counts = {
            "done": sum(1 for s in task.subtasks if s.status == "done"),
            "in-progress": sum(1 for s in task.subtasks if s.status == "in-progress"),
            "pending": sum(1 for s in task.subtasks if s.status == "pending"),
            "blocked": sum(1 for s in task.subtasks if s.status == "blocked"),
            "deferred": sum(1 for s in task.subtasks if s.status == "deferred"),
            "cancelled": sum(1 for s in task.subtasks if s.status == "cancelled"),
        }

        progress_text = f"""
[bold]Subtask Progress:[/]

Completed: [cyan]{done_count}/{total_count} ({percentage:.1f}%)[/]
[green]✓ Done: {status_counts["done"]}[/]  [blue]► In Progress: {status_counts["in-progress"]}[/]  [yellow]○ Pending: {status_counts["pending"]}[/]
[red]! Blocked: {status_counts["blocked"]}[/]  [magenta]⏱ Deferred: {status_counts["deferred"]}[/]  [dim]✗ Cancelled: {status_counts["cancelled"]}[/]
Progress: {create_progress_bar(done_count, total_count)} [cyan]{percentage:.0f}%[/]
"""
        console.print(Panel(progress_text, width=120))


def next_task_command(tasks_path: str) -> None:
    """
    Display the next task to work on based on dependencies and priority.

    Args:
        tasks_path (str): Path to the tasks.json file
    """
    try:
        find_next_task(tasks_path)
    except Exception as e:
        console.print(f"[ERROR] Error finding next task: {str(e)}", style="bold red")
        raise
