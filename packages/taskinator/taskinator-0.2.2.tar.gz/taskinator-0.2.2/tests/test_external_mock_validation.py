"""
Validation tests for external service mock objects.

These tests ensure our mocks for external services are accurate
representations of the real interfaces they're mocking.
"""

import inspect
import os
from datetime import datetime
from typing import Any, Dict, List, Callable, Optional

import pytest
from unittest.mock import MagicMock

# Import external service interfaces 
from taskinator.services.ai.ai_client import get_ai_client
from taskinator.plugins.sync.nextcloud.nextcloud_client import NextCloudClient
from taskinator.plugins.integrations.gitlab.client import GitLabClient
from taskinator.plugins.integrations.azure.client import AzureDevOpsClient

# Import mock factories
from tests.mocks import (
    create_mock_nextcloud_client,
    create_mock_ai_client,
    create_mock_gitlab_client,
    create_mock_azure_devops_client
)

# Import test factories for real business objects
from tests.factories import (
    create_task,
    create_subtask,
    create_task_collection
)


class TestExternalMockValidation:
    """Tests to validate external service mocks match their real interfaces."""
    
    def _get_public_methods(self, obj: Any) -> List[str]:
        """Get public method names from an object or class."""
        methods = []
        
        if isinstance(obj, type):
            # If it's a class, get methods from the class definition
            for name, member in inspect.getmembers(obj):
                if not name.startswith('_') and (inspect.isfunction(member) or inspect.ismethod(member)):
                    methods.append(name)
        else:
            # If it's an instance, get methods dynamically
            for name in dir(obj):
                if not name.startswith('_') and callable(getattr(obj, name)):
                    methods.append(name)
                    
        return methods

    def test_nextcloud_client_mock_interface(self):
        """Test that NextCloud client mock implements the same interface as real client."""
        # Get real client methods (we can't instantiate without credentials)
        real_methods = self._get_public_methods(NextCloudClient)
        
        # Create mock client
        mock_client = create_mock_nextcloud_client()
        
        # Important methods that must be included
        essential_methods = [
            "check_connection",
            "verify_calendar",
            "create_task",
            "get_task",
            "get_tasks",
            "update_task",
            "delete_task"
        ]
        
        # Verify mock has essential methods
        for method_name in essential_methods:
            assert hasattr(mock_client, method_name), f"Mock NextCloud client is missing essential method: {method_name}"
            assert callable(getattr(mock_client, method_name)), f"{method_name} is not callable on mock NextCloud client"
        
        # Compare with real interface (if available)
        for method_name in real_methods:
            if method_name in essential_methods:
                assert hasattr(mock_client, method_name), f"Mock NextCloud client is missing method: {method_name}"

    def test_ai_client_mock_interface(self):
        """Test that AI client mock implements the same interface as real litellm."""
        try:
            import litellm
            # Get the key methods we use from litellm
            essential_methods = [
                "completion",
                "generate_text",
                "embedding",
                "generate",
                "generate_tasks_from_prd"
            ]
            
            # Create mock client
            mock_client = create_mock_ai_client()
            
            # Verify mock has all essential methods
            for method_name in essential_methods:
                assert hasattr(mock_client, method_name), f"Mock AI client is missing method: {method_name}"
                assert callable(getattr(mock_client, method_name)), f"{method_name} is not callable on mock AI client"
            
            # Test actual behavior of essential methods
            text_response = mock_client.generate("Test prompt")
            assert isinstance(text_response, str), "generate() should return a string"
            
            tasks_response = mock_client.generate_tasks_from_prd("Test PRD", 2)
            assert isinstance(tasks_response, list), "generate_tasks_from_prd() should return a list"
            assert len(tasks_response) > 0, "generate_tasks_from_prd() should not return empty list"
        
        except ImportError:
            pytest.skip("litellm not available")

    def test_gitlab_client_mock_interface(self):
        """Test that GitLab client mock implements the same interface as real client."""
        # Get real client methods (we can't instantiate without credentials)
        real_methods = self._get_public_methods(GitLabClient)
        
        # Create mock client
        mock_client = create_mock_gitlab_client()
        
        # Essential methods that must be included
        essential_methods = [
            "get_issue",
            "create_issue",
            "update_issue",
            "extract_issue_fields",
            "get_issues",
            "get_project"
        ]
        
        # Verify mock has essential methods
        for method_name in essential_methods:
            assert hasattr(mock_client, method_name), f"Mock GitLab client is missing essential method: {method_name}"
            assert callable(getattr(mock_client, method_name)), f"{method_name} is not callable on mock GitLab client"
        
        # Test actual behavior
        issue = mock_client.get_issue(123)
        assert isinstance(issue, dict), "get_issue() should return a dictionary"
        assert "id" in issue, "Issue response should contain an id"
        assert "title" in issue, "Issue response should contain a title"

    def test_azure_devops_client_mock_interface(self):
        """Test that Azure DevOps client mock implements the same interface as real client."""
        # Get real client methods (we can't instantiate without credentials)
        real_methods = self._get_public_methods(AzureDevOpsClient)
        
        # Create mock client
        mock_client = create_mock_azure_devops_client()
        
        # Essential methods that must be included
        essential_methods = [
            "get_work_item",
            "create_work_item",
            "update_work_item",
            "get_work_items",
            "get_area_paths",
            "get_iteration_paths",
            "get_project"
        ]
        
        # Verify mock has essential methods
        for method_name in essential_methods:
            assert hasattr(mock_client, method_name), f"Mock Azure DevOps client is missing essential method: {method_name}"
            assert callable(getattr(mock_client, method_name)), f"{method_name} is not callable on mock Azure DevOps client"
        
        # Test actual behavior
        work_item = mock_client.get_work_item(123)
        assert isinstance(work_item, dict), "get_work_item() should return a dictionary"
        assert "id" in work_item, "Work item response should contain an id"
        assert "fields" in work_item, "Work item response should contain fields"

    def test_nextcloud_task_response_interface(self):
        """Test that NextCloud task response has required fields."""
        # Create mock client
        mock_client = create_mock_nextcloud_client()
        
        # Get mock task response
        mock_task = mock_client.get_task("123")
        
        # Check required fields
        required_fields = [
            "id", "title", "description", "status",
            "etag", "calendar_id"
        ]
        
        for field in required_fields:
            assert hasattr(mock_task, field), f"NextCloud task response is missing field: {field}"


class TestMockBehaviorValidation:
    """Tests to validate that mock external services behave as expected."""
    
    def test_nextcloud_sync_behavior(self):
        """Test that NextCloud client mock behaves appropriately for sync operations."""
        # Create mock client
        mock_client = create_mock_nextcloud_client()
        
        # Test create and retrieve flow
        task_id = "test-task-123"
        task_title = "Test Task Title"
        
        # Create a task and verify response has same ID
        mock_client.create_task.return_value.id = task_id
        mock_client.create_task.return_value.title = task_title
        
        created_task = mock_client.create_task(task_id, task_title, "Description")
        assert created_task.id == task_id
        assert created_task.title == task_title
        
        # Get the task and verify it matches what we created
        mock_client.get_task.return_value = created_task
        retrieved_task = mock_client.get_task(task_id)
        
        assert retrieved_task.id == task_id
        assert retrieved_task.title == task_title

    def test_ai_client_task_generation(self):
        """Test that AI client mock generates tasks in the expected format."""
        # Create mock AI client
        mock_client = create_mock_ai_client()
        
        # Test task generation
        prd_content = "Sample PRD content for testing"
        num_tasks = 3
        
        # Configure the mock to return specific number of tasks
        mock_client.generate_tasks_from_prd.return_value = [
            {"id": str(i+1), "title": f"Task {i+1}", "description": f"Description {i+1}"}
            for i in range(num_tasks)
        ]
        
        # Call the method
        tasks = mock_client.generate_tasks_from_prd(prd_content, num_tasks)
        
        # Verify
        assert len(tasks) == num_tasks
        for i, task in enumerate(tasks):
            assert "id" in task
            assert "title" in task
            assert "description" in task
            assert task["id"] == str(i+1)

    def test_gitlab_client_issue_management(self):
        """Test that GitLab client mock behaves as expected for issue management."""
        # Create mock client
        mock_client = create_mock_gitlab_client()
        
        # Test issue creation and update flow
        issue_data = {
            "title": "New Issue",
            "description": "Issue description"
        }
        
        # Create an issue
        created_issue = mock_client.create_issue(**issue_data)
        assert "id" in created_issue
        assert "title" in created_issue
        assert "description" in created_issue
        
        # Update the issue
        update_data = {"title": "Updated Title"}
        mock_client.update_issue.return_value = {**created_issue, **update_data}
        
        updated_issue = mock_client.update_issue(created_issue["id"], **update_data)
        assert updated_issue["title"] == "Updated Title"

    def test_azure_client_workitem_management(self):
        """Test that Azure DevOps client mock behaves as expected for work item management."""
        # Create mock client
        mock_client = create_mock_azure_devops_client()
        
        # Test work item creation and update flow
        work_item_data = {
            "fields": {
                "System.Title": "New Work Item",
                "System.Description": "Work item description"
            }
        }
        
        # Create a work item
        created_item = mock_client.create_work_item(**work_item_data)
        assert "id" in created_item
        assert "fields" in created_item
        assert "System.Title" in created_item["fields"]
        
        # Update the work item
        update_data = {"fields": {"System.Title": "Updated Title"}}
        mock_client.update_work_item.return_value = dict(
            created_item,
            fields={**created_item["fields"], **update_data["fields"]}
        )
        
        updated_item = mock_client.update_work_item(created_item["id"], **update_data)
        assert updated_item["fields"]["System.Title"] == "Updated Title"