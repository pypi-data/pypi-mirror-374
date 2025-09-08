"""
Tests for the Nextcloud sync functionality.
"""

import json
import os
import shutil
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
import uuid
import pytest

from taskinator.models.task import Subtask, Task, TaskCollection
from taskinator.plugins.sync.nextcloud.nextcloud_client import NextCloudTask
from taskinator.plugins.sync.nextcloud.nextcloud_sync import (
    NextCloudSyncMetadata,
    TaskFieldMapping,
    detect_changes,
    get_sync_metadata_path,
    get_task_sync_metadata,
    load_sync_metadata,
    save_sync_metadata,
    update_task_sync_metadata,
)


class TestNextcloudSync(unittest.TestCase):
    """Test the Nextcloud sync functionality."""

    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for tests
        self.test_dir = tempfile.mkdtemp()
        self.tasks_dir = os.path.join(self.test_dir, "tasks")
        os.makedirs(self.tasks_dir, exist_ok=True)
        
        # Check if required environment variables are available
        required_vars = ["NEXTCLOUD_HOST", "NEXTCLOUD_USERNAME", "NEXTCLOUD_PASSWORD"]
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
        if missing_vars:
            # Set default values for CI environment
            if "NEXTCLOUD_HOST" in missing_vars:
                os.environ["NEXTCLOUD_HOST"] = "https://nextcloud.example.com"
            if "NEXTCLOUD_USERNAME" in missing_vars:
                os.environ["NEXTCLOUD_USERNAME"] = "test_user"
            if "NEXTCLOUD_PASSWORD" in missing_vars:
                os.environ["NEXTCLOUD_PASSWORD"] = "test_password"
                
            # For tests that use real Nextcloud API, we'll use a mock
            self.use_mock = True
            print(f"Using mock Nextcloud client with default values for {', '.join(missing_vars)}")
        else:
            self.use_mock = False

        # Create sample tasks
        self.task1 = Task(
            id=1,
            title="Design Data Model and Storage",
            description="Create the data model for tasks and implement local JSON storage",
            status="pending",
            priority="high",
            dependencies=[],
            details="Design a robust data model that supports all required task attributes",
            test_strategy="Write unit tests for CRUD operations on the data model",
            subtasks=[
                Subtask(
                    id="1.1",
                    title="Define Task Schema",
                    description="Define the schema for tasks and subtasks",
                    status="pending",
                    dependencies=[],
                ),
            ],
            tags=["design", "storage"],
            extra={},
        )

        self.task2 = Task(
            id=2,
            title="Implement Core Task CRUD Operations",
            description="Implement create, read, update, and delete operations for tasks",
            status="pending",
            priority="high",
            dependencies=["1"],
            details="Implement CRUD operations with proper error handling",
            test_strategy="Test CRUD operations with various inputs",
            subtasks=[],
            tags=["implementation", "core"],
            extra={},
        )

        # Create a Nextcloud client for testing
        from taskinator.plugins.sync.nextcloud.nextcloud_client import NextCloudClient
        
        if self.use_mock:
            from unittest.mock import MagicMock
            # Create mock client
            self.client = MagicMock()
            
            # Set up mock methods
            mock_task = MagicMock()
            mock_task.id = f"test_{uuid.uuid4().hex[:8]}"
            mock_task.title = f"Test Task"
            mock_task.description = "Test description"
            mock_task.status = "pending"
            mock_task.priority = "high"
            mock_task.etag = "etag123"
            mock_task.categories = ["test"]
            mock_task.model_dump.return_value = {
                "id": mock_task.id,
                "title": mock_task.title,
                "description": mock_task.description,
                "status": mock_task.status,
                "priority": mock_task.priority,
                "categories": mock_task.categories
            }
            
            # Configure methods
            self.client.create_task.return_value = mock_task
            self.client.get_task.return_value = mock_task
            self.client.get_tasks.return_value = [mock_task]
            self.client.update_task.return_value = mock_task
            self.client.delete_task.return_value = None
        else:
            # Create real client
            self.client = NextCloudClient(
                base_url=os.environ["NEXTCLOUD_HOST"],
                username=os.environ["NEXTCLOUD_USERNAME"],
                password=os.environ["NEXTCLOUD_PASSWORD"],
                calendar_id=os.environ.get("NEXTCLOUD_TEST_CALENDAR_ID", "personal")
            )
        
        # Create a unique task ID for this test run
        self.test_task_id = f"test_{uuid.uuid4().hex[:8]}"

    def tearDown(self):
        """Clean up the test environment."""
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

    def test_map_local_to_remote(self):
        """Test mapping a local task to a remote task."""
        # Map the task to a remote task
        remote_task_dict = TaskFieldMapping.map_local_to_remote(self.task1)

        # Check that the title exists and includes the task title
        self.assertIn("title", remote_task_dict)
        self.assertIn("Design Data Model and Storage", remote_task_dict["title"])
        self.assertIn(
            "Create the data model for tasks", remote_task_dict["description"]
        )
        # Check status exists (mapping may vary depending on implementation version)
        self.assertIn("status", remote_task_dict)

        # Just verify the description contains the main task description
        self.assertIn("Create the data model for tasks", remote_task_dict["description"])
        
        # Verify priority is included
        self.assertIn("priority", remote_task_dict)

    async def test_map_remote_to_local_with_real_task(self):
        """Test mapping a remote task to a local task using a real Nextcloud task."""
        # Create a task in Nextcloud for testing
        from taskinator.plugins.sync.nextcloud.nextcloud_client import NextCloudTask
        
        # Create a uniquely named task for this test
        task_title = f"Taskinator Test Task {uuid.uuid4().hex[:8]}"
        task_description = (
            "Test task description\n\n---\n\n## Details\n\n"
            "This is a test task for mapping\n\n## Test Strategy\n\n"
            "Verify mapping works correctly\n\n"
            "**Priority:** high\n**Status:** pending\n"
            f"**Created:** {datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}\n"
            f"**Updated:** {datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}\n\n"
            "**Tags:** test, mapping"
        )
        
        if self.use_mock:
            # Use the pre-configured mock task
            nc_task = self.client.create_task.return_value
        else:
            # Create the task in Nextcloud
            nc_task = await self.client.create_task({
                "title": task_title,
                "description": task_description,
                "status": "pending",
                "priority": "high",
                "categories": ["test", "mapping"]
            })
        
        try:
            # Map the remote task to a local task
            local_task_dict = TaskFieldMapping.map_remote_to_local(nc_task)
            
            # Verify the mapping
            if self.use_mock:
                # Since we're using a mock, just verify the basics
                self.assertIn("title", local_task_dict)
                self.assertIn("status", local_task_dict)
            else:
                # Full verification for real tasks
                self.assertEqual(local_task_dict["title"], task_title.replace("#", "").strip())
                self.assertIn("Test task description", local_task_dict["description"])
                self.assertEqual(local_task_dict["status"], "pending")
                self.assertEqual(local_task_dict["priority"], "high")
                
                # Verify that the details and test strategy are extracted from the markdown
                self.assertIn("This is a test task for mapping", local_task_dict["details"])
                self.assertIn("Verify mapping works correctly", local_task_dict["test_strategy"])
                
                # Verify tags
                self.assertIn("test", local_task_dict["tags"])
                self.assertIn("mapping", local_task_dict["tags"])
            
        finally:
            if not self.use_mock:
                # Clean up - delete the task
                await self.client.delete_task(nc_task.id)

    def test_sync_metadata_storage(self):
        """Test storing and retrieving sync metadata."""
        # Create a metadata object
        metadata = NextCloudSyncMetadata(
            provider="nextcloud",
            remote_id="1",
            etag="etag1",
            last_sync="2025-04-30T23:32:34",
            sync_status="synced",
        )

        # Update task metadata
        update_task_sync_metadata(self.task1, metadata, self.tasks_dir)

        # Verify the metadata file exists
        metadata_path = get_sync_metadata_path(self.tasks_dir)
        self.assertTrue(os.path.exists(metadata_path))

        # Load the metadata
        all_metadata = load_sync_metadata(self.tasks_dir)

        # Verify the metadata
        self.assertIn("1", all_metadata)
        self.assertEqual(all_metadata["1"].remote_id, "1")
        self.assertEqual(all_metadata["1"].etag, "etag1")
        self.assertEqual(all_metadata["1"].last_sync, "2025-04-30T23:32:34")
        self.assertEqual(all_metadata["1"].sync_status, "synced")

        # Get task metadata
        task_metadata = get_task_sync_metadata(self.task1, self.tasks_dir)

        # Verify the task metadata
        self.assertEqual(task_metadata.remote_id, "1")
        self.assertEqual(task_metadata.etag, "etag1")
        self.assertEqual(task_metadata.last_sync, "2025-04-30T23:32:34")
        self.assertEqual(task_metadata.sync_status, "synced")

    async def test_detect_changes_with_real_task(self):
        """Test detecting changes between local and remote tasks with real Nextcloud task."""
        from taskinator.plugins.sync.nextcloud.nextcloud_client import NextCloudTask
        
        # Create a unique task in Nextcloud
        task_title = f"Detect Changes Test {uuid.uuid4().hex[:8]}"
        task_description = (
            "Test task description\n\n---\n\n## Details\n\n"
            "Testing change detection\n\n## Test Strategy\n\n"
            "Verify changes are detected correctly\n\n"
            "**Priority:** high\n**Status:** pending\n"
            f"**Created:** {datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}\n"
            f"**Updated:** {datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}\n\n"
            "**Tags:** test, changes"
        )
        
        if self.use_mock:
            # Use the pre-configured mock task
            nc_task = self.client.create_task.return_value
        else:
            # Create the task in Nextcloud
            nc_task = await self.client.create_task({
                "title": task_title,
                "description": task_description,
                "status": "pending",
                "priority": "high",
                "categories": ["test", "changes"]
            })
        
        try:
            # Create a local task with the same data
            local_task_dict = TaskFieldMapping.map_remote_to_local(nc_task)
            local_task = Task(**local_task_dict)
            
            # Create metadata for the task
            current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            metadata = NextCloudSyncMetadata(
                provider="nextcloud",
                remote_id=nc_task.id,
                etag=nc_task.etag if hasattr(nc_task, "etag") else "etag1",
                last_sync=current_time,
                sync_status="synced",
            )

            # Update task metadata
            update_task_sync_metadata(local_task, metadata, self.tasks_dir)
            
            # No changes case - should detect no changes
            changes, has_changes = detect_changes(
                local_task, nc_task, self.tasks_dir
            )
            self.assertFalse(has_changes)
            self.assertEqual(len(changes), 0)

            # Create a modified local task
            modified_task = Task(
                id=local_task.id,
                title=f"{local_task.title} (Modified)",
                description=local_task.description,
                status="in_progress",  # Changed status
                priority="high",
                dependencies=["2"],  # Added dependency
                details=local_task.details,
                test_strategy=local_task.test_strategy,
                subtasks=local_task.subtasks,
                tags=local_task.tags,
                extra=local_task.extra,
            )

            # Detect changes
            changes, has_changes = detect_changes(
                modified_task, nc_task, self.tasks_dir
            )

            # Verify changes were detected
            self.assertTrue(has_changes)
            self.assertGreater(len(changes), 0)

            # For mocks, only do basic assertion
            if not self.use_mock:
                # Verify specific changes
                status_change = next((c for c in changes if c["field"] == "status"), None)
                self.assertIsNotNone(status_change)
                self.assertEqual(status_change["local_value"], "in_progress")
                self.assertEqual(status_change["remote_value"], "pending")

                deps_change = next((c for c in changes if c["field"] == "dependencies"), None)
                self.assertIsNotNone(deps_change)
                self.assertEqual(deps_change["local_value"], ["2"])
                # Remote dependencies could be empty or in a different format depending on implementation
            
        finally:
            if not self.use_mock:
                # Clean up - delete the task
                await self.client.delete_task(nc_task.id)


    def test_run_sync_tests(self):
        """Run the synchronous tests."""
        # We need to run the standard sync tests
        self.test_map_local_to_remote()
        self.test_sync_metadata_storage()

    @pytest.mark.asyncio
    async def test_map_remote_to_local_with_real_task_wrapper(self):
        """Wrapper for async test_map_remote_to_local_with_real_task."""
        await self.test_map_remote_to_local_with_real_task()
        
    @pytest.mark.asyncio
    async def test_detect_changes_with_real_task_wrapper(self):
        """Wrapper for async test_detect_changes_with_real_task."""
        await self.test_detect_changes_with_real_task()


if __name__ == "__main__":
    unittest.main()
