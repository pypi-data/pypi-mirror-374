"""
Utility functions for tasks.
"""

from typing import Any, Dict, List, Optional, Union

from taskinator.models.task import Subtask, Task, TaskCollection


def find_task_by_id(tasks: TaskCollection, task_id: str) -> Optional[Union[Task, Subtask]]:
    """
    Find a task or subtask by ID.

    Args:
        tasks (TaskCollection): Collection of tasks
        task_id (str): Task or subtask ID

    Returns:
        Optional[Union[Task, Subtask]]: Task or subtask if found, None otherwise
    """
    # Check if this is a subtask ID (contains a period)
    if '.' in task_id:
        parent_id, subtask_id = task_id.split('.', 1)
        
        # Find the parent task first
        for task in tasks.tasks:
            if str(task.id) == parent_id:
                # Now look for the subtask within this parent
                for subtask in task.subtasks:
                    if str(subtask.id) == task_id:
                        return subtask
                break
    else:
        # Regular task ID (no period)
        for task in tasks.tasks:
            if str(task.id) == task_id:
                return task
    
    return None


def task_exists(tasks: TaskCollection, task_id: str) -> bool:
    """
    Check if a task exists.

    Args:
        tasks (TaskCollection): Collection of tasks
        task_id (str): Task ID

    Returns:
        bool: True if the task exists, False otherwise
    """
    return find_task_by_id(tasks, task_id) is not None


def _format_subtasks_list(subtasks: List[Subtask]) -> str:
    """
    Format a list of subtasks for display.

    Args:
        subtasks (List[Subtask]): List of subtasks to format

    Returns:
        str: Formatted subtasks list
    """
    result = ""
    for i, subtask in enumerate(subtasks, 1):
        result += f"{subtask.id}: {subtask.title}\n"
    return result
