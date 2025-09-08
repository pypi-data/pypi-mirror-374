"""
Task management functionality for Taskinator.
"""

import importlib
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from rich.console import Console
from rich.panel import Panel

from taskinator.core.file_storage import (
    backup_tasks,
)
from taskinator.core.file_storage import generate_task_files as fs_generate_task_files
from taskinator.core.file_storage import read_tasks as fs_read_tasks
from taskinator.core.file_storage import (
    reintegrate_task_files as fs_reintegrate_task_files,
)
from taskinator.core.file_storage import write_tasks as fs_write_tasks
from taskinator.models.task import Subtask, Task, TaskCollection
from taskinator.utils.config import get_config
from taskinator.utils.task_utils import find_task_by_id, task_exists

console = Console()
config = get_config()

# Plugin registry
_plugins = {}

# Initialize file storage manager
file_storage = None


def register_plugin(name: str, func: Callable) -> None:
    """
    Register a plugin function.

    Args:
        name (str): Plugin name
        func (Callable): Plugin function
    """
    _plugins[name] = func


def get_plugin(name: str) -> Optional[Callable]:
    """
    Get a plugin function.

    Args:
        name (str): Plugin name

    Returns:
        Optional[Callable]: Plugin function if found, None otherwise
    """
    return _plugins.get(name)


def load_plugins() -> None:
    """
    Load plugins from the plugins directory.
    """
    try:
        # Check if we're in completion mode (tab completion)
        in_completion_mode = "_TYPER_COMPLETE_ARGS" in os.environ

        # Get the plugins directory
        plugins_dir = os.path.join(os.path.dirname(__file__), "..", "plugins")

        # Find all Python files in the plugins directory
        plugin_files = [
            f
            for f in os.listdir(plugins_dir)
            if f.endswith(".py") and not f.startswith("__")
        ]

        # Import each plugin
        for plugin_file in plugin_files:
            plugin_name = plugin_file[:-3]  # Remove .py extension
            try:
                module_name = f"taskinator.plugins.{plugin_name}"
                importlib.import_module(module_name)
                if not in_completion_mode:
                    console.print(f"[INFO] Loaded plugin: {plugin_name}")
            except Exception as e:
                if not in_completion_mode:
                    console.print(
                        f"[ERROR] Error loading plugin {plugin_name}: {str(e)}",
                        style="bold red",
                    )
    except Exception as e:
        if not in_completion_mode:
            console.print(f"[ERROR] Error loading plugins: {str(e)}", style="bold red")


def get_tasks_dir() -> str:
    """
    Get the tasks directory.

    Returns:
        str: Tasks directory
    """
    return config.get("TASKS_DIR", "tasks")


def get_tasks_path() -> str:
    """
    Get the path to the tasks.json file.

    Returns:
        str: Path to the tasks.json file
    """
    tasks_dir = get_tasks_dir()
    return os.path.join(tasks_dir, "tasks.json")


def get_file_storage() -> None:
    """
    Get the file storage manager.

    Returns:
        None
    """
    global file_storage
    if file_storage is None:
        file_storage = FileStorageManager()


def read_tasks(tasks_path: str) -> TaskCollection:
    """
    Read tasks from a JSON file.

    Args:
        tasks_path (str): Path to the tasks.json file

    Returns:
        TaskCollection: Collection of tasks
    """
    return fs_read_tasks(tasks_path)


def write_tasks(tasks_path: str, tasks: TaskCollection) -> None:
    """
    Write tasks to a JSON file.

    Args:
        tasks_path (str): Path to the tasks.json file
        tasks (TaskCollection): Collection of tasks
    """
    fs_write_tasks(tasks_path, tasks)


def generate_task_files(tasks_path: str, output_dir: Optional[str] = None) -> None:
    """
    Generate individual task files from the task collection.

    Args:
        tasks_path (str): Path to the tasks.json file
        output_dir (Optional[str]): Output directory for task files, defaults to tasks directory
    """
    try:
        # Create a backup before generating files
        backup_tasks(tasks_path)

        # Generate task files using the file storage module
        fs_generate_task_files(tasks_path, output_dir)

        console.print(
            Panel(
                f"Successfully generated task files in {output_dir or os.path.dirname(tasks_path)}",
                title="Task Files Generated",
                style="green",
            )
        )
    except Exception as e:
        console.print(
            f"[ERROR] Error generating task files: {str(e)}", style="bold red"
        )
        raise


def reintegrate_task_files(tasks_path: str, input_dir: Optional[str] = None) -> None:
    """
    Reintegrate task files with the JSON data.

    This method reads the individual task files and updates the JSON data
    with any changes made directly to the task files.

    Args:
        tasks_path (str): Path to the tasks.json file
        input_dir (Optional[str]): Input directory for task files, defaults to tasks directory
    """
    try:
        # Create a backup before reintegrating files
        backup_tasks(tasks_path)

        # Reintegrate task files using the file storage module
        fs_reintegrate_task_files(tasks_path, input_dir)

        console.print(
            Panel(
                f"Successfully reintegrated task files from {input_dir or os.path.dirname(tasks_path)}",
                title="Task Files Reintegrated",
                style="green",
            )
        )
    except Exception as e:
        console.print(
            f"[ERROR] Error reintegrating task files: {str(e)}", style="bold red"
        )
        raise


def set_task_status(tasks_path: str, task_id: str, status: str) -> None:
    """
    Update task status.

    Args:
        tasks_path (str): Path to the tasks.json file
        task_id (str): Task ID
        status (str): New status
    """
    try:
        # Read tasks from file
        tasks = read_tasks(tasks_path)

        # Find the task
        task = find_task_by_id(tasks, task_id)

        if not task:
            console.print(f"[ERROR] Task {task_id} not found", style="bold red")
            return

        # Update status
        old_status = task.status
        task.status = status
        task.updated_at = datetime.now()

        # Write tasks to file
        write_tasks(tasks_path, tasks)

        console.print(
            f"[INFO] Updated task {task_id} status from '{old_status}' to '{status}'"
        )

        # Validate dependencies after status update
        console.print("[INFO] Validating dependencies after status update...")
        from taskinator.core.dependency_management import validate_dependencies

        validate_dependencies(tasks_path)

        # Regenerate task files
        console.print("[INFO] Regenerating task files...")
        from taskinator.core.task_generation import generate_task_files

        generate_task_files(tasks_path)

        # Display success message
        console.print(
            Panel(
                f"""
Successfully updated task {task_id} status:
From: {old_status}
To:   {status}
""",
                title="",
                style="green",
            )
        )
    except Exception as e:
        console.print(f"[ERROR] Error setting task status: {str(e)}", style="bold red")
        raise


# Import plugin modules
from . import (
    dependency_management,
    task_expansion,
    task_generation,
    task_listing,
    task_next,
    task_status,
)
from .dependency_management import (
    add_dependency,
    fix_dependencies,
    remove_dependency,
    update_tasks,
    validate_dependencies,
)
from .task_expansion import (
    analyze_task_complexity,
    clear_subtasks,
    display_complexity_report,
    expand_all_tasks,
    expand_task,
)
from .task_generation import (
    add_task,
    parse_prd,
)

# Re-export functions from plugin modules
from .task_listing import (
    list_tasks,
    show_task,
)
from .task_next import next_task_command as next_task
from .task_status import (
    set_task_status,
)

# Load any additional plugins
load_plugins()
