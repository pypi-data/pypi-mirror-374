"""
Task expansion functionality for Taskinator.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from taskinator.core.file_storage import read_tasks, write_tasks
from taskinator.core.task_manager import find_task_by_id, task_exists
from taskinator.models.task import Subtask, Task, TaskCollection
from taskinator.services.ai.ai_client import generate_tasks_from_prd
from taskinator.utils.config import check_ai_available, get_config
from taskinator.utils.task_utils import _format_subtasks_list

console = Console()
config = get_config()

def _research_exists(task_id: str) -> bool:
    research_dir = os.path.join(os.path.dirname(tasks_path), "research")
    research_file = os.path.join(research_dir, f"task_{task_id}.txt")
    return os.path.exists(research_file)

def expand_task(
    tasks_path: str,
    task_id: str,
    num_subtasks: int = 3,
    research: bool = True,
    context: Optional[str] = None,
    options: Optional[Dict] = None,
    force: bool = False,  # Add direct force parameter
) -> None:
    """
    Break down a task into detailed subtasks.

    Args:
        tasks_path (str): Path to the tasks.json file
        task_id (str): Task ID to expand
        num_subtasks (int, optional): Number of subtasks to generate. Defaults to 3.
        research (bool, optional): Whether to use AI research to expand the task. Defaults to True.
        context (Optional[str], optional): Additional context for expansion. Defaults to None.
        options (Optional[Dict], optional): Additional options. Defaults to None.
        force (bool, optional): Force expansion of task with existing subtasks. Defaults to False.
    """
    # First check if AI is available - this is required for task expansion
    if not check_ai_available():
        # No need to print error message here, check_ai_available now prints detailed diagnostics
        return
        
    try:
        # Read tasks from file
        tasks = read_tasks(tasks_path)

        # Find the task
        task = find_task_by_id(tasks, task_id)

        if not task:
            console.print(f"[ERROR] Task {task_id} not found", style="bold red")
            return

        # Check if the task already has subtasks
        if task.subtasks:
            console.print(
                f"[WARNING] Task {task_id} already has subtasks", style="yellow"
            )
            
            # Check for force flag either directly or in options
            force_flag = force or (options and options.get("force", False))
            print(f"[DEBUG] task_expansion.py: force={force}, options={options}, force_flag={force_flag}")
            if force_flag:
                console.print("[INFO] Force flag provided, replacing subtasks automatically")
            else:
                console.print("[INFO] No force flag")
                
            if not force_flag:
                try:
                    # Try to get user input with a timeout to avoid blocking
                    import sys
                    from select import select
                    
                    console.print("Do you want to replace them? (y/n): ", end="")
                    sys.stdout.flush()
                    
                    response = sys.stdin.readline().strip()
                    if response.lower() not in ["y", "yes"]:
                        console.print("[INFO] Expansion cancelled")
                        return
                    
                except Exception as e:
                    # If there's any error with the input handling, assume we're in a non-interactive environment
                    console.print(f"\n[INFO] Non-interactive environment detected ({str(e)}), cancelling expansion")
                    return
            else:
                console.print("[INFO] Force flag provided, replacing subtasks automatically")

        # Generate subtasks
        console.print(
            f"[INFO] Expanding task {task_id} into {num_subtasks} subtasks..."
        )

        # Generate subtasks using AI
        subtasks = _generate_subtasks(task, num_subtasks, research, context)
        
        # Check if we got any subtasks
        if not subtasks:
            # Fall back to template-based subtasks
            console.print("[INFO] No AI-generated subtasks, using template-based subtasks", style="yellow")
            subtasks = _generate_template_subtasks(task, num_subtasks, research, context)

        # Add subtasks to the task
        task.subtasks = subtasks

        # Write tasks to file
        write_tasks(tasks_path, tasks)

        # Generate task files
        console.print("[INFO] Regenerating task files...")
        from taskinator.core.task_generation import generate_task_files

        generate_task_files(tasks_path)

        # Display success message
        success_text = f"Successfully expanded task {task_id} into {len(subtasks)} subtasks:"
        
        if subtasks:
            next_steps = f"""Next steps:
1. Review the subtasks with: taskinator show {task_id}
2. Start working on the first subtask with: taskinator set-status --id={subtasks[0].id} --status=in-progress"""
        else:
            next_steps = "Task expansion completed with no subtasks generated."
            
        console.print(
            Panel(
                f"""
{success_text}
{_format_subtasks_list(subtasks)}

{next_steps}
""",
                title="",
                style="green",
            )
        )
    except Exception as e:
        console.print(f"[ERROR] Error expanding task: {str(e)}", style="bold red")
        raise


def _generate_subtasks(
    task: Task, 
    num_subtasks: int, 
    use_research: bool, 
    additional_context: Optional[str] = None
) -> List[Subtask]:
    """
    Generate subtasks for a task using AI.

    Args:
        task (Task): Task to generate subtasks for
        num_subtasks (int): Number of subtasks to generate
        use_research (bool): Whether to include research in subtasks
        additional_context (Optional[str]): Additional context for expansion

    Returns:
        List[Subtask]: Generated subtasks
    """
    # Check if AI is available (LiteLLM handles credential validation)
    if not check_ai_available():
        # Don't fall back to templates - we're an AI platform
        return []

    # Create a "Virtual PRD" from the task details
    virtual_prd = _create_virtual_prd(task, use_research, num_subtasks, additional_context)
    
    # Call the AI to generate subtasks
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # If no event loop is available, create a new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    console.print(f"[INFO] Generating AI-powered subtasks for task {task.id}...")
    ai_tasks = loop.run_until_complete(generate_tasks_from_prd(virtual_prd, num_subtasks))

    # Convert AI-generated tasks to Subtask objects
    subtasks = []
    for i, ai_task in enumerate(ai_tasks):
        # Create proper subtask ID
        subtask_id = f"{task.id}.{i+1}"
        
        # Create dependencies - each subtask depends on the previous one
        dependencies = []
        if i > 0:
            dependencies.append(f"{task.id}.{i}")
        
        # Create Subtask object
        subtask_data = {
            "id": subtask_id,
            "title": ai_task.get("title", f"Subtask {i+1}"),
            "description": ai_task.get("description", ""),
            "status": "pending",
            "priority": task.priority,
            "dependencies": dependencies,
            "details": ai_task.get("details", ""),
            "test_strategy": ai_task.get("test_strategy", ""),
        }
        
        subtask = Subtask(**subtask_data)
        subtasks.append(subtask)
    
    console.print(
        f"[SUCCESS] Generated {len(subtasks)} AI-powered subtasks for task {task.id}.",
        style="bold green"
    )
    return subtasks

def _create_virtual_prd(task: Task, use_research: bool, num_subtasks: int, additional_context: Optional[str] = None) -> str:
    """
    Create a virtual PRD from a task for AI-powered subtask generation.
    
    Args:
        task (Task): The task to create a virtual PRD for
        use_research (bool): Whether to include research context
        num_subtasks (int): Number of subtasks to generate
        additional_context (Optional[str]): Additional context for expansion
        
    Returns:
        str: Virtual PRD content
    """
    # Start with the task title and description
    virtual_prd = f"""# {task.title} - Implementation Plan

## Overview
{task.description}

## Detailed Requirements
{task.details or "No detailed requirements provided."}

## Test Strategy
{task.test_strategy or "No test strategy provided."}
"""

    # Add research context if requested
    if use_research:
        virtual_prd += f"""
## Research Context
This task requires research-backed implementation with industry best practices and standards.
Focus on:
- Researching best practices for implementation
- Following industry standards
- Referencing established patterns
- Ensuring robust error handling and validation
- Comprehensive testing based on research
"""

    # Add any additional context provided by the user
    if additional_context:
        virtual_prd += f"""
## Additional Context
{additional_context}
"""

    # Add instructions for subtask generation with emphasis on detailed content
    virtual_prd += f"""
## Implementation Approach
This task needs to be broken down into {num_subtasks} subtasks that:
1. Follow a logical sequence of implementation steps
2. Have clear dependencies (each subtask depends on the previous one)
3. Are specific and actionable
4. Include detailed implementation guidance
5. Have clear test criteria

## Required Output Format
For each subtask, provide:
1. A clear, concise title
2. A brief description (1-2 sentences)
3. Implementation notes including technical approach and considerations. Scale level of detail to match the complexity of the task and include specific implementation guidance. Do not overcomplicate.
4. How to verify this task is complete and working correctly. Scale level of detail to match the complexity of the task. Do not overcomplicate.
5. Dependencies on previous subtasks

Each subtask should be self-contained with enough detail that a developer could implement it without referring back to the parent task.
"""
    return virtual_prd

def _generate_template_subtasks(
    task: Task, 
    num_subtasks: int, 
    use_research: bool, 
    additional_context: Optional[str] = None
) -> List[Subtask]:
    """
    Generate template-based subtasks as a fallback when AI generation fails.
    
    Args:
        task (Task): Task to generate subtasks for
        num_subtasks (int): Number of subtasks to generate
        use_research (bool): Whether to include research in subtasks
        additional_context (Optional[str]): Additional context for expansion
        
    Returns:
        List[Subtask]: Generated template subtasks
    """
    subtasks = []
    
    # Parse task details to identify logical components
    details = task.details or task.description or f"Implement {task.title}"
    
    # If the task has a source (from PDD or SOP), use that information
    has_source = hasattr(task, "source") and task.source
    if has_source:
        source_type = task.source.get("type")
        if source_type == "pdd":
            # For PDD-derived tasks, create research-backed subtasks based on process steps
            steps = [
                "Research best practices for the process implementation",
                "Design implementation approach with industry standards",
                "Implement core functionality with reference implementations",
                "Add comprehensive validation based on research",
                "Write tests based on industry testing patterns",
            ]
            # Limit to requested number of subtasks
            steps = steps[:num_subtasks]
        elif source_type == "sop":
            # For SOP-derived tasks, create research-backed subtasks based on SOP steps
            steps = [
                "Research SOP implementation patterns",
                "Implement each step with reference to best practices",
                "Add validation between steps based on industry standards",
                "Implement error recovery mechanisms from research",
                "Create documentation with references to standards",
            ]
            # Limit to requested number of subtasks
            steps = steps[:num_subtasks]
        else:
            # Default research-backed steps if source type is unknown
            steps = [
                f"Research and implement component {i+1} for task {task.id}"
                for i in range(num_subtasks)
            ]
    else:
        # For regular tasks, break down based on research-backed implementation phases
        steps = [
            "Research requirements and design patterns",
            "Implement core functionality with reference implementations",
            "Add validation based on industry standards",
            "Write comprehensive tests based on research",
            "Document the implementation with references",
            "Refactor and optimize based on performance research",
            "Integrate with other components using best practices",
        ]
        # Limit to requested number of subtasks
        steps = steps[:num_subtasks]
    
    # Create subtasks with proper IDs, dependencies, and research-backed details
    for i in range(num_subtasks):
        subtask_id = f"{task.id}.{i+1}"
        
        # Create dependencies - each subtask depends on the previous one
        dependencies = []
        if i > 0:
            dependencies.append(f"{task.id}.{i}")
        else:
            # First subtask depends on the parent task
            dependencies.append(str(task.id))
        
        # Create detailed implementation steps with research references
        implementation_details = f"""
Implementation steps for {steps[i]}:
1. Review the requirements in the parent task
2. Research industry best practices for this component
3. Implement the functionality following researched patterns
4. Test against established benchmarks
5. Document implementation with references to research

This subtask is part of the parent task: {task.title}
"""
        
        # Create research-backed test strategy
        test_strategy = f"""
Test strategy for {steps[i]}:
- Write unit tests based on industry testing patterns
- Test edge cases identified in research
- Benchmark against industry standards
- Ensure integration follows established patterns
"""
        
        # Create subtask with basic fields
        subtask_data = {
            "id": subtask_id,
            "title": steps[i],
            "description": f"Implement {steps[i]} for {task.title}",
            "status": "pending",
            "priority": task.priority,
            "dependencies": dependencies,
            "details": implementation_details,
            "test_strategy": test_strategy,
        }
        
        # Create the subtask
        subtask = Subtask(**subtask_data)
        subtasks.append(subtask)
    
    return subtasks


def expand_all_tasks(
    tasks_path: str,
    num_subtasks: int = None,
    use_research: bool = False,
    additional_context: str = "",
    force_flag: bool = False,
    options: Optional[Dict] = None,
    output_format: str = "text",
) -> None:
    """
    Expand all pending tasks with subtasks.

    Args:
        tasks_path (str): Path to the tasks.json file
        num_subtasks (int, optional): Number of subtasks per task. Defaults to None.
        use_research (bool, optional): Whether to use research (Perplexity). Defaults to False.
        additional_context (str, optional): Additional context for expansion. Defaults to "".
        force_flag (bool, optional): Whether to force expansion of tasks with existing subtasks. Defaults to False.
        options (Optional[Dict], optional): Additional options. Defaults to None.
        output_format (str, optional): Output format (text or json). Defaults to "text".
    """
    try:
        # Read tasks
        console.print("[INFO] Reading tasks from {}...".format(tasks_path))
        tasks = read_tasks(tasks_path)

        # Find pending tasks
        pending_tasks = [
            t
            for t in tasks.tasks
            if t.status == "pending" and (force_flag or not t.subtasks)
        ]

        if not pending_tasks:
            console.print("[INFO] No pending tasks to expand", style="yellow")
            return

        # Use default number of subtasks if not specified
        if num_subtasks is None:
            num_subtasks = config.get("DEFAULT_SUBTASKS", 3)

        # Check if complexity report exists
        complexity_report = _read_complexity_report()

        # Sort tasks by complexity if report exists
        if complexity_report:
            # Create a mapping of task ID to complexity score
            complexity_scores = {}
            for task_analysis in complexity_report.get("tasks", []):
                task_id = str(task_analysis.get("id"))
                score = task_analysis.get("complexity", {}).get("score", 0)
                complexity_scores[task_id] = score

            # Sort tasks by complexity score (highest first)
            pending_tasks.sort(
                key=lambda t: complexity_scores.get(str(t.id), 0), reverse=True
            )

        # Expand each task
        expanded_tasks = []
        for task in pending_tasks:
            # Skip tasks with existing subtasks unless forced
            if task.subtasks and not force_flag:
                continue

            # Get recommended number of subtasks from complexity report if available
            task_num_subtasks = num_subtasks
            if complexity_report:
                task_analysis = next(
                    (
                        t
                        for t in complexity_report.get("tasks", [])
                        if str(t.get("id")) == str(task.id)
                    ),
                    None,
                )

                if task_analysis:
                    task_complexity = task_analysis.get("complexity", {})
                    if "recommended_subtasks" in task_complexity:
                        task_num_subtasks = task_complexity.get("recommended_subtasks")

            # Generate subtasks
            console.print(
                f"[INFO] Generating {task_num_subtasks} subtasks for task {task.id}..."
            )

            # Generate subtasks using AI
            subtasks = _generate_subtasks(
                task, task_num_subtasks, use_research, additional_context
            )

            # Update task with subtasks
            task.subtasks = subtasks
            expanded_tasks.append(task)

        # Write tasks to file
        console.print(f"[INFO] Writing tasks to {tasks_path}")
        write_tasks(tasks_path, tasks)

        # Generate task files
        console.print("[INFO] Regenerating task files...")
        from taskinator.core.task_generation import generate_task_files

        generate_task_files(tasks_path)

        # Display success message
        expanded_task_list = "\n".join(
            [
                f"- {t.id}: {t.title} ({len(t.subtasks)} subtasks)"
                for t in expanded_tasks
            ]
        )
        console.print(
            Panel(
                f"""
Successfully expanded {len(expanded_tasks)} tasks.

Expanded tasks:
{expanded_task_list}
""",
                title="",
                style="green",
            )
        )
    except Exception as e:
        console.print(f"[ERROR] Error expanding tasks: {str(e)}", style="bold red")
        raise


def clear_subtasks(
    tasks_path: str,
    task_id: str,
    options: Optional[Dict] = None,
) -> None:
    """
    Remove subtasks from specified tasks.

    Args:
        tasks_path (str): Path to the tasks.json file
        task_id (str): Task ID to clear subtasks from
        options (Optional[Dict], optional): Additional options. Defaults to None.
    """
    try:
        # Read tasks
        console.print("[INFO] Reading tasks from {}...".format(tasks_path))
        tasks = read_tasks(tasks_path)

        # Find the task
        task = find_task_by_id(tasks, task_id)

        if not task:
            console.print(f"[ERROR] Task {task_id} not found", style="bold red")
            return

        # Check if task has subtasks
        if not task.subtasks:
            console.print(
                f"[INFO] Task {task_id} has no subtasks to clear", style="yellow"
            )
            return

        # Clear subtasks
        subtask_count = len(task.subtasks)
        task.subtasks = []

        # Write tasks to file
        console.print(f"[INFO] Writing tasks to {tasks_path}")
        write_tasks(tasks_path, tasks)

        # Generate task files
        console.print("[INFO] Regenerating task files...")
        from taskinator.core.task_generation import generate_task_files

        generate_task_files(tasks_path)

        # Display success message
        console.print(
            Panel(
                f"""
Successfully cleared {subtask_count} subtasks from task {task_id}.
""",
                title="",
                style="green",
            )
        )
    except Exception as e:
        console.print(
            f"[ERROR] Error clearing subtasks: {str(e)}", style="bold red"
        )
        raise


def analyze_task_complexity(
    tasks_path: str,
    use_research: bool = False,
    threshold: int = 5,
    options: Optional[Dict] = None,
) -> None:
    """
    Analyze tasks and generate expansion recommendations.

    Args:
        tasks_path (str): Path to the tasks.json file
        use_research (bool, optional): Whether to use research for better analysis. Defaults to False.
        threshold (int, optional): Complexity threshold for expansion. Defaults to 5.
        options (Optional[Dict], optional): Additional options. Defaults to None.
    """
    try:
        # Read tasks
        console.print("[INFO] Reading tasks from {}...".format(tasks_path))
        tasks = read_tasks(tasks_path)

        # Find pending tasks
        pending_tasks = [t for t in tasks.tasks if t.status == "pending"]

        if not pending_tasks:
            console.print("[INFO] No pending tasks to analyze", style="yellow")
            return

        # Analyze each task
        console.print(f"[INFO] Analyzing {len(pending_tasks)} pending tasks...")

        # TODO: Replace with actual AI integration
        # For now, we'll generate placeholder complexity analysis
        complexity_report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "use_research": use_research,
                "threshold": threshold,
            },
            "tasks": [],
        }

        for task in pending_tasks:
            # Generate random complexity score (1-10)
            import random

            score = random.randint(1, 10)

            # Calculate recommended subtasks based on score
            recommended_subtasks = max(2, min(8, score))

            # Generate expansion prompt
            expansion_prompt = f"Break down task {task.id} ({task.title}) into {recommended_subtasks} subtasks."

            # Add to report
            complexity_report["tasks"].append(
                {
                    "id": task.id,
                    "title": task.title,
                    "complexity": {
                        "score": score,
                        "analysis": f"This is a placeholder complexity analysis for task {task.id}.",
                        "recommended_subtasks": recommended_subtasks,
                        "expansion_prompt": expansion_prompt,
                    },
                }
            )

        # Sort tasks by complexity score (highest first)
        complexity_report["tasks"].sort(
            key=lambda t: t["complexity"]["score"], reverse=True
        )

        # Write report to file
        report_path = "tasks/task-complexity-report.json"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(complexity_report, f, indent=2)

        console.print(f"[INFO] Complexity report written to {report_path}")

        # Display report summary
        display_complexity_report(report_path)
    except Exception as e:
        console.print(
            f"[ERROR] Error analyzing task complexity: {str(e)}", style="bold red"
        )
        raise


def _read_complexity_report(
    report_path: str = "tasks/task-complexity-report.json",
) -> Optional[Dict]:
    """
    Read complexity report from file.

    Args:
        report_path (str, optional): Path to the complexity report file. Defaults to "tasks/task-complexity-report.json".

    Returns:
        Optional[Dict]: Complexity report or None if file doesn't exist
    """
    if not os.path.exists(report_path):
        return None

    try:
        with open(report_path, "r") as f:
            return json.load(f)
    except Exception as e:
        console.print(
            f"[ERROR] Error reading complexity report: {str(e)}", style="yellow"
        )
        return None


def display_complexity_report(
    report_path: str = "tasks/task-complexity-report.json",
) -> None:
    """
    Display the complexity analysis report.

    Args:
        report_path (str, optional): Path to the complexity report file. Defaults to "tasks/task-complexity-report.json".
    """
    try:
        # Read report
        report = _read_complexity_report(report_path)

        if not report:
            console.print(
                f"[ERROR] Complexity report not found: {report_path}", style="bold red"
            )

            # Ask if user wants to generate a report
            response = input("Do you want to generate a complexity report now? (y/n): ")
            if response.lower() in ["y", "yes"]:
                # Instead of directly calling analyze_task_complexity, suggest the command
                console.print(
                    "[INFO] Run 'taskinator analyze-complexity' to generate a report",
                    style="cyan",
                )

            return

        # Display report header
        console.print(
            Panel(
                f"""
Complexity Analysis Report
Generated: {report["metadata"]["generated_at"]}
Research-backed: {report["metadata"]["use_research"]}
Expansion threshold: {report["metadata"]["threshold"]}
""",
                title="",
                style="cyan",
            )
        )

        # Create complexity distribution
        low_complexity = sum(
            1 for t in report["tasks"] if t["complexity"]["score"] <= 3
        )
        medium_complexity = sum(
            1 for t in report["tasks"] if 4 <= t["complexity"]["score"] <= 7
        )
        high_complexity = sum(
            1 for t in report["tasks"] if t["complexity"]["score"] >= 8
        )

        console.print(
            Panel(
                f"""
Complexity Distribution:
- Low complexity (1-3): {low_complexity} tasks
- Medium complexity (4-7): {medium_complexity} tasks
- High complexity (8-10): {high_complexity} tasks
""",
                title="",
                style="cyan",
            )
        )

        # Display tasks by complexity
        console.print(
            Panel("Tasks by Complexity (Highest to Lowest)", style="bold cyan")
        )

        table = Table(show_header=True, header_style="bold")
        table.add_column("ID", style="cyan")
        table.add_column("Title")
        table.add_column("Complexity", justify="center")
        table.add_column("Recommended Subtasks", justify="center")
        table.add_column("Expansion Command")

        for task in report["tasks"]:
            # Format complexity with color
            score = task["complexity"]["score"]
            if score <= 3:
                complexity = f"[green]{score}/10[/green]"
            elif score <= 7:
                complexity = f"[yellow]{score}/10[/yellow]"
            else:
                complexity = f"[red]{score}/10[/red]"

            # Format expansion command
            expansion_command = f"taskinator expand-task --id={task['id']} --num={task['complexity']['recommended_subtasks']}"

            table.add_row(
                str(task["id"]),
                task["title"],
                complexity,
                str(task["complexity"]["recommended_subtasks"]),
                expansion_command,
            )

        console.print(table)

        # Display suggested actions
        console.print(
            Panel(
                f"""
Suggested Actions:
1. Expand high complexity tasks first: taskinator expand-task --id=<id>
2. Expand all tasks above threshold: taskinator expand-task --all
3. Update the analysis: taskinator analyze-complexity
""",
                title="",
                style="cyan",
            )
        )
    except Exception as e:
        console.print(
            f"[ERROR] Error displaying complexity report: {str(e)}", style="bold red"
        )
        raise
