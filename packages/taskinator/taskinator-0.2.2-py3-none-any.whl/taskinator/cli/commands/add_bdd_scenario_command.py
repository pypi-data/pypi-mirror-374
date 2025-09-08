"""
Add BDD scenario command implementation for Taskinator.
"""

import os
from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Prompt

from taskinator.core.file_storage import read_tasks, write_tasks
from taskinator.utils.config import get_config_value

console = Console()


def add_bdd_scenario_command(
    task_id: str = typer.Argument(..., help="Task ID to add BDD scenario to"),
    scenario_title: Optional[str] = typer.Option(
        None,
        "--title", "-t",
        help="Title for the BDD scenario"
    ),
    interactive: bool = typer.Option(
        True,
        "--interactive/--non-interactive",
        help="Use interactive mode to create the scenario"
    ),
    tasks_path: Optional[str] = typer.Option(
        None,
        "--tasks-file", "-f",
        help="Path to tasks.json file (defaults to ./tasks/tasks.json)"
    )
) -> None:
    """
    Add a BDD scenario to a specific task.
    
    This command allows you to add custom BDD scenarios to tasks, which will be
    included when exporting to Gherkin feature files. You can specify user stories,
    Given/When/Then steps, and acceptance criteria.
    
    Examples:
    
        # Add scenario interactively
        taskinator add-bdd-scenario 1
        
        # Add scenario with title
        taskinator add-bdd-scenario 1 --title "Handle large datasets"
        
        # Add to specific tasks file
        taskinator add-bdd-scenario 1 --tasks-file ./project/tasks/tasks.json
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
        
        # Read tasks
        task_collection = read_tasks(tasks_path)
        
        # Find the target task
        target_task = None
        for task in task_collection.tasks:
            if str(task.id) == str(task_id):
                target_task = task
                break
        
        if not target_task:
            console.print(f"[ERROR] Task {task_id} not found", style="bold red")
            return
        
        console.print(f"[INFO] Adding BDD scenario to task: {target_task.title}", style="blue")
        
        if interactive:
            # Interactive scenario creation
            console.print("\n[bold cyan]Creating BDD Scenario[/bold cyan]")
            
            if not scenario_title:
                scenario_title = Prompt.ask(
                    "[bold]Scenario title[/bold]",
                    default=f"Use {target_task.title} effectively"
                )
            
            console.print(f"\n[bold]Scenario: {scenario_title}[/bold]")
            
            # Collect Given steps
            console.print("\n[dim]Enter Given steps (preconditions). Press Enter on empty line to finish:[/dim]")
            given_steps = []
            while True:
                step = Prompt.ask("  Given", default="")
                if not step:
                    break
                given_steps.append(f"Given {step}")
            
            # Collect When steps
            console.print("\n[dim]Enter When steps (actions). Press Enter on empty line to finish:[/dim]")
            when_steps = []
            while True:
                step = Prompt.ask("  When", default="")
                if not step:
                    break
                when_steps.append(f"When {step}")
            
            # Collect Then steps
            console.print("\n[dim]Enter Then steps (outcomes). Press Enter on empty line to finish:[/dim]")
            then_steps = []
            while True:
                step = Prompt.ask("  Then", default="")
                if not step:
                    break
                then_steps.append(f"Then {step}")
            
            # Build the scenario
            scenario_lines = [f"  Scenario: {scenario_title}"]
            scenario_lines.extend([f"    {step}" for step in given_steps])
            scenario_lines.extend([f"    {step}" for step in when_steps])
            scenario_lines.extend([f"    {step}" for step in then_steps])
            
            scenario_text = "\n".join(scenario_lines)
            
        else:
            # Non-interactive mode - create a basic template
            if not scenario_title:
                scenario_title = f"Use {target_task.title} effectively"
            
            scenario_text = f"""  Scenario: {scenario_title}
    Given the {target_task.title.lower()} is available
    When I use it with appropriate inputs
    Then it should work as expected
    And the results should meet requirements"""
        
        # Add the scenario to the task
        if not hasattr(target_task, 'bdd_scenarios'):
            target_task.bdd_scenarios = []
        
        target_task.bdd_scenarios.append(scenario_text)
        
        # Save the updated tasks
        write_tasks(tasks_path, task_collection)
        
        console.print(f"\n[SUCCESS] Added BDD scenario to task {task_id}", style="green")
        console.print("\n[bold]Added scenario:[/bold]")
        console.print(scenario_text)
        
        # Show next steps
        console.print("\n[bold cyan]Next Steps:[/bold cyan]")
        console.print("1. Review the scenario you just added")
        console.print("2. Run 'taskinator export-gherkin' to generate feature files")
        console.print("3. Use the generated features with your BDD testing framework")
        console.print("4. Add more scenarios if needed with the same command")
        
    except Exception as e:
        console.print(f"[ERROR] Failed to add BDD scenario: {str(e)}", style="bold red")
        raise typer.Exit(1)