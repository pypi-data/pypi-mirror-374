"""
Nextcloud sync plugin implementation for Taskinator.

This module provides the Nextcloud sync plugin implementation for Taskinator.
"""

import asyncio
import logging
import os
import json
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import re

import httpx
from pydantic import BaseModel
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from dotenv import load_dotenv
from taskinator.core.task_manager import get_tasks_path, read_tasks, register_plugin, write_tasks
from taskinator.models.task import Task, TaskCollection, Subtask
from taskinator.config import Config
from taskinator.utils.task_utils import find_task_by_id

from ..plugin_base import SyncDirection, SyncStatus, SyncPlugin
from .nextcloud_client import NextCloudClient, NextCloudTask
from .nextcloud_sync import (
    NextCloudSyncMetadata,
    detect_changes,
    get_task_sync_metadata,
    update_task_sync_metadata,
)

# Set up logging
log = logging.getLogger(__name__)
console = Console()


class TaskFieldMapping:
    """
    Utility class for mapping between Taskinator tasks and Nextcloud tasks.
    """
    
    @staticmethod
    def map_local_to_remote(task: Union[Task, Subtask]) -> Dict[str, Any]:
        """
        Map a Taskinator task or subtask to a Nextcloud task.
        
        Args:
            task: The Taskinator task or subtask to map
            
        Returns:
            Dictionary containing Nextcloud task data
        """
        # Get the title and task ID
        title = task.title
        task_id = str(task.id)
        
        # For subtasks, handle the title formatting
        if isinstance(task, Subtask):
            # For subtasks, we want to keep the title as is
            # The parent-child relationship is handled by the parent_id field
            pass
        else:
            # For regular tasks, we'll only add the ID prefix on initial sync
            # If the task already has metadata, assume it's been synced before
            # and preserve whatever title it has
            if not hasattr(task, "metadata") or not task.metadata:
                # First remove any existing ID prefix that matches our pattern
                title = re.sub(r'^\[\d+(?:\.\d+)?\][ ]?', '', title)
                # Then add the ID prefix in a consistent format
                title = f"[{task.id}] {title}"
                
        description = task.description or ""

        # Include additional details in the description for all tasks
        if hasattr(task, 'details') and task.details:
            description += f"\n\nDetails:\n{task.details}"
        if hasattr(task, 'test_strategy') and task.test_strategy:
            description += f"\n\nTest Strategy:\n{task.test_strategy}"

        # Create extra data dictionary to store additional fields
        extra_data = {}
        
        # Store details and test_strategy in extra data if available
        if hasattr(task, 'details') and task.details:
            extra_data['details'] = task.details
            
        if hasattr(task, 'test_strategy') and task.test_strategy:
            extra_data['test_strategy'] = task.test_strategy
            
        task_data = {
            "title": title,
            "description": description,
            "status": TaskFieldMapping._map_status_to_remote(task.status),
            "extra": extra_data
        }
        
        # Add priority if available (subtasks may not have this)
        if hasattr(task, "priority"):
            task_data["priority"] = TaskFieldMapping._map_priority_to_remote(task.priority)
        else:
            task_data["priority"] = TaskFieldMapping._map_priority_to_remote("medium")  # Default priority
        
        # Add due_date if available
        if hasattr(task, "due_date") and getattr(task, "due_date", ""):
            task_data["due_date"] = getattr(task, "due_date", "")
            
        # Add tags if available
        if hasattr(task, "tags") and task.tags:
            task_data["tags"] = ",".join(task.tags)
        
        # Add parent_id if present
        if hasattr(task, "parent_id") and task.parent_id:
            task_data["parent_id"] = str(task.parent_id)
            
        # Details and test_strategy are now handled for all tasks above
        
        return task_data
    
    @staticmethod
    def map_remote_to_local(remote_task: Any) -> Dict[str, Any]:
        """
        Map a Nextcloud task to a Taskinator task.
        
        Args:
            remote_task: The Nextcloud task to map
            
        Returns:
            Dictionary containing Taskinator task data
        """
        # Extract task ID from title if present
        title = remote_task.title
        task_id = None
        
        # Try to extract the task ID from the title
        # Only match the specific pattern #<number>: or #<number>.<number>:
        match = re.match(r"^#(\d+(?:\.\d+)?):[ ]?(.*)", title)
        
        if match:
            task_id = match.group(1)
            # We'll keep the title as-is from Nextcloud, preserving user changes
        
        # Extract description and check for details/test_strategy markers
        description = remote_task.description or ""
        details = None
        test_strategy = None
        
        # Extract details if present
        details_match = re.search(r'\[DETAILS_START\](.*?)\[DETAILS_END\]', description, re.DOTALL)
        if details_match:
            details = details_match.group(1).strip()
            # Remove the details section from the description
            description = re.sub(r'\[DETAILS_START\].*?\[DETAILS_END\]', '', description, flags=re.DOTALL)
            
        # Extract test_strategy if present
        test_strategy_match = re.search(r'\[TEST_STRATEGY_START\](.*?)\[TEST_STRATEGY_END\]', description, re.DOTALL)
        if test_strategy_match:
            test_strategy = test_strategy_match.group(1).strip()
            # Remove the test_strategy section from the description
            description = re.sub(r'\[TEST_STRATEGY_START\].*?\[TEST_STRATEGY_END\]', '', description, flags=re.DOTALL)
            
        # Clean up any double newlines from the extraction
        description = re.sub(r'\n{3,}', '\n\n', description).strip()
        
        # Create a basic task dictionary
        task_data = {
            "title": title,  # Keep the full title from Nextcloud
            "description": description,
            "status": TaskFieldMapping._map_status_to_local(remote_task.status),
        }
        
        # Add priority if available
        if hasattr(remote_task, "priority"):
            task_data["priority"] = TaskFieldMapping._map_priority_to_local(remote_task.priority)
        
        # Add due_date if available
        if hasattr(remote_task, "due_date") and remote_task.due_date:
            task_data["due_date"] = remote_task.due_date
            
        # Add tags if available
        if hasattr(remote_task, "tags") and remote_task.tags:
            task_data["tags"] = remote_task.tags.split(",")
            
        # Add details and test_strategy if they were extracted from the description
        if details:
            task_data["details"] = details
            
        if test_strategy:
            task_data["test_strategy"] = test_strategy
        
        # Also check for details and test_strategy in the extra field
        # This takes precedence over any extracted from the description
        if hasattr(remote_task, "extra") and remote_task.extra:
            if "details" in remote_task.extra:
                task_data["details"] = remote_task.extra["details"]
                
            if "test_strategy" in remote_task.extra:
                task_data["test_strategy"] = remote_task.extra["test_strategy"]
        
        # Use the extracted task ID if available, otherwise use the remote ID
        if task_id:
            task_data["id"] = task_id
        else:
            # For subtasks, check if there's a parent ID and format the ID accordingly
            if hasattr(remote_task, "parent_id") and remote_task.parent_id:
                # This is a subtask, so we need to format the ID as parent.subtask
                # First, try to find the parent task ID from the parent_id
                parent_id = remote_task.parent_id
                
                # If we can't determine the parent ID format, use a simple numeric ID
                # Extract just the numeric part of the remote ID for the subtask part
                subtask_numeric_id = re.sub(r'[^0-9]', '', remote_task.id)
                if not subtask_numeric_id:
                    subtask_numeric_id = "1"  # Fallback
                
                # Format as parent.subtask
                task_data["id"] = f"{parent_id}.{subtask_numeric_id}"
            else:
                # For regular tasks, just use the remote ID
                task_data["id"] = remote_task.id
        
        return task_data
    
    @staticmethod
    def _map_status_to_remote(status: str) -> str:
        """
        Map a Taskinator status to a Nextcloud status.
        
        Args:
            status: The Taskinator status to map
            
        Returns:
            The corresponding Nextcloud status
        
        Args:
            status: The local status string
            
        Returns:
            The corresponding Nextcloud status string
        """
        # Normalize the status by converting to lowercase and removing any hyphens
        normalized_status = status.lower().replace('-', '')
        
        status_map = {
            "pending": "NEEDS-ACTION",
            "inprogress": "IN-PROCESS",
            "done": "COMPLETED",
        }
        
        # Use the normalized status for lookup, with a default fallback
        return status_map.get(normalized_status, "NEEDS-ACTION")
    
    @staticmethod
    def _map_status_to_local(status: str) -> str:
        """
        Map a Nextcloud status to a Taskinator status.
        
        Args:
            status: The Nextcloud status to map
            
        Returns:
            The corresponding Taskinator status
        """
        # Normalize status to uppercase for consistent mapping from Nextcloud
        if not status:
            return "pending"
            
        # Check for "done" or "completed" in any case
        if status.lower() == "done" or status.lower() == "completed":
            return "done"
            
        status = status.upper()
        status_map = {
            "NEEDS-ACTION": "pending",
            "IN-PROCESS": "in-progress",
            "COMPLETED": "done",
            "CANCELLED": "cancelled",
        }
        return status_map.get(status, "pending")
    
    @staticmethod
    def _map_priority_to_remote(priority: str) -> str:
        """
        Map a Taskinator priority to a Nextcloud priority.
        
        Args:
            priority: The Taskinator priority to map
            
        Returns:
            The corresponding Nextcloud priority
        """
        priority_map = {
            "low": "low",
            "medium": "medium",
            "high": "high",
        }
        return priority_map.get(priority, "medium")
    
    @staticmethod
    def _map_priority_to_local(priority: str) -> str:
        """
        Map a Nextcloud priority to a Taskinator priority.
        
        Args:
            priority: The Nextcloud priority to map
            
        Returns:
            The corresponding Taskinator priority
        """
        priority_map = {
            "low": "low",
            "medium": "medium",
            "high": "high",
        }
        return priority_map.get(priority, "medium")


class SyncStatus(str, Enum):
    """Sync status for a task."""
    SYNCED = "synced"
    PENDING = "pending"
    CONFLICT = "conflict"


class NextCloudSyncMetadata(BaseModel):
    """Metadata for a task synced with Nextcloud."""
    provider: str
    remote_id: str
    last_sync: str
    sync_status: SyncStatus
    last_local_state: Optional[str] = None


class TaskSyncModel(BaseModel):
    """Pydantic model for comparing task changes during sync."""
    title: str
    description: str = ""
    status: str
    due_date: Optional[str] = None
    priority: Optional[Union[int, str]] = None
    tags: List[str] = []
    details: Optional[str] = None
    test_strategy: Optional[str] = None
    
    @classmethod
    def from_task(cls, task: Union[Task, Subtask]) -> "TaskSyncModel":
        """Create a TaskSyncModel from a Task or Subtask."""
        return cls(
            title=task.title,
            description=getattr(task, "description", ""),
            status=task.status,
            due_date=getattr(task, "due_date", None),
            priority=getattr(task, "priority", None),
            tags=getattr(task, "tags", []),
            details=getattr(task, "details", None),
            test_strategy=getattr(task, "test_strategy", None)
        )
    
    @classmethod
    def from_remote(cls, remote_task: Any) -> "TaskSyncModel":
        """Create a TaskSyncModel from a remote task."""
        task_data = TaskFieldMapping.map_remote_to_local(remote_task)
        return cls(
            title=task_data["title"],
            description=task_data.get("description", ""),
            status=task_data["status"],
            due_date=task_data.get("due_date"),
            priority=task_data.get("priority"),
            tags=task_data.get("tags", []),
            details=task_data.get("details"),
            test_strategy=task_data.get("test_strategy")
        )
    
    def has_changes_from(self, other: "TaskSyncModel") -> bool:
        """Check if this model has changes compared to another model."""
        for field in self.__fields__:
            self_value = getattr(self, field)
            other_value = getattr(other, field)
            
            # Skip title comparison entirely - we'll respect whatever title is in each system
            if field == "title":
                continue
            
            # Handle priority comparison specially
            if field == "priority":
                # Convert to string for comparison if either is a string
                if isinstance(self_value, str) or isinstance(other_value, str):
                    self_value = str(self_value) if self_value is not None else None
                    other_value = str(other_value) if other_value is not None else None
            
            if self_value != other_value:
                return True
        return False
    
    def get_diff_from(self, other: "TaskSyncModel") -> Dict[str, Tuple[Any, Any]]:
        """Get differences between this model and another model."""
        diff = {}
        for field in self.__fields__:
            self_value = getattr(self, field)
            other_value = getattr(other, field)
            
            # Skip title comparison entirely - we'll respect whatever title is in each system
            if field == "title":
                continue
            
            # Handle priority comparison specially
            if field == "priority":
                # Convert to string for comparison if either is a string
                if isinstance(self_value, str) or isinstance(other_value, str):
                    self_value_str = str(self_value) if self_value is not None else None
                    other_value_str = str(other_value) if other_value is not None else None
                    if self_value_str != other_value_str:
                        diff[field] = (other_value, self_value)
                elif self_value != other_value:
                    diff[field] = (other_value, self_value)
            elif self_value != other_value:
                diff[field] = (other_value, self_value)
        return diff


class NextCloudSyncPlugin (SyncPlugin):
    """
    Nextcloud sync plugin for Taskinator.
    
    This plugin provides bidirectional synchronization between Taskinator tasks and
    Nextcloud tasks/calendars. It ensures lossless synchronization, meaning that tasks
    can be synced to Nextcloud, deleted locally, and then restored to their original
    state with a sync pull.
    
    Key features:
    - Bidirectional sync (push, pull, or both)
    - Lossless task serialization using Pydantic models
    - Conflict detection and resolution
    - Configuration via environment variables or interactive prompts
    
    Usage:
        taskinator sync:setup nextcloud  # Configure the plugin
        taskinator sync                  # Sync tasks bidirectionally
        taskinator sync:push             # Push local tasks to Nextcloud
        taskinator sync:pull             # Pull remote tasks from Nextcloud
        taskinator sync:status           # Check sync status
        taskinator sync resolve          # Resolve sync conflicts
    """

    name = "sync"
    provider = "nextcloud"
    
    def __init__(self):
        """Initialize the NextCloudSyncPlugin ."""
        self.client = None
        self.host = None
        self.username = None
        self.password = None
        self.app_token = None
        self.calendar_id = None
        self.project_directory = None
        self.debug = False
        
        # Register plugin commands
        register_plugin("sync", self.sync_command)
        register_plugin("sync_status", self.status_command)
        register_plugin("sync_setup", self.setup_command)
        register_plugin("sync_resolve", self.resolve_command)
        register_plugin("sync_push", self.push_command)
        register_plugin("sync_pull", self.pull_command)
        register_plugin("sync_reset_metadata", self.reset_sync_metadata_command)

    async def _get_client(self, project_directory: str = None) -> Optional[NextCloudClient]:
        """
        Connect to Nextcloud server using the configuration.
        
        Args:
            project_directory: The project directory to load configuration from
            
        Returns:
            The Nextcloud client if connection successful, None otherwise
        """
        try:
            # Load configuration
            config = Config(project_directory)

            # Get Nextcloud configuration
            host = config.get("sync.nextcloud.host")
            username = config.get("sync.nextcloud.username")
            password = config.get("sync.nextcloud.password")
            app_token = config.get("sync.nextcloud.app_token")
            calendar_id = config.get("sync.nextcloud.calendar_id", "personal")

            # If password or app_token is not in config, try to get from environment variables
            if not password and not app_token:
                # Load environment variables
                load_dotenv(os.path.join(project_directory, ".env"))
                password = os.environ.get("NEXTCLOUD_PASSWORD")
                app_token = os.environ.get("NEXTCLOUD_APP_TOKEN")

            if not host or not username or (not password and not app_token):
                console.print("[ERROR] Nextcloud configuration is incomplete", style="bold red")
                return None

            # Create client
            client = NextCloudClient(
                base_url=host,
                username=username,
                password=password,
                app_token=app_token,
                calendar_id=calendar_id,
            )

            return client
        except Exception as e:
            console.print(f"[ERROR] Failed to connect to Nextcloud: {str(e)}", style="bold red")
            return None

    async def set_config(self, project_directory: str, config_dict: Dict[str, Any]) -> None:
        """
        Save the Nextcloud configuration.
        
        Args:
            project_directory: The project directory
            config_dict: Dictionary containing configuration values
        """
        try:
            console.print("[INFO] Saving Nextcloud configuration...")
            
            config = Config(project_directory)
            
            # Save configuration to config file
            for key, value in config_dict.items():
                if value:  # Only save non-empty values
                    config.set(f"sync.nextcloud.{key}", value)
            
            config.save()
            
            # Update instance variables
            self.host = config_dict.get("host")
            self.username = config_dict.get("username")
            self.password = config_dict.get("password")
            self.app_token = config_dict.get("app_token")
            self.calendar_id = config_dict.get("calendar_id", "personal")
            
            console.print("[SUCCESS] Nextcloud configuration saved", style="bold green")
        except Exception as e:
            console.print(f"Error saving Nextcloud configuration: {str(e)}")
            raise

    async def setup(self, project_directory: str, non_interactive: bool = False, **kwargs) -> bool:
        """
        Set up the Nextcloud sync plugin.
        
        Args:
            project_directory: The project directory
            non_interactive: Whether to run in non-interactive mode (use environment variables only)
            **kwargs: Additional parameters
            
        Returns:
            True if setup was successful, False otherwise
        """
        try:
            console.print("[INFO] Setting up Nextcloud sync...")
            
            # Store the project directory
            self.project_directory = project_directory
            
            # Load environment variables
            load_dotenv(os.path.join(project_directory, ".env"))
            
            # Get configuration from environment variables or kwargs
            self.host = kwargs.get("host") or os.environ.get("NEXTCLOUD_HOST")
            self.username = kwargs.get("username") or os.environ.get("NEXTCLOUD_USERNAME")
            self.password = kwargs.get("password") or os.environ.get("NEXTCLOUD_PASSWORD")
            self.app_token = kwargs.get("app_token") or os.environ.get("NEXTCLOUD_APP_TOKEN")
            self.calendar_id = kwargs.get("calendar_id") or os.environ.get("NEXTCLOUD_CALENDAR_ID", "personal")
            
            # If any required configuration is missing and we're in interactive mode, prompt for it
            if not non_interactive:
                if not self.host:
                    self.host = Prompt.ask("Enter Nextcloud host URL")
                
                if not self.username:
                    self.username = Prompt.ask("Enter Nextcloud username")
                
                if not self.password and not self.app_token:
                    self.password = Prompt.ask("Enter Nextcloud password", password=True)
            
            # In non-interactive mode, ensure we have all required configuration
            elif not self.host or not self.username or (not self.password and not self.app_token):
                console.print("[ERROR] Required configuration missing and running in non-interactive mode. Please set NEXTCLOUD_HOST, NEXTCLOUD_USERNAME, and either NEXTCLOUD_PASSWORD or NEXTCLOUD_APP_TOKEN environment variables.", style="bold red")
                return False
            
            # Save configuration
            console.print("[INFO] Saving Nextcloud configuration...")
            config = Config(project_directory)
            
            # Set each configuration value individually
            config.set("sync.nextcloud.host", self.host)
            config.set("sync.nextcloud.username", self.username)
            config.set("sync.nextcloud.calendar_id", self.calendar_id)
            
            # Save password or app_token to configuration
            if self.password:
                config.set("sync.nextcloud.password", self.password)
            elif self.app_token:
                config.set("sync.nextcloud.app_token", self.app_token)
            
            # Save the configuration
            config.save()
            
            console.print("[SUCCESS] Nextcloud configuration saved", style="bold green")
            
            # Test connection
            client = await self._get_client(project_directory)
            if client:
                self.client = client
                console.print("[SUCCESS] Connected to Nextcloud successfully", style="bold green")
                return True
            else:
                console.print("[ERROR] Failed to connect to Nextcloud", style="bold red")
                return False
        except Exception as e:
            console.print(f"[ERROR] Failed to set up Nextcloud sync: {str(e)}", style="bold red")
            return False

    async def sync(
        self, project_directory: str, direction: str = "bidirectional", force: bool = False, debug: bool = False, **kwargs
    ) -> Dict[str, Any]:
        """
        Synchronize tasks with Nextcloud.
        
        Args:
            project_directory: The project directory
            direction: Sync direction (push, pull, or bidirectional)
            force: Force update of all tasks, even if no changes detected
            debug: Enable debug logging
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing synchronization results
        """
        try:
            # Enable debug mode if requested
            self.debug = debug
            
            # Store the project directory
            self.project_directory = project_directory
            
            # Map direction string to enum
            direction_map = {
                "push": SyncDirection.LOCAL_TO_REMOTE,
                "pull": SyncDirection.REMOTE_TO_LOCAL,
                "bidirectional": SyncDirection.BIDIRECTIONAL,
            }
            sync_direction = direction_map.get(direction, SyncDirection.BIDIRECTIONAL)
            
            # Connect to Nextcloud
            if not self.client:
                self.client = await self._get_client(project_directory)

            if not self.client:
                return {
                    "status": "error",
                    "message": "Failed to connect to Nextcloud",
                    "errors": 1,
                }
            
            # Get tasks
            tasks_path = get_tasks_path()
            
            # Check if tasks file exists
            if not os.path.exists(tasks_path):
                # In recovery scenario, create an empty tasks file
                if sync_direction in [SyncDirection.REMOTE_TO_LOCAL, SyncDirection.BIDIRECTIONAL]:
                    # Create the directory if it doesn't exist
                    tasks_dir = os.path.dirname(tasks_path)
                    os.makedirs(tasks_dir, exist_ok=True)
                    
                    # Create an empty task collection
                    tasks = TaskCollection(tasks=[])
                    write_tasks(tasks_path, tasks)
                    console.print(f"[INFO] Created empty tasks file at {tasks_path} for recovery", style="bold blue")
                else:
                    console.print(f"[ERROR] Tasks file not found: {tasks_path}", style="bold red")
                    return {
                        "status": "error",
                        "message": f"Tasks file not found: {tasks_path}",
                        "errors": 1,
                    }
            
            # Read tasks from file
            try:
                tasks = read_tasks(tasks_path)
            except Exception as e:
                console.print(f"[ERROR] Error reading tasks from {tasks_path}: {str(e)}", style="bold red")
                return {
                    "status": "error",
                    "message": f"Error reading tasks from {tasks_path}: {str(e)}",
                    "errors": 1,
                }
            
            # Count total tasks including subtasks
            total_tasks = len(tasks.tasks)
            for task in tasks.tasks:
                if hasattr(task, "subtasks") and task.subtasks:
                    total_tasks += len(task.subtasks)
            
            # Initialize results
            results = {
                "total": total_tasks,
                "synced": 0,
                "created": 0,
                "updated": 0,
                "deleted": 0,
                "conflicts": 0,
                "errors": 0,
            }
            
            # Sync tasks based on direction
            # Always pull before push to avoid overwriting remote changes
            if sync_direction in [SyncDirection.REMOTE_TO_LOCAL, SyncDirection.BIDIRECTIONAL]:
                # Pull tasks from Nextcloud
                console.print("[INFO] Pulling tasks from Nextcloud...", style="bold blue")
                pull_results = await self._pull_tasks(tasks, tasks_path, force=force)
                # Store the pull results separately
                pull_metrics = {
                    "pull_synced": pull_results.get("synced", 0),
                    "pull_created": pull_results.get("created", 0),
                    "pull_updated": pull_results.get("updated", 0),
                    "pull_deleted": pull_results.get("deleted", 0),
                    "pull_conflicts": pull_results.get("conflicts", 0),
                    "pull_errors": pull_results.get("errors", 0),
                }
                
                # Update only the error count in the main results
                results["errors"] += pull_results.get("errors", 0)
            
            if sync_direction in [SyncDirection.LOCAL_TO_REMOTE, SyncDirection.BIDIRECTIONAL]:
                # Push tasks to Nextcloud
                console.print("[INFO] Pushing tasks to Nextcloud...", style="bold blue")
                push_results = await self._push_tasks(tasks, tasks_path, force=force)
                
                # Update the main results with push results
                results["synced"] += push_results.get("synced", 0)
                results["created"] += push_results.get("created", 0)
                results["updated"] += push_results.get("updated", 0)
                results["deleted"] += push_results.get("deleted", 0)
                results["conflicts"] += push_results.get("conflicts", 0)
                results["errors"] += push_results.get("errors", 0)
            
            # If we did both pull and push, add the pull metrics to the results for reporting
            if sync_direction == SyncDirection.BIDIRECTIONAL:
                results["pull_synced"] = pull_metrics.get("pull_synced", 0)
                results["pull_created"] = pull_metrics.get("pull_created", 0)
                results["pull_updated"] = pull_metrics.get("pull_updated", 0)
            
            return results
        except Exception as e:
            console.print(f"[ERROR] Error in sync: {str(e)}", style="bold red")
            return {
                "status": "error",
                "message": str(e),
                "errors": 1,
                "total": 0,
                "synced": 0,
                "created": 0,
                "updated": 0,
                "deleted": 0,
                "conflicts": 0,
            }

    async def get_status(
        self, project_directory: str, verbose: bool = False, **kwargs
    ) -> Dict[str, Any]:
        """Get synchronization status.

        Args:
            project_directory: The project directory
            verbose: Whether to include detailed information
            **kwargs: Additional parameters

        Returns:
            Dict[str, Any]: Synchronization status
        """
        try:
            # Store the project directory
            self.project_directory = project_directory
            
            # Connect to Nextcloud
            if not self.client:
                self.client = await self._get_client(project_directory)

            if not self.client:
                return {
                    "status": "error",
                    "message": "Failed to connect to Nextcloud",
                }
            
            # Get tasks
            tasks_path = get_tasks_path()
            if not os.path.exists(tasks_path):
                return {
                    "status": "error",
                    "message": f"Tasks file not found: {tasks_path}",
                }
            
            tasks = read_tasks(tasks_path)
            
            # Count tasks by sync status
            status_counts = {
                "total": len(tasks.tasks),
                "synced": 0,
                "pending": 0,
                "conflict": 0,
                "error": 0,
                "not_synced": 0,
            }
            
            # Check sync status for each task
            for task in tasks.tasks:
                metadata = self.get_task_metadata(task)
                if metadata:
                    if metadata.sync_status == SyncStatus.SYNCED:
                        status_counts["synced"] += 1
                    elif metadata.sync_status == SyncStatus.PENDING:
                        status_counts["pending"] += 1
                    elif metadata.sync_status == SyncStatus.CONFLICT:
                        status_counts["conflict"] += 1
                    elif metadata.sync_status == SyncStatus.ERROR:
                        status_counts["error"] += 1
                else:
                    status_counts["not_synced"] += 1
            
            # If verbose, add information about the Nextcloud connection
            if verbose:
                status_counts["connection"] = {
                    "host": self.host,
                    "username": self.username,
                    "calendar_id": self.calendar_id,
                    "connected": self.client is not None,
                }
            
            return status_counts
        except Exception as e:
            console.print(f"[ERROR] Failed to get sync status: {str(e)}", style="bold red")
            return {
                "status": "error",
                "message": str(e),
            }

    async def resolve_conflicts(
        self, project_directory: str, task_id: Optional[str] = None, resolution: str = "local", **kwargs
    ) -> Dict[str, Any]:
        """
        Resolve synchronization conflicts.

        Args:
            project_directory: The project directory
            task_id: Optional task ID to resolve conflicts for
            resolution: Resolution strategy (local, remote, or interactive)
            **kwargs: Additional parameters

        Returns:
            Dict[str, Any]: Resolution results
        """
        try:
            # Store the project directory
            self.project_directory = project_directory
            
            # Get tasks
            tasks_path = get_tasks_path()
            if not os.path.exists(tasks_path):
                console.print(f"[ERROR] Tasks file not found: {tasks_path}", style="bold red")
                return {
                    "status": "error",
                    "message": f"Tasks file not found: {tasks_path}",
                    "resolved": 0,
                    "failed": 0,
                    "total": 0,
                }
            
            # Read tasks from file
            try:
                tasks = read_tasks(tasks_path)
            except Exception as e:
                console.print(f"[ERROR] Error reading tasks from {tasks_path}: {str(e)}", style="bold red")
                return {
                    "status": "error",
                    "message": f"Error reading tasks from {tasks_path}: {str(e)}",
                    "resolved": 0,
                    "failed": 0,
                    "total": 0,
                }
            
            # Initialize results
            results = {
                "resolved": 0,
                "failed": 0,
                "total": 0,
            }
            
            # Find tasks with conflicts
            conflicts = []
            for task in tasks.tasks:
                metadata = self.get_task_metadata(task)
                if metadata and metadata.sync_status == SyncStatus.CONFLICT:
                    if task_id is None or str(task.id) == str(task_id):
                        conflicts.append(task)
            
            results["total"] = len(conflicts)
            
            if not conflicts:
                console.print("[INFO] No conflicts to resolve", style="bold blue")
                return results
            
            # Resolve conflicts
            for task in conflicts:
                try:
                    metadata = self.get_task_metadata(task)
                    
                    if resolution == "local":
                        # Use local version
                        task_data = TaskFieldMapping.map_local_to_remote(task)
                        updated_task = await self.client.update_task(metadata.remote_id, task_data)
                        
                        if updated_task:
                            metadata.sync_status = SyncStatus.SYNCED
                            metadata.last_sync = datetime.now().isoformat()
                            metadata.last_local_state = TaskSyncModel.from_task(task).json()
                            self.update_task_metadata(task, metadata)
                            results["resolved"] += 1
                        else:
                            results["failed"] += 1
                    elif resolution == "remote":
                        # Use remote version
                        remote_task = await self.client.get_task(metadata.remote_id)
                        
                        if remote_task:
                            task_data = TaskFieldMapping.map_remote_to_local(remote_task)
                            
                            # Update task fields
                            for key, value in task_data.items():
                                if key != "id":  # Don't change the ID
                                    setattr(task, key, value)
                            
                            metadata.sync_status = SyncStatus.SYNCED
                            metadata.last_sync = datetime.now().isoformat()
                            metadata.last_local_state = TaskSyncModel.from_task(task).json()
                            self.update_task_metadata(task, metadata)
                            results["resolved"] += 1
                        else:
                            results["failed"] += 1
                    else:
                        # Interactive resolution not implemented yet
                        console.print(f"[WARNING] Interactive resolution not implemented yet, using local version", style="bold yellow")
                        
                        # Use local version
                        task_data = TaskFieldMapping.map_local_to_remote(task)
                        updated_task = await self.client.update_task(metadata.remote_id, task_data)
                        
                        if updated_task:
                            metadata.sync_status = SyncStatus.SYNCED
                            metadata.last_sync = datetime.now().isoformat()
                            metadata.last_local_state = TaskSyncModel.from_task(task).json()
                            self.update_task_metadata(task, metadata)
                            results["resolved"] += 1
                        else:
                            results["failed"] += 1
                except Exception as e:
                    console.print(f"[ERROR] Error resolving conflict for task {task.id}: {str(e)}", style="bold red")
                    results["failed"] += 1
            
            # Save tasks to file
            write_tasks(tasks_path, tasks)
            
            return results
        except Exception as e:
            console.print(f"[ERROR] Error resolving conflicts: {str(e)}", style="bold red")
            return {
                "resolved": 0,
                "failed": 0,
                "total": 0,
            }

    async def _push_tasks(self, tasks: TaskCollection, tasks_path: str, force: bool = False) -> Dict[str, Any]:
        """
        Push tasks to Nextcloud.
        
        Args:
            tasks: The task collection to push
            tasks_path: Path to the tasks.json file
            force: Force update of all tasks, even if no changes detected
            
        Returns:
            Dictionary containing push results
        """
        results = {
            "created": 0,
            "updated": 0,
            "synced": 0,
            "errors": 0,
        }
        
        try:
            # Get all remote tasks
            remote_tasks = await self.client.get_tasks()
            remote_tasks_by_id = {task.id: task for task in remote_tasks}
            
            # Get the tasks directory
            tasks_dir = os.path.dirname(tasks_path)
            
            # Create a mapping of remote IDs to task IDs
            remote_id_to_task_id = {}
            task_id_to_remote_id = {}
            
            for task in tasks.tasks:
                metadata = self.get_task_metadata(task)
                if metadata and metadata.remote_id:
                    remote_id_to_task_id[metadata.remote_id] = task.id
                    task_id_to_remote_id[str(task.id)] = metadata.remote_id
            
            # First push all parent tasks to Nextcloud
            parent_tasks = [task for task in tasks.tasks if not hasattr(task, "parent_id") or not task.parent_id]
            for task in parent_tasks:
                try:
                    # Get task metadata
                    metadata = self.get_task_metadata(task)
                    
                    # Check if the task has been synced before
                    if metadata and metadata.remote_id:
                        # Check if the remote task still exists
                        if metadata.remote_id in remote_tasks_by_id:
                            # Check if task has changed since last sync
                            task_changed = force
                            
                            # Check if status has changed
                            remote_task = remote_tasks_by_id.get(metadata.remote_id)
                            if remote_task:
                                remote_status = TaskFieldMapping._map_status_to_local(remote_task.status)
                                if task.status != remote_status:
                                    task_changed = True
                                    console.print(f"[INFO] Task {task.id} status changed from {remote_status} to {task.status}", style="bold blue")
                            
                            if task_changed:
                                # Update existing task
                                task_data = TaskFieldMapping.map_local_to_remote(task)
                                updated_task = await self.client.update_task(metadata.remote_id, task_data)
                                
                                if updated_task:
                                    # Update metadata
                                    metadata.last_sync = datetime.now().isoformat()
                                    metadata.sync_status = SyncStatus.SYNCED
                                    metadata.last_local_state = TaskSyncModel.from_task(task).json()
                                    self.update_task_metadata(task, metadata)
                                    results["updated"] += 1
                                    # Force the task to be marked as updated in the results
                                    if "synced" in results and results["synced"] > 0:
                                        results["synced"] -= 1
                                else:
                                    results["errors"] += 1
                            else:
                                # Task already synced and hasn't changed
                                results["synced"] += 1
                        else:
                            # Create new task (remote was deleted)
                            task_data = TaskFieldMapping.map_local_to_remote(task)
                            new_task = await self.client.create_task(task_data)
                            
                            if new_task:
                                # Update metadata
                                metadata.remote_id = new_task.id
                                metadata.last_sync = datetime.now().isoformat()
                                metadata.sync_status = SyncStatus.SYNCED
                                metadata.last_local_state = TaskSyncModel.from_task(task).json()
                                self.update_task_metadata(task, metadata)
                                task_id_to_remote_id[str(task.id)] = new_task.id
                                results["created"] += 1
                            else:
                                results["errors"] += 1
                    else:
                        # Create new task (never synced before)
                        task_data = TaskFieldMapping.map_local_to_remote(task)
                        new_task = await self.client.create_task(task_data)
                        
                        if new_task:
                            # Create metadata
                            new_metadata = NextCloudSyncMetadata(
                                provider="nextcloud",
                                remote_id=new_task.id,
                                last_sync=datetime.now().isoformat(),
                                sync_status=SyncStatus.SYNCED,
                            )
                            new_metadata.last_local_state = TaskSyncModel.from_task(task).json()
                            self.update_task_metadata(task, new_metadata)
                            task_id_to_remote_id[str(task.id)] = new_task.id
                            results["created"] += 1
                        else:
                            results["errors"] += 1
                except Exception as e:
                    # Check if this is a "task not found" error for a completed task
                    if "Task with ID" in str(e) and "not found" in str(e) and task.status == "done":
                        console.print(f"[INFO] Task {task.id} is completed and no longer exists in Nextcloud - this is normal", style="bold blue")
                        # Update metadata to mark it as synced
                        if metadata:
                            metadata.last_sync = datetime.now().isoformat()
                            metadata.sync_status = SyncStatus.SYNCED
                            metadata.last_local_state = TaskSyncModel.from_task(task).json()
                            self.update_task_metadata(task, metadata)
                        results["synced"] += 1
                    else:
                        console.print(f"[ERROR] Error pushing task {task.id}: {str(e)}", style="bold red")
                        results["errors"] += 1
            
            
            # Now push all subtasks
            for task in tasks.tasks:
                
                if hasattr(task, "parent_id") and task.parent_id:
                    try:
                        # Get parent's remote ID
                        parent_id = str(task.parent_id)
                        parent_remote_id = task_id_to_remote_id.get(parent_id)
                        
                        # Debug: Print parent ID and remote ID mapping
                        console.print(f"[DEBUG] Subtask {task.id} - Parent ID: {parent_id}, Parent Remote ID: {parent_remote_id}", style="bold blue")
                        console.print(f"[DEBUG] task_id_to_remote_id mapping: {task_id_to_remote_id}", style="bold blue")
                        
                        if not parent_remote_id:
                            console.print(f"[WARNING] Cannot push subtask {task.id} - parent task {task.parent_id} not synced", style="bold yellow")
                            results["errors"] += 1
                            continue
                        
                        # Get task metadata
                        metadata = self.get_task_metadata(task)
                        subtask_id = task.id
                        
                        # Create new subtask (never synced before or metadata missing)
                        if not metadata:
                            # Create new subtask
                            task_data = TaskFieldMapping.map_local_to_remote(task)
                            # Set parent_id in the task data
                            task_data["parent_id"] = parent_remote_id
                            
                            try:
                                new_task = await self.client.create_task(task_data)
                                
                                if new_task:
                                    # Create metadata
                                    new_metadata = NextCloudSyncMetadata(
                                        provider="nextcloud",
                                        remote_id=new_task.id,
                                        last_sync=datetime.now().isoformat(),
                                        sync_status=SyncStatus.SYNCED,
                                    )
                                    new_metadata.last_local_state = TaskSyncModel.from_task(task).json()
                                    self.update_task_metadata(task, new_metadata)
                                    task_id_to_remote_id[str(task.id)] = new_task.id
                                    results["created"] += 1
                                else:
                                    results["errors"] += 1
                            except Exception as e:
                                console.print(f"[ERROR] Error pushing subtask {task.id}: {str(e)}", style="bold red")
                                results["errors"] += 1
                        # Check if the subtask has been synced before
                        elif metadata.remote_id:
                            # Check if the remote task still exists
                            if metadata.remote_id in remote_tasks_by_id:
                                # Check if task has changed since last sync
                                task_changed = force
                                
                                # Check if status has changed
                                remote_task = remote_tasks_by_id.get(metadata.remote_id)
                                if remote_task:
                                    remote_status = TaskFieldMapping._map_status_to_local(remote_task.status)
                                    if task.status != remote_status:
                                        task_changed = True
                                
                                if task_changed:
                                    # Update existing subtask
                                    task_data = TaskFieldMapping.map_local_to_remote(task)
                                    # Set parent_id in the task data
                                    task_data["parent_id"] = parent_remote_id
                                    updated_task = await self.client.update_task(metadata.remote_id, task_data)
                                    
                                    if updated_task:
                                        # Update metadata
                                        metadata.last_sync = datetime.now().isoformat()
                                        metadata.sync_status = SyncStatus.SYNCED
                                        metadata.last_local_state = TaskSyncModel.from_task(task).json()
                                        self.update_task_metadata(task, metadata)
                                        results["updated"] += 1
                                    else:
                                        results["errors"] += 1
                                else:
                                    # Subtask already synced and hasn't changed
                                    results["synced"] += 1
                            else:
                                # Create new subtask (remote was deleted)
                                task_data = TaskFieldMapping.map_local_to_remote(task)
                                # Set parent_id in the task data
                                task_data["parent_id"] = parent_remote_id
                                new_task = await self.client.create_task(task_data)
                                
                                if new_task:
                                    # Update metadata
                                    metadata.remote_id = new_task.id
                                    metadata.last_sync = datetime.now().isoformat()
                                    metadata.sync_status = SyncStatus.SYNCED
                                    metadata.last_local_state = TaskSyncModel.from_task(task).json()
                                    self.update_task_metadata(task, metadata)
                                    task_id_to_remote_id[str(task.id)] = new_task.id
                                    results["created"] += 1
                                else:
                                    results["errors"] += 1
                    except Exception as e:
                        console.print(f"[ERROR] Error pushing subtask {subtask_id}: {str(e)}", style="bold red")
                        results["errors"] += 1
                        # Even if there's an error, preserve the local status
                        # This ensures that completed subtasks stay completed locally
                        continue
            # Process subtasks directly attached to tasks
            for task in tasks.tasks:
                if hasattr(task, "subtasks") and task.subtasks:
                    # Get task remote ID
                    task_remote_id = task_id_to_remote_id.get(str(task.id))
                    if not task_remote_id:
                        console.print(f"[WARNING] Parent task {task.id} not synced, skipping its subtasks", style="bold yellow")
                        continue
                    
                    for subtask in task.subtasks:
                        try:
                            # Get subtask metadata
                            subtask_id = str(subtask.id)
                            metadata = self.get_task_metadata(subtask)
                            
                            # Create subtask data with parent ID
                            subtask_data = TaskFieldMapping.map_local_to_remote(subtask)
                            # Ensure parent_id is set correctly
                            subtask_data["parent_id"] = task_remote_id
                            
                            # If no metadata exists, create a new subtask in Nextcloud
                            if not metadata:
                                # Create new subtask
                                new_task = await self.client.create_task(subtask_data)
                                
                                if new_task:
                                    # Create metadata
                                    new_metadata = NextCloudSyncMetadata(
                                        provider="nextcloud",
                                        remote_id=new_task.id,
                                        last_sync=datetime.now().isoformat(),
                                        sync_status=SyncStatus.SYNCED,
                                    )
                                    new_metadata.last_local_state = TaskSyncModel.from_task(subtask).json()
                                    self.update_task_metadata(subtask, new_metadata)
                                    task_id_to_remote_id[subtask_id] = new_task.id
                                    results["created"] += 1
                                else:
                                    results["errors"] += 1
                                continue
                            
                            # Check if the subtask exists in Nextcloud
                            subtask_remote_id = metadata.remote_id
                            if not subtask_remote_id or subtask_remote_id not in remote_tasks_by_id:
                                # If the subtask is completed, it's normal for it to not exist in Nextcloud
                                # In this case, we don't need to create a new one or count it as an error
                                if subtask.status == "done":
                                    log.info(f"Subtask {subtask.id} is completed and no longer exists in Nextcloud - this is normal")
                                    continue
                                
                                # If the subtask is not completed, create a new one in Nextcloud
                                try:
                                    await self._create_remote_subtask(subtask, task)
                                    results["created"] += 1
                                except Exception as e:
                                    log.error(f"Error creating subtask {subtask.id}: {e}")
                                    results["errors"] += 1
                                    continue
                            else:
                                # Check if task has changed since last sync
                                task_changed = force
                                
                                # Check if status has changed
                                remote_task = remote_tasks_by_id.get(metadata.remote_id)
                                if remote_task:
                                    remote_status = TaskFieldMapping._map_status_to_local(remote_task.status)
                                    if task.status != remote_status:
                                        task_changed = True
                                        console.print(f"[INFO] Task {subtask.id} status changed from {remote_status} to {subtask.status}", style="bold blue")
                                
                                if task_changed:
                                    # Update existing task
                                    updated_subtask = await self.client.update_task(metadata.remote_id, subtask_data)
                                    
                                    if updated_subtask:
                                        # Update metadata
                                        metadata.last_sync = datetime.now().isoformat()
                                        metadata.sync_status = SyncStatus.SYNCED
                                        metadata.last_local_state = TaskSyncModel.from_task(subtask).json()
                                        self.update_task_metadata(subtask, metadata)
                                        results["updated"] += 1
                                        # Force the task to be marked as updated in the results
                                        if "synced" in results and results["synced"] > 0:
                                            results["synced"] -= 1
                                    else:
                                        results["errors"] += 1
                                else:
                                    # Task already synced and hasn't changed
                                    results["synced"] += 1
                        except Exception as e:
                            console.print(f"[ERROR] Error pushing subtask {subtask_id}: {str(e)}", style="bold red")
                            results["errors"] += 1
                            # Even if there's an error, preserve the local status
                            # This ensures that completed subtasks stay completed locally
                            continue
            
            # Save tasks to file
            write_tasks(tasks_path, tasks)
            
            return results
        except Exception as e:
            console.print(f"[ERROR] Error in _push_tasks: {str(e)}", style="bold red")
            return {
                "created": 0,
                "updated": 0,
                "synced": 0,
                "errors": 1,
            }
    
    async def _pull_tasks(self, tasks: TaskCollection, tasks_path: str, force: bool = False) -> Dict[str, Any]:
        """
        Pull tasks from Nextcloud.
        
        Args:
            tasks: The task collection to update
            tasks_path: Path to the tasks.json file
            force: Force update of all tasks, even if no changes detected
            
        Returns:
            Dictionary containing pull results
        """
        results = {
            "created": 0,
            "updated": 0,
            "synced": 0,
            "errors": 0,
            "conflicts": 0,
        }
        
        try:
            # Get client
            client = await self._get_client(self.project_directory)
            if not client:
                console.print("[ERROR] Failed to connect to Nextcloud", style="bold red")
                return results
                
            # Get remote tasks
            remote_tasks = await client.get_tasks()
            if not remote_tasks:
                console.print("[INFO] No tasks found in Nextcloud")
                return results
                
            # Process remote tasks
            for remote_task in remote_tasks:
                try:
                    # Skip tasks without an ID
                    if not hasattr(remote_task, "id") or not remote_task.id:
                        continue
                        
                    # Check if this is a subtask
                    is_subtask = hasattr(remote_task, "parent_id") and remote_task.parent_id
                    
                    if not is_subtask:
                        # This is a main task
                        
                        # Map remote task to local format
                        task_data = TaskFieldMapping.map_remote_to_local(remote_task)
                        
                        # Check if task exists locally
                        task = tasks.get_task(task_data["id"])
                        
                        if task:
                            # Task exists locally, check for changes
                            
                            # Get metadata if available
                            metadata = self.get_task_metadata(task)
                            
                            if metadata:
                                # Check if the task has changed since last sync
                                remote_model = TaskSyncModel.from_remote(remote_task)
                                local_model = TaskSyncModel.from_task(task)
                                
                                # Get the last synced state
                                if metadata.last_local_state:
                                    try:
                                        last_synced_model = TaskSyncModel.parse_raw(metadata.last_local_state)
                                    except Exception:
                                        # If we can't parse the last synced state, assume it's changed
                                        last_synced_model = None
                                else:
                                    last_synced_model = None
                                
                                # Check if the task has been modified locally
                                local_changed = not last_synced_model or local_model.has_changes_from(last_synced_model)
                                
                                # Check if the task has been modified remotely
                                remote_changed = not last_synced_model or remote_model.has_changes_from(last_synced_model)
                                
                                # Check if the task has been modified since last sync
                                if metadata.last_sync and hasattr(remote_task, "updated_at") and remote_task.updated_at:
                                    try:
                                        # Convert string timestamps to datetime objects, ensuring they're both naive
                                        last_sync_dt = datetime.fromisoformat(metadata.last_sync.replace('Z', '+00:00'))
                                        if last_sync_dt.tzinfo is not None:
                                            last_sync_dt = last_sync_dt.replace(tzinfo=None)
                                            
                                        remote_updated_dt = datetime.fromisoformat(remote_task.updated_at.replace('Z', '+00:00'))
                                        if remote_updated_dt.tzinfo is not None:
                                            remote_updated_dt = remote_updated_dt.replace(tzinfo=None)
                                            
                                        # Check if the remote task has been updated since last sync
                                        remote_updated_since_sync = remote_updated_dt > last_sync_dt
                                    except Exception as e:
                                        # If we can't parse the timestamps, assume it's changed
                                        log.warning(f"Error parsing timestamps: {str(e)}")
                                        remote_updated_since_sync = True
                                else:
                                    remote_updated_since_sync = True
                                
                                # If the task has been modified both locally and remotely, we have a conflict
                                if local_changed and remote_changed and remote_updated_since_sync:
                                    # Add to conflicts
                                    results["conflicts"] += 1
                                    
                                    # Update metadata
                                    metadata.sync_status = SyncStatus.CONFLICT
                                    self.update_task_metadata(task, metadata)
                                    
                                    console.print(f"[WARNING] Conflict detected for task {task.id}: {task.title}", style="bold yellow")
                                elif remote_changed and remote_updated_since_sync:
                                    # Remote has changed, update local
                                    self.update_task_from_remote(task, remote_task)
                                    
                                    # Update metadata
                                    metadata.last_sync = datetime.now().isoformat()
                                    metadata.sync_status = SyncStatus.SYNCED
                                    metadata.last_local_state = TaskSyncModel.from_task(task).json()
                                    self.update_task_metadata(task, metadata)
                                    
                                    results["updated"] += 1
                                else:
                                    # No changes or local changes only
                                    results["synced"] += 1
                            else:
                                # No metadata, create it
                                metadata = NextCloudSyncMetadata(
                                    provider="nextcloud",
                                    remote_id=remote_task.id,
                                    last_sync=datetime.now().isoformat(),
                                    sync_status=SyncStatus.SYNCED,
                                    last_local_state=TaskSyncModel.from_task(task).json(),
                                )
                                self.update_task_metadata(task, metadata)
                                
                                results["synced"] += 1
                        else:
                            # Task doesn't exist locally, create it
                            new_task = Task(**task_data)
                            
                            # Add metadata
                            metadata = NextCloudSyncMetadata(
                                provider="nextcloud",
                                remote_id=remote_task.id,
                                last_sync=datetime.now().isoformat(),
                                sync_status=SyncStatus.SYNCED,
                                last_local_state=TaskSyncModel.from_task(new_task).json(),
                            )
                            self.update_task_metadata(new_task, metadata)
                            
                            # Add to tasks
                            tasks.tasks.append(new_task)
                            
                            results["created"] += 1
                    else:
                        # This is a subtask
                        # Map remote task to local format
                        subtask_data = TaskFieldMapping.map_remote_to_local(remote_task)
                        
                        # Check if subtask exists locally
                        subtask = tasks.get_task(subtask_data["id"])
                        
                        if subtask:
                            # Subtask exists locally, check for changes
                            
                            # Get metadata if available
                            metadata = self.get_task_metadata(subtask)
                            
                            if metadata:
                                # Check if the subtask has changed since last sync
                                remote_model = TaskSyncModel.from_remote(remote_task)
                                local_model = TaskSyncModel.from_task(subtask)
                                
                                # Get the last synced state
                                if metadata.last_local_state:
                                    try:
                                        last_synced_model = TaskSyncModel.parse_raw(metadata.last_local_state)
                                    except Exception:
                                        # If we can't parse the last synced state, assume it's changed
                                        last_synced_model = None
                                else:
                                    last_synced_model = None
                                
                                # Check if the subtask has been modified locally
                                local_changed = not last_synced_model or local_model.has_changes_from(last_synced_model)
                                
                                # Check if the subtask has been modified remotely
                                remote_changed = not last_synced_model or remote_model.has_changes_from(last_synced_model)
                                
                                # Check if the subtask has been modified since last sync
                                if metadata.last_sync and hasattr(remote_task, "updated_at") and remote_task.updated_at:
                                    try:
                                        # Convert string timestamps to datetime objects, ensuring they're both naive
                                        last_sync_dt = datetime.fromisoformat(metadata.last_sync.replace('Z', '+00:00'))
                                        if last_sync_dt.tzinfo is not None:
                                            last_sync_dt = last_sync_dt.replace(tzinfo=None)
                                            
                                        remote_updated_dt = datetime.fromisoformat(remote_task.updated_at.replace('Z', '+00:00'))
                                        if remote_updated_dt.tzinfo is not None:
                                            remote_updated_dt = remote_updated_dt.replace(tzinfo=None)
                                            
                                        # Check if the remote subtask has been updated since last sync
                                        remote_updated_since_sync = remote_updated_dt > last_sync_dt
                                    except Exception as e:
                                        # If we can't parse the timestamps, assume it's changed
                                        log.warning(f"Error parsing timestamps: {str(e)}")
                                        remote_updated_since_sync = True
                                else:
                                    remote_updated_since_sync = True
                                
                                # If the subtask has been modified both locally and remotely, we have a conflict
                                if local_changed and remote_changed and remote_updated_since_sync:
                                    # Add to conflicts
                                    results["conflicts"] += 1
                                    
                                    # Update metadata
                                    metadata.sync_status = SyncStatus.CONFLICT
                                    self.update_task_metadata(subtask, metadata)
                                    
                                    console.print(f"[WARNING] Conflict detected for subtask {subtask.id}: {subtask.title}", style="bold yellow")
                                elif remote_changed and remote_updated_since_sync:
                                    # Remote has changed, update local
                                    self.update_task_from_remote(subtask, remote_task)
                                    
                                    # Update metadata
                                    metadata.last_sync = datetime.now().isoformat()
                                    metadata.sync_status = SyncStatus.SYNCED
                                    metadata.last_local_state = TaskSyncModel.from_task(subtask).json()
                                    self.update_task_metadata(subtask, metadata)
                                    
                                    results["updated"] += 1
                                else:
                                    # No changes or local changes only
                                    results["synced"] += 1
                            else:
                                # No metadata, create it
                                metadata = NextCloudSyncMetadata(
                                    provider="nextcloud",
                                    remote_id=remote_task.id,
                                    last_sync=datetime.now().isoformat(),
                                    sync_status=SyncStatus.SYNCED,
                                    last_local_state=TaskSyncModel.from_task(subtask).json(),
                                )
                                self.update_task_metadata(subtask, metadata)
                            
                            results["synced"] += 1
                        else:
                            # Subtask doesn't exist locally, create it if parent exists
                            
                            # Find parent task
                            parent_id = None
                            if "." in subtask_data["id"]:
                                parent_id = subtask_data["id"].split(".")[0]
                            
                            if parent_id:
                                parent_task = tasks.get_task(parent_id)
                                
                                if parent_task:
                                    # Create subtask
                                    new_subtask = Subtask(**subtask_data)
                                    
                                    # Add metadata
                                    metadata = NextCloudSyncMetadata(
                                        provider="nextcloud",
                                        remote_id=remote_task.id,
                                        last_sync=datetime.now().isoformat(),
                                        sync_status=SyncStatus.SYNCED,
                                        last_local_state=TaskSyncModel.from_task(new_subtask).json(),
                                    )
                                    self.update_task_metadata(new_subtask, metadata)
                                    
                                    # Add to parent task
                                    if not hasattr(parent_task, "subtasks"):
                                        parent_task.subtasks = []
                                    
                                    parent_task.subtasks.append(new_subtask)
                                    
                                    results["created"] += 1
                except Exception as e:
                    log.error(f"Error processing remote task: {str(e)}")
                    results["errors"] += 1
                    
            # Save tasks
            with open(tasks_path, "w") as f:
                f.write(tasks.model_dump_json())
                
            return results
        except Exception as e:
            console.print(f"[ERROR] Error in _pull_tasks: {str(e)}", style="bold red")
            return results
    
    def update_task_from_remote(self, task: Union[Task, Subtask], remote_task: Any) -> None:
        """
        Update a local task with data from a remote task.
        
        Args:
            task: The local task to update
            remote_task: The remote task data
        """
        # Map remote task to local format
        task_data = TaskFieldMapping.map_remote_to_local(remote_task)
        
        # Update task fields
        for key, value in task_data.items():
            if key != "id" and key != "parent_id":  # Don't change the ID or parent_id
                if hasattr(task, key) and value is not None:
                    # Only update if the field exists and the value is not None
                    current_value = getattr(task, key)
                    if current_value != value:
                        # Log status changes for debugging
                        if key == "status" and current_value != value:
                            console.print(f"[INFO] Task {task.id} status changed from {current_value} to {value}")
                        
                        # Update the field
                        setattr(task, key, value)
    
    def get_task_metadata(self, task: Task, provider: str = "nextcloud") -> Optional[NextCloudSyncMetadata]:
        """
        Get sync metadata for a task.
        
        Args:
            task: The task to get metadata for
            provider: The sync provider to get metadata for (default: nextcloud)
            
        Returns:
            The task's sync metadata, or None if not found
        """
        # Get the metadata file path
        metadata_dir = os.path.join(self.project_directory, ".taskinator", "sync_metadata")
        os.makedirs(metadata_dir, exist_ok=True)
        metadata_file = os.path.join(metadata_dir, f"task_{task.id}.json")
        
        # Check if metadata file exists
        if not os.path.exists(metadata_file):
            return None
        
        # Read metadata from file
        try:
            with open(metadata_file, "r") as f:
                metadata_dict = json.load(f)
                return NextCloudSyncMetadata(**metadata_dict)
        except Exception as e:
            console.print(f"[ERROR] Error reading metadata for task {task.id}: {str(e)}", style="bold red")
            return None
    
    def update_task_metadata(self, task: Task, metadata: NextCloudSyncMetadata) -> None:
        """
        Update sync metadata for a task.
        
        Args:
            task: The task to update metadata for
            metadata: The metadata to update
        """
        # Get the metadata file path
        metadata_dir = os.path.join(self.project_directory, ".taskinator", "sync_metadata")
        os.makedirs(metadata_dir, exist_ok=True)
        metadata_file = os.path.join(metadata_dir, f"task_{task.id}.json")
        
        # Write metadata to file
        try:
            with open(metadata_file, "w") as f:
                json.dump(metadata.dict(), f, indent=2)
        except Exception as e:
            console.print(f"[ERROR] Error writing metadata for task {task.id}: {str(e)}", style="bold red")

    # CLI command implementations

    async def setup_command(self, project_directory: str, non_interactive: bool = False, **kwargs) -> None:
        """
        CLI command to set up Nextcloud sync.
        
        Args:
            project_directory: The project directory
            non_interactive: Whether to run in non-interactive mode (use environment variables only)
            **kwargs: Additional parameters
        """
        console.print(
            Panel(
                "Setting up Nextcloud sync...", 
                title="Sync Setup", 
                style="blue"
            )
        )

        if await self.setup(project_directory, non_interactive=non_interactive, **kwargs):
            console.print(
                "[SUCCESS] nextcloud sync set up successfully",
                style="bold green",
            )
        else:
            console.print(
                "[ERROR] Failed to set up Nextcloud sync. Please check your credentials and try again.",
                style="bold red",
            )

    async def push_command(self, project_directory: str, **kwargs) -> None:
        """
        CLI command to push tasks to Nextcloud.
        
        Args:
            project_directory: The project directory
            **kwargs: Additional parameters
        """
        await self.sync_command(project_directory, direction="push", **kwargs)

    async def pull_command(self, project_directory: str, **kwargs) -> None:
        """
        CLI command to pull tasks from Nextcloud.
        
        Args:
            project_directory: The project directory
            **kwargs: Additional parameters
        """
        await self.sync_command(project_directory, direction="pull", **kwargs)

    async def sync_command(
        self, project_directory: str, direction: str = "bidirectional", debug: bool = False, **kwargs
    ) -> None:
        """
        CLI command to synchronize tasks with Nextcloud.
        
        Args:
            project_directory: The project directory
            direction: Sync direction (push, pull, or bidirectional)
            debug: Enable debug logging
            **kwargs: Additional parameters
        """
        console = Console()
        
        with console.status("[bold green]Connecting to Nextcloud..."):
            # Check if we can connect to Nextcloud
            try:
                # Get client
                self.client = await self._get_client(project_directory)
                if not self.client:
                    console.print("[ERROR] Failed to connect to Nextcloud: Invalid configuration", style="bold red")
                    return
                
                # Verify connection
                connection_ok = await self.client.check_connection()
                if not connection_ok:
                    console.print("[ERROR] Failed to connect to Nextcloud", style="bold red")
                    return
                
                # Verify calendar exists
                calendar_verification = await self.client.verify_calendar()
                if not calendar_verification["exists"]:
                    console.print("[ERROR] Calendar not found", style="bold red")
                    
                    # Show available calendars
                    if calendar_verification["all_calendars"]:
                        console.print("Available calendars:", style="bold yellow")
                        for cal in calendar_verification["all_calendars"]:
                            console.print(f"  - {cal['name']} (ID: {cal['id']})", style="bold yellow")
                        
                        # Suggest using a different calendar
                        if calendar_verification["suggested_calendar"]:
                            suggested = calendar_verification["suggested_calendar"]
                            console.print(f"[TIP] Try using calendar: {suggested['name']} (ID: {suggested['id']})", style="bold green")
                            console.print(f"[TIP] Update your configuration with: taskinator sync setup --calendar-id=\"{suggested['id']}\"", style="bold green")
                    else:
                        console.print("[ERROR] No calendars found in your Nextcloud account", style="bold red")
                    
                    return
            except Exception as e:
                console.print(f"[ERROR] Failed to connect to Nextcloud: {str(e)}", style="bold red")
                return
        
        console.print(Panel.fit(f"Synchronizing tasks with Nextcloud ({direction})...", title="Nextcloud Sync"))
        
        try:
            # Sync tasks
            result = await self.sync(project_directory, direction=direction, debug=debug, **kwargs)
            
            # Display results
            if result:
                # Create a table for sync results
                table = Table(title="Nextcloud Sync Results")
                
                # Add columns
                table.add_column("Metric", style="cyan")
                table.add_column("Count", style="green")
                
                # Define the order of metrics to display
                if direction == "bidirectional":
                    # For bidirectional sync, show pull and push metrics separately
                    metrics_order = [
                        "total",
                        "pull_synced", "pull_created", "pull_updated", 
                        "synced", "created", "updated", 
                        "deleted", "conflicts", "errors"
                    ]
                    
                    # Add a header row for pull metrics
                    table.add_row("Pull Operation", "")
                    
                    # Add pull metrics
                    if "pull_synced" in result:
                        table.add_row("  Synced", str(result.get("pull_synced", 0)))
                    if "pull_created" in result:
                        table.add_row("  Created", str(result.get("pull_created", 0)))
                    if "pull_updated" in result:
                        table.add_row("  Updated", str(result.get("pull_updated", 0)))
                    
                    # Add a header row for push metrics
                    table.add_row("Push Operation", "")
                    
                    # Add push metrics
                    table.add_row("  Synced", str(result.get("synced", 0)))
                    table.add_row("  Created", str(result.get("created", 0)))
                    table.add_row("  Updated", str(result.get("updated", 0)))
                    
                    # Add summary metrics
                    table.add_row("Summary", "")
                    table.add_row("  Total Tasks", str(result.get("total", 0)))
                    table.add_row("  Deleted", str(result.get("deleted", 0)))
                    table.add_row("  Conflicts", str(result.get("conflicts", 0)))
                    table.add_row("  Errors", str(result.get("errors", 0)))
                else:
                    # For one-way sync, show metrics in a simple list
                    metrics_order = ["total", "synced", "created", "updated", "deleted", "conflicts", "errors"]
                    
                    # Add rows in the defined order
                    for metric in metrics_order:
                        if metric in result and isinstance(result[metric], int):
                            table.add_row(metric.capitalize(), str(result[metric]))
                
                # Print table
                console.print(table)
                
                # Print success message
                if result.get("errors", 0) == 0:
                    console.print(
                        f"[SUCCESS] Successfully synchronized tasks with Nextcloud ({direction})",
                        style="bold green",
                    )
                else:
                    console.print(
                        f"[WARNING] Synchronized tasks with Nextcloud ({direction}) with {result['errors']} errors",
                        style="bold yellow",
                    )
        except Exception as e:
            console.print(f"[ERROR] Error syncing tasks: {str(e)}", style="bold red")

    async def status_command(self, project_directory: str, verbose: bool = False, **kwargs) -> None:
        """
        CLI command to show Nextcloud sync status.
        
        Args:
            project_directory: The project directory
            verbose: Whether to show verbose output
            **kwargs: Additional parameters
        """
        console.print(
            Panel(
                "Getting Nextcloud sync status...",
                title="Nextcloud Sync Status",
                style="blue",
            )
        )
        
        try:
            # Get sync status
            status = await self.get_status(project_directory, verbose=verbose, **kwargs)
            
            # Display status
            if status:
                # Create a table for sync status
                table = Table(title="Nextcloud Sync Status")
                
                # Add columns
                table.add_column("Metric", style="cyan")
                table.add_column("Count", style="green")
                
                # Add rows
                for key, value in status.items():
                    if key != "connection":
                        table.add_row(key.capitalize(), str(value))
                
                # Add connection info if verbose
                if verbose and "connection" in status:
                    table.add_row("Host", status["connection"].get("host", ""))
                    table.add_row("Username", status["connection"].get("username", ""))
                    table.add_row("Calendar", status["connection"].get("calendar_id", ""))
                    table.add_row(
                        "Connected",
                        "Yes" if status["connection"].get("connected", False) else "No",
                    )
                
                # Print table
                console.print(table)
        except Exception as e:
            console.print(f"[ERROR] Error getting sync status: {str(e)}", style="bold red")

    async def resolve_command(
        self, project_directory: str, task_id: Optional[str] = None, resolution: str = "local", **kwargs
    ) -> None:
        """
        CLI command to resolve sync conflicts.
        
        Args:
            project_directory: The project directory
            task_id: Optional task ID to resolve conflicts for
            resolution: Resolution strategy (local, remote, or interactive)
            **kwargs: Additional parameters
        """
        console.print(
            Panel(
                f"Resolving sync conflicts using {resolution} strategy...",
                title="Nextcloud Sync",
                style="blue",
            )
        )
        
        try:
            # Resolve conflicts
            result = await self.resolve_conflicts(
                project_directory, task_id=task_id, resolution=resolution, **kwargs
            )
            
            # Display results
            if result:
                if result.get("resolved", 0) > 0:
                    console.print(
                        f"[SUCCESS] Resolved {result['resolved']} conflicts using {resolution} strategy",
                        style="bold green",
                    )
                else:
                    console.print(
                        f"[INFO] No conflicts to resolve", style="bold blue"
                    )
        except Exception as e:
            console.print(f"[ERROR] Failed to resolve conflicts: {str(e)}", style="bold red")

    async def reset_sync_metadata_command(self) -> None:
        """
        Reset sync metadata for all tasks.
        This is useful when the remote task list has been deleted or when switching to a new Nextcloud instance.
        """
        console.print(
            Panel(
                "Resetting Nextcloud sync metadata for all tasks...",
                title="Nextcloud Sync Reset",
                style="blue",
            )
        )
        
        # Get tasks path
        tasks_path = get_tasks_path()
        
        # Read tasks
        tasks = read_tasks(tasks_path)
        
        # Reset metadata for all tasks
        reset_count = 0
        for task in tasks.tasks:
            # Reset task metadata
            if hasattr(task, "metadata") and task.metadata:
                nextcloud_metadata = next((m for m in task.metadata if isinstance(m, dict) and m.get("provider") == "nextcloud"), None)
                if nextcloud_metadata:
                    task.metadata.remove(nextcloud_metadata)
                    reset_count += 1
            
            # Reset subtask metadata
            if hasattr(task, "subtasks") and task.subtasks:
                for subtask in task.subtasks:
                    if hasattr(subtask, "metadata") and subtask.metadata:
                        nextcloud_metadata = next((m for m in subtask.metadata if isinstance(m, dict) and m.get("provider") == "nextcloud"), None)
                        if nextcloud_metadata:
                            subtask.metadata.remove(nextcloud_metadata)
                            reset_count += 1
        
        # Save tasks to file
        write_tasks(tasks_path, tasks)
        
        console.print(f"[SUCCESS] Reset sync metadata for {reset_count} tasks", style="bold green")
        console.print("[INFO] You can now run 'taskinator sync push' to push all tasks to Nextcloud as new tasks", style="bold blue")


# Backward compatibility alias
NextCloudSyncPlugin = NextCloudSyncPlugin   # For backward compatibility with existing code
