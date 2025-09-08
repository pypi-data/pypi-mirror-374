"""
Story and feature processing for Taskinator.

This module provides functionality to parse user stories, features, and
other agile artifacts to generate tasks.
"""

import os
import json
import re
from enum import Enum
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple, Set

from taskinator.core.task_manager import read_tasks, write_tasks, get_tasks_path
from taskinator.models.task import Task, TaskCollection
from taskinator.core.story_point_systems import (
    StoryPointSystem,
    get_story_point_system,
    PointSystemType,
)
# Import AI client for future implementation
# from taskinator.services.ai.ai_client import AIClient


# Regex patterns for common formats
USER_STORY_PATTERN = r"As an? (?P<role>[^,]+),\s+I want to\s+(?P<action>[^,]+),\s+so that\s+(?P<benefit>.+)"
FEATURE_PATTERN = r"(?:Feature|Epic):\s*(?P<title>[^\n]+)"
TASK_PATTERN = r"(?:Task|TODO|To-Do):\s*(?P<title>[^\n]+)"
ACCEPTANCE_PATTERN = (
    r"(?:Acceptance Criteria|Acceptance Test):\s*(?P<criteria>.+?)(?:\n\n|\Z)"
)
STORY_POINTS_PATTERN = r"(?:Story Points|Points|SP|Effort):\s*(?P<points>[0-9]+|[0-9]*\.[0-9]+|XS|S|M|L|XL|XXL)"
PRIORITY_PATTERN = r"(?:Priority|Importance):\s*(?P<priority>high|medium|low|[0-9]+)"


class StoryFormat(str, Enum):
    """Enumeration of supported story formats."""

    USER_STORY = "user_story"
    FEATURE = "feature"
    GENERIC = "generic"
    TASK_LIST = "task_list"
    JIRA = "jira"
    AZURE_DEVOPS = "azure_devops"


def detect_story_format(content: str) -> StoryFormat:
    """
    Detect the format of a story/feature description.

    Args:
        content: The content to analyze

    Returns:
        StoryFormat: Detected format
    """
    # Check for user story format
    if re.search(USER_STORY_PATTERN, content, re.IGNORECASE | re.MULTILINE):
        return StoryFormat.USER_STORY

    # Check for feature/epic format
    if re.search(FEATURE_PATTERN, content, re.IGNORECASE | re.MULTILINE):
        return StoryFormat.FEATURE

    # Check for JIRA format (contains JIRA-123 style references)
    if re.search(r"\b[A-Z]+-[0-9]+\b", content):
        return StoryFormat.JIRA

    # Check for Azure DevOps format (contains #123 style references)
    if re.search(r"#[0-9]+", content) and (
        "azure" in content.lower() or "devops" in content.lower()
    ):
        return StoryFormat.AZURE_DEVOPS

    # Check for task list format
    if re.search(r"(?:- \[ \]|TODO:|Task:)", content, re.IGNORECASE | re.MULTILINE):
        return StoryFormat.TASK_LIST

    # Default to generic
    return StoryFormat.GENERIC


def extract_story_metadata(content: str) -> Dict[str, Any]:
    """
    Extract metadata from story/feature description.

    Args:
        content: The story/feature description

    Returns:
        Dict: Extracted metadata
    """
    metadata = {}

    # Look for user story components
    user_story_match = re.search(
        USER_STORY_PATTERN, content, re.IGNORECASE | re.MULTILINE
    )
    if user_story_match:
        metadata["role"] = user_story_match.group("role").strip()
        metadata["action"] = user_story_match.group("action").strip()
        metadata["benefit"] = user_story_match.group("benefit").strip()

    # Look for feature/epic title
    feature_match = re.search(FEATURE_PATTERN, content, re.IGNORECASE | re.MULTILINE)
    if feature_match:
        metadata["feature_title"] = feature_match.group("title").strip()

    # Look for acceptance criteria
    acceptance_match = re.search(
        ACCEPTANCE_PATTERN, content, re.IGNORECASE | re.DOTALL | re.MULTILINE
    )
    if acceptance_match:
        criteria_text = acceptance_match.group("criteria").strip()
        # Split by line breaks or bullet points
        criteria = [
            item.strip().lstrip("*-•").strip()
            for item in re.split(r"\n+|\r\n+", criteria_text)
            if item.strip()
        ]
        metadata["acceptance_criteria"] = criteria

    # Look for story points
    points_match = re.search(
        STORY_POINTS_PATTERN, content, re.IGNORECASE | re.MULTILINE
    )
    if points_match:
        points_str = points_match.group("points").strip()
        try:
            # Try to convert to numeric
            if points_str.lower() in ["xs", "s", "m", "l", "xl", "xxl"]:
                points = points_str.upper()
            else:
                points = float(points_str)
                # Convert to int if it's a whole number
                if points.is_integer():
                    points = int(points)
            metadata["story_points"] = points
        except ValueError:
            # Keep as string if can't convert
            metadata["story_points"] = points_str

    # Look for priority
    priority_match = re.search(PRIORITY_PATTERN, content, re.IGNORECASE | re.MULTILINE)
    if priority_match:
        priority = priority_match.group("priority").strip().lower()
        if priority in ["high", "medium", "low"]:
            metadata["priority"] = priority
        elif priority.isdigit():
            # Convert numeric priority to high/medium/low
            priority_num = int(priority)
            if priority_num <= 1:
                metadata["priority"] = "high"
            elif priority_num <= 3:
                metadata["priority"] = "medium"
            else:
                metadata["priority"] = "low"

    return metadata


def extract_tasks_from_content(content: str) -> List[Dict[str, Any]]:
    """
    Extract explicit tasks from content.

    Args:
        content: The content to extract tasks from

    Returns:
        List[Dict]: List of extracted tasks
    """
    tasks = []

    # Look for tasks defined with "Task:" or "TODO:" prefix
    task_matches = re.finditer(
        r"(?:Task|TODO|To-Do):\s*(?P<title>[^\n]+)",
        content,
        re.IGNORECASE | re.MULTILINE,
    )
    for match in task_matches:
        task = {
            "title": match.group("title").strip(),
            "source": "explicit",
        }
        tasks.append(task)

    # Look for markdown task list items
    task_list_items = re.finditer(r"- \[ \] (?P<title>.+)$", content, re.MULTILINE)
    for match in task_list_items:
        task = {
            "title": match.group("title").strip(),
            "source": "markdown_list",
        }
        tasks.append(task)

    # Look for numbered list items
    numbered_items = re.finditer(r"^\d+\.\s+(?P<title>.+)$", content, re.MULTILINE)
    for match in numbered_items:
        task = {
            "title": match.group("title").strip(),
            "source": "numbered_list",
        }
        tasks.append(task)

    return tasks


def auto_detect_point_system(story_points: Union[int, float, str]) -> str:
    """
    Auto-detect the most likely point system based on the provided value.

    Args:
        story_points: The story point value

    Returns:
        str: Detected point system name
    """
    # Check T-shirt sizes
    if isinstance(story_points, str) and story_points.upper() in [
        "XS",
        "S",
        "M",
        "L",
        "XL",
        "XXL",
    ]:
        return "tshirt"

    # Convert to number if possible
    try:
        numeric_points = (
            float(story_points) if isinstance(story_points, str) else story_points
        )
    except ValueError:
        return "custom"  # Can't convert to number

    # Check Fibonacci sequence
    fibonacci = [1, 2, 3, 5, 8, 13, 21, 34]
    if numeric_points in fibonacci:
        return "fibonacci"

    # Check modified Fibonacci
    modified_fibonacci = [0, 0.5, 1, 2, 3, 5, 8, 13, 20, 40, 100]
    if numeric_points in modified_fibonacci:
        return "modified_fibonacci"

    # Check powers of two
    powers_of_two = [1, 2, 4, 8, 16, 32]
    if numeric_points in powers_of_two:
        return "powers_of_two"

    # Check linear scale
    if 1 <= numeric_points <= 10 and numeric_points.is_integer():
        return "linear"

    # Default to modified Fibonacci as most flexible
    return "modified_fibonacci"


def process_story_file(
    file_path: str,
    point_system: Optional[str] = None,
    ai_assist: bool = True,
    analyze_codebase: bool = True,
    task_prefix: Optional[str] = None,
    output_path: Optional[str] = None,
) -> TaskCollection:
    """
    Process a story/feature file and generate tasks.

    Args:
        file_path: Path to the story/feature file
        point_system: Story point system to use for estimation
        ai_assist: Whether to use AI to enhance task generation
        analyze_codebase: Whether to analyze codebase for context
        task_prefix: Prefix for generated task IDs
        output_path: Path to write tasks to (defaults to tasks.json)

    Returns:
        TaskCollection: Generated tasks
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Story file not found: {file_path}")

    # Read file content
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Detect format and extract metadata
    story_format = detect_story_format(content)
    metadata = extract_story_metadata(content)

    # Extract explicit tasks
    explicit_tasks = extract_tasks_from_content(content)

    # Set up story point system
    if not point_system and "story_points" in metadata:
        # Auto-detect point system from the story points
        point_system = auto_detect_point_system(metadata["story_points"])

    story_point_system = get_story_point_system(point_system or "fibonacci")

    # Generate a task list
    task_collection = generate_tasks_from_story(
        content=content,
        metadata=metadata,
        explicit_tasks=explicit_tasks,
        story_format=story_format,
        story_point_system=story_point_system,
        ai_assist=ai_assist,
        analyze_codebase=analyze_codebase,
        task_prefix=task_prefix,
        file_path=file_path,
    )

    # Write tasks if output path provided
    if output_path:
        write_tasks(task_collection, output_path)

    return task_collection


async def analyze_codebase_for_context(
    content: str, metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Analyze the codebase to provide context for task generation.

    Args:
        content: The story content
        metadata: The extracted metadata

    Returns:
        Dict: Analysis results
    """
    # This is a placeholder for future implementation
    # In a real implementation, this would:
    # 1. Identify relevant code files based on story content
    # 2. Analyze code structure and dependencies
    # 3. Identify technology stack and architecture patterns

    analysis = {
        "relevant_files": [],
        "identified_technologies": [],
        "suggested_approach": "",
    }

    return analysis


def generate_tasks_from_story(
    content: str,
    metadata: Dict[str, Any],
    explicit_tasks: List[Dict[str, Any]],
    story_format: StoryFormat,
    story_point_system: StoryPointSystem,
    ai_assist: bool = True,
    analyze_codebase: bool = False,
    task_prefix: Optional[str] = None,
    file_path: Optional[str] = None,
) -> TaskCollection:
    """
    Generate tasks from a story description.

    Args:
        content: The story content
        metadata: The extracted metadata
        explicit_tasks: Explicitly defined tasks in the content
        story_format: The detected story format
        story_point_system: Story point system to use for estimation
        ai_assist: Whether to use AI to enhance task generation
        analyze_codebase: Whether to analyze codebase for context
        task_prefix: Prefix for generated task IDs
        file_path: Path to the original story file

    Returns:
        TaskCollection: Generated tasks
    """
    # Start with existing tasks collection or create new one
    try:
        tasks_collection = read_tasks()
    except:
        tasks_collection = TaskCollection(
            tasks=[],
            metadata={
                "project_name": "Taskinator",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "version": "0.2.0",
            },
        )

    # Generate a task title from metadata
    task_title = ""
    if "feature_title" in metadata:
        task_title = metadata["feature_title"]
    elif "role" in metadata and "action" in metadata:
        task_title = f"Implement: {metadata['action'].rstrip('.')}"

    if not task_title and explicit_tasks:
        # Use first explicit task as main task
        task_title = explicit_tasks[0]["title"]
        explicit_tasks = explicit_tasks[1:]

    if not task_title:
        # Use file name as fallback
        file_name = os.path.basename(file_path) if file_path else "unknown"
        task_title = f"Implement {os.path.splitext(file_name)[0]}"

    # Generate ID for the main task
    main_task_id = f"{task_prefix}-" if task_prefix else ""
    main_task_id += task_title.lower().replace(" ", "-")[:30]

    # Create the main task
    story_points = metadata.get("story_points")
    main_task = Task(
        id=main_task_id,
        title=task_title,
        description=content[:1000],  # Limit description length
        status="pending",
        priority=metadata.get("priority", "medium"),
        story_points=story_points,
        acceptance_criteria=metadata.get("acceptance_criteria", []),
        source={
            "type": "story",
            "format": story_format,
            "file": os.path.basename(file_path) if file_path else None,
        },
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    # Add explicit tasks as subtasks
    subtasks = []
    for i, task_info in enumerate(explicit_tasks):
        subtask_id = f"{main_task_id}.{i+1}"
        subtask = Task(
            id=subtask_id,
            title=task_info["title"],
            description="",
            status="pending",
            priority=metadata.get("priority", "medium"),
            dependencies=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        subtasks.append(subtask)

    main_task.subtasks = subtasks

    # Add the task to the collection
    tasks_collection.tasks.append(main_task)

    # Use AI to expand the task if requested
    if ai_assist:
        # This would call the task expansion logic from task_expansion.py
        # For now, we'll leave it as a placeholder
        pass

    return tasks_collection
