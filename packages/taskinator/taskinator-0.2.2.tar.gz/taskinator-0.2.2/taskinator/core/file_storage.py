"""
File storage module for Taskinator.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from rich.console import Console

from taskinator.core.file_storage_manager import FileStorageManager
from taskinator.models.task import Subtask, Task, TaskCollection

console = Console()


class FileStorageError(Exception):
    """Exception raised for file storage errors."""

    pass


# Create a global instance of FileStorageManager
file_storage_manager = FileStorageManager()


def read_tasks(tasks_path: str) -> TaskCollection:
    """
    Read tasks from a JSON file.

    Args:
        tasks_path (str): Path to the tasks.json file

    Returns:
        TaskCollection: Collection of tasks
    """
    try:
        # Use the new FileStorageManager to read tasks
        tasks = file_storage_manager.read_tasks(tasks_path)
        return tasks
    except Exception as e:
        error_msg = f"Error reading tasks from {tasks_path}: {str(e)}"
        console.print(f"[ERROR] {error_msg}", style="bold red")
        raise


def write_tasks(tasks_path: str, tasks: TaskCollection) -> None:
    """
    Write tasks to a JSON file.

    Args:
        tasks_path (str): Path to the tasks.json file
        tasks (TaskCollection): Collection of tasks
    """
    try:
        # Use the new FileStorageManager to write tasks
        file_storage_manager.write_tasks(tasks_path, tasks)
        console.print(f"[INFO] Writing tasks to {tasks_path}")
    except Exception as e:
        error_msg = f"Error writing tasks to {tasks_path}: {str(e)}"
        console.print(f"[ERROR] {error_msg}", style="bold red")
        raise


def generate_task_files(tasks_path: str, output_dir: Optional[str] = None) -> None:
    """
    Generate task files from tasks.json.

    Args:
        tasks_path (str): Path to the tasks.json file
        output_dir (Optional[str], optional): Output directory for task files.
                                             Defaults to "tasks".
    """
    try:
        # Use the new FileStorageManager to generate task files
        file_storage_manager.generate_task_files(tasks_path, output_dir)
        console.print(f"[INFO] Generated task files in {output_dir or 'tasks'}")
    except Exception as e:
        error_msg = f"Error generating task files: {str(e)}"
        console.print(f"[ERROR] {error_msg}", style="bold red")
        raise


def reintegrate_task_files(tasks_path: str, input_dir: Optional[str] = None) -> None:
    """
    Reintegrate task files into tasks.json.

    Args:
        tasks_path (str): Path to the tasks.json file
        input_dir (Optional[str], optional): Input directory for task files.
                                           Defaults to "tasks".
    """
    try:
        # Use the new FileStorageManager to reintegrate task files
        file_storage_manager.reintegrate_task_files(tasks_path, input_dir)
        console.print(f"[INFO] Reintegrated task files from {input_dir or 'tasks'}")
    except Exception as e:
        error_msg = f"Error reintegrating task files: {str(e)}"
        console.print(f"[ERROR] {error_msg}", style="bold red")
        raise


def backup_tasks(tasks_path: str, backup_dir: Optional[str] = None) -> str:
    """
    Create a backup of the tasks.json file.

    Args:
        tasks_path (str): Path to the tasks.json file
        backup_dir (Optional[str], optional): Backup directory.
                                            Defaults to "backups".

    Returns:
        str: Path to the backup file
    """
    try:
        # Use the new FileStorageManager to backup tasks
        backup_path = file_storage_manager.backup_tasks(tasks_path, backup_dir)
        console.print(f"[INFO] Created backup at {backup_path}")
        return backup_path
    except Exception as e:
        error_msg = f"Error creating backup: {str(e)}"
        console.print(f"[ERROR] {error_msg}", style="bold red")
        raise
