"""
Task status management functionality for Taskinator.
"""

from typing import Dict, Optional

from rich.console import Console
from rich.panel import Panel

from taskinator.core.task_manager import find_task_by_id, read_tasks, write_tasks
from taskinator.models.task import Subtask, Task, TaskCollection
from taskinator.utils.config import get_config

console = Console()
config = get_config()


def set_task_status(
    tasks_path: str,
    task_id: str,
    new_status: str,
    options: Optional[Dict] = None,
) -> Optional[Dict]:
    """
    Set the status of a task.

    Args:
        tasks_path (str): Path to the tasks.json file
        task_id (str): Task ID to update
        new_status (str): New status
        options (Optional[Dict], optional): Additional options. Defaults to None.

    Returns:
        Optional[Dict]: Result object in MCP mode, None in CLI mode
    """
    try:
        # Validate status
        valid_statuses = [
            "pending",
            "in-progress",
            "done",
            "blocked",
            "deferred",
            "cancelled",
        ]
        if new_status.lower() not in valid_statuses:
            console.print(
                f"[ERROR] Invalid status: {new_status}. "
                f"Valid statuses are: {', '.join(valid_statuses)}",
                style="bold red",
            )
            return None

        # Read tasks
        console.print("[INFO] Reading tasks from {}...".format(tasks_path))
        tasks = read_tasks(tasks_path)

        # Update task status
        old_status = update_single_task_status(tasks_path, task_id, new_status, tasks)

        # Validate dependencies after status update
        console.print("[INFO] Validating dependencies after status update...")
        validate_dependencies(tasks)

        # Regenerate task files
        console.print("[INFO] Regenerating task files...")
        from taskinator.core.task_generation import generate_task_files

        generate_task_files(tasks_path, "tasks")

        # Display success message
        console.print(
            Panel(
                f"""
Successfully updated task {task_id} status:
From: {old_status}
To:   {new_status}
""",
                title="",
                style="green",
            )
        )

        return None
    except Exception as e:
        console.print(f"[ERROR] Error setting task status: {str(e)}", style="bold red")
        raise


def update_single_task_status(
    tasks_path: str,
    task_id: str,
    new_status: str,
    tasks: Optional[TaskCollection] = None,
    show_ui: bool = True,
) -> str:
    """
    Update the status of a single task.

    Args:
        tasks_path (str): Path to the tasks.json file
        task_id (str): Task ID to update
        new_status (str): New status
        tasks (Optional[TaskCollection], optional): Tasks data. Defaults to None.
        show_ui (bool, optional): Whether to show UI elements. Defaults to True.

    Returns:
        str: Old status
    """
    # Read tasks if not provided
    if not tasks:
        tasks = read_tasks(tasks_path)

    # Check if the task ID is a subtask ID (e.g., "1.2")
    if "." in task_id:
        parent_id, subtask_id = task_id.split(".", 1)

        # Find the parent task
        parent_task = next((t for t in tasks.tasks if str(t.id) == parent_id), None)

        if not parent_task:
            raise ValueError(f"Parent task {parent_id} not found")

        # Find the subtask
        subtask = next(
            (s for s in parent_task.subtasks if str(s.id) == subtask_id), None
        )

        if not subtask:
            raise ValueError(f"Subtask {task_id} not found")

        # Update subtask status
        old_status = subtask.status
        subtask.status = new_status.lower()

        if show_ui:
            console.print(
                f"[INFO] Updated subtask {task_id} status from '{old_status}' to '{new_status}'"
            )

        # Write tasks
        write_tasks(tasks_path, tasks)

        return old_status
    else:
        # Find the task
        task = next((t for t in tasks.tasks if str(t.id) == task_id), None)

        if not task:
            raise ValueError(f"Task {task_id} not found")

        # Update task status
        old_status = task.status
        task.status = new_status.lower()

        if show_ui:
            console.print(
                f"[INFO] Updated task {task_id} status from '{old_status}' to '{new_status}'"
            )

        # Write tasks
        write_tasks(tasks_path, tasks)

        return old_status


def validate_dependencies(tasks: TaskCollection) -> None:
    """
    Validate task dependencies.

    Args:
        tasks (TaskCollection): Collection of tasks
    """
    # Check for invalid dependencies
    for task in tasks.tasks:
        for dep_id in task.dependencies:
            dep_task = find_task_by_id(tasks, dep_id)
            if not dep_task:
                console.print(
                    f"[WARNING] Task {task.id} depends on non-existent task {dep_id}",
                    style="yellow",
                )

    # Check for circular dependencies
    for task in tasks.tasks:
        visited = set()
        path = []
        if _has_circular_dependency(tasks, task.id, visited, path):
            console.print(
                f"[WARNING] Circular dependency detected: {' -> '.join(path)}",
                style="yellow",
            )


def _has_circular_dependency(
    tasks: TaskCollection,
    task_id: str,
    visited: set,
    path: list,
) -> bool:
    """
    Check if a task has a circular dependency.

    Args:
        tasks (TaskCollection): Collection of tasks
        task_id (str): Task ID to check
        visited (set): Set of visited task IDs
        path (list): Current dependency path

    Returns:
        bool: True if a circular dependency is detected, False otherwise
    """
    # Add task to path
    path.append(str(task_id))

    # If task is already visited, we have a circular dependency
    if task_id in visited:
        return True

    # Mark task as visited
    visited.add(task_id)

    # Find the task
    task = find_task_by_id(tasks, task_id)

    if not task:
        # Task not found, no circular dependency
        path.pop()
        return False

    # Check dependencies
    for dep_id in task.dependencies:
        if _has_circular_dependency(tasks, dep_id, visited.copy(), path):
            return True

    # No circular dependency found
    path.pop()
    return False
