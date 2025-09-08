"""
UI utilities for Taskinator.
"""

import os
from typing import Dict, List, Optional, Tuple

from rich.box import ROUNDED, Box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from taskinator.utils.config import get_config

console = Console()
config = get_config()

# ASCII art for the Taskinator header
TASKINATOR_ASCII = """
  _____         _    _             _             
 |_   _|_ _ ___| | _(_)_ __   __ _| |_ ___  _ __ 
   | |/ _` / __| |/ / | '_ \\ / _` | __/ _ \\| '__|
   | | (_| \\__ \\   <| | | | | (_| | || (_) | |   
   |_|\\__,_|___/_|\\_\\_|_| |_|\\__,_|\\__\\___/|_|   
"""

# Status colors
STATUS_COLORS = {
    "done": "bold bright_green",
    "in-progress": "bold bright_blue",
    "pending": "bold bright_yellow",
    "blocked": "bold bright_red",
    "deferred": "bold bright_magenta",
    "cancelled": "dim white",
}

# Priority colors
PRIORITY_COLORS = {
    "high": "bold bright_red",
    "medium": "bold bright_yellow",
    "low": "bold bright_green",
}


def display_banner() -> None:
    """Display the Taskinator ASCII art banner."""
    console.print(TASKINATOR_ASCII, style="bold cyan")
    
    # Get project name from tasks.json if available, otherwise fall back to default
    project_name = "[unset]"
    
    # Try to read from tasks.json
    from taskinator.utils.config import get_tasks_path, get_project_path
    
    # Get the real project path (the directory where the command is being run)
    current_project_path = os.getcwd()
    
    # Build the tasks.json path in the current directory
    tasks_path = os.path.join(current_project_path, "tasks", "tasks.json")
    
    try:
        if os.path.exists(tasks_path):
            # Import only when needed to avoid circular imports
            from taskinator.core.file_storage import read_tasks
            tasks = read_tasks(tasks_path)
            
            # Check if metadata has project_name
            if tasks and tasks.metadata and "project_name" in tasks.metadata:
                project_name = tasks.metadata["project_name"]
                
                # Don't use "Taskinator" as a valid name unless it's explicitly set
                if project_name == "Taskinator" and tasks.metadata.get("project_name_set") is not True:
                    project_name = os.path.basename(current_project_path)
    except Exception as e:
        # Just continue with default project name
        pass
    
    # If project_name is still the default, use current directory name
    if project_name == "[unset]":
        project_name = os.path.basename(current_project_path)
    
    # Import the version from the package metadata
    from taskinator import __version__
    
    # Create a panel for the version and project name
    panel = Panel(
        Text("\n    Version: ")
        + Text(__version__)
        + Text("   Project: ")
        + Text(project_name)
        + Text("\n\n"),
        box=ROUNDED,
        width=48,
    )
    console.print(panel)
    console.print()


def display_help() -> None:
    """Display help information for Taskinator."""
    # Task Generation section
    console.print(Panel("Task Generation", style="bold cyan", box=ROUNDED))
    task_gen_table = Table(show_header=False, box=None, padding=(0, 2))
    task_gen_table.add_column("Command", style="cyan")
    task_gen_table.add_column("Options", style="yellow")
    task_gen_table.add_column("Description")

    task_gen_table.add_row(
        "parse-prd",
        "--input=<file.txt> [--tasks=10]",
        "Generate tasks from a PRD document",
    )
    task_gen_table.add_row(
        "generate", "", "Create individual task files from tasks.json"
    )
    console.print(task_gen_table)
    console.print()

    # Task Management section
    console.print(Panel("Task Management", style="bold cyan", box=ROUNDED))
    task_mgmt_table = Table(show_header=False, box=None, padding=(0, 2))
    task_mgmt_table.add_column("Command", style="cyan")
    task_mgmt_table.add_column("Options", style="yellow")
    task_mgmt_table.add_column("Description")

    task_mgmt_table.add_row(
        "list",
        "[--status=<status>] [--with-subtasks]",
        "List all tasks with their status",
    )
    task_mgmt_table.add_row(
        "set-status",
        "--id=<id> --status=<status>",
        "Update task status (done, pending, etc.)",
    )
    task_mgmt_table.add_row(
        "update",
        '--from=<id> --prompt="<context>"',
        "Update tasks based on new requirements",
    )
    task_mgmt_table.add_row(
        "add-task",
        '--prompt="<text>" [--dependencies=<ids>] [--priority=<priority>]',
        "Add a new task using AI",
    )
    task_mgmt_table.add_row(
        "add-dependency", "--id=<id> --depends-on=<id>", "Add a dependency to a task"
    )
    task_mgmt_table.add_row(
        "remove-dependency",
        "--id=<id> --depends-on=<id>",
        "Remove a dependency from a task",
    )
    console.print(task_mgmt_table)
    console.print()

    # Task Analysis & Detail section
    console.print(Panel("Task Analysis & Detail", style="bold cyan", box=ROUNDED))
    task_analysis_table = Table(show_header=False, box=None, padding=(0, 2))
    task_analysis_table.add_column("Command", style="cyan")
    task_analysis_table.add_column("Options", style="yellow")
    task_analysis_table.add_column("Description")

    task_analysis_table.add_row(
        "analyze-complexity",
        "[--research] [--threshold=5]",
        "Analyze tasks and generate expansion recommendations",
    )
    task_analysis_table.add_row(
        "complexity-report", "[--file=<path>]", "Display the complexity analysis report"
    )
    task_analysis_table.add_row(
        "expand",
        '--id=<id> [--num=5] [--research] [--context="<text>"]',
        "Break down tasks into detailed subtasks",
    )
    task_analysis_table.add_row(
        "expand --all",
        "[--force] [--research]",
        "Expand all pending tasks with subtasks",
    )
    task_analysis_table.add_row(
        "clear-subtasks", "--id=<id>", "Remove subtasks from specified tasks"
    )
    console.print(task_analysis_table)
    console.print()

    # Task Navigation & Viewing section
    console.print(Panel("Task Navigation & Viewing", style="bold cyan", box=ROUNDED))
    task_nav_table = Table(show_header=False, box=None, padding=(0, 2))
    task_nav_table.add_column("Command", style="cyan")
    task_nav_table.add_column("Options", style="yellow")
    task_nav_table.add_column("Description")

    task_nav_table.add_row(
        "next", "", "Show the next task to work on based on dependencies and priority"
    )
    task_nav_table.add_row(
        "show", "<id>", "Display detailed information about a specific task"
    )
    console.print(task_nav_table)
    console.print()

    # Dependency Management section
    console.print(Panel("Dependency Management", style="bold cyan", box=ROUNDED))
    dep_mgmt_table = Table(show_header=False, box=None, padding=(0, 2))
    dep_mgmt_table.add_column("Command", style="cyan")
    dep_mgmt_table.add_column("Options", style="yellow")
    dep_mgmt_table.add_column("Description")

    dep_mgmt_table.add_row(
        "validate-dependencies", "", "Identify invalid dependencies without fixing them"
    )
    dep_mgmt_table.add_row(
        "fix-dependencies", "", "Fix invalid dependencies automatically"
    )
    console.print(dep_mgmt_table)
    console.print()

    # Export Options section
    console.print(Panel("Export Options", style="bold cyan", box=ROUNDED))
    export_table = Table(show_header=False, box=None, padding=(0, 2))
    export_table.add_column("Command", style="cyan")
    export_table.add_column("Options", style="yellow")
    export_table.add_column("Description")

    export_table.add_row(
        "export-csv", "[--output=<path>]", "Export tasks to a CSV file"
    )
    export_table.add_row(
        "export-markdown", "[--output=<path>]", "Export tasks to a Markdown file"
    )
    console.print(export_table)
    console.print()

    # Environment Variables section
    console.print(Panel("Environment Variables", style="bold cyan", box=ROUNDED))
    env_table = Table(show_header=False, box=None, padding=(0, 2))
    env_table.add_column("Variable", style="cyan", width=25)
    env_table.add_column("Description", width=40)
    env_table.add_column("Default", style="yellow", width=25)

    env_table.add_row("ANTHROPIC_API_KEY", "Your Anthropic API key", "Required")
    env_table.add_row("MODEL", "Claude model to use", "Default: claude-3-7-sonnet")
    env_table.add_row("MAX_TOKENS", "Maximum tokens for responses", "Default: 4000")
    env_table.add_row("TEMPERATURE", "Temperature for model responses", "Default: 0.7")
    env_table.add_row(
        "PERPLEXITY_API_KEY", "Perplexity API key for research", "Optional"
    )
    env_table.add_row(
        "PERPLEXITY_MODEL", "Perplexity model to use", "Default: sonar-pro"
    )
    env_table.add_row("DEBUG", "Enable debug logging", "Default: false")
    env_table.add_row(
        "LOG_LEVEL", "Console output level (debug,info,warn,error)", "Default: info"
    )
    env_table.add_row(
        "DEFAULT_SUBTASKS", "Default number of subtasks to generate", "Default: 3"
    )
    env_table.add_row("DEFAULT_PRIORITY", "Default task priority", "Default: medium")
    env_table.add_row(
        "PROJECT_NAME", "Project name displayed in UI", "Default: Taskinator"
    )
    console.print(env_table)


def get_status_with_color(status: str) -> Text:
    """
    Get a status string with appropriate color.

    Args:
        status (str): Status string

    Returns:
        Text: Rich Text object with colored status
    """
    status = status.lower()
    color = STATUS_COLORS.get(status, "white")

    # Create status indicators
    indicators = {
        "done": "✓",
        "in-progress": "►",
        "pending": "○",
        "blocked": "!",
        "deferred": "⏱",
        "cancelled": "✗",
    }

    indicator = indicators.get(status, "?")
    return Text(f"{indicator} {status}", style=color)


def format_dependencies_with_status(dependencies: List[str], tasks_data: Dict) -> Text:
    """
    Format dependencies with status indicators.

    Args:
        dependencies (List[str]): List of dependency IDs
        tasks_data (Dict): Tasks data dictionary

    Returns:
        Text: Rich Text object with formatted dependencies
    """
    if not dependencies or len(dependencies) == 0:
        return Text("None")

    result = Text()

    for i, dep_id in enumerate(dependencies):
        # Find the dependency task
        dep_task = None
        for task in tasks_data.get("tasks", []):
            if str(task.get("id")) == str(dep_id):
                dep_task = task
                break

        if dep_task:
            status = dep_task.get("status", "pending").lower()
            if status == "done":
                result.append(f"{dep_id} (✓)", style="bold bright_green")
            else:
                result.append(f"{dep_id} (○)", style="bold bright_yellow")
        else:
            # Dependency not found
            result.append(f"{dep_id} (?)", style="bold bright_red")

        # Add comma if not the last item
        if i < len(dependencies) - 1:
            result.append(", ")

    return result


def create_progress_bar(completed: int, total: int, width: int = 50) -> str:
    """
    Create a text-based progress bar.

    Args:
        completed (int): Number of completed items
        total (int): Total number of items
        width (int, optional): Width of the progress bar. Defaults to 50.

    Returns:
        str: Progress bar string
    """
    if total == 0:
        percentage = 0
    else:
        percentage = int((completed / total) * 100)

    # Calculate the number of filled blocks
    filled_length = int(width * completed / total) if total > 0 else 0

    # Create the progress bar with color
    filled_part = f"[bold bright_green]{'█' * filled_length}[/]"
    empty_part = f"[dim]{'░' * (width - filled_length)}[/]"

    return f"{filled_part}{empty_part}"
