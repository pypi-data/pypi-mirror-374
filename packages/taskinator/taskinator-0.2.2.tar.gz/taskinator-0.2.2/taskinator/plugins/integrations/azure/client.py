"""
Azure DevOps API client for Taskinator.

This module provides functionality to interact with Azure DevOps work items
and queries.
"""

import os
import sys
import logging
from typing import Dict, List, Optional, Any, Union, Set

try:
    from azure.devops.connection import Connection
    from msrest.authentication import BasicAuthentication

    AZURE_DEVOPS_API_AVAILABLE = True
except ImportError:
    AZURE_DEVOPS_API_AVAILABLE = False

logger = logging.getLogger(__name__)


class AzureDevOpsClient:
    """
    Client for Azure DevOps API that provides work item tracking
    functionality.
    """

    def __init__(self):
        """Initialize the Azure DevOps client."""
        if not AZURE_DEVOPS_API_AVAILABLE:
            raise ImportError(
                "azure-devops package is not installed. "
                "Install it with 'pip install azure-devops'"
            )

        self.pat = os.getenv("AZURE_DEVOPS_PAT")
        self.org_url = os.getenv("AZURE_DEVOPS_ORG_URL")
        self.project = os.getenv("AZURE_DEVOPS_PROJECT")

        if not self.pat:
            raise ValueError(
                "Environment variable AZURE_DEVOPS_PAT is not set. "
                "Please set it to your Azure DevOps Personal Access Token."
            )

        if not self.org_url:
            raise ValueError(
                "Environment variable AZURE_DEVOPS_ORG_URL is not set. "
                "Please set it to your Azure DevOps organization URL."
            )

        self.connection = None
        self.wit_client = None
        self._connect()

    def _connect(self):
        """Connect to Azure DevOps API."""
        credentials = BasicAuthentication("", self.pat)
        self.connection = Connection(base_url=self.org_url, creds=credentials)
        self.wit_client = self.connection.clients.get_work_item_tracking_client()
        logger.info(f"Connected to Azure DevOps: {self.org_url}")

    def get_work_item(self, work_item_id: int, expand: str = "Relations") -> Dict:
        """
        Get a work item by ID.

        Args:
            work_item_id: ID of the work item
            expand: Fields to expand (e.g., "Relations")

        Returns:
            Dict: The work item data
        """
        try:
            work_item = self.wit_client.get_work_item(work_item_id, expand=expand)
            return work_item
        except Exception as e:
            logger.error(f"Failed to retrieve work item {work_item_id}: {e}")
            raise

    def get_parent_chain(self, work_item_id: int) -> List[Dict]:
        """
        Get the chain of parent work items up to the root (e.g., Epic).

        Args:
            work_item_id: ID of the work item to start from

        Returns:
            List[Dict]: List of work items in the hierarchy (from leaf to root)
        """
        hierarchy = []
        current_id = work_item_id

        while current_id:
            try:
                work_item = self.get_work_item(current_id)
                hierarchy.append(work_item)

                # Default: no parent
                current_id = None

                # Look for parent link
                for relation in work_item.relations or []:
                    if "Hierarchy-Reverse" in relation.rel:
                        current_id = int(relation.url.split("/")[-1])
                        break

            except Exception as e:
                logger.error(f"Error traversing parent chain: {e}")
                break

        return hierarchy

    def get_children(self, work_item_id: int) -> List[Dict]:
        """
        Get direct child work items.

        Args:
            work_item_id: ID of the parent work item

        Returns:
            List[Dict]: List of child work items
        """
        children = []
        try:
            work_item = self.get_work_item(work_item_id)

            for relation in work_item.relations or []:
                if "Hierarchy-Forward" in relation.rel:
                    child_id = int(relation.url.split("/")[-1])
                    try:
                        child = self.get_work_item(child_id)
                        children.append(child)
                    except Exception as e:
                        logger.error(
                            f"Failed to retrieve child work item {child_id}: {e}"
                        )

        except Exception as e:
            logger.error(
                f"Failed to retrieve children for work item {work_item_id}: {e}"
            )

        return children

    def extract_work_item_fields(self, work_item: Dict) -> Dict:
        """
        Extract relevant fields from a work item.

        Args:
            work_item: Work item object from Azure DevOps

        Returns:
            Dict: Dictionary with relevant fields
        """
        fields = work_item.fields
        result = {
            "id": work_item.id,
            "type": fields.get("System.WorkItemType", "Unknown"),
            "title": fields.get("System.Title", "Untitled"),
            "state": fields.get("System.State"),
            "description": fields.get("System.Description"),
            "assigned_to": (
                fields.get("System.AssignedTo", {}).get("displayName")
                if isinstance(fields.get("System.AssignedTo"), dict)
                else fields.get("System.AssignedTo")
            ),
            "created_date": fields.get("System.CreatedDate"),
            "changed_date": fields.get("System.ChangedDate"),
            "story_points": fields.get("Microsoft.VSTS.Scheduling.StoryPoints"),
            "due_date": fields.get("Microsoft.VSTS.Scheduling.DueDate"),
            "remaining_work": fields.get("Microsoft.VSTS.Scheduling.RemainingWork"),
            "original_estimate": fields.get(
                "Microsoft.VSTS.Scheduling.OriginalEstimate"
            ),
            "priority": fields.get("Microsoft.VSTS.Common.Priority"),
            "tags": fields.get("System.Tags"),
        }
        return result

    def get_work_item_hierarchy_tree(
        self, work_item_id: int, levels_up: int = None, levels_down: int = None
    ) -> Dict:
        """
        Get work item hierarchy as a tree structure.

        Args:
            work_item_id: ID of the central work item
            levels_up: Maximum levels to traverse up (None = all)
            levels_down: Maximum levels to traverse down (None = all)

        Returns:
            Dict: Tree structure representing the work item hierarchy
        """
        # Get the parent chain (from current to root)
        parent_chain = self.get_parent_chain(work_item_id)

        # Limit levels up if specified
        if levels_up is not None and len(parent_chain) > levels_up + 1:
            parent_chain = parent_chain[: levels_up + 1]

        # The root is the last item in the parent chain
        if parent_chain:
            root = parent_chain[-1]
            root_data = self.extract_work_item_fields(root)

            # Build the tree
            tree = self._build_tree(root.id, levels_down)

            return tree
        else:
            # No parent chain, return just the current work item
            work_item = self.get_work_item(work_item_id)
            return self.extract_work_item_fields(work_item)

    def _build_tree(self, work_item_id: int, levels_down: Optional[int] = None) -> Dict:
        """
        Recursively build a work item tree.

        Args:
            work_item_id: ID of the root work item
            levels_down: Maximum levels to traverse down (None = all)

        Returns:
            Dict: Tree structure representing the work item hierarchy
        """
        if levels_down is not None and levels_down < 0:
            return None

        work_item = self.get_work_item(work_item_id)
        node = self.extract_work_item_fields(work_item)

        # Only fetch children if we haven't reached maximum depth
        if levels_down is None or levels_down > 0:
            next_level = None if levels_down is None else levels_down - 1
            children = self.get_children(work_item_id)

            if children:
                node["children"] = []
                for child in children:
                    child_tree = self._build_tree(child.id, next_level)
                    if child_tree:
                        node["children"].append(child_tree)

        return node
