"""
NextCloud synchronization utilities for Taskinator.

This module provides utilities for synchronizing tasks between Taskinator and NextCloud.
"""

import json
import logging
import os
import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from taskinator.core.task_manager import read_tasks, write_tasks
from taskinator.models.task import Task, TaskCollection

from ..plugin_base import SyncDirection, SyncMetadata, SyncStatus
from .nextcloud_client import NextCloudClient, NextCloudTask

# Set up logging
log = logging.getLogger(__name__)


class NextCloudSyncMetadata(SyncMetadata):
    """Metadata for NextCloud synchronization."""

    etag: Optional[str] = None
    fileid: Optional[str] = None
    version_history: List[Dict[str, Any]] = []

    def add_version(
        self, changes: List[Dict[str, Any]], modified_by: str = "local"
    ) -> None:
        """Add a new version to the history.

        Args:
            changes: List of changes made in this version
            modified_by: Who made the modification ('local' or 'nextcloud')
        """
        # Create a new version entry
        version = {
            "version": len(self.version_history) + 1,
            "last_modified": datetime.now().isoformat(),
            "modified_by": modified_by,
            "changes": changes,
        }

        # Add to history
        self.version_history.append(version)


class TaskFieldMapping:
    """
    Handles mapping between Taskinator Task objects and Nextcloud task objects.
    
    This class ensures lossless bidirectional synchronization between Taskinator tasks
    and Nextcloud tasks. It preserves all task attributes during synchronization,
    allowing tasks to be synced to Nextcloud, deleted locally, and then restored
    to their original state with all attributes intact.
    
    The mapping process uses Pydantic models to ensure consistent data formatting
    and validation in both sync directions. This guarantees that task data remains
    properly typed and structured throughout the synchronization process.
    """

    # Mapping from Taskinator to NextCloud
    LOCAL_TO_REMOTE = {
        "title": "title",
        "description": "description",
        "status": "status",  # Special handling required
        "priority": "priority",
        "due_date": "due_date",
        "dependencies": "categories",  # Special handling required
        "categories": "categories",
    }

    # Mapping from NextCloud to Taskinator
    REMOTE_TO_LOCAL = {
        "title": "title",
        "description": "description",
        "status": "status",  # Special handling required
        "priority": "priority",
        "due_date": "due_date",
        "categories": "categories",
    }

    @classmethod
    def map_local_to_remote(cls, task: Task) -> Dict[str, Any]:
        """Map Taskinator task to NextCloud task.

        Args:
            task: Taskinator task

        Returns:
            Dict[str, Any]: Dictionary with NextCloud task fields
        """
        result = {}

        # Handle different types of task objects
        if isinstance(task, str):
            # If task is a string (task ID), return minimal data
            return {"id": task}
        elif hasattr(task, "model_dump"):
            task_dict = task.model_dump()
        elif hasattr(task, "dict"):
            task_dict = task.dict()
        else:
            # Try to convert to dict if it's a dictionary-like object
            try:
                task_dict = dict(task)
            except (TypeError, ValueError):
                # If all else fails, return minimal data with the string representation
                return {"id": str(task)}

        # Include task ID in the title
        task_id = task_dict.get("id", "")
        task_title = task_dict.get("title", "")
        result["title"] = f"#{task_id}: {task_title}"

        # Create a rich markdown description that contains all task details
        # This ensures we can recreate the task exactly as it was
        markdown_description = cls._create_markdown_description(task_dict)
        result["description"] = markdown_description

        for local_field, remote_field in cls.LOCAL_TO_REMOTE.items():
            if local_field in task_dict:
                # Skip title and description as we've already handled them
                if local_field in ["title", "description"]:
                    continue

                # Special handling for status
                if local_field == "status":
                    status_map = {
                        "pending": "pending",
                        "in-progress": "in_progress",
                        "done": "done",
                        "blocked": "pending",
                        "deferred": "pending",
                        "cancelled": "pending",
                    }
                    result[remote_field] = status_map.get(
                        task_dict[local_field].lower(), "pending"
                    )
                # Special handling for dependencies
                elif local_field == "dependencies":
                    # Add dependencies as categories with a special prefix
                    dependencies = task_dict.get(local_field, [])
                    if dependencies:
                        # Convert to strings if they're not already
                        dependencies = [str(dep) for dep in dependencies]
                        
                        # Create dependency tags
                        dependency_tags = [f"Depends on {dep}" for dep in dependencies]
                        
                        # Add to categories if they exist, otherwise create
                        if "categories" in result:
                            result["categories"].extend(dependency_tags)
                        else:
                            result["categories"] = dependency_tags
                        
                        # Store all dependencies in extra metadata
                        if "extra" not in result:
                            result["extra"] = {}
                        result["extra"]["all_dependencies"] = dependencies
                else:
                    # Regular field mapping
                    result[remote_field] = task_dict[local_field]

        return result

    @classmethod
    def map_remote_to_local(cls, remote_task: NextCloudTask) -> Dict[str, Any]:
        """Map NextCloud task to Taskinator task.

        Args:
            remote_task: NextCloud task

        Returns:
            Dict[str, Any]: Dictionary with Taskinator task fields
        """
        result = {}

        # Handle different types of remote task objects
        if hasattr(remote_task, "model_dump"):
            remote_dict = remote_task.model_dump()
        elif hasattr(remote_task, "dict"):
            remote_dict = remote_task.dict()
        else:
            remote_dict = remote_task.__dict__

        # Check if we have the full task data in the extra field
        if remote_dict.get("extra") and "taskinator_full_data" in remote_dict["extra"]:
            # If we have the full data, use it directly
            return remote_dict["extra"]["taskinator_full_data"]

        # Otherwise, map fields manually
        for local_field, remote_field in cls.LOCAL_TO_REMOTE.items():
            if remote_field in remote_dict:
                # Skip special fields
                if remote_field in ["title", "description", "categories"]:
                    continue

                # Map the field
                result[local_field] = remote_dict[remote_field]

        # Extract task ID and title from the title field
        title = remote_dict.get("title", "")
        task_id_match = re.match(r"#(\d+):\s*(.*)", title)
        if task_id_match:
            result["id"] = int(task_id_match.group(1))
            result["title"] = task_id_match.group(2)
        else:
            result["title"] = title

        # Extract description
        result["description"] = cls._extract_description(
            remote_dict.get("description", "")
        )

        # Extract dependencies from categories
        dependencies = []
        for category in remote_dict.get("categories", []):
            dep_match = re.match(r"Depends on (\d+)", category)
            if dep_match:
                dependencies.append(dep_match.group(1))

        # Also check for dependencies in the extra field
        if remote_dict.get("extra") and "all_dependencies" in remote_dict["extra"]:
            for dep in remote_dict["extra"]["all_dependencies"]:
                if dep not in dependencies:
                    dependencies.append(dep)

        if dependencies:
            result["dependencies"] = dependencies

        # Extract tags from categories (excluding dependency tags)
        tags = []
        for category in remote_dict.get("categories", []):
            if not category.startswith("Depends on "):
                tags.append(category)

        if tags:
            result["tags"] = tags

        # Handle parent-child relationship
        if remote_dict.get("parent_id"):
            # Store the parent ID from Nextcloud
            result["parent_id"] = remote_dict["parent_id"]
        elif remote_dict.get("extra") and "parent_id" in remote_dict["extra"]:
            # If parent_id is stored in extra metadata, use that
            result["parent_id"] = remote_dict["extra"]["parent_id"]

        # Extract other fields from the markdown description
        cls._extract_fields_from_markdown(remote_dict.get("description", ""), result)

        return result

    @classmethod
    def _create_markdown_description(cls, task_dict: Dict[str, Any]) -> str:
        """Create a rich markdown description containing all task details.

        Args:
            task_dict: Task dictionary

        Returns:
            str: Markdown description
        """
        # Start with the basic description
        description = task_dict.get("description", "")

        # Add a separator and metadata section
        markdown = f"{description}\n\n---\n\n"

        # Add task details
        if task_dict.get("details"):
            markdown += f"## Details\n\n{task_dict['details']}\n\n"

        # Add test strategy
        if task_dict.get("test_strategy"):
            markdown += f"## Test Strategy\n\n{task_dict['test_strategy']}\n\n"

        # Add priority and status
        markdown += f"**Priority:** {task_dict.get('priority', 'medium')}\n"
        markdown += f"**Status:** {task_dict.get('status', 'pending')}\n"

        # Add dependencies
        deps = task_dict.get("dependencies", [])
        if deps:
            markdown += f"**Dependencies:** {', '.join(deps)}\n"

        # Add timestamps
        if task_dict.get("created_at"):
            markdown += f"**Created:** {task_dict['created_at']}\n"
        if task_dict.get("updated_at"):
            markdown += f"**Updated:** {task_dict['updated_at']}\n"

        # Add complexity information if available
        if task_dict.get("complexity"):
            markdown += f"\n## Complexity\n\n```json\n{json.dumps(task_dict['complexity'], indent=2)}\n```\n"

        # Add subtasks if available
        if task_dict.get("subtasks") and len(task_dict["subtasks"]) > 0:
            markdown += "\n## Subtasks\n\n"
            for subtask in task_dict["subtasks"]:
                status_symbol = "✓" if subtask.get("status") == "done" else "○"
                markdown += f"- [{status_symbol}] **{subtask.get('title', '')}**: {subtask.get('description', '')}\n"

        # Add tags if available
        if task_dict.get("tags") and len(task_dict["tags"]) > 0:
            markdown += f"\n**Tags:** {', '.join(task_dict['tags'])}\n"

        # Add a hidden section with the full JSON data for perfect reconstruction
        # This is commented out because it's redundant with the extra.taskinator_full_data field
        # markdown += f"\n<!-- TASKINATOR_DATA\n{json.dumps(task_dict, indent=2)}\n-->\n"

        return markdown

    @classmethod
    def _extract_description(cls, markdown: str) -> str:
        """Extract the description from the markdown.

        Args:
            markdown: Markdown description

        Returns:
            str: Description
        """
        parts = markdown.split("---", 1)
        return parts[0].strip()

    @classmethod
    def _extract_fields_from_markdown(
        cls, markdown: str, result: Dict[str, Any]
    ) -> None:
        """Extract fields from the markdown description.

        Args:
            markdown: Markdown description
            result: Dictionary to store the extracted fields
        """
        # Check if the markdown has our separator
        if "---" in markdown:
            parts = markdown.split("---", 1)
            metadata = parts[1]

            # Extract details
            if "## Details" in metadata:
                details_parts = metadata.split("## Details", 1)[1]
                if "##" in details_parts:
                    result["details"] = details_parts.split("##", 1)[0].strip()
                else:
                    result["details"] = details_parts.strip()

            # Extract test strategy
            if "## Test Strategy" in metadata:
                strategy_parts = metadata.split("## Test Strategy", 1)[1]
                if "##" in strategy_parts:
                    result["test_strategy"] = strategy_parts.split("##", 1)[0].strip()
                else:
                    result["test_strategy"] = strategy_parts.strip()

            # Extract priority and status
            priority_match = re.search(r"**Priority:** (.*)", metadata)
            if priority_match:
                result["priority"] = priority_match.group(1).strip()

            status_match = re.search(r"**Status:** (.*)", metadata)
            if status_match:
                result["status"] = status_match.group(1).strip()

            # Extract dependencies
            dependencies_match = re.search(r"**Dependencies:** (.*)", metadata)
            if dependencies_match:
                result["dependencies"] = [
                    dep.strip() for dep in dependencies_match.group(1).split(",")
                ]

            # Extract timestamps
            created_match = re.search(r"**Created:** (.*)", metadata)
            if created_match:
                result["created_at"] = created_match.group(1).strip()

            updated_match = re.search(r"**Updated:** (.*)", metadata)
            if updated_match:
                result["updated_at"] = updated_match.group(1).strip()

            # Extract complexity information
            complexity_match = re.search(
                r"## Complexity\n\n```json\n(.*)\n```", metadata, re.DOTALL
            )
            if complexity_match:
                result["complexity"] = json.loads(complexity_match.group(1))

            # Extract subtasks
            subtasks_match = re.search(r"## Subtasks\n\n(.*)", metadata, re.DOTALL)
            if subtasks_match:
                subtasks = []
                for line in subtasks_match.group(1).split("\n"):
                    match = re.match(r"- \[(.*)\] (.*)", line)
                    if match:
                        status = match.group(1).strip()
                        title = match.group(2).strip()
                        subtasks.append({"title": title, "status": status})
                result["subtasks"] = subtasks

            # Extract tags
            tags_match = re.search(r"**Tags:** (.*)", metadata)
            if tags_match:
                result["tags"] = [tag.strip() for tag in tags_match.group(1).split(",")]


def get_sync_metadata_path(tasks_dir: str) -> str:
    """Get the path to the sync metadata file.

    Args:
        tasks_dir: Path to the tasks directory

    Returns:
        str: Path to the sync metadata file
    """
    return os.path.join(tasks_dir, "nextcloud_sync_metadata.json")


def load_sync_metadata(tasks_dir: str) -> Dict[str, NextCloudSyncMetadata]:
    """Load sync metadata from file.

    Args:
        tasks_dir: Path to the tasks directory

    Returns:
        Dict[str, NextCloudSyncMetadata]: Dictionary of task ID to sync metadata
    """
    metadata_path = get_sync_metadata_path(tasks_dir)

    # If the file doesn't exist, return an empty dictionary
    if not os.path.exists(metadata_path):
        return {}

    try:
        with open(metadata_path, "r") as f:
            data = json.load(f)

        # Convert the data to NextCloudSyncMetadata objects
        result = {}
        for task_id, metadata in data.items():
            result[task_id] = NextCloudSyncMetadata.model_validate(metadata)

        return result
    except Exception as e:
        log.error(f"Error loading sync metadata: {e}")
        return {}


def save_sync_metadata(
    metadata: Dict[str, NextCloudSyncMetadata], tasks_dir: str
) -> None:
    """Save sync metadata to file.

    Args:
        metadata: Dictionary of task ID to sync metadata
        tasks_dir: Path to the tasks directory
    """
    metadata_path = get_sync_metadata_path(tasks_dir)

    try:
        # Convert the metadata to dictionaries
        data = {}
        for task_id, meta in metadata.items():
            data[task_id] = meta.model_dump()

        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(metadata_path), exist_ok=True)

        # Write to a temporary file first
        temp_path = f"{metadata_path}.tmp"
        with open(temp_path, "w") as f:
            json.dump(data, f, indent=2)

        # Rename to the final path (atomic operation)
        os.replace(temp_path, metadata_path)
    except Exception as e:
        log.error(f"Error saving sync metadata: {e}")


def get_task_sync_metadata(
    task: Union[Task, str], tasks_dir: str
) -> NextCloudSyncMetadata:
    """Get sync metadata for a task.

    Args:
        task: Task object or task ID
        tasks_dir: Path to the tasks directory

    Returns:
        NextCloudSyncMetadata: Sync metadata for the task
    """
    # Load all metadata
    all_metadata = load_sync_metadata(tasks_dir)

    # Get the task ID as a string
    task_id = str(task.id) if hasattr(task, "id") else str(task)

    # Return the metadata for this task, or a new metadata object if not found
    return all_metadata.get(task_id, NextCloudSyncMetadata(provider="nextcloud"))


def update_task_sync_metadata(
    task: Union[Task, str], metadata: NextCloudSyncMetadata, tasks_dir: str
) -> None:
    """Update sync metadata for a task.

    Args:
        task: Task object or task ID
        metadata: Sync metadata for the task
        tasks_dir: Path to the tasks directory
    """
    # Load all metadata
    all_metadata = load_sync_metadata(tasks_dir)

    # Get the task ID as a string
    task_id = str(task.id) if hasattr(task, "id") else str(task)

    # Update the metadata for this task
    all_metadata[task_id] = metadata

    # Save all metadata
    save_sync_metadata(all_metadata, tasks_dir)


def detect_changes(
    local_task: Union[Task, str], remote_task: NextCloudTask, tasks_dir: str
) -> Tuple[List[Dict[str, Any]], bool]:
    """Detect changes between local and remote tasks.

    Args:
        local_task: Local task or task ID
        remote_task: Remote task
        tasks_dir: Path to the tasks directory

    Returns:
        Tuple[List[Dict[str, Any]], bool]: List of changes and whether changes were detected
    """
    changes = []

    # Get the metadata to check if this task was previously synced
    metadata = get_task_sync_metadata(local_task, tasks_dir)

    # Skip first-time sync (when there's no sync history)
    if not metadata.last_sync:
        return changes, False

    # Get dictionaries
    if hasattr(local_task, "model_dump"):
        local_dict = local_task.model_dump()
    elif hasattr(local_task, "dict"):
        local_dict = local_task.dict()
    else:
        # If local_task is a string ID, we can't compare changes
        return changes, False

    if hasattr(remote_task, "model_dump"):
        remote_dict = remote_task.model_dump()
    elif hasattr(remote_task, "dict"):
        remote_dict = remote_dict.dict()
    else:
        # If remote_task is not a proper object, we can't compare changes
        return changes, False

    # Check if we have full task data in the remote task
    if "extra" in remote_dict and "taskinator_full_data" in remote_dict["extra"]:
        # If we have the full data, we can do a direct comparison
        remote_full_data = remote_dict["extra"]["taskinator_full_data"]

        # Compare only the fields that matter for sync
        fields_to_compare = [
            "title",
            "description",
            "status",
            "priority",
            "dependencies",
        ]

        for field in fields_to_compare:
            if field in local_dict and field in remote_full_data:
                local_value = local_dict[field]
                remote_value = remote_full_data[field]

                # Special handling for status field
                if field == "status":
                    # Normalize status values
                    status_map = {
                        "pending": "pending",
                        "in-progress": "in_progress",
                        "done": "done",
                        "blocked": "pending",
                        "deferred": "pending",
                        "cancelled": "pending",
                    }
                    local_value = status_map.get(local_value, "pending")
                    remote_value = status_map.get(remote_value, "pending")

                # Compare values
                if local_value != remote_value:
                    changes.append(
                        {
                            "field": field,
                            "local_value": local_value,
                            "remote_value": remote_value,
                        }
                    )

        return changes, len(changes) > 0

    # Normalize string values for comparison
    def normalize_string(s):
        if s is None:
            return ""
        return str(s).strip().lower()

    # Compare fields
    for local_field, remote_field in TaskFieldMapping.LOCAL_TO_REMOTE.items():
        # Special handling for dependencies
        if local_field == "dependencies":
            # Get dependencies from local task
            local_deps = set(str(dep) for dep in local_dict.get(local_field, []))

            # Get dependencies from remote task's extra metadata
            remote_deps = set()
            if remote_dict.get("extra") and "all_dependencies" in remote_dict["extra"]:
                remote_deps = set(
                    str(dep) for dep in remote_dict["extra"]["all_dependencies"]
                )

            # If dependencies are different, add a change
            if local_deps != remote_deps:
                changes.append(
                    {
                        "field": local_field,
                        "local_value": sorted(list(local_deps)),
                        "remote_value": sorted(list(remote_deps)),
                    }
                )
        # Special handling for status
        elif local_field == "status":
            # Map status values
            status_map = {
                "pending": "pending",
                "in-progress": "in_progress",
                "done": "done",
                "blocked": "pending",
                "deferred": "pending",
                "cancelled": "pending",
            }

            local_status = status_map.get(
                local_dict.get(local_field, "pending"), "pending"
            )
            remote_status = remote_dict.get(
                TaskFieldMapping.LOCAL_TO_REMOTE[local_field], "pending"
            )

            if local_status != remote_status:
                changes.append(
                    {
                        "field": local_field,
                        "local_value": local_status,
                        "remote_value": remote_status,
                    }
                )
        # Special handling for categories
        elif local_field == "categories":
            # Get regular categories (excluding dependency tags)
            local_cats = set(
                normalize_string(cat) for cat in local_dict.get(local_field, [])
            )

            # Get remote categories (excluding dependency tags)
            remote_cats = set()
            for cat in remote_dict.get(
                TaskFieldMapping.LOCAL_TO_REMOTE[local_field], []
            ):
                if not str(cat).startswith("Depends on "):
                    remote_cats.add(normalize_string(cat))

            if local_cats != remote_cats:
                changes.append(
                    {
                        "field": local_field,
                        "local_value": sorted(list(local_cats)),
                        "remote_value": sorted(list(remote_cats)),
                    }
                )
        # Regular field comparison
        elif local_field in local_dict and remote_field in remote_dict:
            local_value = local_dict[local_field]
            remote_value = remote_dict[remote_field]

            # Convert to strings for comparison if they're strings
            if isinstance(local_value, str) or isinstance(remote_value, str):
                local_value = normalize_string(local_value)
                remote_value = normalize_string(remote_value)

            # Compare values
            if local_value != remote_value:
                changes.append(
                    {
                        "field": local_field,
                        "local_value": local_value,
                        "remote_value": remote_value,
                    }
                )

    return changes, len(changes) > 0
