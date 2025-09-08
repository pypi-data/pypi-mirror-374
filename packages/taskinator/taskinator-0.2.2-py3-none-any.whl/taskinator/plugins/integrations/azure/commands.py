"""
Azure DevOps integration commands for Taskinator CLI.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union, Tuple

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

try:
    from .plugin import AzureDevOpsPlugin

    AZURE_DEVOPS_AVAILABLE = True
except ImportError:
    AZURE_DEVOPS_AVAILABLE = False

from taskinator.utils.ui import console

logger = logging.getLogger(__name__)


def check_azure_devops_available():
    """Check if Azure DevOps integration is available."""
    if not AZURE_DEVOPS_AVAILABLE:
        console.print(
            "[ERROR] Azure DevOps integration is not available. "
            "Install the required dependencies with: "
            "pip install taskinator[azure]",
            style="bold red",
        )
        raise typer.Exit(1)

    # Check for environment variables
    missing_vars = []
    for var in ["AZURE_DEVOPS_PAT", "AZURE_DEVOPS_ORG_URL"]:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        console.print(
            f"[ERROR] Required environment variables are not set: {', '.join(missing_vars)}",
            style="bold red",
        )
        raise typer.Exit(1)


def azure_devops_show_command(work_item_id: int, parents: bool = False):
    """Show information about an Azure DevOps work item."""
    check_azure_devops_available()

    try:
        # Initialize plugin
        plugin = AzureDevOpsPlugin()

        if parents:
            # Get parent chain
            parent_chain = plugin.get_parent_chain(work_item_id)

            # Display parent chain
            console.print(f"[green]Parent chain for work item {work_item_id}:")

            # Create a table
            table = Table(box=box.ROUNDED)
            table.add_column("Level", style="cyan")
            table.add_column("ID", style="cyan")
            table.add_column("Type", style="green")
            table.add_column("Title", style="cyan")
            table.add_column("State", style="yellow")
            table.add_column("Story Points", style="magenta")

            for i, item in enumerate(reversed(parent_chain), 1):
                table.add_row(
                    str(i),
                    str(item["id"]),
                    item["type"],
                    item["title"],
                    item.get("state", ""),
                    str(item.get("story_points", "")),
                )

            console.print(table)
        else:
            # Get work item
            work_item = plugin.get_work_item(work_item_id)

            # Display work item details
            console.print(f"[green]Work item {work_item_id}:")

            # Create a table
            table = Table(show_header=False, box=box.ROUNDED)
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="white")

            for field, value in work_item.items():
                if value is not None and value != "":
                    table.add_row(field, str(value))

            console.print(table)

    except Exception as e:
        console.print(f"[ERROR] Failed to show work item: {e}", style="bold red")
        raise typer.Exit(1)


def azure_devops_import_command(
    work_item_id: int,
    include_parents: bool = False,
    output: Optional[str] = None,
):
    """
    Import an Azure DevOps work item and its children as Taskinator tasks.
    """
    check_azure_devops_available()

    try:
        # Initialize plugin
        plugin = AzureDevOpsPlugin()

        console.print(f"[green]Importing work item {work_item_id} and its children...")

        # Import work item
        task_collection = plugin.import_work_item_with_children(
            work_item_id,
            include_parents=include_parents,
            output_path=output,
        )

        # Display results
        console.print(
            f"[green]Successfully imported {len(task_collection.tasks)} tasks."
        )

        # Show the first-level tasks
        table = Table(title="Imported Tasks", box=box.ROUNDED)
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Story Points", style="magenta")
        table.add_column("Subtasks", style="cyan")

        for task in task_collection.tasks:
            subtask_count = len(task.subtasks) if task.subtasks else 0
            source = task.source if hasattr(task, "source") else {}

            table.add_row(
                task.id,
                task.title,
                source.get("work_item_type", ""),
                str(task.story_points) if task.story_points is not None else "",
                str(subtask_count) if subtask_count > 0 else "",
            )

        console.print(table)

        # Show next steps
        console.print("\n[bold]Next Steps:[/bold]")
        console.print("1. Review the generated tasks with [cyan]taskinator list[/cyan]")
        console.print("2. Start working on tasks with [cyan]taskinator next[/cyan]")

    except Exception as e:
        console.print(f"[ERROR] Failed to import work item: {e}", style="bold red")
        raise typer.Exit(1)


def azure_devops_tree_command(
    work_item_id: int,
    levels_up: Optional[int] = None,
    levels_down: Optional[int] = None,
):
    """Show the hierarchy tree of an Azure DevOps work item."""
    check_azure_devops_available()

    try:
        # Initialize plugin
        plugin = AzureDevOpsPlugin()

        console.print(f"[green]Fetching hierarchy tree for work item {work_item_id}...")

        # Get the hierarchy
        tree = plugin.get_work_item_hierarchy(work_item_id)

        # Display hierarchy
        console.print(f"[green]Work item hierarchy tree:")
        _print_hierarchy_tree(tree)

    except Exception as e:
        console.print(
            f"[ERROR] Failed to fetch work item hierarchy: {e}", style="bold red"
        )
        raise typer.Exit(1)


def _print_hierarchy_tree(node, indent=0):
    """Helper function to print the hierarchy tree."""
    item_type = node.get("type", "Unknown")
    item_id = node.get("id", "")
    item_title = node.get("title", "")
    story_points = node.get("story_points")

    indent_str = "  " * indent
    story_points_str = f" [{story_points} SP]" if story_points else ""

    console.print(
        f"{indent_str}[cyan]#{item_id}[/cyan] [{item_type}] {item_title}{story_points_str}"
    )

    if "children" in node and node["children"]:
        for child in node["children"]:
            _print_hierarchy_tree(child, indent + 1)
