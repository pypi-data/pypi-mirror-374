"""
GitLab integration commands for Taskinator CLI.
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
    from .plugin import GitLabPlugin

    GITLAB_AVAILABLE = True
except ImportError:
    GITLAB_AVAILABLE = False

from taskinator.utils.ui import console

logger = logging.getLogger(__name__)


def check_gitlab_available():
    """Check if GitLab integration is available."""
    if not GITLAB_AVAILABLE:
        console.print(
            "[ERROR] GitLab integration is not available. "
            "Install the required dependencies with: "
            "pip install taskinator[gitlab]",
            style="bold red",
        )
        raise typer.Exit(1)

    # Check for environment variables
    missing_vars = []
    required_vars = [["GITLAB_API_TOKEN", "GITLAB_TOKEN"], "GITLAB_PROJECT_ID"]
    
    # Check if either GITLAB_API_TOKEN or GITLAB_TOKEN is set
    if not (os.getenv("GITLAB_API_TOKEN") or os.getenv("GITLAB_TOKEN")):
        missing_vars.append("GITLAB_API_TOKEN or GITLAB_TOKEN")
        
    # Check other required vars
    for var in required_vars:
        if isinstance(var, str) and not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        console.print(
            f"[ERROR] Required environment variables are not set: {', '.join(missing_vars)}",
            style="bold red",
        )
        console.print(
            "[INFO] Set the following environment variables:",
            style="yellow",
        )
        console.print("  GITLAB_API_TOKEN or GITLAB_TOKEN: Your GitLab personal access token")
        console.print(
            "  GITLAB_PROJECT_ID: Your GitLab project ID or path (namespace/project)"
        )
        console.print(
            "  GITLAB_URL: Your GitLab instance URL (default: https://gitlab.com)"
        )
        raise typer.Exit(1)


def gitlab_show_command(issue_iid: int, parents: bool = False):
    """Show information about a GitLab issue."""
    check_gitlab_available()

    try:
        # Initialize plugin
        plugin = GitLabPlugin()

        if parents:
            # Get parent chain
            parent_chain = plugin.get_parent_chain(issue_iid)

            # Display parent chain
            console.print(f"[green]Parent chain for issue #{issue_iid}:")

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
            # Get issue
            issue = plugin.get_issue(issue_iid)

            # Display issue details
            console.print(f"[green]Issue #{issue_iid}:")

            # Create a table
            table = Table(show_header=False, box=box.ROUNDED)
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="white")

            for field, value in issue.items():
                if value is not None and value != "":
                    # Handle lists specially
                    if isinstance(value, list):
                        value = ", ".join(str(item) for item in value)
                    table.add_row(field, str(value))

            console.print(table)

    except Exception as e:
        console.print(f"[ERROR] Failed to show issue: {e}", style="bold red")
        raise typer.Exit(1)


def gitlab_import_command(
    issue_iid: int,
    include_parents: bool = False,
    output: Optional[str] = None,
):
    """
    Import a GitLab issue and its children as Taskinator tasks.
    """
    check_gitlab_available()

    try:
        # Initialize plugin
        plugin = GitLabPlugin()

        console.print(f"[green]Importing issue #{issue_iid} and its children...")

        # Import issue
        task_collection = plugin.import_issue_with_children(
            issue_iid,
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
                source.get("issue_type", ""),
                str(task.story_points) if task.story_points is not None else "",
                str(subtask_count) if subtask_count > 0 else "",
            )

        console.print(table)

        # Show next steps
        console.print("\n[bold]Next Steps:[/bold]")
        console.print("1. Review the generated tasks with [cyan]taskinator list[/cyan]")
        console.print("2. Start working on tasks with [cyan]taskinator next[/cyan]")

    except Exception as e:
        console.print(f"[ERROR] Failed to import issue: {e}", style="bold red")
        raise typer.Exit(1)


def gitlab_tree_command(
    issue_iid: int, levels_up: Optional[int] = None, levels_down: Optional[int] = None
):
    """Show the hierarchy tree of a GitLab issue."""
    check_gitlab_available()

    try:
        # Initialize plugin
        plugin = GitLabPlugin()

        console.print(f"[green]Fetching hierarchy tree for issue #{issue_iid}...")

        # Get the hierarchy
        tree = plugin.get_issue_hierarchy(issue_iid)

        # Display hierarchy
        console.print(f"[green]Issue hierarchy tree:")
        _print_hierarchy_tree(tree)

    except Exception as e:
        console.print(f"[ERROR] Failed to fetch issue hierarchy: {e}", style="bold red")
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
