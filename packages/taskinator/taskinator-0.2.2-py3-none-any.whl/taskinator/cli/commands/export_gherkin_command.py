"""
Export Gherkin command implementation for Taskinator.
"""

import json
import os
from typing import Optional

import typer
from rich.console import Console

from taskinator.core.gherkin_exporter import (
    export_tasks_to_gherkin,
    export_tasks_to_individual_features
)
from taskinator.utils.config import get_config_value

console = Console()


def export_gherkin_command(
    output_dir: Optional[str] = typer.Option(
        None, 
        "--output", "-o", 
        help="Output directory for feature files (defaults to ./features)"
    ),
    project_name: Optional[str] = typer.Option(
        None,
        "--project", "-p",
        help="Project name for the feature file (defaults to 'Project')"
    ),
    individual: bool = typer.Option(
        True,
        "--individual/--combined", "-i",
        help="Export each task to its own feature file (default: True)"
    ),
    tasks_path: Optional[str] = typer.Option(
        None,
        "--tasks-file", "-f",
        help="Path to tasks.json file (defaults to ./tasks/tasks.json)"
    )
) -> None:
    """
    Export tasks to Gherkin feature files for BDD testing.
    
    This command converts your Taskinator tasks into executable Gherkin feature files
    that can be used with BDD testing frameworks like Cucumber, pytest-bdd, etc.
    
    Examples:
    
        # Export all tasks to a single feature file
        taskinator export-gherkin
        
        # Export each task to individual feature files
        taskinator export-gherkin --individual
        
        # Export to specific directory with project name
        taskinator export-gherkin --output ./features --project "My App"
        
        # Export from specific tasks file
        taskinator export-gherkin --tasks-file ./project/tasks/tasks.json
    """
    try:
        # Set default values
        if tasks_path is None:
            tasks_path = get_config_value("tasks_file_path")
            if not tasks_path:
                tasks_path = os.path.join(os.getcwd(), "tasks", "tasks.json")
        
        if not os.path.exists(tasks_path):
            console.print(f"[ERROR] Tasks file not found: {tasks_path}", style="bold red")
            console.print("[INFO] Run 'taskinator init' or 'taskinator parse-prd' to create tasks", style="yellow")
            return
        
        if project_name is None:
            # Try to get project name from tasks.json metadata
            try:
                with open(tasks_path, "r") as f:
                    data = json.load(f)
                    if "metadata" in data and "project_name" in data["metadata"]:
                        project_name = data["metadata"]["project_name"]
            except Exception:
                pass
                
            # Fall back to current directory name if no project name found
            if project_name is None:
                project_name = os.path.basename(os.getcwd())
        
        if output_dir is None:
            # Use the same logic as the core exporter
            project_root = os.path.dirname(os.path.dirname(tasks_path))
            output_dir = os.path.join(project_root, "features")
        
        console.print(f"[INFO] Exporting tasks from {tasks_path}", style="blue")
        console.print(f"[INFO] Output directory: {output_dir}", style="blue")
        console.print(f"[INFO] Project name: {project_name}", style="blue")
        
        if individual:
            # Export each task to its own feature file (DEFAULT)
            console.print("[INFO] Exporting each task to its own feature file...", style="blue")
            feature_paths = export_tasks_to_individual_features(
                tasks_path=tasks_path,
                output_dir=output_dir,
                project_name=project_name
            )
            
            if feature_paths:
                console.print(f"\n[SUCCESS] Successfully exported {len(feature_paths)} feature files:", style="green")
                for path in feature_paths[:5]:  # Show first 5
                    console.print(f"  - {os.path.relpath(path)}", style="dim")
                if len(feature_paths) > 5:
                    console.print(f"  ... and {len(feature_paths) - 5} more files", style="dim")
        else:
            # Export all tasks to a single combined feature file
            console.print("[INFO] Exporting tasks to single combined feature file...", style="blue")
            feature_path = export_tasks_to_gherkin(
                tasks_path=tasks_path,
                output_dir=output_dir,
                project_name=project_name
            )
            
            if feature_path:
                console.print(f"\n[SUCCESS] Combined feature file created: {os.path.relpath(feature_path)}", style="green")
        
        # Show next steps
        console.print("\n[bold cyan]Next Steps:[/bold cyan]")
        console.print("1. Review the generated feature files")
        console.print("2. Modify scenarios as needed for your BDD tests")
        console.print("3. Use 'taskinator import-gherkin' to sync changes back to tasks")
        console.print("4. Run your BDD test suite (e.g., pytest-bdd, cucumber)")
        
    except Exception as e:
        console.print(f"[ERROR] Failed to export Gherkin features: {str(e)}", style="bold red")
        raise typer.Exit(1)