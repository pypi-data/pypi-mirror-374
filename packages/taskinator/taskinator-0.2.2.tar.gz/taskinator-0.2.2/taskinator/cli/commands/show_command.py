"""
Show command implementation for Taskinator.
"""

import json
import os
from typing import Dict, List, Optional

from rich.box import ROUNDED, Box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

# Define color constants
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

STATUS_INDICATORS = {
    "done": "✓",
    "in-progress": "►",
    "pending": "○",
    "blocked": "!",
    "deferred": "⏱",
    "cancelled": "✗",
}


def get_status_with_color(status: str) -> Text:
    """
    Get a colored status string.

    Args:
        status (str): Status string

    Returns:
        Text: Colored status string
    """
    color = STATUS_COLORS.get(status, "white")
    indicator = STATUS_INDICATORS.get(status, "?")

    return Text(f"{indicator} {status}", style=color)


def show_task_standalone(tasks_path: str, task_id: str) -> None:
    """
    Show detailed information about a specific task.

    This is a standalone implementation that doesn't rely on any other functions
    to avoid circular dependencies.

    Args:
        tasks_path (str): Path to the tasks.json file
        task_id (str): ID of the task to show
    """
    try:
        # Read tasks directly from file
        console.print(f"[INFO] Reading tasks from {tasks_path}...")

        if not os.path.exists(tasks_path):
            console.print(
                f"[ERROR] Tasks file {tasks_path} does not exist", style="bold red"
            )
            return

        with open(tasks_path, "r") as f:
            data = json.load(f)

        tasks = data.get("tasks", [])

        if not tasks:
            console.print("[ERROR] No tasks found", style="bold red")
            return

        # Create a lookup dictionary for tasks by ID
        task_lookup = {str(task["id"]): task for task in tasks}

        # Check if this is a subtask ID (contains a period)
        if '.' in task_id:
            parent_id, subtask_id = task_id.split('.', 1)
            
            # Find the parent task first
            parent_task = task_lookup.get(str(parent_id))
            
            if not parent_task:
                console.print(f"[ERROR] Parent task with ID {parent_id} not found", style="bold red")
                return
                
            # Now look for the subtask within this parent
            subtasks = parent_task.get("subtasks", [])
            task = None
            
            for subtask in subtasks:
                if str(subtask.get("id")) == task_id:
                    task = subtask
                    break
                    
            if not task:
                console.print(f"[ERROR] Subtask with ID {task_id} not found", style="bold red")
                return
                
            # For subtasks, we'll display a slightly different view
            is_subtask = True
            parent_task_id = parent_id
        else:
            # Regular task ID (no period)
            task = task_lookup.get(str(task_id))
            is_subtask = False
            
        if not task:
            console.print(f"[ERROR] Task with ID {task_id} not found", style="bold red")
            return

        # Create task details panel
        if is_subtask:
            title_text = Text(f"Subtask #{task['id']}: {task.get('title', '')}")
        else:
            title_text = Text(f"Task #{task['id']}: {task.get('title', '')}")


        # Create status text
        status = task.get("status", "pending")
        status_color = STATUS_COLORS.get(status, "white")
        status_indicator = STATUS_INDICATORS.get(status, "?")
        status_text = Text("Status: ")
        status_text.append(f"{status_indicator} {status}", style=status_color)

        # Create priority text
        priority = task.get("priority", "medium")
        priority_color = PRIORITY_COLORS.get(priority, "white")
        priority_text = Text("Priority: ")
        priority_text.append(priority, style=priority_color)

        # Create dependencies text
        dependencies = task.get("dependencies", [])
        deps_text = Text("Dependencies: ")

        if dependencies:
            deps_list = []
            for dep_id in dependencies:
                dep_task = task_lookup.get(str(dep_id))
                if dep_task:
                    dep_status = dep_task.get("status", "unknown")
                    dep_status_color = STATUS_COLORS.get(dep_status, "white")
                    dep_status_indicator = STATUS_INDICATORS.get(dep_status, "?")

                    deps_text.append(f"{dep_id} ({dep_task.get('title', '')}) - ")
                    deps_text.append(
                        f"{dep_status_indicator} {dep_status}", style=dep_status_color
                    )
                else:
                    deps_text.append(f"{dep_id} (Not found)")

            # Join with commas if multiple dependencies
            if len(dependencies) > 1:
                deps_text = Text("Dependencies: ")
                for i, dep_id in enumerate(dependencies):
                    dep_task = task_lookup.get(str(dep_id))
                    if dep_task:
                        dep_status = dep_task.get("status", "unknown")
                        dep_status_color = STATUS_COLORS.get(dep_status, "white")
                        dep_status_indicator = STATUS_INDICATORS.get(dep_status, "?")

                        if i > 0:
                            deps_text.append(", ")

                        deps_text.append(f"{dep_id}")
                        deps_text.append(
                            f" ({dep_status_indicator})", style=dep_status_color
                        )
                    else:
                        if i > 0:
                            deps_text.append(", ")
                        deps_text.append(f"{dep_id} (Not found)")
        else:
            deps_text.append("None")

        # Get task details
        description = task.get("description", "")
        details = task.get("details", "")
        test_strategy = task.get("test_strategy", "")

        # Get subtasks if any
        subtasks = task.get("subtasks", [])
        subtasks_table = None

        if subtasks:
            subtasks_table = Table(title=f"Subtasks for Task #{task_id}", box=ROUNDED)
            subtasks_table.add_column("ID", style="cyan")
            subtasks_table.add_column("Title")
            subtasks_table.add_column("Status", justify="center")
            subtasks_table.add_column("Description")
            subtasks_table.add_column("Priority", justify="center")

            for subtask in subtasks:
                # Extract the subtask ID and format it properly
                # If the ID contains multiple dots (e.g., "1.1.1"), simplify it to "1.1"
                raw_subtask_id = subtask.get('id', '')
                if "." in raw_subtask_id:
                    # Split the ID by dots and keep only the first and last parts
                    parts = raw_subtask_id.split(".")
                    if len(parts) > 2:
                        # For IDs like "1.1.1", format as "1.1"
                        subtask_id = f"{parts[0]}.{parts[-1]}"
                    else:
                        # For IDs already in the correct format, keep as is
                        subtask_id = raw_subtask_id
                else:
                    # If there's no dot, format as parent.subtask
                    subtask_id = f"{task_id}.{raw_subtask_id}"
                
                subtask_title = subtask.get("title", "")
                subtask_status = subtask.get("status", "pending")
                subtask_description = subtask.get("description", "")
                subtask_priority = subtask.get("priority", "medium")

                status_color = STATUS_COLORS.get(subtask_status, "white")
                status_indicator = STATUS_INDICATORS.get(subtask_status, "?")
                status_display = f"{status_indicator} {subtask_status}"
                
                priority_color = PRIORITY_COLORS.get(subtask_priority, "white")

                subtasks_table.add_row(
                    subtask_id,
                    subtask_title,
                    Text(status_display, style=status_color),
                    subtask_description[:50]
                    + ("..." if len(subtask_description) > 50 else ""),
                    Text(subtask_priority, style=priority_color)
                )
                
                # If this subtask has details or test_strategy, create a panel for it
                subtask_details = subtask.get("details", "")
                subtask_test_strategy = subtask.get("test_strategy", "")
                
                if subtask_details or subtask_test_strategy:
                    subtask_panel_content = Text()
                    
                    if subtask_details:
                        subtask_panel_content.append("Implementation Details:\n", style="bold")
                        subtask_panel_content.append(subtask_details)
                        subtask_panel_content.append("\n\n")
                    
                    if subtask_test_strategy:
                        subtask_panel_content.append("Test Strategy:\n", style="bold")
                        subtask_panel_content.append(subtask_test_strategy)
                    
                    # Create a panel for this subtask's details
                    subtask_panel = Panel(
                        subtask_panel_content,
                        title=f"Subtask #{subtask_id}: {subtask_title}",
                        width=100,
                        border_style="blue",
                        box=ROUNDED,
                    )
                    
                    # Add this panel to be displayed after the subtasks table
                    if not hasattr(subtasks_table, "detail_panels"):
                        subtasks_table.detail_panels = []
                    
                    subtasks_table.detail_panels.append(subtask_panel)

        # Check for research findings
        research_table = None
        tasks_dir = os.path.dirname(tasks_path)
        research_dir = os.path.join(tasks_dir, "research")
        task_id_padded = str(task_id).zfill(3)
        task_research_file = os.path.join(research_dir, f"task_{task_id_padded}.txt")

        if os.path.exists(task_research_file):
            try:
                with open(task_research_file, "r") as f:
                    research_content = f.read()

                # Extract only the section relevant to this task
                task_section = ""
                task_id_marker = f"Task ID: {task_id_padded}"
                alt_task_id_marker = f"Task ID: {int(task_id):03d}"

                # Try different formats of task ID markers
                for marker in [
                    f"Task ID: {task_id_padded}",
                    f"Task ID: {int(task_id):03d}",
                    f"Task ID: {task_id}",
                    f"Task ID: 0{task_id}",
                    f"Task ID:{task_id}",
                ]:
                    if marker in research_content:
                        # Find the start of this task's section
                        start_idx = research_content.find(marker)
                        if start_idx != -1:
                            # Find the start of the next task's section or the end of content
                            next_task_idx = research_content.find(
                                "Task ID:", start_idx + len(marker)
                            )
                            if next_task_idx == -1:
                                # This is the last task section, extract to the end
                                task_section = research_content[start_idx:]
                            else:
                                # Extract just this task's section
                                task_section = research_content[start_idx:next_task_idx]
                            break

                # If we couldn't find a specific section, use a reasonable portion of the content
                if not task_section and "Task ID:" in research_content:
                    # Just extract the header and a brief intro
                    header_end = research_content.find("Task ID:")
                    if header_end != -1:
                        task_section = (
                            research_content[:header_end]
                            + "\n\n[Research contains information about multiple tasks]"
                        )

                # If still no task section, use the full content
                if not task_section:
                    task_section = research_content

                # Create a panel for research findings
                research_panel = Panel(
                    Markdown(task_section),
                    title=f"Research Findings for Task #{task_id}",
                    width=100,
                    border_style="blue",
                    box=ROUNDED,
                    padding=(1, 2),
                )

                research_table = research_panel
            except Exception as e:
                console.print(
                    f"[WARNING] Error loading research findings: {str(e)}",
                    style="yellow",
                )

        # Create the main panel content
        panel_content = Text()
        panel_content.append(title_text.plain, style="bold cyan")
        panel_content.append("\n\n")
        panel_content.append(status_text)
        panel_content.append("\n")
        panel_content.append(priority_text)
        panel_content.append("\n")
        panel_content.append(deps_text)
        panel_content.append("\n\n")

        if description:
            panel_content.append("Description:\n", style="bold")
            panel_content.append(description)
            panel_content.append("\n\n")

        if details:
            panel_content.append("Details:\n", style="bold")
            panel_content.append(details)
            panel_content.append("\n\n")

        if test_strategy:
            panel_content.append("Test Strategy:\n", style="bold")
            panel_content.append(test_strategy)
            panel_content.append("\n")

        panel = Panel(
            panel_content,
            title=f"Task #{task_id} Details",
            width=100,
            border_style="cyan",
            box=ROUNDED,
        )

        console.print(panel)

        # Print subtasks table if available
        if subtasks_table:
            console.print(subtasks_table)
            
            # Print detail panels for subtasks if available
            if hasattr(subtasks_table, "detail_panels"):
                for panel in subtasks_table.detail_panels:
                    console.print(panel)

        # Print research findings if available
        if research_table:
            console.print(research_table)

        # Print suggested actions
        actions_panel_content = Text()
        actions_panel_content.append("\n")
        actions_panel_content.append("   Suggested Actions:\n\n")

        if status == "done":
            actions_panel_content.append("   • This task is already completed.\n")

            # Check if there are any pending subtasks
            pending_subtasks = [
                s for s in subtasks if s.get("status", "pending") != "done"
            ]
            if pending_subtasks:
                actions_panel_content.append("   • Complete pending subtasks: ")
                actions_panel_content.append(
                    f"taskinator set-status --id={task_id}.X --status=done",
                    style="cyan",
                )
                actions_panel_content.append("\n")

            # Find dependent tasks that are now unblocked
            dependent_tasks = []
            for t_id, t in task_lookup.items():
                if str(task_id) in [str(d) for d in t.get("dependencies", [])]:
                    dependent_tasks.append((t_id, t.get("title", "")))

            if dependent_tasks:
                actions_panel_content.append("   • Next tasks to work on:\n")
                for dep_id, dep_title in dependent_tasks:
                    actions_panel_content.append(f"     - Task #{dep_id}: ")
                    actions_panel_content.append(dep_title, style="cyan")
                    actions_panel_content.append("\n")

            actions_panel_content.append("   • View next task: ")
            actions_panel_content.append("taskinator next", style="cyan")
            actions_panel_content.append("\n")
        elif status == "in-progress":
            actions_panel_content.append("   • Mark as done: ")
            actions_panel_content.append(
                f"taskinator set-status --id={task_id} --status=done", style="cyan"
            )
            actions_panel_content.append("\n")
            actions_panel_content.append("   • Add subtasks: ")
            actions_panel_content.append(
                f"taskinator expand-task --id={task_id}", style="cyan"
            )
            actions_panel_content.append("\n")
        else:
            actions_panel_content.append("   • Start working: ")
            actions_panel_content.append(
                f"taskinator set-status --id={task_id} --status=in-progress",
                style="cyan",
            )
            actions_panel_content.append("\n")
            actions_panel_content.append("   • Add subtasks: ")
            actions_panel_content.append(
                f"taskinator expand-task --id={task_id}", style="cyan"
            )
            actions_panel_content.append("\n")

        actions_panel_content.append("   • View dependencies: ")
        actions_panel_content.append("taskinator list", style="cyan")
        actions_panel_content.append("\n")
        actions_panel_content.append("\n")

        actions_panel = Panel(
            actions_panel_content,
            title="Next Steps",
            width=100,
            border_style="green",
            box=ROUNDED,
        )

        console.print(actions_panel)

    except Exception as e:
        console.print(f"[ERROR] Error showing task: {str(e)}", style="bold red")
        raise


def show_command(task_id: str) -> None:
    """
    Show detailed information about a specific task.

    This is a standalone implementation that doesn't rely on any other functions
    to avoid circular dependencies.

    Args:
        task_id (str): ID of the task to show
    """
    try:
        tasks_path = os.path.join(os.getcwd(), "tasks", "tasks.json")
        show_task_standalone(tasks_path, task_id)
    except Exception as e:
        console.print(f"[ERROR] Error showing task: {str(e)}", style="bold red")
