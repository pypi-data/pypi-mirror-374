"""
Analyze complexity command implementation for Taskinator.
"""

import asyncio
import json
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from taskinator.core.file_storage import read_tasks
from taskinator.models.task import Task
from taskinator.utils.config import check_ai_available, get_config_value

console = Console()


async def analyze_task_complexity_batch(
    tasks: List[Task], research: bool = False
) -> List[Dict[str, Any]]:
    """
    Analyze multiple tasks' complexity using AI in a single batch request.

    Args:
        tasks: List of task objects to analyze
        research: Whether to use Perplexity for research-backed analysis

    Returns:
        List of dictionaries containing complexity analysis for each task
    """
    try:
        # Import LiteLLM here to avoid import errors if it's not installed
        import litellm
        from litellm import completion

        # Get model configuration
        model = os.environ.get("MODEL", "anthropic/claude-3-7-sonnet-20250219")
        max_tokens = int(os.environ.get("MAX_TOKENS", 4000))
        temperature = float(os.environ.get("TEMPERATURE", 0.7))

        # Create system and user prompts for batch complexity analysis
        system_prompt = """You are a software development complexity analyzer. Your job is to:
1. Analyze each of the given tasks
2. Assess their complexity on a scale of 1-10
3. Provide a brief analysis of why you assigned that complexity score
4. Recommend how many subtasks each should be broken into (between 2-8)
5. Return your analysis in JSON format

Consider factors like:
- Technical complexity
- Scope and size
- Dependencies and integrations
- Potential challenges and risks
- Required expertise

Return your analysis in this JSON array format:
[
  {
    "taskId": 1,
    "taskTitle": "Task title here",
    "complexityScore": 7, // Integer from 1-10
    "analysis": "Brief explanation of complexity factors...",
    "recommendedSubtasks": 5, // Integer from 2-8
    "expansionPrompt": "Suggested prompt for breaking down this task"
  },
  // ... additional tasks
]"""

        # Create the user prompt with all task details
        task_descriptions = []
        for task in tasks:
            task_id = str(task.id).zfill(3)
            task_title = task.title

            task_desc = f"""Task ID: {task_id}
Title: {task_title}
Description: {task.description}
Details: {task.details}
"""
            task_descriptions.append(task_desc)

        # Join all task descriptions with separators
        all_tasks_text = "\n---\n".join(task_descriptions)

        user_prompt = f"""Analyze the complexity of these software development tasks:

{all_tasks_text}

Please provide a thorough complexity analysis for each task in the JSON array format specified."""

        # If research is enabled, use Perplexity for enhanced analysis
        research_findings = ""
        if research:
            perplexity_api_key = os.environ.get("PERPLEXITY_API_KEY")
            if perplexity_api_key:
                try:
                    console.print(
                        f"[INFO] Using Perplexity for research-backed analysis...",
                        style="blue",
                    )

                    # Use Perplexity via LiteLLM
                    perplexity_model = os.environ.get("PERPLEXITY_MODEL", "sonar-pro")

                    research_prompt = f"""You are conducting a detailed analysis of software development tasks to determine their complexity and how they should be broken down into subtasks.

Please research these tasks thoroughly, considering best practices, industry standards, and potential implementation challenges:

{all_tasks_text}

Based on your research, provide:
1. Technical approaches and considerations for each task
2. Potential challenges and solutions
3. Similar implementations and best practices
4. Required skills and expertise
5. Estimated complexity and scope

Return your findings in a detailed report that covers each task individually.
"""

                    # Call Perplexity via LiteLLM
                    console.print(
                        "[INFO] Calling Perplexity API for research...", style="blue"
                    )
                    research_response = completion(
                        model=f"perplexity/{perplexity_model}",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a software development research assistant.",
                            },
                            {"role": "user", "content": research_prompt},
                        ],
                        max_tokens=max_tokens,
                        temperature=temperature,
                        api_key=perplexity_api_key,
                    )

                    # Extract research findings
                    research_findings = research_response.choices[0].message.content
                    console.print(
                        "[SUCCESS] Successfully generated research with Perplexity AI",
                        style="green",
                    )

                    # Store research findings in tasks/research directory
                    try:
                        # Get the tasks directory path
                        tasks_file_path = get_config_value("tasks_file_path")
                        console.print(
                            f"[DEBUG] tasks_file_path: {tasks_file_path}", style="dim"
                        )

                        tasks_dir = os.path.dirname(tasks_file_path)
                        console.print(f"[DEBUG] tasks_dir: {tasks_dir}", style="dim")

                        # Create research directory if it doesn't exist
                        research_dir = os.path.join(tasks_dir, "research")
                        console.print(
                            f"[DEBUG] research_dir: {research_dir}", style="dim"
                        )
                        os.makedirs(research_dir, exist_ok=True)

                        # Extract task-specific research sections
                        task_research_sections = {}

                        # Parse the research findings to extract task-specific sections
                        lines = research_findings.split("\n")
                        current_task_id = None
                        current_section = []

                        # First try to parse with the expected format
                        for line in lines:
                            # Check if this line starts a new task section
                            if "Task ID:" in line and "-" in line:
                                # If we were collecting a previous task, save it
                                if current_task_id is not None and current_section:
                                    task_research_sections[current_task_id] = "\n".join(
                                        current_section
                                    )

                                # Extract the task ID from the line
                                try:
                                    # Format: "Task ID: 001 - Design Data Model and Storage"
                                    task_id_part = (
                                        line.split("Task ID:")[1]
                                        .strip()
                                        .split("-")[0]
                                        .strip()
                                    )
                                    # Remove leading zeros
                                    current_task_id = str(int(task_id_part))
                                    current_section = [line]
                                except (IndexError, ValueError):
                                    current_task_id = None
                            elif current_task_id is not None:
                                current_section.append(line)

                        # Save the last section if any
                        if current_task_id is not None and current_section:
                            task_research_sections[current_task_id] = "\n".join(
                                current_section
                            )

                        # If no task sections were found, try alternative parsing approaches
                        if not task_research_sections:
                            console.print(
                                "[DEBUG] No task sections found with standard format, trying alternative parsing",
                                style="dim",
                            )

                            # Try to find sections based on task titles or IDs
                            for task in tasks:
                                try:
                                    task_id = str(task.id)
                                    task_title = task.title
                                except AttributeError:
                                    try:
                                        task_id = str(task.get("id", ""))
                                        task_title = task.get("title", "")
                                    except Exception:
                                        continue

                                # Look for sections that mention this task's title
                                section_start = -1
                                section_end = -1

                                # Check for task title mentions
                                for i, line in enumerate(lines):
                                    if (
                                        task_title in line
                                        or f"Task {task_id}" in line
                                        or f"Task ID: {task_id}" in line
                                    ):
                                        section_start = i
                                        # Find the end of this section (next task mention or end of text)
                                        for j in range(i + 1, len(lines)):
                                            # Check if we've hit another task section
                                            for other_task in tasks:
                                                try:
                                                    other_id = str(other_task.id)
                                                    other_title = other_task.title
                                                    if (
                                                        other_id != task_id
                                                        and (
                                                            other_title in lines[j]
                                                            or f"Task {other_id}"
                                                            in lines[j]
                                                            or f"Task ID: {other_id}"
                                                            in lines[j]
                                                        )
                                                    ):
                                                        section_end = j
                                                        break
                                                except (AttributeError, Exception):
                                                    continue
                                            if section_end != -1:
                                                break

                                        # If we didn't find an end, use the end of the text
                                        if section_end == -1:
                                            section_end = len(lines)

                                        # Extract and save this section
                                        if section_start != -1 and section_end != -1:
                                            section_content = "\n".join(
                                                lines[section_start:section_end]
                                            )
                                            task_research_sections[task_id] = section_content
                                        break

                            # If we still don't have any sections, try dividing the research evenly
                            if not task_research_sections:
                                console.print(
                                    "[DEBUG] No task sections found with alternative parsing, dividing research evenly",
                                    style="dim",
                                )

                                # Divide the research text roughly evenly among tasks
                                chunk_size = max(1, len(lines) // len(tasks))
                                for i, task in enumerate(tasks):
                                    try:
                                        task_id = str(task.id)
                                    except AttributeError:
                                        try:
                                            task_id = str(task.get("id", ""))
                                        except Exception:
                                            task_id = str(i + 1)

                                    start_idx = i * chunk_size
                                    end_idx = min((i + 1) * chunk_size, len(lines))

                                    if start_idx < len(lines):
                                        section_content = "\n".join(lines[start_idx:end_idx])
                                        task_research_sections[task_id] = section_content

                        # If we STILL don't have research sections, use the entire research text for each task
                        if not task_research_sections:
                            console.print(
                                "[WARNING] Could not parse task-specific sections from research. Using full research for each task.",
                                style="yellow",
                            )

                            # Use the entire research text for each task
                            for task in tasks:
                                try:
                                    task_id = str(task.id)
                                except AttributeError:
                                    try:
                                        task_id = str(task.get("id", ""))
                                    except Exception:
                                        continue

                                task_research_sections[task_id] = research_findings

                        # Save research findings for each task
                        console.print(
                            f"[DEBUG] Number of tasks: {len(tasks)}", style="dim"
                        )
                        for i, task in enumerate(tasks):
                            # Get task ID and title safely
                            try:
                                # First try to access as object attributes
                                task_id = str(task.id)
                                task_title = task.title
                                console.print(
                                    f"[DEBUG] Got task info via attributes: ID={task_id}, Title={task_title}",
                                    style="dim",
                                )
                            except AttributeError:
                                # If that fails, try dictionary access
                                try:
                                    task_id = str(task.get("id", ""))
                                    task_title = task.get("title", "")
                                    console.print(
                                        f"[DEBUG] Got task info via dictionary: ID={task_id}, Title={task_title}",
                                        style="dim",
                                    )
                                except Exception as e:
                                    # Last resort, use index
                                    task_id = str(i + 1)
                                    task_title = f"Task {i + 1}"
                                    console.print(
                                        f"[DEBUG] Using fallback task info: ID={task_id}, Title={task_title}",
                                        style="dim",
                                    )

                            console.print(
                                f"[DEBUG] Processing task {i+1}/{len(tasks)}: ID={task_id}, Title={task_title}",
                                style="dim",
                            )

                            # Get task-specific research or use a default message
                            task_research = task_research_sections.get(task_id)
                            
                            if not task_research:
                                console.print(
                                    f"[WARNING] No research content found for task {task_id}. This indicates research parsing failed.",
                                    style="yellow",
                                )
                                task_research = f"""No specific research found for this task.

This may indicate that:
1. The research content couldn't be parsed properly
2. The task wasn't mentioned in the research response
3. There was an error in the research API call

Full research content length: {len(research_findings)} characters
Research parsing attempted but failed to extract task-specific sections."""

                            # Add header information
                            header = f"# Research for Task {task_id}: {task_title}\n\n"
                            header += f"Generated: {datetime.now().isoformat()}\n\n"

                            # Format the final content
                            final_content = header + task_research

                            # Save to file
                            task_id_padded = str(task_id).zfill(3)
                            task_research_file = os.path.join(
                                research_dir, f"task_{task_id_padded}.txt"
                            )
                            console.print(
                                f"[DEBUG] Writing to file: {task_research_file}",
                                style="dim",
                            )

                            try:
                                with open(task_research_file, "w") as f:
                                    f.write(final_content)

                                console.print(
                                    f"[DEBUG] Successfully wrote research for task {task_id}",
                                    style="dim",
                                )
                            except Exception as e:
                                console.print(
                                    f"[ERROR] Error writing research file for task {task_id}: {str(e)}",
                                    style="bold red",
                                )

                        console.print(
                            f"[INFO] Saved research findings to {research_dir}",
                            style="blue",
                        )

                    except Exception as e:
                        console.print(
                            f"[ERROR] Error saving research findings: {str(e)}",
                            style="bold red",
                        )
                        import traceback

                        console.print(
                            f"[DEBUG] Traceback: {traceback.format_exc()}", style="dim"
                        )

                    # Enhance the user prompt with research findings
                    user_prompt += f"\n\nResearch findings:\n{research_findings}"

                except Exception as e:
                    console.print(
                        f"[WARNING] Error using Perplexity for research: {str(e)}",
                        style="yellow",
                    )
                    console.print(
                        "[INFO] Falling back to standard analysis without research",
                        style="yellow",
                    )
                    # Initialize research_findings as empty if there was an error
                    research_findings = ""
            else:
                console.print(
                    "[WARNING] PERPLEXITY_API_KEY not set. Research-backed analysis not available.",
                    style="yellow",
                )

        # Capture prompt and response if TASKINATOR_CAPTURE is set
        should_capture = os.environ.get("TASKINATOR_CAPTURE", "").lower() == "true"
        capture_dir = "ANALYZE_COMPLEXITY"

        if should_capture:
            os.makedirs(capture_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Save the prompt
            prompt_file = os.path.join(capture_dir, f"prompt_{timestamp}.json")
            with open(prompt_file, "w") as f:
                json.dump(
                    {
                        "system": system_prompt,
                        "user": user_prompt,
                        "timestamp": datetime.now().isoformat(),
                        "model": model,
                        "research": research,
                    },
                    f,
                    indent=2,
                )

            console.print(f"[INFO] Saved prompt to {prompt_file}", style="blue")

        # Call Claude via LiteLLM for complexity analysis with streaming
        console.print(
            f"[INFO] Analyzing complexity of {len(tasks)} tasks in batch mode...",
            style="blue",
        )

        # Configure LiteLLM with the 128k output token beta header
        litellm.headers = {"anthropic-beta": "output-128k-2025-02-19"}

        # Add retry logic for handling API overload errors
        max_retries = 3
        retry_delay = 2  # seconds
        response_text = ""

        for attempt in range(max_retries):
            try:
                # Use streaming for better UX
                response = completion(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=True,
                )

                # Process the streaming response
                console.print(
                    "[INFO] Receiving streaming response from AI...", style="blue"
                )
                response_text = ""

                for chunk in response:
                    if chunk["choices"][0]["delta"].get("content"):
                        content = chunk["choices"][0]["delta"]["content"]
                        response_text += content
                        # Print a progress indicator (just a dot) to show activity
                        print(".", end="", flush=True)

                print()  # New line after streaming completes
                console.print(
                    "[SUCCESS] Successfully received complete response from AI",
                    style="green",
                )
                break  # If successful, break out of the retry loop

            except Exception as e:
                if "overloaded" in str(e).lower() and attempt < max_retries - 1:
                    # If API is overloaded and we have retries left
                    retry_delay_with_jitter = retry_delay + (attempt * 2)
                    console.print(
                        f"[WARNING] API overloaded, retrying in {retry_delay_with_jitter} seconds (attempt {attempt+1}/{max_retries})...",
                        style="yellow",
                    )
                    await asyncio.sleep(retry_delay_with_jitter)
                else:
                    # If it's not an overload error or we're out of retries, re-raise
                    console.print(
                        f"[ERROR] Error calling AI: {str(e)}", style="bold red"
                    )
                    raise

        # Capture the response if enabled
        if should_capture and response_text:
            response_file = os.path.join(capture_dir, f"response_{timestamp}.json")
            with open(response_file, "w") as f:
                json.dump(
                    {
                        "raw_response": response_text,
                        "timestamp": datetime.now().isoformat(),
                        "model": model,
                    },
                    f,
                    indent=2,
                )

            console.print(f"[INFO] Saved response to {response_file}", style="blue")

        # Parse the JSON response
        # Try to find JSON in code blocks
        json_match = None
        if "```json" in response_text:
            json_parts = response_text.split("```json")
            if len(json_parts) > 1:
                json_content = json_parts[1].split("```")[0].strip()
                json_match = json_content
        elif "```" in response_text:
            json_parts = response_text.split("```")
            if len(json_parts) > 1:
                json_content = json_parts[1].strip()
                json_match = json_content

        # If no code blocks, try to find JSON array directly
        if not json_match:
            start_idx = response_text.find("[")
            end_idx = response_text.rfind("]")
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_match = response_text[start_idx : end_idx + 1]

        # Parse the JSON
        if json_match:
            console.print("[INFO] Parsing complexity analysis...", style="blue")
            console.print("[INFO] Extracted JSON array pattern", style="blue")

            # Clean the JSON string if needed
            cleaned_json = json_match.strip()
            console.print(
                f"Cleaned response (first 100 chars):\n{cleaned_json[:100]}",
                style="dim",
            )
            console.print(f"Last 100 chars:\n{cleaned_json[-100:]}", style="dim")

            console.print(
                "[INFO] Applied strict JSON array extraction", style="blue"
            )
            analysis_array = json.loads(cleaned_json)

            if not isinstance(analysis_array, list):
                raise ValueError("Parsed JSON is not an array")

            # Map the analysis results to tasks by ID
            # Normalize task IDs by stripping leading zeros and converting to string
            task_map = {str(task.id): task for task in tasks}
            result_list = []

            for analysis in analysis_array:
                # Get the task ID from the analysis and normalize it
                raw_task_id = str(analysis.get("taskId"))
                # Strip leading zeros and ensure it's a string
                task_id = str(int(raw_task_id)) if raw_task_id.isdigit() else raw_task_id
                
                if task_id in task_map:
                    # Add task ID and title if not present
                    if "taskId" not in analysis:
                        analysis["taskId"] = task_id
                    if "taskTitle" not in analysis:
                        analysis["taskTitle"] = task_map[task_id].title

                    # Convert to our internal format
                    result = {
                        "id": task_id,
                        "title": analysis.get("taskTitle", task_map[task_id].title),
                        "complexity_score": analysis.get("complexityScore", 5),
                        "analysis": analysis.get(
                            "analysis", "No analysis provided"
                        ),
                        "recommended_subtasks": analysis.get(
                            "recommendedSubtasks", 3
                        ),
                        "expansion_prompt": analysis.get(
                            "expansionPrompt",
                            f"Break down task {task_id} into subtasks",
                        ),
                    }
                    result_list.append(result)

            # If we're missing any tasks, add fallback entries
            for task in tasks:
                if str(task.id) not in [r["id"] for r in result_list]:
                    console.print(f"[WARNING] Missing analysis for task {task.id}, adding fallback", style="yellow")
                    result_list.append({
                        "id": str(task.id),
                        "title": task.title,
                        "complexity_score": 5,
                        "analysis": "Analysis not available - AI response may not have included this task",
                        "recommended_subtasks": 3,
                        "expansion_prompt": f"Break down task {task.id} ({task.title}) into subtasks",
                    })

            return result_list
        else:
            raise ValueError("Could not extract JSON from response")

        

    except Exception as e:
        console.print(
            f"[ERROR] Error analyzing task complexity with AI: {str(e)}",
            style="bold red",
        )

        # Return fallback analyses for all tasks
        return [
            {
                "id": str(task.id),
                "title": task.title,
                "complexity_score": 5,
                "analysis": "Error occurred during analysis. Please check your API keys and try again.",
                "recommended_subtasks": 3,
                "expansion_prompt": f"Break down task {task.id} ({task.title}) into 3 subtasks.",
            }
            for task in tasks
        ]


async def analyze_complexity_command(
    research: bool = False, threshold: int = 5
) -> None:
    """
    Analyze tasks and generate expansion recommendations.

    Args:
        research (bool, optional): Whether to use research for better analysis. Defaults to False.
        threshold (int, optional): Complexity threshold for expansion. Defaults to 5.
    """
    try:
        # Check if AI is available
        if not check_ai_available():
            # No need to print error message here, check_ai_available now prints detailed diagnostics
            return

        # Get tasks path from config
        tasks_path = get_config_value("tasks_file_path")

        # Read tasks
        console.print(f"[INFO] Reading tasks from {tasks_path}...")
        tasks = read_tasks(tasks_path)

        # Find pending tasks
        pending_tasks = [t for t in tasks.tasks if t.status == "pending"]

        if not pending_tasks:
            console.print("[INFO] No pending tasks to analyze", style="yellow")
            return

        # Analyze each task
        console.print(f"[INFO] Analyzing {len(pending_tasks)} pending tasks...")

        # Create the complexity report structure
        # Get project name from task collection
        tasks_json_path = tasks_path
        project_name = None
        try:
            with open(tasks_json_path, "r") as f:
                data = json.load(f)
                if "metadata" in data and "project_name" in data["metadata"]:
                    project_name = data["metadata"]["project_name"]
        except Exception:
            pass
            
        # Use the current directory name as a fallback when no project name is available
        if not project_name:
            project_name = os.path.basename(os.getcwd())
            
        complexity_report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "use_research": research,
                "threshold": threshold,
                "project_name": project_name,
            },
            "tasks": [],
        }

        # Use the batch analysis approach
        start_time = time.time()
        analyses = await analyze_task_complexity_batch(pending_tasks, research)
        end_time = time.time()

        console.print(
            f"[INFO] Analysis completed in {end_time - start_time:.2f} seconds"
        )

        # Add analyses to the report
        for analysis in analyses:
            complexity_report["tasks"].append(
                {
                    "id": analysis["id"],
                    "title": analysis["title"],
                    "complexity": {
                        "score": analysis["complexity_score"],
                        "analysis": analysis["analysis"],
                        "recommended_subtasks": analysis["recommended_subtasks"],
                        "expansion_prompt": analysis.get(
                            "expansion_prompt",
                            f"Break down task {analysis['id']} ({analysis['title']}) into {analysis['recommended_subtasks']} subtasks.",
                        ),
                    },
                }
            )

        # Sort tasks by complexity score (highest first)
        complexity_report["tasks"].sort(
            key=lambda t: t["complexity"]["score"], reverse=True
        )

        # Write report to file
        report_path = os.path.join(
            os.path.dirname(tasks_path), "task-complexity-report.json"
        )
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


def display_complexity_report(report_path: str) -> None:
    """
    Display the complexity analysis report.

    Args:
        report_path: Path to the complexity report file
    """
    try:
        # Read the report
        with open(report_path, "r") as f:
            report = json.load(f)

        # Extract metadata
        metadata = report.get("metadata", {})
        generated_at = metadata.get("generated_at", datetime.now().isoformat())
        use_research = metadata.get("use_research", False)
        threshold = metadata.get("threshold", 5)

        # Format the date for display
        try:
            dt = datetime.fromisoformat(generated_at)
            formatted_date = dt.strftime("%Y-%m-%d, %I:%M:%S %p")
        except:
            formatted_date = generated_at

        # Get tasks and sort by complexity score
        tasks = report.get("tasks", [])
        tasks.sort(key=lambda t: t.get("complexity", {}).get("score", 0), reverse=True)

        # Count tasks by complexity level
        high_complexity = sum(
            1 for t in tasks if t.get("complexity", {}).get("score", 0) >= 8
        )
        medium_complexity = sum(
            1 for t in tasks if 5 <= t.get("complexity", {}).get("score", 0) < 8
        )
        low_complexity = sum(
            1 for t in tasks if t.get("complexity", {}).get("score", 0) < 5
        )

        # Calculate percentages
        total_tasks = len(tasks)
        high_percent = int(
            (high_complexity / total_tasks * 100) if total_tasks > 0 else 0
        )
        medium_percent = int(
            (medium_complexity / total_tasks * 100) if total_tasks > 0 else 0
        )
        low_percent = int(
            (low_complexity / total_tasks * 100) if total_tasks > 0 else 0
        )

        # Get project name from the report metadata
        project_name = metadata.get("project_name")

        # Create the report header
        console.print()
        console.print(
            Panel(
                "[bold white]Task Complexity Analysis Report[/bold white]",
                expand=False,
                border_style="white",
                padding=(1, 2),
            )
        )

        # Display metadata
        metadata_table = Table(show_header=False, box=box.SIMPLE)
        metadata_table.add_column("Key", style="bold white")
        metadata_table.add_column("Value")

        metadata_table.add_row("Generated:", formatted_date)
        metadata_table.add_row("Tasks Analyzed:", str(total_tasks))
        metadata_table.add_row("Threshold Score:", str(threshold))
        metadata_table.add_row("Project:", project_name)
        metadata_table.add_row("Research-backed:", "Yes" if use_research else "No")

        console.print(metadata_table)

        # Display complexity distribution
        console.print()
        console.print(
            Panel(
                f"""
[bold white]Complexity Distribution[/bold white]

Low (1-4): {low_complexity} tasks ({low_percent}%)
Medium (5-7): {medium_complexity} tasks ({medium_percent}%)
High (8-10): {high_complexity} tasks ({high_percent}%)
            """.strip(),
                expand=False,
                border_style="white",
                padding=(1, 2),
            )
        )

        # Create a table for tasks
        table = Table(
            show_header=True,
            box=box.SIMPLE_HEAD,
            header_style="bold white",
            expand=True,
        )

        # Add columns
        table.add_column("ID", justify="left", no_wrap=True)
        table.add_column("Title", justify="left")
        table.add_column("Score", justify="center", no_wrap=True)
        table.add_column("Subtasks", justify="center", no_wrap=True)
        table.add_column("Expansion Command", justify="left", no_wrap=False)

        # Add rows for each task
        for task in tasks:
            task_id = task.get("id", "")
            title = task.get("title", "")

            # Truncate long titles
            if len(title) > 35:
                title = title[:32] + "..."

            complexity = task.get("complexity", {})
            score = complexity.get("score", 0)
            recommended_subtasks = complexity.get("recommended_subtasks", 3)

            # Create expansion command
            expansion_command = (
                f"taskinator expand-task --id={task_id} --num={recommended_subtasks}"
            )

            # Add expansion prompt if available
            expansion_prompt = complexity.get("expansion_prompt", "")
            if expansion_prompt and len(expansion_prompt) > 10:
                # Format the prompt for display
                formatted_prompt = f' --prompt="{expansion_prompt[:50]}..."'
                expansion_command += formatted_prompt

            # Color-code the complexity score
            if score >= 8:
                score_display = f"[bold red]🔴 {score}[/bold red]"
            elif score >= 5:
                score_display = f"[bold yellow]🟡 {score}[/bold yellow]"
            else:
                score_display = f"[bold green]🟢 {score}[/bold green]"

            # Add the row
            table.add_row(
                str(task_id),
                title,
                score_display,
                str(recommended_subtasks),
                expansion_command,
            )

        # Display the table
        console.print(table)

        # Display suggested actions
        console.print()
        console.print(
            Panel(
                """
[bold white]Suggested Actions:[/bold white]

1. Expand all complex tasks: taskinator expand-task --all
2. Expand a specific task: taskinator expand-task --id=<id>
3. Regenerate with research: taskinator analyze-complexity --research
            """.strip(),
                expand=False,
                border_style="white",
                padding=(1, 2),
            )
        )

    except Exception as e:
        console.print(
            f"[ERROR] Error displaying complexity report: {str(e)}", style="bold red"
        )
