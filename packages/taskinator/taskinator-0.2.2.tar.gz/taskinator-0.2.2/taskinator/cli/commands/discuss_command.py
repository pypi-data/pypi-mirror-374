"""
Discuss command implementation for interactive task discussion and modification.
"""

import json
import os
import sys
from typing import Optional

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from taskinator.core.file_storage import read_tasks, write_tasks
from taskinator.core.task_expansion import expand_task
from taskinator.cli.commands.analyze_complexity_command import analyze_complexity_command
from taskinator.cli.commands.next_command import next_command
from taskinator.cli.commands.set_status_command import set_status_command
from taskinator.cli.commands.show_command import show_command
from taskinator.services.ai.ai_client import get_ai_client, get_model_config, is_ai_available
from taskinator.utils.config import get_config_value

console = Console()


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


def discuss_command(
    task_id: Optional[str] = None,
    comment: Optional[str] = None,
    project_dir: str = None,
) -> None:
    """
    Interactive discussion interface for task modifications.

    Args:
        task_id: Optional specific task ID to discuss
        comment: Optional non-interactive comment for direct processing
        project_dir: Project directory (defaults to current directory)
    """
    if project_dir is None:
        project_dir = os.getcwd()

    tasks_path = os.path.join(project_dir, "tasks", "tasks.json")

    # Load current tasks
    try:
        task_collection = read_tasks(tasks_path)
        # Convert Task objects to dictionaries for easier manipulation
        tasks = [
            task.model_dump() if hasattr(task, "model_dump") else task
            for task in task_collection.tasks
        ]
    except Exception as e:
        console.print(f"[ERROR] Could not load tasks: {str(e)}", style="bold red")
        return

    if not tasks:
        console.print(
            "[ERROR] No tasks found. Run 'taskinator init' or 'taskinator parse-prd' first.",
            style="bold red",
        )
        return

    # Check if AI is available
    if not is_ai_available():
        console.print(
            "[ERROR] AI functionality is not available. Please check your model configuration and credentials.",
            style="bold red",
        )
        return
    
    # Initialize AI client
    try:
        client = get_ai_client()
        if client is None:
            console.print(
                "[ERROR] Could not initialize AI client", style="bold red"
            )
            return
    except Exception as e:
        console.print(
            f"[ERROR] Could not initialize AI client: {str(e)}", style="bold red"
        )
        return

    # Display context
    _display_discussion_context(tasks, task_id)

    # Handle non-interactive mode
    if comment:
        _handle_non_interactive_discussion(
            tasks, tasks_path, client, comment, task_id, task_collection, project_dir
        )
        return

    # Interactive discussion loop
    _handle_interactive_discussion(tasks, tasks_path, client, task_id, task_collection, project_dir)


def _display_discussion_context(tasks: list, task_id: Optional[str] = None) -> None:
    """Display the current context for discussion."""
    console.print("\n")
    console.print(
        Panel.fit(
            "🤝 [bold cyan]Task Discussion Interface[/bold cyan]\n\n"
            "You can discuss modifications to your task list with the AI assistant.\n"
            "The assistant can help reorder tasks, modify priorities, adjust dependencies,\n"
            "update task descriptions, and more.\n\n"
            "[dim]Type 'help' for commands, 'quit' to exit[/dim]",
            border_style="cyan",
        )
    )

    if task_id:
        # Show specific task context
        task = next((t for t in tasks if t.get("id") == task_id), None)
        if task:
            console.print(f"\n[bold]Discussing Task {task_id}:[/bold]")
            console.print(f"Title: {task.get('title', 'N/A')}")
            console.print(f"Status: {task.get('status', 'N/A')}")
            console.print(f"Priority: {task.get('priority', 'N/A')}")
            console.print(
                f"Dependencies: {', '.join(task.get('dependencies', [])) or 'None'}"
            )
            if task.get("description"):
                console.print(
                    f"Description: {task['description'][:200]}{'...' if len(task['description']) > 200 else ''}"
                )
        else:
            console.print(f"[ERROR] Task {task_id} not found", style="bold red")
            return
    else:
        # Show project overview
        console.print(f"\n[bold]Project Overview:[/bold]")
        console.print(f"Total Tasks: {len(tasks)}")

        status_counts = {}
        priority_counts = {}
        for task in tasks:
            status = task.get("status", "unknown")
            priority = task.get("priority", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
            priority_counts[priority] = priority_counts.get(priority, 0) + 1

        console.print("Status Distribution:", dict(status_counts))
        console.print("Priority Distribution:", dict(priority_counts))

        console.print("\n[bold]Current Task Order:[/bold]")
        for i, task in enumerate(tasks[:10], 1):  # Show first 10 tasks
            title = task.get("title", "Untitled")[:50]
            console.print(f"  {i}. {title} (Priority: {task.get('priority', 'N/A')})")
        if len(tasks) > 10:
            console.print(f"  ... and {len(tasks) - 10} more tasks")


def _handle_interactive_discussion(
    tasks: list,
    tasks_path: str,
    client,
    task_id: Optional[str] = None,
    task_collection=None,
    project_dir: str = None,
) -> None:
    """Handle the interactive discussion loop."""
    if project_dir is None:
        project_dir = os.getcwd()
        
    console.print(
        "\n[bold green]Ready to discuss! What would you like to do?[/bold green]"
    )
    console.print(
        "[dim]Task Management: 'reorder tasks 2 and 3', 'increase priority of task 5'[/dim]"
    )
    console.print(
        "[dim]Direct Commands: 'analyze --research', 'expand 3 --num 5', 'next', 'status 2 completed'[/dim]"
    )
    console.print(
        "[dim]Stack Management: 'stack suggest', 'stack discuss', 'stack show', 'tech stack'[/dim]\n"
    )

    conversation_history = []

    while True:
        try:
            # Handle multi-line input properly
            console.print("[bold blue]You:[/bold blue] ", end="")
            user_input = _get_multiline_input()

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit", "q"]:
                console.print("[yellow]Goodbye![/yellow]")
                break
            elif user_input.lower() == "help":
                _show_help()
                continue
            elif user_input.lower() in ["show", "list", "current"]:
                _display_current_tasks(tasks)
                continue
            elif user_input.lower().startswith(("analyze", "complexity")):
                _handle_analyze_command(user_input, project_dir)
                continue
            elif user_input.lower().startswith("expand"):
                _handle_expand_command(user_input, tasks_path)
                continue
            elif user_input.lower().startswith("next"):
                _handle_next_command(project_dir)
                continue
            elif user_input.lower().startswith("status"):
                _handle_status_command(user_input, project_dir)
                continue
            elif user_input.lower().startswith(("stack", "technology stack", "tech stack")):
                _handle_stack_discussion_command(user_input, project_dir)
                continue
            elif user_input.lower().startswith(("show task", "show ")):
                _handle_show_task_command(user_input, project_dir)
                # After showing a task, provide a gentle hint about available options
                if user_input.lower().startswith("show "):
                    parts = user_input.split()
                    if len(parts) >= 2:
                        task_id_shown = parts[1]
                        console.print(f"\n[dim]💡 You can ask for suggestions, show other tasks, or request modifications[/dim]")
                continue

            # Add user input to conversation history
            conversation_history.append({"role": "user", "content": user_input})

            # Get AI response
            console.print("\n[dim]🤔 Thinking...[/dim]")
            ai_response = _get_ai_response(client, tasks, conversation_history, task_id)

            if ai_response:
                # Display AI response
                console.print(f"\n[bold green]Assistant:[/bold green]")
                console.print(Markdown(ai_response))

                # Add AI response to conversation history
                conversation_history.append(
                    {"role": "assistant", "content": ai_response}
                )

                # Check if the response suggests actual changes that need implementation
                has_specific_changes = any(word in ai_response.lower() for word in [
                    "reorder", "move", "change", "update", "modify", "set", "add", "remove"
                ])
                
                # Only ask about implementation if the AI is suggesting specific changes
                if has_specific_changes and ("implement" in ai_response.lower() or "apply" in ai_response.lower()):
                    # Check if AI already included a question about implementing
                    if "would you like me to implement" not in ai_response.lower():
                        implement = Prompt.ask(
                            "\n[bold yellow]Would you like me to implement these changes?[/bold yellow] (y/n)",
                            default="n",
                        )
                    else:
                        # AI already asked, just get the answer
                        implement = Prompt.ask("(y/n)", default="n")
                    
                    if implement.lower() in ["y", "yes"]:
                        _implement_changes(
                            tasks,
                            tasks_path,
                            client,
                            conversation_history,
                            task_collection,
                        )

        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"\n[ERROR] {str(e)}", style="bold red")


def _handle_non_interactive_discussion(
    tasks: list,
    tasks_path: str,
    client,
    comment: str,
    task_id: Optional[str] = None,
    task_collection=None,
    project_dir: str = None,
) -> None:
    """Handle non-interactive discussion with direct comment processing."""
    console.print(f"\n[bold blue]Processing request:[/bold blue] {comment}")

    conversation_history = [{"role": "user", "content": comment}]

    # Get AI response
    console.print("\n[dim]🤔 Analyzing request...[/dim]")
    ai_response = _get_ai_response(client, tasks, conversation_history, task_id)

    if ai_response:
        console.print(f"\n[bold green]Assistant:[/bold green]")
        console.print(Markdown(ai_response))

        # Automatically implement changes in non-interactive mode
        conversation_history.append({"role": "assistant", "content": ai_response})
        _implement_changes(
            tasks, tasks_path, client, conversation_history, task_collection
        )


def _get_ai_response(
    client, tasks: list, conversation_history: list, task_id: Optional[str] = None
) -> str:
    """Get AI response for the current conversation."""

    # Prepare context
    context = f"""You are an AI assistant helping to manage and modify a task list for a software project. 

Current tasks:
{json.dumps(tasks, indent=2)}

{"Focused on task ID: " + task_id if task_id else "Discussing the entire project"}

You can help with:
- Reordering tasks
- Changing task priorities  
- Modifying dependencies
- Updating task descriptions
- Adding or removing tasks
- Adjusting task status
- Analyzing and discussing tasks
- Providing suggestions and insights

IMPORTANT CONTEXT AWARENESS:
- If the user is just viewing or asking about a task (like "show 1"), provide analysis, insights, or suggestions rather than asking to implement changes
- If the user is asking for specific modifications (like "reorder tasks 2 and 3"), then explain what you would do and ask if they want you to implement the changes
- When viewing tasks, offer helpful suggestions like "This task might benefit from...", "Consider breaking this down into...", "This depends on...", etc.
- Only use "implement" or "apply" language when the user has requested actual changes to be made

Be conversational and helpful, matching the intent of the user's request."""

    try:
        model_config = get_model_config()
        messages = [{"role": "system", "content": context}] + conversation_history

        response = client.completion(
            model=model_config["model"],
            messages=messages,
            max_tokens=model_config["max_tokens"],
            temperature=model_config["temperature"]
        )

        return response.choices[0].message.content if response.choices else ""

    except Exception as e:
        console.print(f"[ERROR] AI request failed: {str(e)}", style="bold red")
        return ""


def _implement_changes(
    tasks: list,
    tasks_path: str,
    client,
    conversation_history: list,
    task_collection=None,
) -> None:
    """Implement the discussed changes to the task list."""
    
    # If task_collection is not provided, we need to read it from the file
    if task_collection is None:
        from taskinator.core.file_storage import read_tasks
        task_collection = read_tasks(tasks_path)

    # Get structured change instructions from AI
    change_prompt = """Based on our conversation, please provide specific JSON instructions for modifying the task list. 

IMPORTANT: Return ONLY valid JSON, no markdown code blocks, no explanations, no other text.

The JSON object must have this exact structure:
{
  "changes": [
    {
      "action": "reorder|update_priority|update_dependencies|update_task|add_task|remove_task",
      "task_id": "string_id_of_task",
      "details": {"key": "value"}
    }
  ]
}

Supported actions:
- "reorder": details {"new_position": number}
- "update_priority": details {"priority": "high|medium|low"}
- "update_dependencies": details {"dependencies": ["id1", "id2"]}
- "update_task": details {"title": "...", "description": "...", etc}

Example:
{
  "changes": [
    {"action": "reorder", "task_id": "2", "details": {"new_position": 3}},
    {"action": "reorder", "task_id": "3", "details": {"new_position": 2}}
  ]
}

Return only the JSON object with no other formatting or text."""

    try:
        model_config = get_model_config()
        messages = conversation_history + [{"role": "user", "content": change_prompt}]

        response = client.completion(
            model=model_config["model"],
            messages=messages,
            max_tokens=model_config["max_tokens"],
            temperature=model_config["temperature"]
        )

        if response.choices:
            change_instructions = response.choices[0].message.content.strip()

            # Try to parse JSON
            try:
                # Clean up the JSON string to handle formatting issues
                json_str = change_instructions.strip()
                
                # Try to extract JSON from code blocks if present
                if "```json" in json_str:
                    json_parts = json_str.split("```json")
                    if len(json_parts) > 1:
                        json_content = json_parts[1].split("```")[0].strip()
                        json_str = json_content
                elif "```" in json_str:
                    json_parts = json_str.split("```")
                    if len(json_parts) > 1:
                        json_content = json_parts[1].strip()
                        json_str = json_content
                
                # Remove any leading/trailing whitespace and newlines
                json_str = json_str.strip()
                
                # Try to find JSON object boundaries if not clean
                if not json_str.startswith("{"):
                    start_idx = json_str.find("{")
                    if start_idx != -1:
                        json_str = json_str[start_idx:]
                
                if not json_str.endswith("}"):
                    end_idx = json_str.rfind("}")
                    if end_idx != -1:
                        json_str = json_str[:end_idx + 1]

                changes = json.loads(json_str)
                _apply_changes(tasks, changes)

                # Save updated tasks
                # Convert dictionaries back to Task objects
                from taskinator.models.task import Task

                task_collection.tasks = [
                    Task(**task) if isinstance(task, dict) else task for task in tasks
                ]
                write_tasks(tasks_path, task_collection)
                console.print(
                    "\n[bold green]✅ Changes applied successfully![/bold green]"
                )

                # Show updated task list summary
                _display_current_tasks(tasks[:5])  # Show first 5 tasks
                
                # Clear conversation history after successful implementation
                conversation_history = []
                
                # Provide guidance for next steps
                console.print("\n[bold cyan]Changes applied successfully![/bold cyan]")
                console.print("[dim]What would you like to do next?[/dim]")
                console.print("[dim]- Continue with task management[/dim]")
                console.print("[dim]- Run 'analyze' for complexity analysis[/dim]")
                console.print("[dim]- Run 'next' to see recommended tasks[/dim]")
                console.print("[dim]- Type 'quit' to exit[/dim]")

            except json.JSONDecodeError as e:
                console.print(
                    f"[ERROR] Could not parse change instructions as JSON: {str(e)}",
                    style="bold red",
                )
                console.print(
                    f"[DEBUG] Raw response: {change_instructions[:500]}...",
                    style="dim",
                )

    except Exception as e:
        console.print(
            f"[ERROR] Failed to implement changes: {str(e)}", style="bold red"
        )


def _apply_changes(tasks: list, changes: dict) -> None:
    """Apply the structured changes to the task list."""

    for change in changes.get("changes", []):
        action = change.get("action")
        task_id = change.get("task_id")
        details = change.get("details", {})

        if action == "reorder":
            _reorder_task(tasks, task_id, details.get("new_position"))
        elif action == "update_priority":
            _update_task_field(tasks, task_id, "priority", details.get("priority"))
        elif action == "update_dependencies":
            _update_task_field(
                tasks, task_id, "dependencies", details.get("dependencies", [])
            )
        elif action == "update_task":
            _update_task_multiple_fields(tasks, task_id, details)
        # Add more actions as needed


def _reorder_task(tasks: list, task_id: str, new_position: int) -> None:
    """Reorder a task to a new position."""
    # Find the task
    task_index = next((i for i, t in enumerate(tasks) if t.get("id") == task_id), None)
    if task_index is not None and 0 <= new_position - 1 < len(tasks):
        task = tasks.pop(task_index)
        tasks.insert(new_position - 1, task)


def _update_task_field(tasks: list, task_id: str, field: str, value) -> None:
    """Update a specific field of a task."""
    task = next((t for t in tasks if t.get("id") == task_id), None)
    if task:
        task[field] = value


def _update_task_multiple_fields(tasks: list, task_id: str, updates: dict) -> None:
    """Update multiple fields of a task."""
    task = next((t for t in tasks if t.get("id") == task_id), None)
    if task:
        task.update(updates)


def _show_help() -> None:
    """Show help information for the discuss interface."""
    help_text = """
[bold]Available Commands:[/bold]
- [cyan]help[/cyan] - Show this help message
- [cyan]show/list/current[/cyan] - Display current task list
- [cyan]analyze[/cyan] or [cyan]complexity[/cyan] - Analyze task complexity
- [cyan]expand <task_id>[/cyan] - Expand a task into subtasks
- [cyan]next[/cyan] - Get next recommended task
- [cyan]status <task_id> <new_status>[/cyan] - Change task status
- [cyan]show <task_id>[/cyan] - Show detailed task information
- [cyan]quit/exit/q[/cyan] - Exit the discussion

[bold]Task Management Requests:[/bold]
- "Reorder tasks 2 and 3"
- "Move task 5 to position 2"
- "Increase priority of task 4 to high"
- "Remove dependency on task 1 from task 3"
- "Change the title of task 2 to 'New Title'"
- "Add a dependency on task 1 to task 4"

[bold]Direct Commands:[/bold]
- [cyan]analyze --research[/cyan] - Run complexity analysis with research
- [cyan]expand 3 --num 5[/cyan] - Expand task 3 into 5 subtasks
- [cyan]status 2 completed[/cyan] - Mark task 2 as completed
- [cyan]show 4[/cyan] - Show details for task 4

[bold]Stack Management:[/bold]
- [cyan]stack suggest[/cyan] - Generate technology stack suggestions
- [cyan]stack discuss[/cyan] - Interactive discussion about stack
- [cyan]stack show[/cyan] - Show current stack status
- [cyan]tech stack[/cyan] - Alternative way to access stack features

[bold]Tips:[/bold]
- Use direct commands for quick actions
- Use natural language for complex modifications
- The assistant will explain changes before implementing them
"""
    console.print(Panel(help_text, title="Help", border_style="blue"))


def _display_current_tasks(tasks: list) -> None:
    """Display a summary of current tasks."""
    console.print("\n[bold]Current Tasks:[/bold]")
    for i, task in enumerate(tasks, 1):
        title = task.get("title", "Untitled")[:50]
        priority = task.get("priority", "N/A")
        status = task.get("status", "N/A")
        deps = ", ".join(task.get("dependencies", [])) or "None"
        console.print(f"  {i}. {title}")
        console.print(
            f"     Priority: {priority}, Status: {status}, Dependencies: {deps}"
        )


def _handle_analyze_command(user_input: str, project_dir: str) -> None:
    """Handle analyze/complexity command."""
    try:
        # Parse options from user input
        research = "--research" in user_input or "research" in user_input.lower()
        
        # Change to project directory for the command
        old_cwd = os.getcwd()
        os.chdir(project_dir)
        
        console.print(f"[INFO] Running complexity analysis{'with research' if research else ''}...")
        
        # Run the analyze command
        import asyncio
        asyncio.run(analyze_complexity_command(research=research))
        
    except Exception as e:
        console.print(f"[ERROR] Error running analysis: {str(e)}", style="bold red")
    finally:
        # Restore original directory
        os.chdir(old_cwd)


def _handle_expand_command(user_input: str, tasks_path: str) -> None:
    """Handle expand task command."""
    try:
        # Parse task ID and options from user input
        parts = user_input.lower().split()
        task_id = None
        num_subtasks = 3
        force = False
        
        # Look for task ID (first number after 'expand')
        for i, part in enumerate(parts):
            if part == "expand" and i + 1 < len(parts):
                try:
                    task_id = parts[i + 1]
                    break
                except (ValueError, IndexError):
                    continue
        
        # Look for --num option
        if "--num" in user_input:
            try:
                num_idx = parts.index("--num")
                if num_idx + 1 < len(parts):
                    num_subtasks = int(parts[num_idx + 1])
            except (ValueError, IndexError):
                pass
        
        # Look for --force option
        force = "--force" in user_input or "force" in user_input.lower()
        
        if not task_id:
            console.print("[ERROR] Please specify a task ID to expand", style="bold red")
            console.print("[INFO] Example: expand 3 --num 5", style="yellow")
            return
        
        console.print(f"[INFO] Expanding task {task_id} into {num_subtasks} subtasks...")
        
        # Run the expand command
        expand_task(
            tasks_path=tasks_path,
            task_id=str(task_id),
            num_subtasks=num_subtasks,
            force=force
        )
        
    except Exception as e:
        console.print(f"[ERROR] Error expanding task: {str(e)}", style="bold red")


def _handle_next_command(project_dir: str) -> None:
    """Handle next task command."""
    try:
        old_cwd = os.getcwd()
        os.chdir(project_dir)
        
        console.print("[INFO] Finding next recommended task...")
        next_command()
        
    except Exception as e:
        console.print(f"[ERROR] Error getting next task: {str(e)}", style="bold red")
    finally:
        os.chdir(old_cwd)


def _handle_status_command(user_input: str, project_dir: str) -> None:
    """Handle status change command."""
    try:
        # Parse task ID and status from user input
        parts = user_input.split()
        task_id = None
        new_status = None
        
        # Look for task ID and status
        if len(parts) >= 3:  # status <id> <status>
            task_id = parts[1]
            new_status = parts[2]
        
        if not task_id or not new_status:
            console.print("[ERROR] Please specify task ID and new status", style="bold red")
            console.print("[INFO] Example: status 3 completed", style="yellow")
            return
        
        old_cwd = os.getcwd()
        os.chdir(project_dir)
        
        console.print(f"[INFO] Setting task {task_id} status to {new_status}...")
        set_status_command(task_id=task_id, status=new_status)
        
    except Exception as e:
        console.print(f"[ERROR] Error setting task status: {str(e)}", style="bold red")
    finally:
        os.chdir(old_cwd)


def _handle_show_task_command(user_input: str, project_dir: str) -> None:
    """Handle show task command."""
    try:
        # Parse task ID from user input
        parts = user_input.split()
        task_id = None
        
        # Handle both "show task X" and "show X" formats
        if len(parts) >= 2:
            if parts[0].lower() == "show":
                if parts[1].lower() == "task" and len(parts) >= 3:
                    # "show task X" format
                    task_id = parts[2]
                else:
                    # "show X" format
                    task_id = parts[1]
        
        if not task_id:
            console.print("[ERROR] Please specify a task ID", style="bold red")
            console.print("[INFO] Examples: 'show 3' or 'show task 3'", style="yellow")
            return
        
        old_cwd = os.getcwd()
        os.chdir(project_dir)
        
        console.print(f"[INFO] Showing details for task {task_id}...")
        show_command(task_id=task_id)
        
    except Exception as e:
        console.print(f"[ERROR] Error showing task: {str(e)}", style="bold red")
    finally:
        os.chdir(old_cwd)


def _handle_stack_discussion_command(user_input: str, project_dir: str) -> None:
    """Handle technology stack discussion command."""
    try:
        from taskinator.cli.commands.stack_command import stack_command
        
        console.print("[INFO] Switching to technology stack discussion...")
        
        # Determine the specific stack action based on user input
        if "suggest" in user_input.lower():
            stack_command("suggest", project_dir, interactive=True)
        elif "show" in user_input.lower() or "status" in user_input.lower():
            stack_command("show", project_dir, interactive=False)
        elif "compile" in user_input.lower() or "lock" in user_input.lower():
            stack_command("compile", project_dir, interactive=True)
        else:
            # Default to discuss mode
            stack_command("discuss", project_dir, interactive=True)
        
    except Exception as e:
        console.print(f"[ERROR] Error handling stack discussion: {str(e)}", style="bold red")
