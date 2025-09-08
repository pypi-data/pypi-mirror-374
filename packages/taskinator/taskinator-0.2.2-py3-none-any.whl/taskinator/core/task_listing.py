"""
Task listing functionality for Taskinator.
"""

from typing import Dict, List, Optional, Union

from rich.box import ROUNDED
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from taskinator.core.task_manager import find_task_by_id, read_tasks
from taskinator.models.task import Task, TaskCollection
from taskinator.utils.config import get_config
from taskinator.utils.ui import (
    create_progress_bar,
    format_dependencies_with_status,
    get_status_with_color,
)

console = Console()
config = get_config()

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


def list_tasks(
    tasks_path: str,
    status_filter: Optional[str] = None,
    with_subtasks: bool = False,
    output_format: str = "text",
) -> Optional[Dict]:
    """
    List all tasks with their status.

    Args:
        tasks_path (str): Path to the tasks.json file
        status_filter (Optional[str], optional): Filter tasks by status. Defaults to None.
        with_subtasks (bool, optional): Whether to show subtasks. Defaults to False.
        output_format (str, optional): Output format. Defaults to "text".

    Returns:
        Optional[Dict]: Task data in JSON format if output_format is "json", None otherwise
    """
    try:
        # Read tasks
        console.print("[INFO] Reading tasks from {}...".format(tasks_path))
        tasks = read_tasks(tasks_path)

        # Filter tasks by status if requested
        if status_filter:
            filtered_tasks = [t for t in tasks.tasks if t.status == status_filter]
        else:
            filtered_tasks = tasks.tasks

        if output_format == "json":
            # Return tasks as JSON
            return {
                "tasks": [t.dict() for t in filtered_tasks],
                "total": len(filtered_tasks),
            }

        # Create dashboard
        dashboard_panel = _create_dashboard(tasks)
        console.print(dashboard_panel)

        # Create dependency panel
        dependency_panel = _create_dependency_panel(tasks)
        console.print(dependency_panel)

        # Create task table
        _create_task_table(tasks, filtered_tasks, with_subtasks)

        # Create next task panel
        next_task = _find_next_task(tasks)
        if next_task:
            _create_next_task_panel(next_task, tasks)

        # Create suggested steps panel
        _create_suggested_steps_panel()

        return None
    except Exception as e:
        console.print(f"[ERROR] Error listing tasks: {str(e)}", style="bold red")
        raise


def _create_dashboard(tasks: TaskCollection) -> Panel:
    """
    Create the dashboard panel with task statistics.

    Args:
        tasks (TaskCollection): Collection of tasks

    Returns:
        Panel: Dashboard panel
    """
    # Calculate task metrics
    total_tasks = len(tasks.tasks)
    done_tasks = sum(1 for t in tasks.tasks if t.status == "done")
    in_progress_tasks = sum(1 for t in tasks.tasks if t.status == "in-progress")
    pending_tasks = sum(1 for t in tasks.tasks if t.status == "pending")
    blocked_tasks = sum(1 for t in tasks.tasks if t.status == "blocked")
    deferred_tasks = sum(1 for t in tasks.tasks if t.status == "deferred")
    cancelled_tasks = sum(1 for t in tasks.tasks if t.status == "cancelled")

    # Calculate subtask metrics
    all_subtasks = []
    for task in tasks.tasks:
        all_subtasks.extend(task.subtasks)

    total_subtasks = len(all_subtasks)
    done_subtasks = sum(1 for s in all_subtasks if s.status == "done")
    in_progress_subtasks = sum(1 for s in all_subtasks if s.status == "in-progress")
    pending_subtasks = sum(1 for s in all_subtasks if s.status == "pending")
    blocked_subtasks = sum(1 for s in all_subtasks if s.status == "blocked")
    deferred_subtasks = sum(1 for s in all_subtasks if s.status == "deferred")
    cancelled_subtasks = sum(1 for s in all_subtasks if s.status == "cancelled")

    # Calculate priority breakdown
    high_priority = sum(1 for t in tasks.tasks if t.priority == "high")
    medium_priority = sum(1 for t in tasks.tasks if t.priority == "medium")
    low_priority = sum(1 for t in tasks.tasks if t.priority == "low")

    # Create progress bars
    task_progress = create_progress_bar(done_tasks, total_tasks, 50)
    subtask_progress = create_progress_bar(done_subtasks, total_subtasks, 50)

    # Calculate percentages
    task_percentage = (done_tasks / total_tasks) * 100 if total_tasks > 0 else 0
    subtask_percentage = (
        (done_subtasks / total_subtasks) * 100 if total_subtasks > 0 else 0
    )

    # Create dashboard text
    dashboard_text = f"""
[bold cyan]Project Dashboard[/]
Tasks Progress: {task_progress} [cyan]{task_percentage:.0f}%[/]
[bold green]Done: {done_tasks}[/]  [bold blue]In Progress: {in_progress_tasks}[/]  [bold yellow]Pending: {pending_tasks}[/]  [bold red]Blocked: {blocked_tasks}[/]
[bold magenta]Deferred: {deferred_tasks}[/]  [dim]Cancelled: {cancelled_tasks}[/]

[bold cyan]Subtasks Progress:[/]
{subtask_progress} [cyan]{subtask_percentage:.0f}%[/]
Completed: [bold cyan]{done_subtasks}/{total_subtasks}[/]  [bold blue]In Progress: {in_progress_subtasks}[/]  [bold yellow]Pending: {pending_subtasks}[/]  [bold red]Blocked: {blocked_subtasks}[/]  [bold magenta]Deferred: {deferred_subtasks}[/]
[dim]Cancelled: {cancelled_subtasks}[/]

[bold cyan]Priority Breakdown:[/]
• [bold red]High priority: {high_priority}[/]
• [bold yellow]Medium priority: {medium_priority}[/]
• [bold green]Low priority: {low_priority}[/]
"""

    # Create dashboard panel
    return Panel(
        dashboard_text,
        width=80,
    )


def _calculate_dependency_metrics(tasks: TaskCollection) -> Dict:
    """
    Calculate dependency metrics for the dashboard.

    Args:
        tasks (TaskCollection): Collection of tasks

    Returns:
        Dict: Dependency metrics
    """
    # Count tasks with no dependencies
    no_dependencies = sum(1 for t in tasks.tasks if not t.dependencies)

    # Count tasks that are ready to work on (all dependencies satisfied)
    ready_tasks = 0
    for task in tasks.tasks:
        if task.status != "pending":
            continue

        # Check if all dependencies are done
        all_deps_done = True
        for dep_id in task.dependencies:
            dep_task = find_task_by_id(tasks, dep_id)
            if not dep_task or dep_task.status != "done":
                all_deps_done = False
                break

        if all_deps_done:
            ready_tasks += 1

    # Count tasks blocked by dependencies
    blocked_tasks = sum(
        1 for t in tasks.tasks if t.status == "pending" and t.dependencies
    )

    # Find the most depended-on task
    dependency_counts = {}
    for task in tasks.tasks:
        for dep_id in task.dependencies:
            dependency_counts[dep_id] = dependency_counts.get(dep_id, 0) + 1

    most_depended_on = "None"
    max_dependents = 0
    for dep_id, count in dependency_counts.items():
        if count > max_dependents:
            most_depended_on = {"id": dep_id, "count": count}
            max_dependents = count

    # Calculate average dependencies per task
    total_dependencies = sum(len(t.dependencies) for t in tasks.tasks)
    avg_dependencies = total_dependencies / len(tasks.tasks) if tasks.tasks else 0

    return {
        "no_dependencies": no_dependencies,
        "ready_tasks": ready_tasks,
        "blocked_tasks": blocked_tasks,
        "most_depended_on": most_depended_on,
        "avg_dependencies": avg_dependencies,
    }


def _create_dependency_panel(tasks: TaskCollection) -> Panel:
    """
    Create the dependency panel with dependency metrics.

    Args:
        tasks (TaskCollection): Collection of tasks

    Returns:
        Panel: Dependency panel
    """
    # Calculate dependency metrics
    metrics = _calculate_dependency_metrics(tasks)

    # Create dependency text
    dependency_text = f"""
[bold cyan]Dependency Metrics[/]
No dependencies: {metrics["no_dependencies"]}
Ready to work on: {metrics["ready_tasks"]}
Blocked by dependencies: {metrics["blocked_tasks"]}
Most depended on: {metrics["most_depended_on"]["id"]} ({metrics["most_depended_on"]["count"]} tasks)
Average dependencies per task: {metrics["avg_dependencies"]:.1f}
"""

    # Create dependency panel
    return Panel(
        dependency_text,
        width=80,
    )


def _create_task_table(
    tasks: TaskCollection,
    filtered_tasks: List[Task],
    with_subtasks: bool,
) -> None:
    """
    Create and display the task table.

    Args:
        tasks (TaskCollection): Collection of tasks
        filtered_tasks (List[Task]): Filtered tasks to display
        with_subtasks (bool): Whether to show subtasks
    """
    # Create table
    table = Table(show_header=True, header_style="bold")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Status", style="white")
    table.add_column("Priority", style="white")
    table.add_column("Dependencies", style="white")

    # Add tasks to table
    for task in filtered_tasks:
        # Format dependencies
        dependencies = "None"
        if task.dependencies:
            dependencies = format_dependencies_with_status(
                task.dependencies, tasks.dict()
            ).plain

        # Add task row with colored status and priority
        table.add_row(
            f"[cyan]{task.id}[/cyan]",
            task.title,
            get_status_with_color(task.status),
            f"[{PRIORITY_COLORS.get(task.priority, 'white')}]{task.priority}[/{PRIORITY_COLORS.get(task.priority, 'white')}]",
            dependencies,
        )

        # Add subtasks if requested
        if with_subtasks and task.subtasks:
            for subtask in task.subtasks:
                # Format subtask dependencies
                subtask_deps = (
                    "None"
                    if not subtask.dependencies
                    else ", ".join(str(dep) for dep in subtask.dependencies)
                )
                status_color = STATUS_COLORS.get(subtask.status, "white")
                status_indicator = {
                    "done": "✓",
                    "in-progress": "►",
                    "pending": "○",
                    "blocked": "!",
                    "deferred": "⏱",
                    "cancelled": "✗",
                }.get(subtask.status, "?")

                # Add subtask row with indentation and colored status
                table.add_row(
                    f"[dim cyan]↳ {task.id}.{subtask.id}[/dim cyan]",
                    f"[dim]{subtask.title}[/dim]",
                    f"[{status_color}]{status_indicator} {subtask.status}[/]",
                    "",  # No priority for subtasks
                    subtask_deps,
                )

    # Display table
    console.print(table)


def _create_next_task_panel(next_task: Dict, tasks: TaskCollection) -> None:
    """
    Create and display the next task panel.

    Args:
        next_task (Dict): Next task data
        tasks (TaskCollection): Collection of tasks
    """
    # Find the task in the collection
    task = None
    for t in tasks.tasks:
        if str(t.id) == next_task["id"]:
            task = t
            break

    if not task:
        return

    # Format dependencies with status
    dependencies_text = "None"
    if task.dependencies:
        dependencies_text = format_dependencies_with_status(
            task.dependencies, tasks.dict()
        ).plain

    # Format subtasks with status
    subtasks_text = ""
    if task.subtasks:
        for subtask in task.subtasks:
            status_text = get_status_with_color(subtask.status).plain
            subtasks_text += f"{subtask.id} [{status_text}] {subtask.title}\n"

    # Create panel
    panel = Panel(
        f"""
[bold]🔥 Next Task to Work On: #{task.id} - {task.title}[/bold]

Priority: [bold {PRIORITY_COLORS.get(task.priority, "white")}]{task.priority}[/bold {PRIORITY_COLORS.get(task.priority, "white")}]   Status: {get_status_with_color(task.status)}
Dependencies: {dependencies_text}

Description: {task.description}

[bold]Subtasks:[/bold]
{subtasks_text}

Start working: [bold cyan]taskinator set-status --id={task.id} --status=in-progress[/bold cyan]
View details: [bold cyan]taskinator show {task.id}[/bold cyan]
""",
        title="⚡ RECOMMENDED NEXT TASK ⚡",
        border_style="yellow",
        width=100,
    )

    console.print(panel)


def _create_suggested_steps_panel() -> None:
    """Create and display the suggested next steps panel."""
    panel = Panel(
        """
[bold]Suggested Next Steps:[/bold]

1. Run [bold cyan]taskinator next[/bold cyan] to see what to work on next
2. Run [bold cyan]taskinator expand-task --id=<id>[/bold cyan] to break down a task into subtasks
3. Run [bold cyan]taskinator set-status --id=<id> --status=done[/bold cyan] to mark a task as complete
""",
        border_style="cyan",
        width=100,
    )

    console.print(panel)


def _find_next_task(tasks: TaskCollection) -> Optional[Dict]:
    """
    Find the next task to work on based on dependencies and status.

    Args:
        tasks (TaskCollection): Collection of tasks

    Returns:
        Optional[Dict]: Next task data if found, None otherwise
    """
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
    return {
        "id": str(next_task.id),
        "title": next_task.title,
        "status": next_task.status,
        "priority": next_task.priority,
        "dependencies": [str(dep) for dep in next_task.dependencies],
        "description": next_task.description,
    }


def find_next_task(
    tasks_path: str,
    output_format: str = "text",
) -> Optional[Dict]:
    """
    Find the next task to work on based on dependencies and priority.

    Args:
        tasks_path (str): Path to the tasks.json file
        output_format (str, optional): Output format (text or json). Defaults to "text".

    Returns:
        Optional[Dict]: Next task data for json format
    """
    try:
        console.print("[INFO] Reading tasks from {}...".format(tasks_path))
        tasks = read_tasks(tasks_path)

        if not tasks.tasks:
            console.print(
                "[ERROR] No tasks found in {}".format(tasks_path), style="bold red"
            )
            return None

        # Find the next task
        next_task = _find_next_task(tasks)

        if not next_task:
            console.print("[INFO] No tasks ready to work on", style="yellow")
            return None

        # Return JSON data if requested
        if output_format == "json":
            return {
                "next_task": next_task,
            }

        # Create the next task panel instead of showing the full task
        # This breaks the circular dependency
        _create_next_task_panel(next_task, tasks)

        return None
    except Exception as e:
        console.print(f"[ERROR] Error finding next task: {str(e)}", style="bold red")
        raise


def next_task(
    tasks_path: str,
    output_format: str = "text",
) -> Optional[Dict]:
    """
    Display the next task to work on based on dependencies and priority.

    This is a convenience wrapper around find_next_task that provides a more
    user-friendly output format.

    Args:
        tasks_path (str): Path to the tasks.json file
        output_format (str, optional): Output format (text or json). Defaults to "text".

    Returns:
        Optional[Dict]: Next task data for json format
    """
    try:
        # Find the next task
        next_task_data = find_next_task(tasks_path, output_format="json")

        if not next_task_data or not next_task_data.get("next_task"):
            return None

        # Get the next task
        task_data = next_task_data["next_task"]

        # Return JSON data if requested
        if output_format == "json":
            return next_task_data

        # Read tasks to get the full collection
        tasks = read_tasks(tasks_path)

        # Display the next task panel
        _create_next_task_panel(task_data, tasks)

        # Show the full task details without showing suggested actions
        # to break the circular dependency
        task_id = str(task_data["id"])
        task = find_task_by_id(tasks, task_id)

        if task:
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
            priority_color = PRIORITY_COLORS.get(task.priority, "white")
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
                    status_color = STATUS_COLORS.get(subtask.status, "white")
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
                    "in-progress": sum(
                        1 for s in task.subtasks if s.status == "in-progress"
                    ),
                    "pending": sum(1 for s in task.subtasks if s.status == "pending"),
                    "blocked": sum(1 for s in task.subtasks if s.status == "blocked"),
                    "deferred": sum(1 for s in task.subtasks if s.status == "deferred"),
                    "cancelled": sum(
                        1 for s in task.subtasks if s.status == "cancelled"
                    ),
                }

                progress_text = f"""
[bold]Subtask Progress:[/]

Completed: [cyan]{done_count}/{total_count} ({percentage:.1f}%)[/]
[green]✓ Done: {status_counts["done"]}[/]  [blue]► In Progress: {status_counts["in-progress"]}[/]  [yellow]○ Pending: {status_counts["pending"]}[/]
[red]! Blocked: {status_counts["blocked"]}[/]  [magenta]⏱ Deferred: {status_counts["deferred"]}[/]  [dim]✗ Cancelled: {status_counts["cancelled"]}[/]
Progress: {create_progress_bar(done_count, total_count)} [cyan]{percentage:.0f}%[/]
"""
                console.print(Panel(progress_text, width=120))

        return None
    except Exception as e:
        console.print(f"[ERROR] Error finding next task: {str(e)}", style="bold red")
        raise


def show_task(tasks_path: str, task_id: str) -> None:
    """
    Display detailed information about a specific task.

    Args:
        tasks_path (str): Path to the tasks.json file
        task_id (str): Task ID to show
    """
    try:
        console.print("[INFO] Reading tasks from {}...".format(tasks_path))
        tasks = read_tasks(tasks_path)

        # Find the task
        task = None
        for t in tasks.tasks:
            if str(t.id) == task_id:
                task = t
                break

        if not task:
            console.print(f"[ERROR] Task {task_id} not found", style="bold red")
            return

        # Display task header
        console.print()
        console.print(Panel(f"Task: #{task.id} - {task.title}", style="bold cyan"))

        # Create task details table
        table = Table(show_header=False, show_lines=True, box=ROUNDED)
        table.add_column("Field", style="bold cyan", width=14, justify="right")
        table.add_column("Value")

        # Add rows with proper formatting
        table.add_row("ID:", f"[bold cyan]{task.id}[/]")
        table.add_row("Title:", f"[bold]{task.title}[/]")

        # Format status with color
        status_color = STATUS_COLORS.get(task.status, "white")
        status_indicator = {
            "done": "✓",
            "in-progress": "►",
            "pending": "○",
            "blocked": "!",
            "deferred": "⏱",
            "cancelled": "✗",
        }.get(task.status, "?")
        table.add_row("Status:", f"[{status_color}]{status_indicator} {task.status}[/]")

        # Format priority with color
        priority_color = PRIORITY_COLORS.get(task.priority, "white")
        table.add_row("Priority:", f"[{priority_color}]{task.priority}[/]")

        # Format dependencies
        deps_text = (
            "None"
            if not task.dependencies
            else ", ".join(str(dep) for dep in task.dependencies)
        )
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
                status_color = STATUS_COLORS.get(subtask.status, "white")
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
                "in-progress": sum(
                    1 for s in task.subtasks if s.status == "in-progress"
                ),
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

        # Display suggested actions
        actions_text = f"""
[bold]Suggested Actions:[/]
1. Mark as in-progress: [cyan]taskinator set-status --id={task.id} --status=in-progress[/]
2. Mark as done when completed: [cyan]taskinator set-status --id={task.id} --status=done[/]
{f"3. Update subtask status: [cyan]taskinator set-status --id={task.id}.{task.subtasks[0].id} --status=done[/]" if task.subtasks else ""}
"""
        console.print(Panel(actions_text, width=120))
    except Exception as e:
        console.print(f"[ERROR] Error showing task: {str(e)}", style="bold red")
        raise
