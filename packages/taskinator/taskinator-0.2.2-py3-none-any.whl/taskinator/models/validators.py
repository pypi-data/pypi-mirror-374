"""
Validation and normalization utilities for task data models.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from rich.console import Console

from taskinator.models.task import Subtask, Task, TaskCollection

console = Console()


def normalize_task_id(task_id: Union[int, str]) -> str:
    """
    Normalize a task ID to a string.

    Args:
        task_id (Union[int, str]): Task ID to normalize

    Returns:
        str: Normalized task ID
    """
    return str(task_id)


def normalize_dependencies(dependencies: List[Union[int, str]]) -> List[str]:
    """
    Normalize a list of dependencies to strings.

    Args:
        dependencies (List[Union[int, str]]): List of dependencies to normalize

    Returns:
        List[str]: Normalized dependencies
    """
    return [normalize_task_id(dep) for dep in dependencies]


def validate_task_status(status: str) -> str:
    """
    Validate a task status.

    Args:
        status (str): Status to validate

    Returns:
        str: Validated status

    Raises:
        ValueError: If status is invalid
    """
    valid_statuses = [
        "pending",
        "in-progress",
        "done",
        "blocked",
        "deferred",
        "cancelled",
    ]

    status = status.lower()
    if status not in valid_statuses:
        raise ValueError(
            f"Invalid status: {status}. Valid statuses are: {', '.join(valid_statuses)}"
        )

    return status


def validate_task_priority(priority: str) -> str:
    """
    Validate a task priority.

    Args:
        priority (str): Priority to validate

    Returns:
        str: Validated priority

    Raises:
        ValueError: If priority is invalid
    """
    valid_priorities = ["high", "medium", "low"]

    priority = priority.lower()
    if priority not in valid_priorities:
        raise ValueError(
            f"Invalid priority: {priority}. Valid priorities are: {', '.join(valid_priorities)}"
        )

    return priority


def validate_task_dependencies(
    task_id: str, dependencies: List[str], tasks: TaskCollection
) -> List[str]:
    """
    Validate task dependencies.

    Args:
        task_id (str): Task ID
        dependencies (List[str]): List of dependencies to validate
        tasks (TaskCollection): Collection of tasks

    Returns:
        List[str]: Validated dependencies

    Raises:
        ValueError: If a dependency is invalid
    """
    validated_deps = []

    for dep_id in dependencies:
        # Normalize dependency ID
        dep_id = normalize_task_id(dep_id)

        # Check if dependency exists
        if not any(normalize_task_id(t.id) == dep_id for t in tasks.tasks):
            raise ValueError(f"Dependency {dep_id} not found")

        # Check for self-dependency
        if dep_id == task_id:
            raise ValueError(f"Task {task_id} cannot depend on itself")

        validated_deps.append(dep_id)

    return validated_deps


def detect_circular_dependencies(tasks: TaskCollection) -> List[Dict[str, Any]]:
    """
    Detect circular dependencies in a task collection.

    Args:
        tasks (TaskCollection): Collection of tasks

    Returns:
        List[Dict[str, Any]]: List of circular dependencies
    """
    circular_deps = []

    for task in tasks.tasks:
        visited = set()
        path = []

        if _has_circular_dependency(tasks, normalize_task_id(task.id), visited, path):
            circular_deps.append({"task_id": task.id, "path": path})

    return circular_deps


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
    path.append(task_id)

    # If task is already visited, we have a circular dependency
    if task_id in visited:
        return True

    # Mark task as visited
    visited.add(task_id)

    # Find the task
    task = next((t for t in tasks.tasks if normalize_task_id(t.id) == task_id), None)

    if not task:
        # Task not found, no circular dependency
        path.pop()
        return False

    # Check dependencies
    for dep_id in task.dependencies:
        dep_id = normalize_task_id(dep_id)
        if _has_circular_dependency(tasks, dep_id, visited.copy(), path):
            return True

    # No circular dependency found
    path.pop()
    return False


def validate_subtask_id(parent_id: str, subtask_id: str) -> str:
    """
    Validate a subtask ID.

    Args:
        parent_id (str): Parent task ID
        subtask_id (str): Subtask ID to validate

    Returns:
        str: Validated subtask ID

    Raises:
        ValueError: If subtask ID is invalid
    """
    # Normalize parent ID
    parent_id = normalize_task_id(parent_id)

    # Check if subtask ID starts with parent ID
    if not subtask_id.startswith(f"{parent_id}."):
        raise ValueError(
            f"Subtask ID {subtask_id} must start with parent ID {parent_id}"
        )

    return subtask_id


def generate_subtask_id(parent_id: str, subtasks: List[Subtask]) -> str:
    """
    Generate a new subtask ID.

    Args:
        parent_id (str): Parent task ID
        subtasks (List[Subtask]): Existing subtasks

    Returns:
        str: New subtask ID
    """
    # Normalize parent ID
    parent_id = normalize_task_id(parent_id)

    # Find the highest subtask index
    highest_index = 0
    for subtask in subtasks:
        if subtask.id.startswith(f"{parent_id}."):
            try:
                index = int(subtask.id.split(".")[-1])
                highest_index = max(highest_index, index)
            except ValueError:
                pass

    # Generate new subtask ID
    return f"{parent_id}.{highest_index + 1}"


def generate_task_id(tasks: TaskCollection) -> str:
    """
    Generate a new task ID.

    Args:
        tasks (TaskCollection): Collection of tasks

    Returns:
        str: New task ID
    """
    # Find the highest task ID
    highest_id = 0
    for task in tasks.tasks:
        try:
            task_id = int(normalize_task_id(task.id).split(".")[0])
            highest_id = max(highest_id, task_id)
        except ValueError:
            pass

    # Generate new task ID
    return str(highest_id + 1)


def create_timestamp() -> str:
    """
    Create a timestamp in ISO format.

    Returns:
        str: Timestamp in ISO format
    """
    return datetime.now().isoformat()
