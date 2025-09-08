"""
Command implementations for the Taskinator CLI.
"""

import os
from typing import Optional

import typer
from rich.console import Console

from taskinator.cli.commands.list_command import list_command as list_tasks_command
from taskinator.cli.commands.next_command import next_command as next_task_command
from taskinator.cli.commands.set_status_command import (
    set_status_command as set_status_standalone,
)
from taskinator.cli.commands.show_command import show_command as show_task_command
from taskinator.cli.init_command import init_project
from taskinator.core.task_manager import (
    add_dependency,
    add_task,
    analyze_task_complexity,
    clear_subtasks,
    expand_all_tasks,
    expand_task,
    fix_dependencies,
    generate_task_files,
    parse_prd,
    reintegrate_task_files,
    remove_dependency,
    update_tasks,
    validate_dependencies,
)
from taskinator.utils.config import get_config

console = Console()
config = get_config()


def list_command(status: Optional[str] = None, with_subtasks: bool = False) -> None:
    """List all tasks with their status."""
    try:
        # Use the standalone list_command implementation
        list_tasks_command(status, with_subtasks)
    except Exception as e:
        console.print(f"[ERROR] Error listing tasks: {str(e)}", style="bold red")


def next_command() -> None:
    """Show the next task to work on based on dependencies and priority."""
    try:
        # Use the standalone next_command implementation
        next_task_command()
    except Exception as e:
        console.print(f"[ERROR] Error finding next task: {str(e)}", style="bold red")


def show_command(task_id: str) -> None:
    """Display detailed information about a specific task."""
    try:
        # Use the standalone show_command implementation
        show_task_command(task_id)
    except Exception as e:
        console.print(f"[ERROR] Error showing task: {str(e)}", style="bold red")


def set_status_command(task_id: str, status: str) -> None:
    """Update task status (done, pending, etc.)."""
    try:
        # Use the standalone set_status_command implementation
        set_status_standalone(task_id, status)
    except Exception as e:
        console.print(f"[ERROR] Error setting task status: {str(e)}", style="bold red")


def parse_prd_command(prd_path: str, num_tasks: int = 10) -> None:
    """Generate tasks from a PRD document."""
    try:
        tasks_path = os.path.join(os.getcwd(), "tasks", "tasks.json")
        parse_prd(prd_path, tasks_path, num_tasks)
    except Exception as e:
        console.print(f"[ERROR] Error parsing PRD: {str(e)}", style="bold red")


def generate_command() -> None:
    """Create individual task files from tasks.json."""
    try:
        tasks_path = os.path.join(os.getcwd(), "tasks", "tasks.json")
        output_dir = os.path.join(os.getcwd(), "tasks")
        generate_task_files(tasks_path, output_dir)
    except Exception as e:
        console.print(
            f"[ERROR] Error generating task files: {str(e)}", style="bold red"
        )


def reintegrate_command() -> None:
    """Reintegrate task files back into tasks.json."""
    try:
        tasks_path = os.path.join(os.getcwd(), "tasks", "tasks.json")
        input_dir = os.path.join(os.getcwd(), "tasks")
        reintegrate_task_files(tasks_path, input_dir)
    except Exception as e:
        console.print(
            f"[ERROR] Error reintegrating task files: {str(e)}", style="bold red"
        )


def update_command(from_id: str, prompt: str) -> None:
    """Update tasks based on new requirements."""
    try:
        tasks_path = os.path.join(os.getcwd(), "tasks", "tasks.json")
        update_tasks(tasks_path, from_id, prompt)
    except Exception as e:
        console.print(f"[ERROR] Error updating tasks: {str(e)}", style="bold red")


def add_task_command(
    prompt: str, dependencies: Optional[str] = None, priority: str = "medium"
) -> None:
    """Add a new task using AI."""
    try:
        tasks_path = os.path.join(os.getcwd(), "tasks", "tasks.json")
        deps_list = dependencies.split(",") if dependencies else []
        add_task(tasks_path, prompt, deps_list, priority)
    except Exception as e:
        console.print(f"[ERROR] Error adding task: {str(e)}", style="bold red")


def add_dependency_command(task_id: str, depends_on: str) -> None:
    """Add a dependency to a task."""
    try:
        tasks_path = os.path.join(os.getcwd(), "tasks", "tasks.json")
        add_dependency(tasks_path, task_id, depends_on)
    except Exception as e:
        console.print(f"[ERROR] Error adding dependency: {str(e)}", style="bold red")


def remove_dependency_command(task_id: str, depends_on: str) -> None:
    """Remove a dependency from a task."""
    try:
        tasks_path = os.path.join(os.getcwd(), "tasks", "tasks.json")
        remove_dependency(tasks_path, task_id, depends_on)
    except Exception as e:
        console.print(f"[ERROR] Error removing dependency: {str(e)}", style="bold red")


def analyze_complexity_command(research: bool = False, threshold: int = 5) -> None:
    """Analyze tasks and generate expansion recommendations."""
    try:
        tasks_path = os.path.join(os.getcwd(), "tasks", "tasks.json")
        analyze_task_complexity(tasks_path, research, threshold)
    except Exception as e:
        console.print(f"[ERROR] Error analyzing complexity: {str(e)}", style="bold red")


def complexity_report_command(file_path: Optional[str] = None) -> None:
    """Display the complexity analysis report."""
    try:
        if not file_path:
            file_path = os.path.join(
                os.getcwd(), "tasks", "task-complexity-report.json"
            )
        # This function will be implemented in the task_manager module
        from taskinator.core.task_manager import display_complexity_report

        display_complexity_report(file_path)
    except Exception as e:
        console.print(
            f"[ERROR] Error displaying complexity report: {str(e)}", style="bold red"
        )


def expand_command(
    task_id: Optional[str] = None,
    num_subtasks: Optional[int] = None,
    research: bool = False,
    all_tasks: bool = False,
    force: bool = False,
) -> None:
    """Break down tasks into detailed subtasks."""
    try:
        print(f"[DEBUG] commands_original.py expand_command: force={force}")
        tasks_path = os.path.join(os.getcwd(), "tasks", "tasks.json")

        if not num_subtasks:
            num_subtasks = config.get("DEFAULT_SUBTASKS", 3)

        if all_tasks:
            expand_all_tasks(tasks_path, num_subtasks, research, "", force)
        elif task_id:
            print(f"[DEBUG] commands_original.py calling expand_task with force={force}")
            # Pass force flag directly
            expand_task(tasks_path, task_id, num_subtasks, research, "", None, force)
    except Exception as e:
        console.print(f"[ERROR] Error expanding task: {str(e)}", style="bold red")


def clear_subtasks_command(task_id: str) -> None:
    """Remove subtasks from specified tasks."""
    try:
        tasks_path = os.path.join(os.getcwd(), "tasks", "tasks.json")
        clear_subtasks(tasks_path, task_id)
    except Exception as e:
        console.print(f"[ERROR] Error clearing subtasks: {str(e)}", style="bold red")


def validate_dependencies_command() -> None:
    """Identify invalid dependencies without fixing them."""
    try:
        tasks_path = os.path.join(os.getcwd(), "tasks", "tasks.json")
        validate_dependencies(tasks_path)
    except Exception as e:
        console.print(
            f"[ERROR] Error validating dependencies: {str(e)}", style="bold red"
        )


def fix_dependencies_command() -> None:
    """Fix invalid dependencies automatically."""
    try:
        tasks_path = os.path.join(os.getcwd(), "tasks", "tasks.json")
        fix_dependencies(tasks_path)
    except Exception as e:
        console.print(f"[ERROR] Error fixing dependencies: {str(e)}", style="bold red")


def init_command(project_name: Optional[str] = None, compat: bool = False, yes: bool = False) -> None:
    """Initialize a new project with a basic task structure."""
    try:
        # Use the current working directory
        tasks_dir = os.path.join(os.getcwd(), "tasks")
        tasks_path = os.path.join(tasks_dir, "tasks.json")
        options = {"compat": compat, "yes": yes}
        init_project(project_name, tasks_path, options)
    except Exception as e:
        console.print(f"[ERROR] Error initializing project: {str(e)}", style="bold red")


def export_csv(
    output: str = typer.Option("tasks/export.csv", help="Path to the output CSV file"),
):
    """Export tasks to a CSV file."""
    display_banner()
    from taskinator.plugins.export_plugin import export_to_csv_command

    # Use the provided output path or default to current directory
    if output == "tasks/export.csv":
        output = os.path.join(os.getcwd(), "tasks", "export.csv")

    # Use current working directory for tasks.json
    tasks_path = os.path.join(os.getcwd(), "tasks", "tasks.json")
    export_to_csv_command(tasks_path, output)


def export_markdown(
    output: str = typer.Option(
        "tasks/tasks.md", help="Path to the output Markdown file"
    ),
):
    """Export tasks to a Markdown file."""
    display_banner()
    from taskinator.plugins.export_plugin import export_to_markdown_command

    # Use the provided output path or default to current directory
    if output == "tasks/tasks.md":
        output = os.path.join(os.getcwd(), "tasks", "tasks.md")

    # Use current working directory for tasks.json
    tasks_path = os.path.join(os.getcwd(), "tasks", "tasks.json")
    export_to_markdown_command(tasks_path, output)
