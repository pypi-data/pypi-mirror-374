"""
Story and feature processing commands for the Taskinator CLI.

This module implements commands for processing user stories and features
to generate tasks.
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from taskinator.core.story_processor import (
    process_story_file,
    StoryFormat,
    auto_detect_point_system,
)
from taskinator.core.story_point_systems import (
    get_story_point_system,
    PointSystemType,
)
from taskinator.models.task import Task, TaskCollection
from taskinator.utils.ui import console


def parse_story_command(
    file_path: str,
    point_system: Optional[str] = None,
    ai_assist: bool = True,
    analyze_codebase: bool = False,
    task_prefix: Optional[str] = None,
    output: Optional[str] = None,
) -> None:
    """Parse a user story or feature and generate tasks."""
    try:
        # Validate file exists
        if not os.path.exists(file_path):
            console.print(f"[ERROR] File not found: {file_path}", style="bold red")
            return

        # Process the story file
        task_collection = process_story_file(
            file_path=file_path,
            point_system=point_system,
            ai_assist=ai_assist,
            analyze_codebase=analyze_codebase,
            task_prefix=task_prefix,
            output_path=output,
        )

        # Display results
        if task_collection and task_collection.tasks:
            _display_generated_tasks(task_collection, file_path)
        else:
            console.print(f"[yellow]No tasks were generated from {file_path}")

    except Exception as e:
        console.print(f"[ERROR] Failed to process story file: {e}", style="bold red")
        raise


def _display_generated_tasks(task_collection: TaskCollection, source_file: str) -> None:
    """
    Display the generated tasks.

    Args:
        task_collection: The task collection
        source_file: The source file path
    """
    # Display task information
    console.print(
        f"[green]Tasks generated from: [bold]{os.path.basename(source_file)}[/bold]"
    )

    # Count tasks and subtasks
    total_tasks = len(task_collection.tasks)
    total_subtasks = sum(
        len(task.subtasks) for task in task_collection.tasks if task.subtasks
    )

    console.print(
        f"[green]Generated {total_tasks} tasks with {total_subtasks} subtasks"
    )

    # Show tasks table
    table = Table(title="Generated Tasks", box=box.ROUNDED)
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Story Points", style="yellow")
    table.add_column("Subtasks", style="magenta")

    for task in task_collection.tasks:
        subtask_count = len(task.subtasks) if task.subtasks else 0

        table.add_row(
            task.id,
            task.title,
            str(task.story_points) if task.story_points is not None else "",
            str(subtask_count) if subtask_count > 0 else "",
        )

    console.print(table)

    # Show an example of the first task with subtasks
    for task in task_collection.tasks:
        if task.subtasks:
            console.print(f"\n[bold]Task: {task.title}[/bold]")

            subtask_table = Table(show_header=False, box=box.SIMPLE)
            subtask_table.add_column("ID", style="dim")
            subtask_table.add_column("Title")

            for subtask in task.subtasks[:5]:  # Show up to 5 subtasks
                subtask_table.add_row(subtask.id, subtask.title)

            if len(task.subtasks) > 5:
                subtask_table.add_row(
                    "...", f"[dim]+ {len(task.subtasks) - 5} more subtasks[/dim]"
                )

            console.print(subtask_table)
            break  # Just show the first task with subtasks

    # Show next steps
    console.print("\n[bold]Next Steps:[/bold]")
    console.print("1. Review the generated tasks with [cyan]taskinator list[/cyan]")
    console.print(
        "2. Expand tasks for more detail with [cyan]taskinator expand <task-id>[/cyan]"
    )
    console.print("3. Start working on the next task with [cyan]taskinator next[/cyan]")


def story_point_systems_command() -> None:
    """Display available story point systems."""
    table = Table(title="Story Point Systems", box=box.ROUNDED)
    table.add_column("System Name", style="cyan")
    table.add_column("Description", style="green")
    table.add_column("Values", style="yellow")

    # Add rows for each system
    table.add_row(
        "fibonacci",
        "Classic Fibonacci sequence, emphasizing exponential growth in complexity",
        "1, 2, 3, 5, 8, 13, 21, 34",
    )

    table.add_row(
        "powers_of_two",
        "Binary-like scale emphasizing doubling complexity",
        "1, 2, 4, 8, 16, 32",
    )

    table.add_row(
        "linear",
        "Simple linear scale with more granularity",
        "1, 2, 3, 4, 5, 6, 7, 8, 9, 10",
    )

    table.add_row(
        "tshirt",
        "T-shirt sizes, less precise but more intuitive",
        "XS, S, M, L, XL, XXL",
    )

    table.add_row(
        "modified_fibonacci",
        "Modified Fibonacci with smaller and larger increments",
        "0, 0.5, 1, 2, 3, 5, 8, 13, 20, 40, 100",
    )

    console.print(table)

    # Show usage info
    console.print("\n[bold]Usage:[/bold]")
    console.print("Specify a point system when parsing stories:")
    console.print(
        "[dim]taskinator parse-story my-story.md --point-system fibonacci[/dim]"
    )
    console.print("\nPoint system affects task generation complexity and detail level.")

    # Show right-sizing info
    console.print("\n[bold]Right-sizing Tasks:[/bold]")
    console.print("- Low points (1-3): Minimal breakdown, fewer subtasks")
    console.print("- Medium points (5-8): Moderate breakdown with more subtasks")
    console.print("- High points (13+): Extensive breakdown with deeper hierarchy")


def story_point_system_explain_command(
    point_value: str, system: str = "fibonacci"
) -> None:
    """Explain how a story point value affects task generation."""
    try:
        # Get story point system
        point_system = get_story_point_system(system)

        # Get point value (allow string or numeric)
        try:
            if point_value.lower() in ["xs", "s", "m", "l", "xl", "xxl"]:
                point_val = point_value.upper()
            else:
                point_val = float(point_value)
                if point_val.is_integer():
                    point_val = int(point_val)
        except ValueError:
            console.print(
                f"[ERROR] Invalid point value: {point_value}", style="bold red"
            )
            return

        # Get complexity level
        complexity = point_system.get_complexity_level(point_val)

        # Get recommendations
        subtask_count = point_system.get_recommended_subtask_count(point_val)
        task_depth = point_system.get_recommended_task_depth(point_val)
        research_level = point_system.get_recommended_research_level(point_val)
        detail_level = point_system.get_detail_level(point_val)

        # Display results
        console.print(
            f"\n[bold]Analysis for {point_value} points in {system} system:[/bold]\n"
        )

        table = Table(show_header=False, box=box.SIMPLE_HEAD)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Complexity Level", complexity.title())
        table.add_row("Recommended Subtasks", str(subtask_count))
        table.add_row("Task Hierarchy Depth", str(task_depth))
        table.add_row("Research Level", research_level.title())
        table.add_row("Detail Level", detail_level.title())

        console.print(table)

        # Display task example
        console.print("\n[bold]Example Task Structure:[/bold]")

        if complexity == "trivial":
            console.print("├── Main Task (simple implementation, no subtasks needed)")

        elif complexity == "simple":
            console.print("├── Main Task")
            console.print("│   ├── Subtask 1")
            console.print("│   └── Subtask 2")

        elif complexity == "moderate":
            console.print("├── Main Task")
            console.print("│   ├── Subtask 1")
            console.print("│   │   └── Implementation Item")
            console.print("│   ├── Subtask 2")
            console.print("│   └── Subtask 3")

        elif complexity in ["complex", "very_complex"]:
            console.print("├── Main Task")
            console.print("│   ├── Planning Phase")
            console.print("│   │   ├── Research Item")
            console.print("│   │   └── Design Item")
            console.print("│   ├── Implementation Phase")
            console.print("│   │   ├── Component 1")
            console.print("│   │   │   └── Implementation Tasks...")
            console.print("│   │   └── Component 2")
            console.print("│   └── Testing Phase")
            console.print("│       ├── Unit Tests")
            console.print("│       └── Integration Tests")

    except Exception as e:
        console.print(f"[ERROR] Failed to analyze point value: {e}", style="bold red")
