"""
GitLab API client for Taskinator.

This module provides functionality to interact with GitLab issues
and their relationships.
"""

import os
import sys
import logging
import time
import traceback
from typing import Dict, List, Optional, Any, Union, Set, Tuple
from urllib.parse import urlparse

try:
    import gitlab

    GITLAB_API_AVAILABLE = True
except ImportError:
    GITLAB_API_AVAILABLE = False

logger = logging.getLogger(__name__)


class GitLabClient:
    """
    Client for GitLab API that provides issue tracking functionality.
    """

    def __init__(self):
        """Initialize the GitLab client."""
        if not GITLAB_API_AVAILABLE:
            raise ImportError(
                "python-gitlab package is not installed. "
                "Install it with 'pip install python-gitlab'"
            )

        self.token = os.getenv("GITLAB_API_TOKEN") or os.getenv("GITLAB_TOKEN")
        self.gitlab_url = os.getenv("GITLAB_URL", "https://gitlab.com")
        self.project_id = os.getenv("GITLAB_PROJECT_ID")

        if not self.token:
            raise ValueError(
                "Environment variable GITLAB_API_TOKEN or GITLAB_TOKEN is not set. "
                "Please set it to your GitLab Personal Access Token."
            )

        if not self.project_id:
            raise ValueError(
                "Environment variable GITLAB_PROJECT_ID is not set. "
                "Please set it to your GitLab project ID or path (namespace/project)."
            )

        self.gl = None
        self.project = None
        self._connect()

    def _connect(self):
        """Connect to GitLab API."""
        try:
            self.gl = gitlab.Gitlab(url=self.gitlab_url, private_token=self.token)
            self.gl.auth()

            # Get the project by ID or path
            try:
                # Try as an integer ID first
                id_or_path = int(self.project_id)
                self.project = self.gl.projects.get(id_or_path)
            except ValueError:
                # If not an integer, it's a path
                # First try direct path lookup
                logger.debug(f"Looking up project by path: {self.project_id}")
                try:
                    self.project = self.gl.projects.get(self.project_id)
                    logger.debug(f"Found project by path: {self.project_id}")
                except Exception as path_error:
                    # If direct path lookup fails, try searching by path
                    logger.debug(f"Path lookup failed: {path_error}, trying search")
                    try:
                        projects = self.gl.projects.list(search=self.project_id.split('/')[-1])
                        for project in projects:
                            if project.path_with_namespace == self.project_id:
                                self.project = project
                                logger.debug(f"Found project by search: {self.project_id}")
                                break
                        else:
                            # Project not found in search results
                            raise ValueError(f"Could not find project: {self.project_id}")
                    except Exception as search_error:
                        # If all methods fail, raise the original error
                        logger.error(f"Project search failed: {search_error}")
                        raise path_error
            logger.info(
                f"Connected to GitLab project: {self.project.path_with_namespace}"
            )
        except Exception as e:
            logger.error(f"Error connecting to GitLab: {e}")
            raise

    def get_issue(self, issue_iid: int) -> Dict:
        """
        Get a GitLab issue by internal ID (iid).

        Args:
            issue_iid: Internal ID of the issue within the project

        Returns:
            Dict: The issue data
        """
        try:
            issue = self.project.issues.get(issue_iid)
            return issue
        except Exception as e:
            logger.error(f"Failed to retrieve issue {issue_iid}: {e}")
            raise

    def get_parent_issue(self, issue_iid: int) -> Optional[Dict]:
        """
        Get the parent issue.

        In GitLab, issues can be linked with different relationships.
        We look for issues with 'relates_to', 'blocks', or other relationships.

        Args:
            issue_iid: Internal ID of the issue

        Returns:
            Optional[Dict]: The parent issue if found, None otherwise
        """
        issue = self.get_issue(issue_iid)

        # Check issue description for linked issues in the format of #123 or project#123
        # Also check for epic links in the description
        parent = self._find_parent_from_description(issue)
        if parent:
            return parent

        # Check for linked issues
        try:
            links = issue.links.list(all=True)

            # Check for blocking issues (issues that block this one are potential parents)
            for link in links:
                # Check if this is a blocking link
                if hasattr(link, "link_type") and link.link_type == "blocks":
                    # If the current issue is blocked by another issue, that's a potential parent
                    if (
                        link.target_issue_iid != issue_iid
                    ):  # Make sure it's not pointing to itself
                        return self.get_issue(link.target_issue_iid)

            # If no blocking issues found, look for related issues
            for link in links:
                if hasattr(link, "link_type") and link.link_type == "relates_to":
                    # Related issue with a lower ID might be a parent (heuristic)
                    if link.target_issue_iid < issue_iid:
                        return self.get_issue(link.target_issue_iid)
        except Exception as e:
            logger.warning(f"Error getting linked issues for {issue_iid}: {e}")

        # Check if issue belongs to an epic
        try:
            if hasattr(issue, "epic") and issue.epic:
                # Return the epic as parent
                return self._get_epic(issue.epic_iid)
        except Exception as e:
            logger.warning(f"Error checking epic for issue {issue_iid}: {e}")

        return None

    def _find_parent_from_description(self, issue) -> Optional[Dict]:
        """
        Find parent issue references from issue description.

        Args:
            issue: GitLab issue object

        Returns:
            Optional[Dict]: Parent issue if found, None otherwise
        """
        if not issue.description:
            return None

        # Check for references like "Parent: #123" or "Relates to: #123"
        import re

        parent_patterns = [
            r"Parent:\s*#(\d+)",
            r"Part of:?\s*#(\d+)",
            r"Related to:?\s*#(\d+)",
            r"Depends on:?\s*#(\d+)",
            r"/parent_of\s*#(\d+)",
            r"/relates_to\s*#(\d+)",
        ]

        for pattern in parent_patterns:
            match = re.search(pattern, issue.description)
            if match:
                parent_iid = int(match.group(1))
                try:
                    return self.get_issue(parent_iid)
                except Exception as e:
                    logger.warning(f"Error retrieving parent issue #{parent_iid}: {e}")

        # Check for epic references
        epic_patterns = [
            r"Epic:?\s*&(\d+)",
            r"Part of epic:?\s*&(\d+)",
        ]

        for pattern in epic_patterns:
            match = re.search(pattern, issue.description)
            if match:
                epic_iid = int(match.group(1))
                try:
                    return self._get_epic(epic_iid)
                except Exception as e:
                    logger.warning(f"Error retrieving epic &{epic_iid}: {e}")

        return None

    def _get_epic(self, epic_iid: int) -> Optional[Dict]:
        """
        Get an epic by its internal ID.

        Args:
            epic_iid: Epic internal ID

        Returns:
            Optional[Dict]: The epic if found and accessible, None otherwise
        """
        try:
            # Check if the project belongs to a group
            if (
                hasattr(self.project, "namespace")
                and self.project.namespace.get("kind") == "group"
            ):
                # Get the group and then the epic
                group = self.gl.groups.get(self.project.namespace.get("id"))
                return group.epics.get(epic_iid)
        except Exception as e:
            logger.warning(f"Error retrieving epic {epic_iid}: {e}")

        return None

    def get_parent_chain(self, issue_iid: int) -> List[Dict]:
        """
        Get the chain of parent issues up to the root.

        Args:
            issue_iid: Internal ID of the issue

        Returns:
            List[Dict]: List of issues in the hierarchy (from leaf to root)
        """
        hierarchy = []
        current_iid = issue_iid
        visited_issues = set()  # To prevent infinite loops

        # Get the original issue first
        try:
            current_issue = self.get_issue(current_iid)
            if current_issue:
                hierarchy.append(current_issue)
                visited_issues.add(current_iid)
        except Exception as e:
            logger.error(f"Error retrieving issue {current_iid}: {e}")
            return hierarchy  # Return empty or partial hierarchy

        max_depth = 10  # Limit the search depth to prevent infinite loops
        depth = 0

        # Find parent chain
        while depth < max_depth:
            parent_issue = self.get_parent_issue(current_iid)

            if not parent_issue:
                break

            # Check if we've already seen this issue to prevent circular references
            if parent_issue.iid in visited_issues:
                logger.warning(
                    f"Circular reference detected for issue {parent_issue.iid}"
                )
                break

            hierarchy.append(parent_issue)
            visited_issues.add(parent_issue.iid)

            current_iid = parent_issue.iid
            depth += 1

        return hierarchy

    def get_children(self, issue_iid: int) -> List[Dict]:
        """
        Get child issues for a given issue.

        This function attempts multiple strategies to find all possible child issues:
        - Epic issues (if issue is an epic)
        - Links where this issue blocks another issue (parent -> child relationship)
        - Links where this issue is related to another issue with specific link types
        - Child references in issue description (Child: #123, Subtask: #123, etc.)
        - Direct child issues (if GitLab API supports it for this project)
        - Issue hierarchy children (if GitLab API supports it for this project)
        
        Args:
            issue_iid: Internal ID of the parent issue

        Returns:
            List[Dict]: List of child issues
        """
        logger.debug(f"Looking for children of issue {issue_iid}")
        children = []
        seen_issue_ids = set()  # To avoid duplicates
        issue = self.get_issue(issue_iid)
        
        # Method 1: Check if this is an epic and get its issues
        if hasattr(issue, "issues") and callable(getattr(issue, "issues", None)):
            try:
                logger.debug(f"Attempting to get epic issues for {issue_iid}")
                epic_issues = issue.issues()
                if epic_issues:
                    logger.debug(f"Found {len(epic_issues)} epic issues")
                    for epic_issue in epic_issues:
                        if epic_issue.iid not in seen_issue_ids:
                            seen_issue_ids.add(epic_issue.iid)
                            children.append(epic_issue)
            except Exception as e:
                logger.warning(f"Error getting epic issues: {e}")

        # Method 2: Check for linked issues that this issue blocks
        try:
            logger.debug(f"Getting linked issues for {issue_iid}")
            links = None
            try:
                links = issue.links.list(all=True)
                logger.debug(f"Found {len(links) if links else 0} links")
            except Exception as link_error:
                logger.warning(f"Error getting links via issue.links.list: {link_error}")
                # Try alternative approach
                try:
                    # Some GitLab versions use different APIs
                    links = self.project.issues.get(issue_iid).links.list()
                    logger.debug(f"Found {len(links) if links else 0} links via alternative method")
                except Exception as alt_link_error:
                    logger.warning(f"Alternative link method also failed: {alt_link_error}")
                    links = None

            if links:
                for link in links:
                    # If this issue blocks another issue, that's a child
                    link_type = getattr(link, "link_type", None)
                    
                    # Different link types that could indicate a child relationship
                    is_child_link = False
                    
                    if link_type == "blocks" or link_type == "child_of":
                        is_child_link = True
                    elif link_type == "relates_to" or link_type == "relates_to_development":
                        # Relates_to could be child OR parent - we handle both
                        is_child_link = True
                    
                    if is_child_link:
                        # Determine target issue ID - different GitLab versions have different attributes
                        target_issue_id = None
                        if hasattr(link, "target_issue_iid"):
                            target_issue_id = link.target_issue_iid
                        elif hasattr(link, "target_issue_id"):
                            target_issue_id = link.target_issue_id
                        elif hasattr(link, "target_iid"):
                            target_issue_id = link.target_iid
                        elif hasattr(link, "target_id"):
                            target_issue_id = link.target_id
                        
                        # Check if current issue is the source
                        source_issue_id = None
                        if hasattr(link, "source_issue_iid"):
                            source_issue_id = link.source_issue_iid
                        elif hasattr(link, "source_issue_id"):
                            source_issue_id = link.source_issue_id
                        elif hasattr(link, "source_iid"):
                            source_issue_id = link.source_iid
                        elif hasattr(link, "source_id"):
                            source_issue_id = link.source_id
                        
                        # For blocking relationships, current issue should be source
                        # For other relationships, could be either way, so check both
                        is_child = False
                        child_id = None
                        
                        if link_type == "blocks" and source_issue_id == issue_iid and target_issue_id:
                            # Current issue blocks another issue (child)
                            is_child = True
                            child_id = target_issue_id
                        elif link_type == "child_of" and target_issue_id == issue_iid and source_issue_id:
                            # Current issue is parent of source issue
                            is_child = True
                            child_id = source_issue_id
                        elif link_type in ("relates_to", "relates_to_development"):
                            # For relates_to, assume target is child if not already seen
                            # This is a heuristic - relates_to is bidirectional
                            if source_issue_id == issue_iid and target_issue_id:
                                is_child = True
                                child_id = target_issue_id
                            elif target_issue_id == issue_iid and source_issue_id:
                                # This could potentially be either parent or child
                                # For relates_to, just add both directions to be safe
                                is_child = True
                                child_id = source_issue_id
                        
                        if is_child and child_id and child_id not in seen_issue_ids:
                            try:
                                logger.debug(f"Found potential child issue {child_id}")
                                child = self.get_issue(child_id)
                                seen_issue_ids.add(child_id)
                                children.append(child)
                            except Exception as e:
                                logger.warning(
                                    f"Error retrieving child issue {child_id}: {e}"
                                )
        except Exception as e:
            logger.warning(f"Error processing linked issues for {issue_iid}: {e}")
            logger.debug(f"Error details: {traceback.format_exc()}")
            
            # Method 3: Try alternative approach if list() call failed
            try:
                logger.debug("Attempting alternative approach for related issues")
                # Try direct API methods that might be available in some GitLab versions
                relation_methods = ["related_issues", "related_merge_requests", "children"]
                
                for method_name in relation_methods:
                    if hasattr(issue, method_name):
                        try:
                            method = getattr(issue, method_name)
                            if callable(method):
                                relations = method.list()
                                logger.debug(f"Found {len(relations)} items from {method_name}")
                                for related in relations:
                                    if hasattr(related, "iid") and related.iid not in seen_issue_ids:
                                        seen_issue_ids.add(related.iid)
                                        children.append(related)
                        except Exception as method_error:
                            logger.debug(f"Method {method_name} failed: {method_error}")
            except Exception as alt_e:
                logger.debug(f"Alternative related issues approach failed: {alt_e}")

        # Method 4: Check issue description for child references
        if issue.description:
            import re

            child_patterns = [
                r"Child:\s*#(\d+)",
                r"Subtask:\s*#(\d+)",
                r"Blocks:\s*#(\d+)",
                r"/blocks\s*#(\d+)",
                r"/child_of\s*#(\d+)",
                r"Child task:?\s*#(\d+)",
                r"Sub-?task:?\s*#(\d+)",
                r"Children:?[\s\n]*#(\d+)",  # Multiple children with newlines
            ]

            for pattern in child_patterns:
                for match in re.finditer(pattern, issue.description):
                    child_iid = int(match.group(1))
                    if child_iid not in seen_issue_ids:
                        try:
                            logger.debug(f"Found child reference #{child_iid} in description")
                            child = self.get_issue(child_iid)
                            seen_issue_ids.add(child_iid)
                            children.append(child)
                        except Exception as e:
                            logger.warning(
                                f"Error retrieving child issue #{child_iid} from description: {e}"
                            )
            
            # Also check for issue URLs in description
            # These might be in the format https://gitlab.com/namespace/project/-/issues/123
            url_pattern = rf"https?://[^/]+/[^/]+/[^/]+/-/issues/(\d+)"
            for match in re.finditer(url_pattern, issue.description):
                child_iid = int(match.group(1))
                if child_iid not in seen_issue_ids and child_iid != issue_iid:  # Skip self-references
                    try:
                        logger.debug(f"Found child URL reference to issue #{child_iid} in description")
                        child = self.get_issue(child_iid)
                        seen_issue_ids.add(child_iid)
                        children.append(child)
                    except Exception as e:
                        logger.warning(
                            f"Error retrieving child issue #{child_iid} from URL reference: {e}"
                        )
                        
        # Log results
        logger.debug(f"Found {len(children)} children for issue {issue_iid}")
        return children

    def extract_issue_fields(self, issue: Dict) -> Dict:
        """
        Extract relevant fields from a GitLab issue or epic.

        Args:
            issue: GitLab issue object

        Returns:
            Dict: Dictionary with relevant fields
        """
        is_epic = hasattr(issue, "title") and not hasattr(issue, "iid")

        result = {
            "id": issue.iid if hasattr(issue, "iid") else issue.id,
            "global_id": issue.id,
            "type": "epic" if is_epic else "issue",
            "title": issue.title,
            "description": issue.description,
            "state": issue.state,
            "created_at": issue.created_at,
            "updated_at": issue.updated_at,
            "web_url": issue.web_url if hasattr(issue, "web_url") else None,
        }

        # Add additional fields specific to issues
        if not is_epic and hasattr(issue, "labels"):
            result["labels"] = issue.labels

        # Handle assignees - could be list of dicts, list of objects, or single object
        if hasattr(issue, "assignees"):
            assignees = []
            if issue.assignees:
                for assignee in issue.assignees:
                    if isinstance(assignee, dict) and "name" in assignee:
                        assignees.append(assignee.get("name", ""))
                    elif hasattr(assignee, "name"):
                        assignees.append(assignee.name)
                    else:
                        assignees.append(str(assignee))
            result["assignees"] = assignees
        elif hasattr(issue, "assignee") and issue.assignee:
            if isinstance(issue.assignee, dict) and "name" in issue.assignee:
                result["assignees"] = [issue.assignee.get("name", "")]
            elif hasattr(issue.assignee, "name"):
                result["assignees"] = [issue.assignee.name]
            else:
                result["assignees"] = [str(issue.assignee)]

        # Extract weight (story points) if available
        if hasattr(issue, "weight") and issue.weight is not None:
            result["story_points"] = issue.weight

        # Extract due date if available
        if hasattr(issue, "due_date") and issue.due_date:
            result["due_date"] = issue.due_date

        # Extract milestone if available
        if hasattr(issue, "milestone") and issue.milestone:
            # Check if milestone is a dictionary or an object
            if isinstance(issue.milestone, dict):
                result["milestone"] = issue.milestone.get("title", "")
            elif hasattr(issue.milestone, "title"):
                result["milestone"] = issue.milestone.title
            else:
                result["milestone"] = str(issue.milestone)

        # Extract time tracking if available
        if hasattr(issue, "time_stats") and issue.time_stats:
            try:
                # Handle different object types for time_stats
                if callable(issue.time_stats):
                    # If time_stats is a method, call it
                    time_stats_data = issue.time_stats()
                    if isinstance(time_stats_data, dict):
                        result["time_estimate"] = time_stats_data.get("time_estimate", 0)
                        result["total_time_spent"] = time_stats_data.get("total_time_spent", 0)
                    else:
                        result["time_estimate"] = getattr(time_stats_data, "time_estimate", 0)
                        result["total_time_spent"] = getattr(time_stats_data, "total_time_spent", 0)
                elif isinstance(issue.time_stats, dict):
                    result["time_estimate"] = issue.time_stats.get("time_estimate", 0)
                    result["total_time_spent"] = issue.time_stats.get("total_time_spent", 0)
                elif hasattr(issue.time_stats, "time_estimate"):
                    # If it's an object with attributes
                    result["time_estimate"] = getattr(issue.time_stats, "time_estimate", 0)
                    result["total_time_spent"] = getattr(issue.time_stats, "total_time_spent", 0)
                else:
                    logger.warning(f"time_stats has unsupported type: {type(issue.time_stats)}")
                    result["time_estimate"] = 0
                    result["total_time_spent"] = 0
            except Exception as e:
                logger.warning(f"Error processing time_stats: {e}")
                result["time_estimate"] = 0
                result["total_time_spent"] = 0

        return result

    def get_issue_hierarchy_tree(
        self, issue_iid: int, levels_up: int = None, levels_down: int = None
    ) -> Dict:
        """Get issue hierarchy as a tree structure.
        
        This function fetches the entire issue structure, including parents and children.
        When debugging, enable DEBUG level logging for detailed diagnostics.
        
        Args:
            issue_iid: The internal issue ID to fetch
            levels_up: How many parent levels to include (None = all)
            levels_down: How many child levels to include (None = all)
            
        Returns:
            Dict containing the issue hierarchy structure
        
        Raises:
            Exception: Various GitLab API or parsing errors that might occur
        """
        """
        Get issue hierarchy as a tree structure.

        Args:
            issue_iid: Internal ID of the central issue
            levels_up: Maximum levels to traverse up (None = all)
            levels_down: Maximum levels to traverse down (None = all)

        Returns:
            Dict: Tree structure representing the issue hierarchy
        """
        # Get the parent chain (from current to root)
        try:
            logger.debug(f"Getting parent chain for issue_iid: {issue_iid}")
            parent_chain = self.get_parent_chain(issue_iid)
            logger.debug(f"Parent chain length: {len(parent_chain) if parent_chain else 0}")
        except Exception as e:
            logger.error(f"Error getting parent chain: {e}")
            logger.debug(f"Parent chain error details: {traceback.format_exc()}")
            parent_chain = []

        # Limit levels up if specified
        if levels_up is not None and len(parent_chain) > levels_up + 1:
            parent_chain = parent_chain[: levels_up + 1]

        # The root is the last item in the parent chain
        if parent_chain:
            # If we want the focus to be on the original issue, not the root
            root_issue = parent_chain[0]  # Start with the original issue
            root_data = self.extract_issue_fields(root_issue)

            # Build the tree for children
            tree = self._build_tree(root_issue.iid, levels_down)

            # If we have parents, add them to the tree as context
            if len(parent_chain) > 1:
                root_data["parent_context"] = []
                for parent in parent_chain[1:]:
                    parent_data = self.extract_issue_fields(parent)
                    root_data["parent_context"].append(parent_data)

            return tree
        else:
            # No parent chain, return just the current issue
            issue = self.get_issue(issue_iid)
            return self.extract_issue_fields(issue)

    def _build_tree(self, issue_iid: int, levels_down: Optional[int] = None) -> Dict:
        """
        Recursively build an issue tree.

        This method builds a complete tree structure for the issue hierarchy,
        recursively fetching all child issues up to the specified depth.
        
        Args:
            issue_iid: Internal ID of the root issue
            levels_down: Maximum levels to traverse down (None = all)

        Returns:
            Dict: Tree structure representing the issue hierarchy
        """
        if levels_down is not None and levels_down < 0:
            logger.debug(f"Reached maximum depth for issue {issue_iid}")
            return None

        logger.debug(f"Building tree for issue {issue_iid} (levels_down: {levels_down})")
        
        # Fetch the issue
        try:
            issue = self.get_issue(issue_iid)
            node = self.extract_issue_fields(issue)
        except Exception as e:
            logger.error(f"Error getting issue {issue_iid} for tree building: {e}")
            return None

        # Only fetch children if we haven't reached maximum depth
        if levels_down is None or levels_down > 0:
            next_level = None if levels_down is None else levels_down - 1
            
            try:
                logger.debug(f"Fetching children for issue {issue_iid}")
                children = self.get_children(issue_iid)
                
                if children:
                    logger.debug(f"Found {len(children)} children for issue {issue_iid}")
                    node["children"] = []
                    
                    for i, child in enumerate(children):
                        try:
                            # Get child IID, handling different object types
                            child_iid = None
                            if hasattr(child, "iid"):
                                child_iid = child.iid
                            elif isinstance(child, dict) and "iid" in child:
                                child_iid = child["iid"]
                            elif hasattr(child, "id"):
                                child_iid = child.id
                            elif isinstance(child, dict) and "id" in child:
                                child_iid = child["id"]
                                
                            if not child_iid:
                                logger.warning(f"Could not determine IID for child {i} of issue {issue_iid}")
                                continue
                                
                            logger.debug(f"Building subtree for child {child_iid} of issue {issue_iid}")
                            child_tree = self._build_tree(child_iid, next_level)
                            
                            if child_tree:
                                node["children"].append(child_tree)
                                logger.debug(f"Added child {child_iid} to issue {issue_iid} tree")
                            else:
                                logger.warning(f"Failed to build tree for child {child_iid} of issue {issue_iid}")
                        except Exception as child_error:
                            logger.warning(f"Error processing child {i} of issue {issue_iid}: {child_error}")
                            continue
                else:
                    logger.debug(f"No children found for issue {issue_iid}")
            except Exception as e:
                logger.warning(f"Error getting children for issue {issue_iid}: {e}")

        return node
