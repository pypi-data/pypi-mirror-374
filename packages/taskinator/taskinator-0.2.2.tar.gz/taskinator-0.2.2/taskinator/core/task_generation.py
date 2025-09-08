"""
Task generation module for Taskinator.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from rich.console import Console
from rich.panel import Panel

from taskinator.core.file_storage_manager import FileStorageManager
from taskinator.models.task import Subtask, Task, TaskCollection
from taskinator.services.ai.ai_client import (
    generate_tasks_from_prd as ai_generate_tasks,
)
from taskinator.utils.config import check_ai_available, get_config
from taskinator.utils.task_utils import find_task_by_id, task_exists

console = Console()
config = get_config()


def parse_prd(
    prd_path: str,
    tasks_path: str,
    num_tasks: int = 10,
) -> None:
    """
    Generate tasks from a PRD document.

    Args:
        prd_path (str): Path to the PRD document
        tasks_path (str): Path to the tasks.json file
        num_tasks (int, optional): Number of tasks to generate. Defaults to 10.
    """
    try:
        # Check if AI functionality is available
        if not check_ai_available():
            # The check_ai_available function will now display appropriate error messages
            # with detailed information about which credentials are missing
            return

        # Read PRD document
        with open(prd_path, "r") as f:
            prd_content = f.read()

        # Generate tasks using AI
        console.print("[INFO] Generating tasks from PRD...")

        # Generate tasks from PRD
        generated_tasks = _generate_tasks_from_prd(
            prd_content, num_tasks, TaskCollection(tasks=[])
        )

        # If no tasks were generated, return early
        if not generated_tasks:
            console.print(
                "[ERROR] Failed to generate tasks from PRD.", style="bold red"
            )
            return

        # Create TaskCollection with generated tasks
        tasks = TaskCollection(
            tasks=generated_tasks,
            metadata={
                "project_name": "PRD Project",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "version": "0.1.0",
                "prd_path": prd_path,
            },
        )

        # Save PRD path to configuration for future reference
        from taskinator.utils.config import save_config_value
        save_config_value("PRD_PATH", prd_path)

        # Write tasks to file
        console.print(f"[INFO] Writing tasks to {tasks_path}")
        file_storage = FileStorageManager(os.path.dirname(tasks_path))
        file_storage.write_tasks(tasks_path, tasks)

        # Generate task files
        console.print("[INFO] Generating task files...")
        file_storage.generate_task_files(tasks_path, None, os.path.dirname(tasks_path))

        # Display success message
        console.print(
            Panel(
                f"""
Successfully generated {len(generated_tasks)} tasks from PRD.

Created:
- {tasks_path}
- Individual task files in {os.path.dirname(tasks_path)}

Next steps:
1. Define your technology stack: taskinator stack recommend --research
2. Refine stack choices: taskinator stack discuss
3. Lock final stack: taskinator stack compile
4. Analyze task complexity: taskinator analyze-complexity --research
5. Review tasks: taskinator list
6. Start development: taskinator next
""",
                title="",
                style="green",
            )
        )
    except Exception as e:
        console.print(f"[ERROR] Error parsing PRD: {str(e)}", style="bold red")


def add_task(
    tasks_path: str,
    prompt: str,
    dependencies: List[str] = None,
    priority: str = "medium",
) -> None:
    """
    Add a new task using AI.

    Args:
        tasks_path (str): Path to the tasks.json file
        prompt (str): Task prompt
        dependencies (List[str], optional): List of dependency IDs. Defaults to None.
        priority (str, optional): Task priority. Defaults to "medium".
    """
    try:
        # Read tasks from file
        file_storage = FileStorageManager(os.path.dirname(tasks_path))
        tasks = file_storage.read_tasks(tasks_path)

        # Generate a new task ID
        new_id = str(
            max([int(t.id) for t in tasks.tasks if t.id.isdigit()], default=0) + 1
        )

        # Create a new task
        new_task = Task(
            id=new_id,
            title=prompt,
            description=prompt,
            status="pending",
            priority=priority,
            dependencies=dependencies or [],
            details=f"Task generated from prompt: {prompt}",
            test_strategy="No test strategy provided.",
            subtasks=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Add the task to the collection
        tasks.tasks.append(new_task)

        # Write tasks to file
        file_storage.write_tasks(tasks_path, tasks)

        # Regenerate task files
        console.print("[INFO] Regenerating task files...")
        file_storage.generate_task_files(tasks_path, None, os.path.dirname(tasks_path))

        # Display success message
        console.print(
            Panel(
                f"""
Successfully added task {new_id}: {prompt}

Dependencies: {', '.join(dependencies) if dependencies else 'None'}
Priority: {priority}

Next steps:
1. Review the tasks with: taskinator list
2. Start working on the task with: taskinator show {new_id}
3. Customize the task to fit your project needs
""",
                title="",
                style="green",
            )
        )
    except Exception as e:
        console.print(f"[ERROR] Error adding task: {str(e)}", style="bold red")
        raise


def _generate_tasks_from_prd(
    prd_content: str,
    num_tasks: int,
    existing_tasks: TaskCollection,
) -> List[Task]:
    """
    Generate tasks from a PRD using AI.

    Args:
        prd_content (str): PRD content
        num_tasks (int): Number of tasks to generate
        existing_tasks (TaskCollection): Existing tasks

    Returns:
        List[Task]: Generated tasks
    """
    try:
        # Check if AI functionality is available
        if not check_ai_available():
            # The check_ai_available function will now display appropriate error messages
            # with detailed information about which credentials are missing
            
            # Return empty list to indicate no tasks were generated
            return []

        # Call the AI to generate tasks
        # Run the async function in a synchronous context
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # If no event loop is available, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        ai_tasks = loop.run_until_complete(ai_generate_tasks(prd_content, num_tasks))

        if not ai_tasks:
            console.print(
                "[WARNING] No tasks were generated by the AI.", style="bold yellow"
            )
            return []

        # Convert AI-generated tasks to Task objects
        tasks = []
        next_id = existing_tasks.get_next_id()

        for i, ai_task in enumerate(ai_tasks):
            # Ensure task has all required fields
            task_id = str(next_id + i)
            title = ai_task.get("title", f"Task {task_id}")
            description = ai_task.get("description", "")
            status = ai_task.get("status", "pending")
            priority = ai_task.get("priority", "medium")
            dependencies = [str(dep) for dep in ai_task.get("dependencies", [])]
            details = ai_task.get("details", "")
            test_strategy = ai_task.get("test_strategy", "")

            # Create Task object
            task = Task(
                id=task_id,
                title=title,
                description=description,
                status=status,
                priority=priority,
                dependencies=dependencies,
                details=details,
                test_strategy=test_strategy,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
            )

            tasks.append(task)

        console.print(
            f"[SUCCESS] Generated {len(tasks)} tasks from PRD.", style="bold green"
        )
        return tasks

    except Exception as e:
        console.print(
            f"[ERROR] Error generating tasks from PRD: {str(e)}", style="bold red"
        )
        return []


def generate_task_files(tasks_path: str, output_dir: Optional[str] = None) -> None:
    """
    Generate individual task files from tasks.json.

    Args:
        tasks_path (str): Path to the tasks.json file
        output_dir (Optional[str], optional): Output directory for task files. Defaults to None.
    """
    try:
        # Read tasks from file
        file_storage = FileStorageManager(os.path.dirname(tasks_path))
        tasks = file_storage.read_tasks(tasks_path)

        # Create output directory if it doesn't exist
        if output_dir is None:
            output_dir = os.path.dirname(tasks_path)
        else:
            output_dir = os.path.join(os.getcwd(), output_dir)

        os.makedirs(output_dir, exist_ok=True)

        # Generate task files
        for task in tasks.tasks:
            task_file = os.path.join(output_dir, f"task_{str(task.id).zfill(3)}.txt")
            with open(task_file, "w") as f:
                # Write task header
                f.write(f"# Task ID: {task.id}\n")
                f.write(f"# Title: {task.title}\n")
                f.write(f"# Status: {task.status}\n")
                f.write(
                    f"# Dependencies: {', '.join(task.dependencies) if task.dependencies else 'None'}\n"
                )
                f.write(f"# Priority: {task.priority}\n")
                f.write(f"# Description: {task.description}\n")

                # Write task details
                f.write("# Details:\n")
                if task.details:
                    f.write(f"{task.details}\n\n")
                else:
                    f.write("No details provided.\n\n")

                # Write test strategy
                f.write("# Test Strategy:\n")
                if task.test_strategy:
                    f.write(f"{task.test_strategy}\n")
                else:
                    f.write("No test strategy provided.\n")

            console.print(f"[INFO] Generated: {os.path.basename(task_file)}")
    except Exception as e:
        error_msg = f"Error generating task files: {str(e)}"
        console.print(f"[ERROR] {error_msg}", style="bold red")
        raise
