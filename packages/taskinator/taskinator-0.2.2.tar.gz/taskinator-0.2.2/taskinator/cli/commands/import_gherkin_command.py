"""
Import Gherkin command implementation for Taskinator.
"""

import os
from typing import Optional

import typer
from rich.console import Console

from taskinator.core.gherkin_importer import import_features_to_tasks
from taskinator.utils.config import get_config_value

console = Console()


def import_gherkin_command(
    features_dir: Optional[str] = typer.Option(
        None,
        "--features", "-f",
        help="Directory containing .feature files (defaults to ./features or ./tasks/features)"
    ),
    tasks_path: Optional[str] = typer.Option(
        None,
        "--tasks-file", "-t",
        help="Path to tasks.json file (defaults to ./tasks/tasks.json)"
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run", "-n",
        help="Show what would be changed without making actual modifications"
    )
) -> None:
    """
    Import/sync Gherkin feature files back to Taskinator tasks.
    
    This command reads modified Gherkin feature files and synchronizes any changes
    back to your Taskinator tasks. This enables a bi-directional BDD workflow
    where you can modify feature files and have those changes reflected in your
    task management.
    
    Examples:
    
        # Import changes from default features directory  
        taskinator import-gherkin
        
        # Import from specific directory
        taskinator import-gherkin --features ./bdd/features
        
        # Preview changes without making modifications
        taskinator import-gherkin --dry-run
        
        # Import to specific tasks file
        taskinator import-gherkin --tasks-file ./project/tasks/tasks.json
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
        
        if features_dir is None:
            # Try common locations for feature files (prioritize ./features)
            candidates = [
                os.path.join(os.getcwd(), "features"),  # ./features (standard BDD location)
                os.path.join(os.path.dirname(tasks_path), "features"),
                os.path.dirname(tasks_path)  # Same directory as tasks (legacy)
            ]
            
            for candidate in candidates:
                if os.path.isdir(candidate):
                    # Check if it actually contains .feature files
                    has_features = any(f.endswith('.feature') for f in os.listdir(candidate))
                    if has_features:
                        features_dir = candidate
                        break
            
            if features_dir is None:
                console.print("[ERROR] No features directory found", style="bold red")
                console.print("[INFO] Try:", style="yellow")
                console.print("  1. Run 'taskinator export-gherkin' first to create feature files", style="yellow")
                console.print("  2. Specify the features directory with --features", style="yellow")
                return
        
        if not os.path.isdir(features_dir):
            console.print(f"[ERROR] Features directory not found: {features_dir}", style="bold red")
            return
        
        console.print(f"[INFO] Importing features from {features_dir}", style="blue")
        console.print(f"[INFO] Target tasks file: {tasks_path}", style="blue")
        
        if dry_run:
            console.print("[INFO] DRY RUN MODE - No changes will be made", style="yellow")
            # TODO: Implement dry run functionality in the importer
            console.print("[WARNING] Dry run mode not yet implemented", style="yellow")
            return
        
        # Import features
        modified_count, processed_count = import_features_to_tasks(
            tasks_path=tasks_path,
            features_dir=features_dir
        )
        
        # Show results
        if modified_count > 0:
            console.print(f"\n[SUCCESS] Successfully synchronized {modified_count} tasks from {processed_count} feature files", style="green")
            
            # Show next steps
            console.print("\n[bold cyan]Next Steps:[/bold cyan]")
            console.print("1. Review the updated tasks with 'taskinator list'")
            console.print("2. Regenerate task files with 'taskinator generate-task-files'")
            console.print("3. Check dependencies with 'taskinator validate-dependencies'")
            
        elif processed_count > 0:
            console.print(f"\n[INFO] Processed {processed_count} feature files, but no tasks needed updating", style="blue")
            console.print("[INFO] This means your feature files are already in sync with your tasks", style="blue")
        else:
            console.print("\n[WARNING] No feature files were processed", style="yellow")
            console.print("[INFO] Make sure your features directory contains .feature files", style="yellow")
        
    except Exception as e:
        console.print(f"[ERROR] Failed to import Gherkin features: {str(e)}", style="bold red")
        raise typer.Exit(1)