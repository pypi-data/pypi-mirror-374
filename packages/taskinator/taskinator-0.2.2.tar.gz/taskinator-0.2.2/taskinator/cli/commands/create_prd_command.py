"""
Create PRD command implementation for guided PRD creation.
"""

import os
import sys
import asyncio
from typing import Optional, Dict, Any, List
from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich import print as rprint

from taskinator.core import (
    PRDTemplate,
    TemplateType,
    template_manager,
    PRDCreator,
    PRDCreationState,
    UserCommand
)
from taskinator.core.task_manager import parse_prd
from taskinator.services.ai.ai_client import get_ai_client, is_ai_available
from taskinator.utils.config import get_config_value

console = Console()


def create_prd_command(
    name: Optional[str] = None,
    template: str = "standard",
    output: Optional[str] = None,
    update: Optional[str] = None,
) -> None:
    """
    Create a PRD document through guided interactive process.
    
    Args:
        name: Project or feature name (used for filename generation)
        template: PRD template to use (standard, minimal, feature)
        output: Custom output path
        update: Path to an existing PRD to update instead of creating new
    """
    # Verify AI client is available
    if not is_ai_available():
        console.print(
            "[ERROR] AI functionality is not available. Please check your model configuration and credentials.",
            style="bold red",
        )
        return

    try:
        client = get_ai_client()
        if client is None:
            console.print("[ERROR] Could not initialize AI client", style="bold red")
            return
    except Exception as e:
        console.print(f"[ERROR] Could not initialize AI client: {str(e)}", style="bold red")
        return

    # Get project name if not provided
    if not name:
        name = Prompt.ask(
            "[bold cyan]Enter project/feature name:[/bold cyan]", 
            default=os.path.basename(os.getcwd())
        )

    # Validate template type
    if not template_manager.validate_template_name(template.lower()):
        available_templates = [name for name, _ in template_manager.list_templates()]
        console.print(
            f"[ERROR] Invalid template type: {template}. Available templates: {', '.join(available_templates)}",
            style="bold red"
        )
        return

    # Create PRDCreator instance
    try:
        template_type = TemplateType(template.lower())
        creator = PRDCreator(
            name=name,
            template_type=template_type,
            output_path=output,
            update_path=update
        )
    except Exception as e:
        console.print(f"[ERROR] Could not initialize PRD creator: {str(e)}", style="bold red")
        return

    # Display welcome banner
    _display_welcome(creator)

    # Handle PRD creation session
    _handle_prd_creation_session(creator, client)


def _display_welcome(creator: PRDCreator) -> None:
    """Display welcome message and instructions."""
    welcome_message = creator.get_welcome_message()
    console.print("\n")
    console.print(
        Panel(
            welcome_message,
            title="PRD Creator",
            border_style="cyan",
        )
    )


def _handle_prd_creation_session(creator: PRDCreator, client) -> None:
    """Handle the interactive PRD creation session."""
    # Start the creation process
    section_key, section = creator.start()
    
    # Display the initial section prompt
    _display_section_prompt(section)
    
    try:
        while True:
            # Get user input
            console.print("\n[bold blue]Your input:[/bold blue] ", end="")
            user_input = _get_multiline_input()
            
            # Check if user wants to quit
            if user_input.lower() in ["quit", "exit", "q"]:
                if Confirm.ask("[yellow]Are you sure you want to exit? Progress may be lost.[/yellow]"):
                    console.print("[yellow]Exiting PRD creation.[/yellow]")
                    break
                else:
                    continue
                    
            # Handle input
            response = creator.handle_input(user_input)
            
            # Process response based on its type
            if response.get("type") == "help":
                console.print(Panel(response.get("message"), border_style="cyan"))
                
            elif response.get("type") in ["next_section", "previous_section", "edit_section"]:
                # Display section prompt for navigation
                _display_section_prompt(
                    response.get("section"), 
                    message=response.get("message"),
                    current_content=response.get("current_content", "")
                )
                
            elif response.get("type") == "preview":
                # Show preview of the PRD
                console.print(Panel(
                    f"PRD Preview ({response.get('completion_stats', {}).get('percentage', 0)}% complete)",
                    border_style="green"
                ))
                console.print(Markdown(response.get("markdown", "")))
                console.print("\nContinue editing or type /finish when complete.")
                
            elif response.get("type") == "finished":
                # PRD is complete
                console.print(Panel(
                    f"[green]✅ PRD creation complete![/green]",
                    border_style="green"
                ))
                
                # Save the PRD
                save_result = creator.handle_input("/save")
                if save_result.get("type") == "saved":
                    console.print(f"[green]PRD saved to {save_result.get('path')}[/green]")
                    
                    # Ask if user wants to generate tasks from this PRD
                    if Confirm.ask("[bold cyan]Would you like to generate tasks from this PRD?[/bold cyan]"):
                        _generate_tasks_from_prd(save_result.get('path'))
                        
                break
                
            elif response.get("type") == "saved":
                # PRD was saved
                console.print(f"[green]✅ PRD saved to {response.get('path')}[/green]")
                
            elif response.get("type") == "error":
                # Error occurred
                console.print(f"[bold red]Error: {response.get('message')}[/bold red]")
                
            elif response.get("type") == "warning":
                # Warning message
                console.print(f"[bold yellow]Warning: {response.get('message')}[/bold yellow]")
                
            elif response.get("type") == "info":
                # Informational message
                console.print(f"[cyan]{response.get('message')}[/cyan]")
                
            elif response.get("type") == "content_updated":
                # Content was updated
                if response.get("validation_errors"):
                    # Display validation errors
                    console.print("[yellow]Validation issues:[/yellow]")
                    for error in response.get("validation_errors", []):
                        console.print(f"[yellow]- {error}[/yellow]")
                        
                # If there's a next section, display it
                if "next_section" in response:
                    _display_section_prompt(
                        response.get("next_section"), 
                        message=response.get("message")
                    )
                else:
                    console.print(response.get("message"))
                    
    except KeyboardInterrupt:
        console.print("\n[yellow]PRD creation interrupted.[/yellow]")
        if Confirm.ask("[bold yellow]Would you like to save your progress?[/bold yellow]"):
            save_result = creator.handle_input("/save")
            if save_result.get("type") == "saved":
                console.print(f"[green]PRD saved to {save_result.get('path')}[/green]")
                
    except Exception as e:
        console.print(f"[bold red]Error during PRD creation: {str(e)}[/bold red]")


def _display_section_prompt(section, message=None, current_content="") -> None:
    """Display the prompt for a PRD section."""
    if message:
        console.print(f"[cyan]{message}[/cyan]")
    
    # Display section information
    # Create panel content
    panel_content = f"[bold]{section.title}[/bold]\n\n{section.description}\n\n[cyan]{section.prompt}[/cyan]"
    
    # Add example if available
    if section.examples:
        panel_content += f"\n\n[dim]Example:\n{section.examples[0]}[/dim]"
    
    console.print(
        Panel(
            panel_content,
            border_style="blue",
            title=f"{'Required' if section.required else 'Optional'} Section"
        )
    )
    
    # If editing existing content, show it
    if current_content:
        console.print("\n[bold]Current content:[/bold]")
        console.print(Syntax(current_content, "markdown"))
        
    console.print("\n[dim]Type your response or use commands like /help, /skip, /back, /preview[/dim]")


def _get_multiline_input() -> str:
    """
    Get user input that properly handles multi-line pasting.
    
    Detects multi-line paste operations and treats them as a single
    input rather than multiple separate interactions.
    
    Returns:
        str: The complete user input
    """
    import sys
    import select
    
    # Read the first line
    first_line = input()
    
    # Check if there's immediately more input available (indicates a paste)
    ready, _, _ = select.select([sys.stdin], [], [], 0)
    if ready:
        # More input is buffered - read all of it
        additional_lines = []
        while True:
            ready, _, _ = select.select([sys.stdin], [], [], 0.1)
            if ready:
                line = sys.stdin.readline().rstrip('\n\r')
                if line:
                    additional_lines.append(line)
                else:
                    break
            else:
                break
        
        # Combine all lines if we found additional content
        if additional_lines:
            all_lines = [first_line] + additional_lines
            return '\n'.join(all_lines).strip()
    
    # Single line input
    return first_line.strip()


def _get_ai_assistance(client, prompt: str, context: Dict[str, Any]) -> str:
    """Get AI assistance during PRD creation."""
    try:
        from taskinator.utils.config import get_model_config
        
        model_config = get_model_config()
        system_prompt = f"""You are an AI assistant helping with PRD (Product Requirements Document) creation.
        The user is working on a '{context.get('template_name')}' section about '{context.get('section_title')}'. 
        
        {context.get('section_description')}
        
        Provide helpful, concise guidance that helps the user write an effective section.
        Focus on being practical, concrete, and specific.
        If the user asks for an example, provide a realistic example for this section.
        Keep responses brief and focused, under 250 words.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        response = client.completion(
            model=model_config["model"],
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content if response.choices else ""
    
    except Exception as e:
        return f"Error getting AI assistance: {str(e)}"


def _generate_tasks_from_prd(prd_path: str) -> None:
    """Generate tasks from the created PRD."""
    try:
        # Ask for number of tasks to generate
        num_tasks = int(Prompt.ask(
            "[bold cyan]How many tasks would you like to generate?[/bold cyan]", 
            default="10"
        ))
        
        # Generate tasks
        console.print("[cyan]Generating tasks from PRD...[/cyan]")
        tasks_path = os.path.join(os.getcwd(), "tasks", "tasks.json")
        parse_prd(prd_path, tasks_path, num_tasks)
        
        console.print("[green]✅ Tasks generated successfully![/green]")
        console.print("Run 'taskinator list' to see the generated tasks.")
        
    except Exception as e:
        console.print(f"[bold red]Error generating tasks: {str(e)}[/bold red]")