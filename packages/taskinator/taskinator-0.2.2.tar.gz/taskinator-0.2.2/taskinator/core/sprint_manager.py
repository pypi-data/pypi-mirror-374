"""
Sprint management functionality for Taskinator.

This module provides core functionality for managing sprints and associated tasks.
"""

import os
import json
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple

from taskinator.models.sprint import Sprint, SprintCollection, SprintStatus, DailyProgress
from taskinator.models.task import Task, TaskCollection
from taskinator.core.task_manager import read_tasks, write_tasks, get_tasks_path
from taskinator.core.file_storage import FileStorageError


def get_sprints_path(tasks_path: Optional[str] = None) -> str:
    """
    Get the path to the sprints.json file.
    
    Args:
        tasks_path: Optional path to tasks.json file
        
    Returns:
        Path to sprints.json
    """
    if tasks_path:
        tasks_dir = os.path.dirname(tasks_path)
    else:
        tasks_dir = os.path.dirname(get_tasks_path())
        
    return os.path.join(tasks_dir, "sprints.json")


def read_sprints(sprints_path: Optional[str] = None) -> SprintCollection:
    """
    Read sprints from the sprints.json file.
    
    Args:
        sprints_path: Optional path to sprints.json file
        
    Returns:
        SprintCollection: Collection of sprints
        
    Raises:
        FileStorageError: If sprints.json cannot be read
    """
    if sprints_path is None:
        sprints_path = get_sprints_path()
        
    try:
        if os.path.exists(sprints_path):
            with open(sprints_path, "r") as f:
                sprints_data = json.load(f)
                return SprintCollection.model_validate(sprints_data)
        else:
            # If file doesn't exist, create a new collection
            return SprintCollection()
            
    except (json.JSONDecodeError, FileNotFoundError) as e:
        raise FileStorageError(f"Error reading sprints file: {e}")


def write_sprints(sprints: SprintCollection, sprints_path: Optional[str] = None) -> bool:
    """
    Write sprints to the sprints.json file.
    
    Args:
        sprints: SprintCollection to write
        sprints_path: Optional path to sprints.json file
        
    Returns:
        bool: True if successful, False otherwise
        
    Raises:
        FileStorageError: If sprints.json cannot be written
    """
    if sprints_path is None:
        sprints_path = get_sprints_path()
        
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(sprints_path), exist_ok=True)
        
        # Update timestamp
        sprints.metadata["updated_at"] = datetime.now().isoformat()
        
        # Write JSON file
        with open(sprints_path, "w") as f:
            f.write(sprints.model_dump_json())
            
        return True
        
    except (IOError, OSError) as e:
        raise FileStorageError(f"Error writing sprints file: {e}")


def create_sprint(
    name: str, 
    goal: str = "", 
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    capacity: Optional[float] = None,
    tasks_path: Optional[str] = None
) -> Sprint:
    """
    Create a new sprint.
    
    Args:
        name: Sprint name
        goal: Sprint goal
        start_date: Sprint start date
        end_date: Sprint end date
        capacity: Team capacity in story points
        tasks_path: Optional path to tasks.json file
        
    Returns:
        Sprint: Created sprint
        
    Raises:
        ValueError: If a sprint with the same ID already exists
    """
    # Read existing sprints
    sprints = read_sprints(get_sprints_path(tasks_path))
    
    # Generate sprint ID from name
    sprint_id = f"sprint-{len(sprints.sprints) + 1}"
    
    # Create sprint
    sprint = Sprint(
        id=sprint_id,
        name=name,
        goal=goal,
        start_date=start_date,
        end_date=end_date,
        status=SprintStatus.PLANNED,
        capacity=capacity,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    
    # Add sprint to collection
    if not sprints.add_sprint(sprint):
        raise ValueError(f"Sprint with ID {sprint_id} already exists.")
        
    # Write sprints to file
    write_sprints(sprints, get_sprints_path(tasks_path))
    
    return sprint


def get_sprint(sprint_id: str, tasks_path: Optional[str] = None) -> Optional[Sprint]:
    """
    Get a sprint by ID.
    
    Args:
        sprint_id: Sprint ID
        tasks_path: Optional path to tasks.json file
        
    Returns:
        Sprint: Found sprint or None if not found
    """
    sprints = read_sprints(get_sprints_path(tasks_path))
    return sprints.get_sprint(sprint_id)


def update_sprint(sprint: Sprint, tasks_path: Optional[str] = None) -> bool:
    """
    Update a sprint.
    
    Args:
        sprint: Sprint to update
        tasks_path: Optional path to tasks.json file
        
    Returns:
        bool: True if successful, False if sprint not found
    """
    sprints = read_sprints(get_sprints_path(tasks_path))
    
    # Update sprint
    if not sprints.update_sprint(sprint):
        return False
        
    # Write sprints to file
    write_sprints(sprints, get_sprints_path(tasks_path))
    
    return True


def delete_sprint(sprint_id: str, tasks_path: Optional[str] = None) -> bool:
    """
    Delete a sprint.
    
    Args:
        sprint_id: Sprint ID to delete
        tasks_path: Optional path to tasks.json file
        
    Returns:
        bool: True if successful, False if sprint not found
    """
    sprints = read_sprints(get_sprints_path(tasks_path))
    
    # Remove sprint
    if not sprints.remove_sprint(sprint_id):
        return False
        
    # Write sprints to file
    write_sprints(sprints, get_sprints_path(tasks_path))
    
    # Remove sprint_id from tasks
    unassign_all_tasks_from_sprint(sprint_id, tasks_path)
    
    return True


def list_sprints(
    status: Optional[str] = None, 
    tasks_path: Optional[str] = None
) -> List[Sprint]:
    """
    List sprints, optionally filtered by status.
    
    Args:
        status: Optional status to filter by
        tasks_path: Optional path to tasks.json file
        
    Returns:
        List[Sprint]: List of sprints
    """
    sprints = read_sprints(get_sprints_path(tasks_path))
    
    if status:
        try:
            status_enum = SprintStatus(status)
            return [s for s in sprints.sprints if s.status == status_enum]
        except ValueError:
            # Invalid status
            return []
    
    return sprints.sprints


def get_active_sprint(tasks_path: Optional[str] = None) -> Optional[Sprint]:
    """
    Get the currently active sprint.
    
    Args:
        tasks_path: Optional path to tasks.json file
        
    Returns:
        Sprint: Active sprint or None if no active sprint
    """
    sprints = read_sprints(get_sprints_path(tasks_path))
    return sprints.get_active_sprint()


def start_sprint(
    sprint_id: str, 
    start_date: Optional[datetime] = None,
    tasks_path: Optional[str] = None
) -> bool:
    """
    Start a sprint.
    
    Args:
        sprint_id: Sprint ID to start
        start_date: Optional start date (defaults to now)
        tasks_path: Optional path to tasks.json file
        
    Returns:
        bool: True if successful, False if sprint not found or already active
        
    Raises:
        ValueError: If another sprint is already active
    """
    sprints = read_sprints(get_sprints_path(tasks_path))
    
    # Check if another sprint is active
    active_sprint = sprints.get_active_sprint()
    if active_sprint and active_sprint.id != sprint_id:
        raise ValueError(
            f"Sprint '{active_sprint.name}' (ID: {active_sprint.id}) is already active."
        )
        
    # Get sprint to start
    sprint = sprints.get_sprint(sprint_id)
    if not sprint:
        return False
        
    # Check if sprint is already active
    if sprint.status == SprintStatus.ACTIVE:
        return False
        
    # Set start date if not provided
    if start_date is None:
        start_date = datetime.now()
        
    # Update sprint
    sprint.status = SprintStatus.ACTIVE
    sprint.start_date = start_date
    sprint.updated_at = datetime.now()
    
    # Add initial progress entry
    sprint_tasks = get_sprint_tasks(sprint_id, tasks_path)
    total_points = sum(task.story_points or 0 for task in sprint_tasks)
    
    sprint.add_progress(
        date_value=start_date,
        remaining_points=total_points,
        completed_points=0.0,
        added_points=0.0,
        notes="Sprint started"
    )
    
    # Update sprint
    sprints.update_sprint(sprint)
    
    # Write sprints to file
    write_sprints(sprints, get_sprints_path(tasks_path))
    
    return True


def complete_sprint(
    sprint_id: str,
    retrospective: Optional[str] = None,
    tasks_path: Optional[str] = None
) -> bool:
    """
    Complete a sprint.
    
    Args:
        sprint_id: Sprint ID to complete
        retrospective: Optional retrospective notes
        tasks_path: Optional path to tasks.json file
        
    Returns:
        bool: True if successful, False if sprint not found or not active
    """
    sprints = read_sprints(get_sprints_path(tasks_path))
    
    # Get sprint to complete
    sprint = sprints.get_sprint(sprint_id)
    if not sprint:
        return False
        
    # Check if sprint is active
    if sprint.status != SprintStatus.ACTIVE:
        return False
        
    # Update sprint
    sprint.status = SprintStatus.COMPLETED
    sprint.updated_at = datetime.now()
    
    # Set end date if not already set
    if not sprint.end_date:
        sprint.end_date = datetime.now()
        
    # Set retrospective if provided
    if retrospective:
        sprint.retrospective = retrospective
        
    # Add final progress entry
    sprint_tasks = get_sprint_tasks(sprint_id, tasks_path)
    remaining_points = sum(
        task.story_points or 0 
        for task in sprint_tasks 
        if task.status != "done"
    )
    completed_points = sum(
        task.story_points or 0 
        for task in sprint_tasks 
        if task.status == "done"
    )
    
    sprint.add_progress(
        date_value=datetime.now(),
        remaining_points=remaining_points,
        completed_points=completed_points,
        added_points=0.0,
        notes="Sprint completed"
    )
    
    # Update sprint
    sprints.update_sprint(sprint)
    
    # Write sprints to file
    write_sprints(sprints, get_sprints_path(tasks_path))
    
    return True


def cancel_sprint(
    sprint_id: str,
    tasks_path: Optional[str] = None
) -> bool:
    """
    Cancel a sprint.
    
    Args:
        sprint_id: Sprint ID to cancel
        tasks_path: Optional path to tasks.json file
        
    Returns:
        bool: True if successful, False if sprint not found
    """
    sprints = read_sprints(get_sprints_path(tasks_path))
    
    # Get sprint to cancel
    sprint = sprints.get_sprint(sprint_id)
    if not sprint:
        return False
        
    # Update sprint
    sprint.status = SprintStatus.CANCELLED
    sprint.updated_at = datetime.now()
    
    # Update sprint
    sprints.update_sprint(sprint)
    
    # Write sprints to file
    write_sprints(sprints, get_sprints_path(tasks_path))
    
    return True


def get_sprint_tasks(sprint_id: str, tasks_path: Optional[str] = None) -> List[Task]:
    """
    Get tasks associated with a sprint.
    
    Args:
        sprint_id: Sprint ID
        tasks_path: Optional path to tasks.json file
        
    Returns:
        List[Task]: List of tasks in the sprint
    """
    tasks_collection = read_tasks(tasks_path)
    
    # Filter tasks by sprint_id
    return [task for task in tasks_collection.tasks if task.sprint_id == sprint_id]


def add_task_to_sprint(
    task_id: str,
    sprint_id: str,
    story_points: Optional[float] = None,
    tasks_path: Optional[str] = None
) -> bool:
    """
    Add a task to a sprint.
    
    Args:
        task_id: Task ID to add
        sprint_id: Sprint ID to add task to
        story_points: Optional story points to set
        tasks_path: Optional path to tasks.json file
        
    Returns:
        bool: True if successful, False if task or sprint not found
        
    Raises:
        ValueError: If task is already in a different sprint
    """
    # Get task collection
    tasks_collection = read_tasks(tasks_path)
    
    # Find task
    task = tasks_collection.get_task(task_id)
    if not task:
        return False
        
    # Check if task is already in a sprint
    if task.sprint_id and task.sprint_id != sprint_id:
        raise ValueError(f"Task {task_id} is already in sprint {task.sprint_id}")
        
    # Check if sprint exists
    sprint = get_sprint(sprint_id, tasks_path)
    if not sprint:
        return False
        
    # Update task
    task.sprint_id = sprint_id
    if story_points is not None:
        task.story_points = story_points
    task.updated_at = datetime.now()
    
    # Write tasks to file
    write_tasks(tasks_collection, tasks_path)
    
    # If sprint is active, update sprint progress
    if sprint.status == SprintStatus.ACTIVE:
        update_sprint_progress(sprint_id, tasks_path=tasks_path)
        
    return True


def remove_task_from_sprint(task_id: str, tasks_path: Optional[str] = None) -> bool:
    """
    Remove a task from its sprint.
    
    Args:
        task_id: Task ID to remove
        tasks_path: Optional path to tasks.json file
        
    Returns:
        bool: True if successful, False if task not found or not in a sprint
    """
    # Get task collection
    tasks_collection = read_tasks(tasks_path)
    
    # Find task
    task = tasks_collection.get_task(task_id)
    if not task:
        return False
        
    # Check if task is in a sprint
    if not task.sprint_id:
        return False
        
    # Get the sprint before updating the task
    sprint_id = task.sprint_id
    sprint = get_sprint(sprint_id, tasks_path)
    
    # Update task
    task.sprint_id = None
    task.updated_at = datetime.now()
    
    # Write tasks to file
    write_tasks(tasks_collection, tasks_path)
    
    # If sprint is active, update sprint progress
    if sprint and sprint.status == SprintStatus.ACTIVE:
        update_sprint_progress(sprint_id, tasks_path=tasks_path)
        
    return True


def unassign_all_tasks_from_sprint(sprint_id: str, tasks_path: Optional[str] = None) -> int:
    """
    Unassign all tasks from a sprint.
    
    Args:
        sprint_id: Sprint ID
        tasks_path: Optional path to tasks.json file
        
    Returns:
        int: Number of tasks unassigned
    """
    # Get task collection
    tasks_collection = read_tasks(tasks_path)
    
    # Find tasks in the sprint
    count = 0
    for task in tasks_collection.tasks:
        if task.sprint_id == sprint_id:
            task.sprint_id = None
            task.updated_at = datetime.now()
            count += 1
            
    # Write tasks to file if any were updated
    if count > 0:
        write_tasks(tasks_collection, tasks_path)
        
    return count


def set_task_story_points(
    task_id: str, 
    story_points: float,
    tasks_path: Optional[str] = None
) -> bool:
    """
    Set story points for a task.
    
    Args:
        task_id: Task ID
        story_points: Story points value
        tasks_path: Optional path to tasks.json file
        
    Returns:
        bool: True if successful, False if task not found
    """
    # Get task collection
    tasks_collection = read_tasks(tasks_path)
    
    # Find task
    task = tasks_collection.get_task(task_id)
    if not task:
        return False
        
    # Update task
    task.story_points = story_points
    task.updated_at = datetime.now()
    
    # Write tasks to file
    write_tasks(tasks_collection, tasks_path)
    
    # If task is in a sprint, update sprint progress
    if task.sprint_id:
        sprint = get_sprint(task.sprint_id, tasks_path)
        if sprint and sprint.status == SprintStatus.ACTIVE:
            update_sprint_progress(task.sprint_id, tasks_path=tasks_path)
            
    return True


def get_sprint_stats(sprint_id: str, tasks_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Get statistics for a sprint.
    
    Args:
        sprint_id: Sprint ID
        tasks_path: Optional path to tasks.json file
        
    Returns:
        Dict: Sprint statistics
    """
    # Get sprint
    sprint = get_sprint(sprint_id, tasks_path)
    if not sprint:
        return {}
        
    # Get tasks in sprint
    tasks = get_sprint_tasks(sprint_id, tasks_path)
    
    # Calculate statistics
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.status == "done")
    in_progress_tasks = sum(1 for task in tasks if task.status == "in-progress")
    blocked_tasks = sum(1 for task in tasks if task.status == "blocked")
    pending_tasks = sum(1 for task in tasks if task.status == "pending")
    
    total_points = sum(task.story_points or 0 for task in tasks)
    completed_points = sum(task.story_points or 0 for task in tasks if task.status == "done")
    
    completion_rate_tasks = (completed_tasks / total_tasks) if total_tasks > 0 else 0
    completion_rate_points = (completed_points / total_points) if total_points > 0 else 0
    
    # Calculate days elapsed and remaining
    days_elapsed = 0
    days_remaining = 0
    days_total = 0
    
    if sprint.start_date:
        if sprint.status == SprintStatus.PLANNED:
            # Sprint hasn't started
            days_elapsed = 0
            if sprint.end_date:
                days_total = (sprint.end_date - sprint.start_date).days
                days_remaining = days_total
        else:
            # Sprint is active or completed
            start_date = sprint.start_date
            
            if sprint.status == SprintStatus.ACTIVE:
                current_date = datetime.now()
                days_elapsed = (current_date - start_date).days
                
                if sprint.end_date:
                    days_total = (sprint.end_date - start_date).days
                    days_remaining = max(0, days_total - days_elapsed)
            elif sprint.status == SprintStatus.COMPLETED and sprint.end_date:
                days_elapsed = (sprint.end_date - start_date).days
                days_total = days_elapsed
                days_remaining = 0
    
    return {
        "id": sprint_id,
        "name": sprint.name,
        "status": sprint.status.value if hasattr(sprint.status, "value") else sprint.status,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "in_progress_tasks": in_progress_tasks,
        "blocked_tasks": blocked_tasks,
        "pending_tasks": pending_tasks,
        "total_points": total_points,
        "completed_points": completed_points,
        "completion_rate_tasks": completion_rate_tasks,
        "completion_rate_points": completion_rate_points,
        "days_elapsed": days_elapsed,
        "days_remaining": days_remaining,
        "days_total": days_total,
        "capacity": sprint.capacity,
    }


def update_sprint_progress(
    sprint_id: str,
    current_date: Optional[Union[datetime, date]] = None,
    tasks_path: Optional[str] = None
) -> bool:
    """
    Update progress tracking for a sprint.
    
    Args:
        sprint_id: Sprint ID
        current_date: Optional date for the progress entry (defaults to today)
        tasks_path: Optional path to tasks.json file
        
    Returns:
        bool: True if successful, False if sprint not found or not active
    """
    # Get sprint
    sprints = read_sprints(get_sprints_path(tasks_path))
    
    sprint = sprints.get_sprint(sprint_id)
    if not sprint:
        return False
        
    # Check if sprint is active
    if sprint.status != SprintStatus.ACTIVE:
        return False
        
    # Set current_date if not provided
    if current_date is None:
        current_date = datetime.now()
    elif isinstance(current_date, date) and not isinstance(current_date, datetime):
        current_date = datetime.combine(current_date, datetime.min.time())
        
    # Get tasks in sprint
    tasks = get_sprint_tasks(sprint_id, tasks_path)
    
    # Calculate remaining and completed points
    remaining_points = sum(
        task.story_points or 0 
        for task in tasks 
        if task.status != "done"
    )
    completed_points = sum(
        task.story_points or 0 
        for task in tasks 
        if task.status == "done"
    )
    
    # Calculate points added since last entry
    added_points = 0.0
    if sprint.progress:
        last_entry = max(sprint.progress, key=lambda p: p.date)
        total_points_previous = last_entry.remaining_points + last_entry.completed_points
        total_points_current = remaining_points + completed_points
        added_points = max(0.0, total_points_current - total_points_previous)
    
    # Add progress entry
    sprint.add_progress(
        date_value=current_date,
        remaining_points=remaining_points,
        completed_points=completed_points,
        added_points=added_points,
        notes=f"Progress update: {completed_points} points completed, {remaining_points} points remaining"
    )
    
    # Update sprint
    sprint.updated_at = datetime.now()
    sprints.update_sprint(sprint)
    
    # Write sprints to file
    write_sprints(sprints, get_sprints_path(tasks_path))
    
    return True


def generate_burndown_data(sprint_id: str, tasks_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate data for a burndown chart.
    
    Args:
        sprint_id: Sprint ID
        tasks_path: Optional path to tasks.json file
        
    Returns:
        Dict: Burndown chart data
    """
    # Get sprint
    sprint = get_sprint(sprint_id, tasks_path)
    if not sprint:
        return {}
        
    # Check if sprint has start and end dates
    if not sprint.start_date:
        return {
            "error": "Sprint has no start date"
        }
        
    # Determine ideal burndown
    if not sprint.progress:
        return {
            "error": "Sprint has no progress tracking data"
        }
        
    # Sort progress entries by date
    progress = sorted(sprint.progress, key=lambda p: p.date)
    
    # Get initial and current/final point values
    initial_points = progress[0].remaining_points + progress[0].completed_points
    current_points = progress[-1].remaining_points + progress[-1].completed_points
    
    # Determine all dates in sprint
    all_dates = []
    if sprint.start_date and sprint.end_date:
        current_date = sprint.start_date.date() if isinstance(sprint.start_date, datetime) else sprint.start_date
        end_date = sprint.end_date.date() if isinstance(sprint.end_date, datetime) else sprint.end_date
        
        while current_date <= end_date:
            all_dates.append(current_date)
            current_date += timedelta(days=1)
    else:
        # Just use the progress dates
        date_set = set()
        for entry in progress:
            entry_date = entry.date.date() if isinstance(entry.date, datetime) else entry.date
            date_set.add(entry_date)
        
        all_dates = sorted(date_set)
    
    # Generate ideal burndown line
    ideal_burndown = []
    if all_dates:
        total_days = len(all_dates)
        daily_ideal_reduction = initial_points / total_days if total_days > 0 else 0
        
        for i, current_date in enumerate(all_dates):
            ideal_burndown.append({
                "date": current_date.isoformat(),
                "value": max(0, initial_points - (daily_ideal_reduction * i))
            })
    
    # Convert progress entries to chart data format
    actual_burndown = []
    dates_with_entries = set()
    for entry in progress:
        entry_date = entry.date.date() if isinstance(entry.date, datetime) else entry.date
        dates_with_entries.add(entry_date)
        actual_burndown.append({
            "date": entry_date.isoformat(),
            "remaining": entry.remaining_points,
            "completed": entry.completed_points,
            "added": entry.added_points
        })
        
    # Fill in missing dates with data from previous entry
    actual_burndown_map = {entry["date"]: entry for entry in actual_burndown}
    complete_burndown = []
    
    previous_entry = None
    for current_date in all_dates:
        date_str = current_date.isoformat()
        
        if date_str in actual_burndown_map:
            entry = actual_burndown_map[date_str]
            complete_burndown.append(entry)
            previous_entry = entry
        elif previous_entry:
            # Copy previous entry with new date
            complete_burndown.append({
                "date": date_str,
                "remaining": previous_entry["remaining"],
                "completed": previous_entry["completed"],
                "added": 0.0
            })
            
    return {
        "sprint": {
            "id": sprint.id,
            "name": sprint.name,
            "start_date": sprint.start_date.date().isoformat() if sprint.start_date else None,
            "end_date": sprint.end_date.date().isoformat() if sprint.end_date else None,
            "status": sprint.status.value if hasattr(sprint.status, "value") else sprint.status,
            "initial_points": initial_points,
            "current_points": current_points,
        },
        "ideal_burndown": ideal_burndown,
        "actual_burndown": complete_burndown
    }