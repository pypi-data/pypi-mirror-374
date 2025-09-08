"""
GitLab integration plugin for Taskinator.

This plugin provides integration with GitLab for generating tasks from
issues and tracking issue hierarchies.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
import traceback

from taskinator.models.task import Task, TaskCollection
from taskinator.core.task_manager import read_tasks, write_tasks
from taskinator.core.story_point_systems import StoryPointSystem, get_story_point_system
from taskinator.utils.config import get_tasks_dir, get_tasks_path

try:
    from .client import GitLabClient, GITLAB_API_AVAILABLE
except ImportError:
    GITLAB_API_AVAILABLE = False

logger = logging.getLogger(__name__)


class GitLabPlugin:
    """
    GitLab integration plugin for Taskinator.

    This plugin provides functionality to:
    1. Generate tasks from GitLab issues
    2. Traverse issue hierarchies
    3. Import issues into Taskinator task structure
    """

    def __init__(self):
        """Initialize the GitLab plugin."""
        self.client = None
        self.available = GITLAB_API_AVAILABLE

        if self.available:
            try:
                # Try to initialize the client
                self.client = GitLabClient()
                logger.info("GitLab plugin initialized successfully.")
            except (ImportError, ValueError) as e:
                logger.warning(f"GitLab plugin initialization failed: {e}")
                self.available = False
        else:
            logger.warning(
                "GitLab API not available. Install with 'pip install python-gitlab'."
            )

    def is_available(self) -> bool:
        """
        Check if the plugin is available.

        Returns:
            bool: True if the plugin is available, False otherwise
        """
        return self.available

    def get_issue(self, issue_iid: int) -> Dict:
        """
        Get a GitLab issue by internal ID.

        Args:
            issue_iid: Internal ID of the issue within the project

        Returns:
            Dict: The issue data
        """
        if not self.available:
            raise RuntimeError("GitLab plugin is not available.")

        return self.client.extract_issue_fields(self.client.get_issue(issue_iid))

    def get_parent_chain(self, issue_iid: int) -> List[Dict]:
        """
        Get the chain of parent issues.

        Args:
            issue_iid: Internal ID of the issue

        Returns:
            List[Dict]: The parent chain
        """
        if not self.available:
            raise RuntimeError("GitLab plugin is not available.")

        hierarchy = self.client.get_parent_chain(issue_iid)
        return [self.client.extract_issue_fields(item) for item in hierarchy]

    def get_issue_hierarchy(self, issue_iid: int) -> Dict:
        """
        Get the issue hierarchy.

        Args:
            issue_iid: Internal ID of the issue

        Returns:
            Dict: The issue hierarchy
        """
        if not self.available:
            raise RuntimeError("GitLab plugin is not available.")

        return self.client.get_issue_hierarchy_tree(issue_iid)

    def issue_to_task(self, issue_iid: int) -> Task:
        """
        Convert a GitLab issue to a Taskinator task.

        Args:
            issue_iid: Internal ID of the issue

        Returns:
            Task: Taskinator task object
        """
        if not self.available:
            raise RuntimeError("GitLab plugin is not available.")

        # Get the issue data
        issue = self.get_issue(issue_iid)

        # Map labels to priority
        priority = "medium"  # Default
        if "labels" in issue:
            for label in issue["labels"]:
                label_lower = label.lower()
                if (
                    "high" in label_lower
                    or "critical" in label_lower
                    or "urgent" in label_lower
                ):
                    priority = "high"
                    break
                if (
                    "low" in label_lower
                    or "minor" in label_lower
                    or "trivial" in label_lower
                ):
                    priority = "low"
                    break

        # Generate task ID from issue information
        task_id = f"gitlab-{issue['id']}"

        # Create task
        # Add the GitLab URL to the description for better visibility
        description = issue.get("description", "") or ""
        web_url = issue.get("web_url") or ""
        
        # Only append URL if it's not already in the description
        if web_url and web_url not in description:
            description_with_url = f"{description}\n\nGitLab Issue: {web_url}"
        else:
            description_with_url = description
            
        task = Task(
            id=task_id,
            title=issue["title"],
            description=description_with_url,
            status=self._map_issue_state_to_status(issue.get("state")),
            priority=priority,
            acceptance_criteria=[],
            story_points=issue.get("story_points"),
            source={
                "type": "gitlab",
                "url": web_url,
                "id": str(issue["id"]),
                "issue_type": issue.get("type", "issue"),  # Default to issue if type not specified
            },
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={
                "gitlab_url": web_url,
                "gitlab_id": str(issue["id"]),
                "imported_at": datetime.now().isoformat(),
                "issue_type": issue.get("type", "issue")  # Default to issue if type not specified
            }  # Store GitLab information in metadata for easier access
        )

        return task

    def _map_issue_state_to_status(self, state: str) -> str:
        """
        Map GitLab issue state to Taskinator status.

        Args:
            state: GitLab issue state

        Returns:
            str: Taskinator status
        """
        if not state:
            return "pending"

        state = state.lower()

        if state in ["closed", "completed", "resolved"]:
            return "done"
        elif state in ["active", "in progress"]:
            return "in-progress"
        elif state in ["opened"]:
            # In GitLab, "opened" means the issue exists but no one is necessarily working on it yet
            return "pending"
        else:
            return "pending"

    def import_issue_with_children(
        self,
        issue_iid: int,
        include_parents: bool = False,
        output_path: Optional[str] = None,
    ) -> TaskCollection:
        """
        Import a GitLab issue with its children as Taskinator tasks.

        Args:
            issue_iid: Internal ID of the issue
            include_parents: Also include parent issues
            output_path: Path to write tasks to (defaults to tasks.json)

        Returns:
            TaskCollection: Collection of tasks
        """
        if not self.available:
            raise RuntimeError("GitLab plugin is not available.")

        # Determine tasks path and create directories if needed
        try:
            # Use custom path if provided, otherwise use the standard tasks path from config
            tasks_path = output_path or get_tasks_path()
            tasks_dir = os.path.dirname(tasks_path)
            
            # Ensure the directory exists
            os.makedirs(tasks_dir, exist_ok=True)
            logger.debug(f"Tasks path set to: {tasks_path}")
            
            # Try to read existing tasks file if it exists
            if os.path.exists(tasks_path):
                try:
                    logger.debug(f"Reading existing tasks from {tasks_path}")
                    tasks_collection = read_tasks(tasks_path)
                    logger.debug(f"Successfully read tasks from {tasks_path}")
                except Exception as e:
                    logger.warning(f"Error reading tasks from {tasks_path}: {e}")
                    # Create a new collection if the file has issues
                    tasks_collection = self._create_new_task_collection()
            else:
                # File doesn't exist, create a new collection
                logger.debug(f"Tasks file {tasks_path} doesn't exist, creating new collection")
                tasks_collection = self._create_new_task_collection()
        except Exception as e:
            logger.warning(f"Error determining tasks path: {e}")
            # Fallback to a default path in tasks directory
            tasks_dir = get_tasks_dir()
            os.makedirs(tasks_dir, exist_ok=True)
            tasks_path = os.path.join(tasks_dir, "tasks.json")
            logger.debug(f"Using fallback tasks path: {tasks_path}")
            tasks_collection = self._create_new_task_collection()

        # Determine the root issue
        try:
            logger.debug(f"Finding root issue for {issue_iid}, include_parents={include_parents}")
            if include_parents:
                # Get the parent chain and use the topmost parent as root
                parent_chain = self.client.get_parent_chain(issue_iid)
                logger.debug(f"Parent chain length: {len(parent_chain) if parent_chain else 0}")
                
                if parent_chain and len(parent_chain) > 1:
                    root_issue = parent_chain[-1]
                    logger.debug(f"Root issue type: {type(root_issue)}")
                    
                    # Check if root_issue is a function or object, and handle accordingly
                    if callable(root_issue):
                        # If it's a function (unlikely but possible), just use issue_iid
                        logger.warning("Unexpected function returned as issue. Using original issue ID.")
                        root_iid = issue_iid
                    else:
                        try:
                            # Check if it's a dictionary or object with attribute access
                            if isinstance(root_issue, dict) and 'id' in root_issue:
                                root_iid = root_issue['id']
                                logger.debug(f"Using dict id: {root_iid}")
                            elif hasattr(root_issue, 'iid'):
                                root_iid = root_issue.iid
                                logger.debug(f"Using object iid: {root_iid}")
                            else:
                                logger.warning("Could not determine root issue ID. Using original issue ID.")
                                logger.debug(f"Root issue dir: {dir(root_issue)}")  
                                root_iid = issue_iid
                        except Exception as e:
                            logger.warning(f"Error accessing root issue ID: {e}. Using original issue ID.")
                            logger.debug(f"Exception details: {traceback.format_exc()}")
                            root_iid = issue_iid
                else:
                    logger.debug("No parent chain or single item, using original issue ID")
                    root_iid = issue_iid
            else:
                logger.debug("Parents not included, using original issue ID")
                root_iid = issue_iid
        except Exception as e:
            logger.warning(f"Error determining root issue: {e}")
            logger.debug(f"Root issue exception details: {traceback.format_exc()}")
            root_iid = issue_iid

        # Get the issue hierarchy tree
        logger.debug(f"Getting hierarchy tree for root_iid: {root_iid}")
        try:
            hierarchy_tree = self.client.get_issue_hierarchy_tree(root_iid)
            logger.debug(f"Hierarchy tree type: {type(hierarchy_tree)}, keys: {hierarchy_tree.keys() if isinstance(hierarchy_tree, dict) else 'N/A'}")
        except Exception as e:
            logger.error(f"Error getting hierarchy tree: {e}")
            logger.debug(f"Hierarchy exception details: {traceback.format_exc()}")
            raise

        # Convert the hierarchy tree to tasks
        logger.debug("Converting hierarchy tree to tasks")
        try:
            main_task = self._convert_hierarchy_to_tasks(hierarchy_tree)
            logger.debug(f"Main task ID: {main_task.id}, title: {main_task.title}")
        except Exception as e:
            logger.error(f"Error converting hierarchy to tasks: {e}")
            logger.debug(f"Conversion exception details: {traceback.format_exc()}")
            raise

        # Check if task with this ID already exists in collection, replace it if found
        task_id = main_task.id
        found = False
        
        # Look for existing task with the same ID
        for i, task in enumerate(tasks_collection.tasks):
            if task.id == task_id:
                logger.debug(f"Found existing task with ID {task_id}, replacing it")
                tasks_collection.tasks[i] = main_task
                found = True
                break
                
        # If no existing task found, add as a new task
        if not found:
            logger.debug(f"No existing task found with ID {task_id}, adding as new task")
            tasks_collection.tasks.append(main_task)

        # Write tasks if output path provided or use default path
        try:
            logger.debug(f"Writing tasks to {tasks_path}")
            # Make sure the directory exists
            os.makedirs(os.path.dirname(tasks_path), exist_ok=True)
            # Write the tasks
            write_tasks(tasks_path, tasks_collection)
            logger.debug(f"Successfully wrote tasks to {tasks_path}")
        except Exception as e:
            logger.error(f"Error writing tasks to {tasks_path}: {e}")

        return tasks_collection

    def _create_new_task_collection(self) -> TaskCollection:
        """Create a new empty task collection.

        Returns:
            TaskCollection: New empty task collection with default metadata
        """
        return TaskCollection(
            tasks=[],
            metadata={
                "project_name": "Taskinator",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "version": "0.2.0",
            },
        )

    def _convert_hierarchy_to_tasks(self, item: Dict) -> Task:
        """Convert an issue hierarchy to tasks.
        
        This method recursively converts GitLab issue hierarchies to Taskinator tasks.
        The function handles subtasks and all metadata mapping from GitLab to Taskinator.
        
        Args:
            item: Issue hierarchy node from GitLab API
            
        Returns:
            Task: Taskinator task with all subtasks included
            
        Raises:
            Exception: If any conversion errors occur
        """
        """
        Convert an issue hierarchy to tasks.

        Args:
            item: Issue hierarchy node

        Returns:
            Task: Task object with subtasks
        """
        # Create the main task
        task_id = f"gitlab-{item['id']}"

        # Map labels to priority if they exist
        priority = "medium"  # Default
        if "labels" in item:
            for label in item["labels"]:
                label_lower = label.lower()
                if (
                    "high" in label_lower
                    or "critical" in label_lower
                    or "urgent" in label_lower
                ):
                    priority = "high"
                    break
                if (
                    "low" in label_lower
                    or "minor" in label_lower
                    or "trivial" in label_lower
                ):
                    priority = "low"
                    break

        # Add the GitLab URL to the description for better visibility
        description = item.get("description", "") or ""
        web_url = item.get("web_url") or ""
        
        # Only append URL if it's not already in the description
        if web_url and web_url not in description:
            description_with_url = f"{description}\n\nGitLab Issue: {web_url}"
        else:
            description_with_url = description
            
        task = Task(
            id=task_id,
            title=item["title"],
            description=description_with_url,
            status=self._map_issue_state_to_status(item.get("state")),
            priority=priority,
            acceptance_criteria=[],
            story_points=item.get("story_points"),
            source={
                "type": "gitlab",
                "url": web_url,
                "id": str(item["id"]),
                "issue_type": item.get("type", "issue"),  # Default to issue if type not specified
            },
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={
                "gitlab_url": web_url,
                "gitlab_id": str(item["id"]),
                "imported_at": datetime.now().isoformat(),
                "issue_type": item.get("type", "issue")  # Default to issue if type not specified
            }  # Store GitLab information in metadata for easier access
        )

        # Add subtasks if present
        if "children" in item and item["children"]:
            logger.debug(f"Processing {len(item['children'])} children for task {task_id}")
            subtasks = []
            for i, child in enumerate(item["children"]):
                try:
                    # Skip empty or invalid entries
                    if not child:
                        logger.warning(f"Skipping empty child at index {i}")
                        continue
                        
                    # Convert the child to a task recursively
                    logger.debug(f"Converting child {i} to subtask")
                    subtask = self._convert_hierarchy_to_tasks(child)
                    
                    # Adjust subtask ID to be a proper subtask ID
                    subtask_number = len(subtasks) + 1
                    original_id = subtask.id
                    subtask.id = f"{task_id}.{subtask_number}"
                    
                    # Store the original GitLab ID in metadata
                    if not subtask.metadata:
                        subtask.metadata = {}
                    subtask.metadata["original_gitlab_id"] = original_id
                    
                    subtasks.append(subtask)
                    logger.debug(f"Added subtask {subtask.id} from GitLab issue {child.get('id')}")
                except Exception as e:
                    logger.warning(f"Error converting child {i} to subtask: {e}")
                    logger.debug(f"Child conversion error details: {traceback.format_exc()}")

            # Only set subtasks if we found any valid ones
            if subtasks:
                task.subtasks = subtasks
                logger.debug(f"Added {len(subtasks)} subtasks to task {task_id}")

        return task
