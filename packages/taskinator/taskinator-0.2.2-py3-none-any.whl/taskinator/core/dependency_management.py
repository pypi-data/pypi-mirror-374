"""
Dependency management functionality for Taskinator.
"""

from typing import Dict, List, Optional, Set, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from taskinator.core.task_manager import read_tasks, write_tasks
from taskinator.models.task import Subtask, Task, TaskCollection
from taskinator.utils.config import get_config
from taskinator.utils.task_utils import find_task_by_id, task_exists

console = Console()
config = get_config()


def add_dependency(
    tasks_path: str,
    task_id: str,
    depends_on: str,
    options: Optional[Dict] = None,
) -> None:
    """
    Add a dependency to a task.

    Args:
        tasks_path (str): Path to the tasks.json file
        task_id (str): Task ID to add dependency to
        depends_on (str): Task ID that this task depends on
        options (Optional[Dict], optional): Additional options. Defaults to None.
    """
    try:
        # Read tasks
        console.print("[INFO] Reading tasks from {}...".format(tasks_path))
        tasks = read_tasks(tasks_path)

        # Find the task
        task = find_task_by_id(tasks, task_id)
        if not task:
            console.print(f"[ERROR] Task {task_id} not found", style="bold red")
            return

        # Find the dependency task
        dep_task = find_task_by_id(tasks, depends_on)
        if not dep_task:
            console.print(
                f"[ERROR] Dependency task {depends_on} not found", style="bold red"
            )
            return

        # Check if dependency already exists
        if depends_on in task.dependencies:
            console.print(
                f"[WARNING] Task {task_id} already depends on {depends_on}",
                style="yellow",
            )
            return

        # Check for circular dependencies
        if _would_create_circular_dependency(tasks, task_id, depends_on):
            console.print(
                f"[ERROR] Adding this dependency would create a circular dependency chain",
                style="bold red",
            )
            return

        # Add dependency
        task.dependencies.append(depends_on)

        # Write tasks to file
        console.print(f"[INFO] Writing tasks to {tasks_path}")
        write_tasks(tasks_path, tasks)

        # Display success message
        console.print(
            Panel(
                f"""
Successfully added dependency:
Task {task_id} now depends on {depends_on}
""",
                title="",
                style="green",
            )
        )
    except Exception as e:
        console.print(f"[ERROR] Error adding dependency: {str(e)}", style="bold red")
        raise


def remove_dependency(
    tasks_path: str,
    task_id: str,
    depends_on: str,
    options: Optional[Dict] = None,
) -> None:
    """
    Remove a dependency from a task.

    Args:
        tasks_path (str): Path to the tasks.json file
        task_id (str): Task ID to remove dependency from
        depends_on (str): Task ID to remove from dependencies
        options (Optional[Dict], optional): Additional options. Defaults to None.
    """
    try:
        # Read tasks
        console.print("[INFO] Reading tasks from {}...".format(tasks_path))
        tasks = read_tasks(tasks_path)

        # Find the task
        task = find_task_by_id(tasks, task_id)
        if not task:
            console.print(f"[ERROR] Task {task_id} not found", style="bold red")
            return

        # Check if dependency exists
        if depends_on not in task.dependencies:
            console.print(
                f"[WARNING] Task {task_id} does not depend on {depends_on}",
                style="yellow",
            )
            return

        # Remove dependency
        task.dependencies.remove(depends_on)

        # Write tasks to file
        console.print(f"[INFO] Writing tasks to {tasks_path}")
        write_tasks(tasks_path, tasks)

        # Display success message
        console.print(
            Panel(
                f"""
Successfully removed dependency:
Task {task_id} no longer depends on {depends_on}
""",
                title="",
                style="green",
            )
        )
    except Exception as e:
        console.print(f"[ERROR] Error removing dependency: {str(e)}", style="bold red")
        raise


def validate_dependencies(tasks_path: str) -> Dict[str, List[str]]:
    """
    Validate task dependencies.

    Args:
        tasks_path (str): Path to the tasks.json file

    Returns:
        Dict[str, List[str]]: Dictionary of invalid dependencies
    """
    try:
        # Read tasks from file
        tasks = read_tasks(tasks_path)

        # Find invalid dependencies
        invalid_deps = {}

        for task in tasks.tasks:
            task_id = str(task.id)
            invalid = []

            for dep in task.dependencies:
                if not task_exists(tasks, dep):
                    invalid.append(dep)

            if invalid:
                invalid_deps[task_id] = invalid

            # Check subtasks
            for subtask in task.subtasks:
                subtask_id = str(subtask.id)
                invalid = []

                for dep in subtask.dependencies:
                    if not task_exists(tasks, dep) and dep != task_id:
                        invalid.append(dep)

                if invalid:
                    invalid_deps[subtask_id] = invalid

        # Display results
        if invalid_deps:
            console.print("[WARNING] Found invalid dependencies:", style="yellow")
            for task_id, deps in invalid_deps.items():
                console.print(f"  Task {task_id}: {', '.join(deps)}", style="yellow")
        else:
            console.print("[INFO] All dependencies are valid")

        return invalid_deps
    except Exception as e:
        console.print(
            f"[ERROR] Error validating dependencies: {str(e)}", style="bold red"
        )
        raise


def fix_dependencies(tasks_path: str) -> None:
    """
    Fix invalid dependencies automatically.

    Args:
        tasks_path (str): Path to the tasks.json file
    """
    try:
        # Read tasks from file
        tasks = read_tasks(tasks_path)

        # Find and fix invalid dependencies
        fixed_count = 0

        for task in tasks.tasks:
            task_id = str(task.id)
            valid_deps = []

            for dep in task.dependencies:
                if task_exists(tasks, dep):
                    valid_deps.append(dep)
                else:
                    fixed_count += 1

            task.dependencies = valid_deps

            # Check subtasks
            for subtask in task.subtasks:
                subtask_id = str(subtask.id)
                valid_deps = []

                for dep in subtask.dependencies:
                    if task_exists(tasks, dep) or dep == task_id:
                        valid_deps.append(dep)
                    else:
                        fixed_count += 1

                subtask.dependencies = valid_deps

        # Write tasks to file
        write_tasks(tasks_path, tasks)

        # Display results
        if fixed_count > 0:
            console.print(f"[INFO] Fixed {fixed_count} invalid dependencies")
        else:
            console.print("[INFO] No invalid dependencies found")
    except Exception as e:
        console.print(f"[ERROR] Error fixing dependencies: {str(e)}", style="bold red")
        raise


def validate_and_fix_dependencies(tasks: TaskCollection) -> Tuple[int, int]:
    """
    Validate and fix dependencies in a task collection.

    Args:
        tasks (TaskCollection): Collection of tasks

    Returns:
        Tuple[int, int]: Number of fixed missing dependencies, number of fixed circular dependencies
    """
    # Fix missing dependencies
    fixed_missing = 0
    for task in tasks.tasks:
        valid_deps = []
        for dep_id in task.dependencies:
            if task_exists(tasks, dep_id):
                valid_deps.append(dep_id)
            else:
                fixed_missing += 1
                console.print(
                    f"[INFO] Removing missing dependency {dep_id} from task {task.id}",
                    style="yellow",
                )

        task.dependencies = valid_deps

    # Fix circular dependencies
    fixed_circular = 0
    for task in tasks.tasks:
        while True:
            visited = set()
            path = []
            if _has_circular_dependency(tasks, str(task.id), visited, path):
                # Remove the last dependency in the chain
                if len(path) >= 2:
                    last_task_id = path[-1]
                    second_last_task_id = path[-2]

                    last_task = find_task_by_id(tasks, last_task_id)
                    if last_task and second_last_task_id in last_task.dependencies:
                        last_task.dependencies.remove(second_last_task_id)
                        fixed_circular += 1
                        console.print(
                            f"[INFO] Removing circular dependency {second_last_task_id} from task {last_task_id}",
                            style="yellow",
                        )
            else:
                break

    return fixed_missing, fixed_circular


def _has_circular_dependency(
    tasks: TaskCollection,
    task_id: str,
    visited: Set[str],
    path: List[str],
) -> bool:
    """
    Check if a task has a circular dependency.

    Args:
        tasks (TaskCollection): Collection of tasks
        task_id (str): Task ID to check
        visited (Set[str]): Set of visited task IDs
        path (List[str]): Current dependency path

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


def _would_create_circular_dependency(
    tasks: TaskCollection,
    task_id: str,
    depends_on: str,
) -> bool:
    """
    Check if adding a dependency would create a circular dependency.

    Args:
        tasks (TaskCollection): Collection of tasks
        task_id (str): Task ID to add dependency to
        depends_on (str): Task ID that this task would depend on

    Returns:
        bool: True if adding the dependency would create a circular dependency, False otherwise
    """
    # If the dependency task depends on the task, we would have a circular dependency
    dep_task = find_task_by_id(tasks, depends_on)
    if not dep_task:
        return False

    # Check if the dependency task depends on the task directly
    if task_id in dep_task.dependencies:
        return True

    # Check if the dependency task depends on the task indirectly
    visited = set()

    def check_indirect_dependency(current_task_id: str) -> bool:
        if current_task_id in visited:
            return False

        visited.add(current_task_id)

        current_task = find_task_by_id(tasks, current_task_id)
        if not current_task:
            return False

        if task_id in current_task.dependencies:
            return True

        for dep_id in current_task.dependencies:
            if check_indirect_dependency(dep_id):
                return True

        return False

    return check_indirect_dependency(depends_on)


def update_tasks(
    tasks_path: str,
    from_id: str,
    prompt: str,
    use_research: bool = False,
    options: Optional[Dict] = None,
) -> None:
    """
    Update tasks based on new context.

    Args:
        tasks_path (str): Path to the tasks.json file
        from_id (str): Task ID to start updating from
        prompt (str): Prompt with new context
        use_research (bool, optional): Whether to use research (Perplexity). Defaults to False.
        options (Optional[Dict], optional): Additional options. Defaults to None.
    """
    try:
        # Read tasks
        console.print("[INFO] Reading tasks from {}...".format(tasks_path))
        tasks = read_tasks(tasks_path)

        # Find the task
        task = find_task_by_id(tasks, from_id)
        if not task:
            console.print(f"[ERROR] Task {from_id} not found", style="bold red")
            return

        # Find all tasks that come after this task
        task_ids = [t.id for t in tasks.tasks]
        if isinstance(task.id, int):
            from_index = task_ids.index(task.id)
            tasks_to_update = tasks.tasks[from_index:]
        else:
            # If task ID is not an integer, update only that task
            tasks_to_update = [task]

        # TODO: Replace with actual AI integration
        # For now, we'll just update the task descriptions
        for task in tasks_to_update:
            task.description = f"{task.description} (Updated: {prompt})"
            task.details = f"{task.details or ''}\n\nUpdate: {prompt}"

        # Write tasks to file
        console.print(f"[INFO] Writing tasks to {tasks_path}")
        write_tasks(tasks_path, tasks)

        # Display success message
        console.print(
            Panel(
                f"""
Successfully updated {len(tasks_to_update)} tasks starting from task {from_id}.
Update context: {prompt}
""",
                title="",
                style="green",
            )
        )
    except Exception as e:
        console.print(f"[ERROR] Error updating tasks: {str(e)}", style="bold red")
        raise
