"""
Sprint management commands for the Taskinator CLI.

This module implements commands for managing sprints and sprint tasks.
"""

import os
import json
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich.text import Text
from rich import box

from taskinator.core.sprint_manager import (
    create_sprint, get_sprint, update_sprint, delete_sprint,
    list_sprints, get_active_sprint, start_sprint, complete_sprint,
    cancel_sprint, get_sprint_tasks, add_task_to_sprint,
    remove_task_from_sprint, set_task_story_points,
    get_sprint_stats, update_sprint_progress, generate_burndown_data,
)
from taskinator.core.task_manager import read_tasks, write_tasks, get_tasks_path
from taskinator.models.sprint import Sprint, SprintStatus
from taskinator.utils.ui import console


def sprint_create_command(
    name: str,
    goal: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    capacity: Optional[float] = None,
) -> None:
    """Create a new sprint."""
    try:
        # Parse dates
        start_datetime = None
        if start_date:
            try:
                start_datetime = datetime.fromisoformat(start_date)
            except ValueError:
                console.print(f"[ERROR] Invalid start date format: {start_date}. Use YYYY-MM-DD.", style="bold red")
                return
                
        end_datetime = None
        if end_date:
            try:
                end_datetime = datetime.fromisoformat(end_date)
            except ValueError:
                console.print(f"[ERROR] Invalid end date format: {end_date}. Use YYYY-MM-DD.", style="bold red")
                return
        
        # Create sprint
        sprint = create_sprint(
            name=name,
            goal=goal or "",
            start_date=start_datetime,
            end_date=end_datetime,
            capacity=capacity,
        )
        
        console.print(f"[green]Sprint '{sprint.name}' created with ID: {sprint.id}")
        
        # Show sprint details
        table = Table(title=f"Sprint: {sprint.name}", box=box.ROUNDED)
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("ID", sprint.id)
        table.add_row("Name", sprint.name)
        table.add_row("Goal", sprint.goal or "")
        table.add_row("Status", sprint.status.value if hasattr(sprint.status, "value") else str(sprint.status))
        table.add_row("Start Date", sprint.start_date.strftime("%Y-%m-%d") if sprint.start_date else "")
        table.add_row("End Date", sprint.end_date.strftime("%Y-%m-%d") if sprint.end_date else "")
        table.add_row("Capacity", str(sprint.capacity) if sprint.capacity else "")
        
        console.print(table)
        
    except ValueError as e:
        console.print(f"[ERROR] {e}", style="bold red")
    except Exception as e:
        console.print(f"[ERROR] Failed to create sprint: {e}", style="bold red")


def sprint_list_command(
    status: Optional[str] = None,
) -> None:
    """List all sprints."""
    try:
        sprints = list_sprints(status)
        
        if not sprints:
            if status:
                console.print(f"[yellow]No sprints found with status: {status}")
            else:
                console.print("[yellow]No sprints found")
            return
            
        table = Table(title="Sprints", box=box.ROUNDED)
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Goal")
        table.add_column("Status", style="magenta")
        table.add_column("Dates", style="blue")
        table.add_column("Capacity", style="yellow")
        table.add_column("Progress", style="green")
        
        # Get active sprint for highlighting
        active_sprint = get_active_sprint()
        
        for sprint in sprints:
            # Format dates
            dates = ""
            if sprint.start_date:
                dates += f"Start: {sprint.start_date.strftime('%Y-%m-%d')}"
            if sprint.end_date:
                dates += f"\nEnd: {sprint.end_date.strftime('%Y-%m-%d')}"
                
            # Get sprint stats
            stats = get_sprint_stats(sprint.id)
            
            # Calculate progress
            progress = ""
            if stats.get("total_points", 0) > 0:
                completion = stats.get("completion_rate_points", 0) * 100
                progress = f"{completion:.1f}% ({stats.get('completed_points', 0)}/{stats.get('total_points', 0)} pts)"
            
            # Style for active sprint
            style = "bold" if active_sprint and active_sprint.id == sprint.id else ""
            
            table.add_row(
                sprint.id,
                sprint.name,
                Text(sprint.goal or "", style=style),
                sprint.status.value if hasattr(sprint.status, "value") else str(sprint.status),
                dates,
                str(sprint.capacity) if sprint.capacity else "",
                progress,
                style=style
            )
            
        console.print(table)
        
    except Exception as e:
        console.print(f"[ERROR] Failed to list sprints: {e}", style="bold red")


def sprint_show_command(
    sprint_id: str,
) -> None:
    """Show sprint details."""
    try:
        sprint = get_sprint(sprint_id)
        if not sprint:
            console.print(f"[ERROR] Sprint not found: {sprint_id}", style="bold red")
            return
            
        # Get sprint tasks
        tasks = get_sprint_tasks(sprint_id)
        
        # Get sprint stats
        stats = get_sprint_stats(sprint_id)
            
        # Show sprint details
        table = Table(title=f"Sprint: {sprint.name}", box=box.ROUNDED)
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("ID", sprint.id)
        table.add_row("Name", sprint.name)
        table.add_row("Goal", sprint.goal or "")
        table.add_row("Status", sprint.status.value if hasattr(sprint.status, "value") else str(sprint.status))
        table.add_row("Start Date", sprint.start_date.strftime("%Y-%m-%d") if sprint.start_date else "")
        table.add_row("End Date", sprint.end_date.strftime("%Y-%m-%d") if sprint.end_date else "")
        table.add_row("Capacity", str(sprint.capacity) if sprint.capacity else "")
        
        # Show progress info
        if stats.get("total_tasks", 0) > 0:
            table.add_row("Tasks", f"{stats.get('completed_tasks', 0)}/{stats.get('total_tasks', 0)} completed")
            
        if stats.get("total_points", 0) > 0:
            table.add_row("Story Points", f"{stats.get('completed_points', 0)}/{stats.get('total_points', 0)} completed")
            
        if sprint.status == SprintStatus.ACTIVE:
            table.add_row("Days", f"{stats.get('days_elapsed', 0)}/{stats.get('days_total', 0)} elapsed")
            
        if sprint.retrospective:
            table.add_row("Retrospective", sprint.retrospective)
            
        console.print(table)
        
        # Show tasks
        if tasks:
            tasks_table = Table(title=f"Tasks in Sprint: {sprint.name}", box=box.ROUNDED)
            tasks_table.add_column("ID", style="cyan")
            tasks_table.add_column("Title", style="green")
            tasks_table.add_column("Status", style="magenta")
            tasks_table.add_column("Story Points", style="yellow")
            tasks_table.add_column("Type", style="blue")
            tasks_table.add_column("Assignee", style="green")
            
            for task in tasks:
                # Status style
                status_style = "green" if task.status == "done" else "yellow" if task.status == "in-progress" else "red" if task.status == "blocked" else ""
                
                tasks_table.add_row(
                    str(task.id),
                    task.title,
                    Text(task.status, style=status_style),
                    str(task.story_points) if task.story_points is not None else "",
                    task.task_type or "",
                    task.assignee or ""
                )
                
            console.print(tasks_table)
        else:
            console.print("[yellow]No tasks in this sprint yet")
            
        # Show burndown if sprint is active or completed
        if sprint.status in (SprintStatus.ACTIVE, SprintStatus.COMPLETED) and sprint.progress:
            console.print("\n[bold]Burndown Chart:[/bold]")
            
            # Get burndown data
            burndown_data = generate_burndown_data(sprint_id)
            
            if "error" in burndown_data:
                console.print(f"[yellow]{burndown_data['error']}")
            else:
                # Display text-based burndown chart
                actual_burndown = burndown_data.get("actual_burndown", [])
                if actual_burndown:
                    burndown_table = Table(box=None)
                    burndown_table.add_column("Date", style="cyan")
                    burndown_table.add_column("Remaining", style="yellow")
                    burndown_table.add_column("Progress", style="green")
                    
                    max_points = max(entry.get("remaining", 0) for entry in actual_burndown)
                    
                    for entry in actual_burndown:
                        date = entry.get("date", "")
                        remaining = entry.get("remaining", 0)
                        
                        # Create a simple bar
                        if max_points > 0:
                            bar_width = 30
                            filled = int((remaining / max_points) * bar_width)
                            bar = "█" * filled + "░" * (bar_width - filled)
                        else:
                            bar = ""
                            
                        burndown_table.add_row(
                            date,
                            str(remaining),
                            bar
                        )
                        
                    console.print(burndown_table)
        
    except Exception as e:
        console.print(f"[ERROR] Failed to show sprint: {e}", style="bold red")


def sprint_start_command(
    sprint_id: str,
    start_date: Optional[str] = None,
) -> None:
    """Start a sprint."""
    try:
        # Parse start date
        start_datetime = None
        if start_date:
            try:
                start_datetime = datetime.fromisoformat(start_date)
            except ValueError:
                console.print(f"[ERROR] Invalid start date format: {start_date}. Use YYYY-MM-DD.", style="bold red")
                return
                
        # Start sprint
        if start_sprint(sprint_id, start_datetime):
            console.print(f"[green]Sprint {sprint_id} started successfully")
            
            # Show sprint details
            sprint_show_command(sprint_id)
        else:
            console.print(f"[ERROR] Failed to start sprint {sprint_id}", style="bold red")
            
    except ValueError as e:
        console.print(f"[ERROR] {e}", style="bold red")
    except Exception as e:
        console.print(f"[ERROR] Failed to start sprint: {e}", style="bold red")


def sprint_complete_command(
    sprint_id: str,
    notes: Optional[str] = None,
) -> None:
    """Complete a sprint."""
    try:
        # Complete sprint
        if complete_sprint(sprint_id, notes):
            console.print(f"[green]Sprint {sprint_id} completed successfully")
            
            # Show sprint details
            sprint_show_command(sprint_id)
        else:
            console.print(f"[ERROR] Failed to complete sprint {sprint_id}", style="bold red")
            
    except Exception as e:
        console.print(f"[ERROR] Failed to complete sprint: {e}", style="bold red")


def sprint_cancel_command(
    sprint_id: str,
) -> None:
    """Cancel a sprint."""
    try:
        # Cancel sprint
        if cancel_sprint(sprint_id):
            console.print(f"[green]Sprint {sprint_id} cancelled successfully")
        else:
            console.print(f"[ERROR] Failed to cancel sprint {sprint_id}", style="bold red")
            
    except Exception as e:
        console.print(f"[ERROR] Failed to cancel sprint: {e}", style="bold red")


def sprint_add_task_command(
    sprint_id: str,
    task_id: str,
    points: Optional[float] = None,
) -> None:
    """Add a task to a sprint."""
    try:
        # Add task to sprint
        if add_task_to_sprint(task_id, sprint_id, points):
            console.print(f"[green]Task {task_id} added to sprint {sprint_id} successfully")
        else:
            console.print(f"[ERROR] Failed to add task {task_id} to sprint {sprint_id}", style="bold red")
            
    except ValueError as e:
        console.print(f"[ERROR] {e}", style="bold red")
    except Exception as e:
        console.print(f"[ERROR] Failed to add task to sprint: {e}", style="bold red")


def sprint_remove_task_command(
    task_id: str,
) -> None:
    """Remove a task from its sprint."""
    try:
        # Remove task from sprint
        if remove_task_from_sprint(task_id):
            console.print(f"[green]Task {task_id} removed from sprint successfully")
        else:
            console.print(f"[ERROR] Failed to remove task {task_id} from sprint", style="bold red")
            
    except Exception as e:
        console.print(f"[ERROR] Failed to remove task from sprint: {e}", style="bold red")


def sprint_set_points_command(
    task_id: str,
    points: float,
) -> None:
    """Set story points for a task."""
    try:
        # Set story points
        if set_task_story_points(task_id, points):
            console.print(f"[green]Story points for task {task_id} set to {points}")
        else:
            console.print(f"[ERROR] Failed to set story points for task {task_id}", style="bold red")
            
    except Exception as e:
        console.print(f"[ERROR] Failed to set story points: {e}", style="bold red")


def sprint_update_progress_command(
    sprint_id: str,
    date_str: Optional[str] = None,
) -> None:
    """Update sprint progress tracking."""
    try:
        # Parse date
        current_date = None
        if date_str:
            try:
                current_date = datetime.fromisoformat(date_str)
            except ValueError:
                console.print(f"[ERROR] Invalid date format: {date_str}. Use YYYY-MM-DD.", style="bold red")
                return
                
        # Update progress
        if update_sprint_progress(sprint_id, current_date):
            console.print(f"[green]Progress for sprint {sprint_id} updated successfully")
            
            # Show sprint details
            sprint_show_command(sprint_id)
        else:
            console.print(f"[ERROR] Failed to update progress for sprint {sprint_id}", style="bold red")
            
    except Exception as e:
        console.print(f"[ERROR] Failed to update sprint progress: {e}", style="bold red")


def sprint_burndown_command(
    sprint_id: str,
    output: Optional[str] = None,
    format: str = "text",
) -> None:
    """Generate burndown chart for a sprint."""
    try:
        # Get sprint
        sprint = get_sprint(sprint_id)
        if not sprint:
            console.print(f"[ERROR] Sprint not found: {sprint_id}", style="bold red")
            return
            
        # Generate burndown data
        burndown_data = generate_burndown_data(sprint_id)
        
        if "error" in burndown_data:
            console.print(f"[ERROR] {burndown_data['error']}", style="bold red")
            return
            
        # Handle different output formats
        if format.lower() == "text":
            _display_text_burndown(burndown_data)
        elif format.lower() == "json":
            _export_json_burndown(burndown_data, output, sprint_id)
        else:
            console.print(f"[ERROR] Unsupported format: {format}", style="bold red")
            
    except Exception as e:
        console.print(f"[ERROR] Failed to generate burndown chart: {e}", style="bold red")


def _display_text_burndown(burndown_data: Dict[str, Any]) -> None:
    """Display a text-based burndown chart."""
    sprint_info = burndown_data.get("sprint", {})
    actual_burndown = burndown_data.get("actual_burndown", [])
    
    if not actual_burndown:
        console.print("[yellow]No burndown data available")
        return
        
    # Create table header
    console.print(f"\n[bold]Burndown Chart: {sprint_info.get('name', '')}[/bold]")
    
    table = Table(box=box.ROUNDED)
    table.add_column("Date", style="cyan")
    table.add_column("Remaining", style="yellow")
    table.add_column("Completed", style="green")
    table.add_column("Added", style="blue")
    table.add_column("Burndown", style="magenta")
    
    # Create progress bars for burndown
    max_points = sprint_info.get("initial_points", 0)
    
    for entry in actual_burndown:
        date = entry.get("date", "")
        remaining = entry.get("remaining", 0)
        completed = entry.get("completed", 0)
        added = entry.get("added", 0)
        
        # Create a simple bar
        if max_points > 0:
            bar_width = 20
            filled = int((remaining / max_points) * bar_width)
            bar = "█" * filled + "░" * (bar_width - filled)
        else:
            bar = ""
            
        table.add_row(
            date,
            str(remaining),
            str(completed),
            str(added),
            bar
        )
        
    console.print(table)
    
    # Show summary
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"Initial scope: {sprint_info.get('initial_points', 0)} points")
    console.print(f"Current scope: {sprint_info.get('current_points', 0)} points")
    console.print(f"Completion: {(1 - (burndown_data['actual_burndown'][-1]['remaining'] / max_points)) * 100:.1f}% complete")


def _export_json_burndown(burndown_data: Dict[str, Any], output_path: Optional[str], sprint_id: str) -> None:
    """Export burndown data to a JSON file."""
    if not output_path:
        output_path = f"sprint-{sprint_id}-burndown.json"
        
    try:
        with open(output_path, "w") as f:
            json.dump(burndown_data, f, indent=2)
            
        console.print(f"[green]Burndown data exported to: {output_path}")
    except (IOError, OSError) as e:
        console.print(f"[ERROR] Failed to write JSON file: {e}", style="bold red")