"""
Azure DevOps integration plugin for Taskinator.

This plugin provides integration with Azure DevOps for generating tasks from
work items and tracking work item hierarchies.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime

from taskinator.models.task import Task, TaskCollection
from taskinator.core.task_manager import read_tasks, write_tasks
from taskinator.core.story_point_systems import StoryPointSystem, get_story_point_system

try:
    from .client import AzureDevOpsClient, AZURE_DEVOPS_API_AVAILABLE
except ImportError:
    AZURE_DEVOPS_API_AVAILABLE = False

logger = logging.getLogger(__name__)


class AzureDevOpsPlugin:
    """
    Azure DevOps integration plugin for Taskinator.

    This plugin provides functionality to:
    1. Generate tasks from Azure DevOps work items
    2. Traverse work item hierarchies
    3. Import work items into Taskinator task structure
    """

    def __init__(self):
        """Initialize the Azure DevOps plugin."""
        self.client = None
        self.available = AZURE_DEVOPS_API_AVAILABLE

        if self.available:
            try:
                # Try to initialize the client
                self.client = AzureDevOpsClient()
                logger.info("Azure DevOps plugin initialized successfully.")
            except (ImportError, ValueError) as e:
                logger.warning(f"Azure DevOps plugin initialization failed: {e}")
                self.available = False
        else:
            logger.warning(
                "Azure DevOps API not available. Install with 'pip install azure-devops'."
            )

    def is_available(self) -> bool:
        """
        Check if the plugin is available.

        Returns:
            bool: True if the plugin is available, False otherwise
        """
        return self.available

    def get_work_item(self, work_item_id: int) -> Dict:
        """
        Get a work item by ID.

        Args:
            work_item_id: ID of the work item

        Returns:
            Dict: The work item data
        """
        if not self.available:
            raise RuntimeError("Azure DevOps plugin is not available.")

        return self.client.extract_work_item_fields(
            self.client.get_work_item(work_item_id)
        )

    def get_parent_chain(self, work_item_id: int) -> List[Dict]:
        """
        Get the chain of parent work items.

        Args:
            work_item_id: ID of the work item

        Returns:
            List[Dict]: The parent chain
        """
        if not self.available:
            raise RuntimeError("Azure DevOps plugin is not available.")

        hierarchy = self.client.get_parent_chain(work_item_id)
        return [self.client.extract_work_item_fields(item) for item in hierarchy]

    def get_work_item_hierarchy(self, work_item_id: int) -> Dict:
        """
        Get the work item hierarchy.

        Args:
            work_item_id: ID of the work item

        Returns:
            Dict: The work item hierarchy
        """
        if not self.available:
            raise RuntimeError("Azure DevOps plugin is not available.")

        return self.client.get_work_item_hierarchy_tree(work_item_id)

    def work_item_to_task(self, work_item_id: int) -> Task:
        """
        Convert an Azure DevOps work item to a Taskinator task.

        Args:
            work_item_id: ID of the work item

        Returns:
            Task: Taskinator task object
        """
        if not self.available:
            raise RuntimeError("Azure DevOps plugin is not available.")

        # Get the work item data
        work_item = self.get_work_item(work_item_id)

        # Map priority
        priority = "medium"  # Default
        if work_item.get("priority") is not None:
            priority_mapping = {1: "high", 2: "high", 3: "medium", 4: "low"}
            priority = priority_mapping.get(work_item["priority"], "medium")

        # Generate task ID from title
        task_id = f"azdo-{work_item['id']}"

        # Create task
        task = Task(
            id=task_id,
            title=work_item["title"],
            description=work_item.get("description", ""),
            status=self._map_work_item_state_to_status(work_item.get("state")),
            priority=priority,
            acceptance_criteria=[],
            story_points=work_item.get("story_points"),
            source={
                "type": "azure_devops",
                "url": f"{os.getenv('AZURE_DEVOPS_ORG_URL')}/_workitems/edit/{work_item['id']}",
                "id": work_item["id"],
                "work_item_type": work_item["type"],
            },
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        return task

    def _map_work_item_state_to_status(self, state: str) -> str:
        """
        Map Azure DevOps work item state to Taskinator status.

        Args:
            state: Azure DevOps work item state

        Returns:
            str: Taskinator status
        """
        if not state:
            return "pending"

        state = state.lower()

        if state in ["done", "closed", "completed", "resolved"]:
            return "done"
        elif state in ["active", "in progress", "doing", "started"]:
            return "in-progress"
        elif state in ["blocked", "impediment"]:
            return "blocked"
        elif state in ["removed", "rejected"]:
            return "cancelled"
        else:
            return "pending"

    def import_work_item_with_children(
        self,
        work_item_id: int,
        include_parents: bool = False,
        output_path: Optional[str] = None,
    ) -> TaskCollection:
        """
        Import an Azure DevOps work item with its children as Taskinator tasks.

        Args:
            work_item_id: ID of the work item
            include_parents: Also include parent work items
            output_path: Path to write tasks to (defaults to tasks.json)

        Returns:
            TaskCollection: Collection of tasks
        """
        if not self.available:
            raise RuntimeError("Azure DevOps plugin is not available.")

        # Start with existing tasks collection or create new one
        try:
            tasks_collection = read_tasks(output_path)
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

        # Determine the root work item
        if include_parents:
            # Get the parent chain and use the topmost parent as root
            parent_chain = self.client.get_parent_chain(work_item_id)
            if parent_chain:
                root_work_item = parent_chain[-1]
                root_id = root_work_item.id
            else:
                root_id = work_item_id
        else:
            root_id = work_item_id

        # Get the work item hierarchy tree
        hierarchy_tree = self.client.get_work_item_hierarchy_tree(root_id)

        # Convert the hierarchy tree to tasks
        main_task = self._convert_hierarchy_to_tasks(hierarchy_tree)

        # Add the task to the collection
        tasks_collection.tasks.append(main_task)

        # Write tasks if output path provided
        if output_path:
            write_tasks(tasks_collection, output_path)

        return tasks_collection

    def _convert_hierarchy_to_tasks(self, item: Dict) -> Task:
        """
        Convert a work item hierarchy to tasks.

        Args:
            item: Work item hierarchy node

        Returns:
            Task: Task object with subtasks
        """
        # Create the main task
        task_id = f"azdo-{item['id']}"

        # Map priority
        priority = "medium"  # Default
        if item.get("priority") is not None:
            priority_mapping = {1: "high", 2: "high", 3: "medium", 4: "low"}
            priority = priority_mapping.get(item["priority"], "medium")

        task = Task(
            id=task_id,
            title=item["title"],
            description=item.get("description", ""),
            status=self._map_work_item_state_to_status(item.get("state")),
            priority=priority,
            acceptance_criteria=[],
            story_points=item.get("story_points"),
            source={
                "type": "azure_devops",
                "url": f"{os.getenv('AZURE_DEVOPS_ORG_URL')}/_workitems/edit/{item['id']}",
                "id": item["id"],
                "work_item_type": item["type"],
            },
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Add subtasks
        if "children" in item:
            subtasks = []
            for child in item["children"]:
                subtask = self._convert_hierarchy_to_tasks(child)
                # Adjust subtask ID to be a proper subtask ID
                subtask_number = len(subtasks) + 1
                subtask.id = f"{task_id}.{subtask_number}"
                subtasks.append(subtask)

            task.subtasks = subtasks

        return task
