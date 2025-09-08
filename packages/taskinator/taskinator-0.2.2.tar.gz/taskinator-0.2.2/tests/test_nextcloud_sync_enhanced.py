"""
Tests for the enhanced Nextcloud sync functionality.
"""

import json
import os
import shutil
import tempfile
import unittest
import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from taskinator.models.task import Subtask, Task, TaskCollection
from taskinator.plugins.sync.nextcloud.nextcloud_client import NextCloudTask
from taskinator.plugins.sync.nextcloud.nextcloud_plugin import NextCloudSyncPlugin 
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
from taskinator.plugins.sync.plugin_base import SyncDirection, SyncStatus


class TestNextcloudSyncEnhanced(unittest.TestCase):
    """Test the enhanced Nextcloud sync functionality."""

    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for tests
        self.test_dir = tempfile.mkdtemp()
        self.tasks_dir = os.path.join(self.test_dir, "tasks")
        os.makedirs(self.tasks_dir, exist_ok=True)
        self.tasks_json_path = os.path.join(self.tasks_dir, "tasks.json")

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
            subtasks=[],
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

        # Create a task collection
        self.task_collection = TaskCollection(
            tasks=[self.task1, self.task2],
            metadata={
                "project_name": "Test Project",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "version": "0.1.0",
            },
        )

        # Create a mock client
        self.mock_client = MagicMock()

        # Create a plugin with the mock client
        self.plugin = NextCloudSyncPlugin ()
        self.plugin.client = self.mock_client

        # Mock the config attribute
        self.plugin.config = MagicMock()
        self.plugin.config.host = "https://nextcloud.example.com"
        self.plugin.config.username = "test_user"
        self.plugin.config.calendar_id = "personal"

        # Mock write_tasks to avoid the 'str' object has no attribute 'model_dump' error
        self.write_tasks_patcher = patch(
            "taskinator.plugins.sync.nextcloud.nextcloud_plugin.write_tasks"
        )
        self.mock_write_tasks = self.write_tasks_patcher.start()

        # Save tasks to file
        with open(self.tasks_json_path, "w") as f:
            json.dump(self.task_collection.model_dump(), f)

    def tearDown(self):
        """Clean up the test environment."""
        # Stop the patcher
        self.write_tasks_patcher.stop()

        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

    @pytest.mark.asyncio
    async def test_get_status_basic(self):
        """Test getting basic sync status."""
        # Create metadata for task1 (synced)
        metadata1 = NextCloudSyncMetadata(
            provider="nextcloud",
            remote_id="remote1",
            etag="etag1",
            last_sync="2025-05-02T09:33:18",
            sync_status=SyncStatus.SYNCED,
        )
        update_task_sync_metadata(self.task1, metadata1, self.tasks_dir)

        # Create metadata for task2 (conflict)
        metadata2 = NextCloudSyncMetadata(
            provider="nextcloud",
            remote_id="remote2",
            etag="etag2",
            last_sync="2025-05-02T09:33:18",
            sync_status=SyncStatus.CONFLICT,
        )
        update_task_sync_metadata(self.task2, metadata2, self.tasks_dir)

        # Get status
        status = await self.plugin.get_status(self.tasks_json_path)

        # Verify status
        self.assertEqual(status["total"], 2)
        self.assertEqual(status["synced"], 1)
        self.assertEqual(status["conflict"], 1)
        self.assertEqual(status["pending"], 0)
        self.assertEqual(status["error"], 0)
        self.assertEqual(status["not_synced"], 0)

    @pytest.mark.asyncio
    async def test_get_status_verbose(self):
        """Test getting verbose sync status."""
        # Create metadata for task1 (synced)
        metadata1 = NextCloudSyncMetadata(
            provider="nextcloud",
            remote_id="remote1",
            etag="etag1",
            last_sync="2025-05-02T09:33:18",
            sync_status=SyncStatus.SYNCED,
        )
        update_task_sync_metadata(self.task1, metadata1, self.tasks_dir)

        # Create metadata for task2 (conflict)
        metadata2 = NextCloudSyncMetadata(
            provider="nextcloud",
            remote_id="remote2",
            etag="etag2",
            last_sync="2025-05-02T09:33:18",
            sync_status=SyncStatus.CONFLICT,
        )
        update_task_sync_metadata(self.task2, metadata2, self.tasks_dir)

        # Get status with verbose flag
        status = await self.plugin.get_status(self.tasks_json_path, verbose=True)

        # Verify status
        self.assertEqual(status["total"], 2)
        self.assertEqual(status["synced"], 1)
        self.assertEqual(status["conflict"], 1)

        # Verify details
        self.assertIn("details", status)
        self.assertIn("1", status["details"])
        self.assertIn("2", status["details"])

        # Verify task1 details
        self.assertEqual(
            status["details"]["1"]["title"], "Design Data Model and Storage"
        )
        self.assertEqual(status["details"]["1"]["status"], "synced")
        self.assertEqual(status["details"]["1"]["remote_id"], "remote1")

        # Verify task2 details
        self.assertEqual(
            status["details"]["2"]["title"], "Implement Core Task CRUD Operations"
        )
        self.assertEqual(status["details"]["2"]["status"], "conflict")
        self.assertEqual(status["details"]["2"]["remote_id"], "remote2")

        # Verify connection info
        self.assertIn("connection", status)

    @pytest.mark.asyncio
    async def test_resolve_conflicts_local(self):
        """Test resolving conflicts with local strategy."""
        # Create metadata for task2 (conflict)
        metadata2 = NextCloudSyncMetadata(
            provider="nextcloud",
            remote_id="remote2",
            etag="etag2",
            last_sync="2025-05-02T09:33:18",
            sync_status=SyncStatus.CONFLICT,
        )
        update_task_sync_metadata(self.task2, metadata2, self.tasks_dir)

        # Mock remote task
        remote_task = NextCloudTask(
            id="remote2",
            title="#2: Remote Task Title",
            description="Remote description",
            status="pending",
            categories=["implementation", "core"],
            created_at="2025-05-02T09:33:18",
            updated_at="2025-05-02T09:33:18",
            extra={
                "all_dependencies": ["1"],
                "taskinator_full_data": {
                    "id": 2,
                    "title": "Remote Task Title",
                    "description": "Remote description",
                    "status": "pending",
                    "priority": "high",
                    "dependencies": ["1"],
                    "details": "Remote details",
                    "test_strategy": "Remote test strategy",
                    "subtasks": [],
                    "tags": ["implementation", "core"],
                },
            },
        )

        # Mock client.get_task to return the remote task
        self.mock_client.get_task.return_value = remote_task

        # Mock client.update_task to return the updated task
        updated_remote_task = NextCloudTask(
            id="remote2",
            title="#2: Implement Core Task CRUD Operations",
            description="Implement create, read, update, and delete operations for tasks",
            status="pending",
            categories=["implementation", "core"],
            created_at="2025-05-02T09:33:18",
            updated_at="2025-05-02T09:33:18",
            etag="new_etag",
            extra={
                "all_dependencies": ["1"],
                "taskinator_full_data": self.task2.model_dump(),
            },
        )
        self.mock_client.update_task.return_value = updated_remote_task

        # Resolve conflicts with local strategy
        results = await self.plugin.resolve_conflicts(
            self.tasks_json_path, task_id="2", resolution="local"
        )

        # Verify results
        self.assertEqual(results["total"], 1)
        self.assertEqual(results["resolved"], 1)
        self.assertEqual(results["failed"], 0)

        # Verify details
        self.assertIn("details", results)
        self.assertIn("2", results["details"])
        self.assertEqual(results["details"]["2"]["resolution"], "local")
        self.assertEqual(results["details"]["2"]["status"], "Resolved")

        # Verify metadata was updated
        metadata = get_task_sync_metadata(self.task2, self.tasks_dir)
        self.assertEqual(metadata.sync_status, SyncStatus.SYNCED)
        self.assertEqual(metadata.etag, "new_etag")

    @pytest.mark.asyncio
    async def test_resolve_conflicts_remote(self):
        """Test resolving conflicts with remote strategy."""
        # Create metadata for task2 (conflict)
        metadata2 = NextCloudSyncMetadata(
            provider="nextcloud",
            remote_id="remote2",
            etag="etag2",
            last_sync="2025-05-02T09:33:18",
            sync_status=SyncStatus.CONFLICT,
        )
        update_task_sync_metadata(self.task2, metadata2, self.tasks_dir)

        # Mock remote task
        remote_task = NextCloudTask(
            id="remote2",
            title="#2: Remote Task Title",
            description="Remote description",
            status="pending",
            categories=["implementation", "core"],
            created_at="2025-05-02T09:33:18",
            updated_at="2025-05-02T09:33:18",
            etag="new_etag",
            extra={
                "all_dependencies": ["1"],
                "taskinator_full_data": {
                    "id": 2,
                    "title": "Remote Task Title",
                    "description": "Remote description",
                    "status": "pending",
                    "priority": "high",
                    "dependencies": ["1"],
                    "details": "Remote details",
                    "test_strategy": "Remote test strategy",
                    "subtasks": [],
                    "tags": ["implementation", "core"],
                },
            },
        )

        # Mock client.get_task to return the remote task
        self.mock_client.get_task.return_value = remote_task

        # Instead of patching setattr, directly update the task with the remote data
        # Resolve conflicts with remote strategy
        results = await self.plugin.resolve_conflicts(
            self.tasks_json_path, task_id="2", resolution="remote"
        )

        # Verify results
        self.assertEqual(results["total"], 1)
        self.assertEqual(results["resolved"], 1)
        self.assertEqual(results["failed"], 0)

        # Verify details
        self.assertIn("details", results)
        self.assertIn("2", results["details"])
        self.assertEqual(results["details"]["2"]["resolution"], "remote")
        self.assertEqual(results["details"]["2"]["status"], "Resolved")

        # Verify metadata was updated
        metadata = get_task_sync_metadata(self.task2, self.tasks_dir)
        self.assertEqual(metadata.sync_status, SyncStatus.SYNCED)
        self.assertEqual(metadata.etag, "new_etag")

    @pytest.mark.asyncio
    async def test_resolve_conflicts_all(self):
        """Test resolving all conflicts."""
        # Create metadata for task1 (conflict)
        metadata1 = NextCloudSyncMetadata(
            provider="nextcloud",
            remote_id="remote1",
            etag="etag1",
            last_sync="2025-05-02T09:33:18",
            sync_status=SyncStatus.CONFLICT,
        )
        update_task_sync_metadata(self.task1, metadata1, self.tasks_dir)

        # Create metadata for task2 (conflict)
        metadata2 = NextCloudSyncMetadata(
            provider="nextcloud",
            remote_id="remote2",
            etag="etag2",
            last_sync="2025-05-02T09:33:18",
            sync_status=SyncStatus.CONFLICT,
        )
        update_task_sync_metadata(self.task2, metadata2, self.tasks_dir)

        # Mock client.get_task to return remote tasks
        def mock_get_task(remote_id):
            if remote_id == "remote1":
                return NextCloudTask(
                    id="remote1",
                    title="#1: Remote Task 1",
                    description="Remote description 1",
                    status="pending",
                    categories=["design", "storage"],
                    created_at="2025-05-02T09:33:18",
                    updated_at="2025-05-02T09:33:18",
                    etag="new_etag1",
                    extra={
                        "all_dependencies": [],
                        "taskinator_full_data": {
                            "id": 1,
                            "title": "Remote Task 1",
                            "description": "Remote description 1",
                            "status": "pending",
                            "priority": "high",
                            "dependencies": [],
                            "details": "Remote details 1",
                            "test_strategy": "Remote test strategy 1",
                            "subtasks": [],
                            "tags": ["design", "storage"],
                        },
                    },
                )
            elif remote_id == "remote2":
                return NextCloudTask(
                    id="remote2",
                    title="#2: Remote Task 2",
                    description="Remote description 2",
                    status="pending",
                    categories=["implementation", "core"],
                    created_at="2025-05-02T09:33:18",
                    updated_at="2025-05-02T09:33:18",
                    etag="new_etag2",
                    extra={
                        "all_dependencies": ["1"],
                        "taskinator_full_data": {
                            "id": 2,
                            "title": "Remote Task 2",
                            "description": "Remote description 2",
                            "status": "pending",
                            "priority": "high",
                            "dependencies": ["1"],
                            "details": "Remote details 2",
                            "test_strategy": "Remote test strategy 2",
                            "subtasks": [],
                            "tags": ["implementation", "core"],
                        },
                    },
                )
            return None

        self.mock_client.get_task.side_effect = mock_get_task

        # Mock client.update_task to return updated tasks
        def mock_update_task(remote_id, task_data):
            if remote_id == "remote1":
                return NextCloudTask(
                    id="remote1",
                    title=task_data["title"],
                    description=task_data["description"],
                    status=task_data["status"],
                    categories=task_data["categories"],
                    created_at="2025-05-02T09:33:18",
                    updated_at="2025-05-02T09:33:18",
                    etag="updated_etag1",
                    extra=task_data["extra"],
                )
            elif remote_id == "remote2":
                return NextCloudTask(
                    id="remote2",
                    title=task_data["title"],
                    description=task_data["description"],
                    status=task_data["status"],
                    categories=task_data["categories"],
                    created_at="2025-05-02T09:33:18",
                    updated_at="2025-05-02T09:33:18",
                    etag="updated_etag2",
                    extra=task_data["extra"],
                )
            return None

        self.mock_client.update_task.side_effect = mock_update_task

        # Test the actual implementation
        results = await self.plugin.resolve_conflicts(
            self.tasks_json_path, resolution="local"
        )

        # Verify results
        self.assertEqual(results["total"], 2)
        self.assertEqual(results["resolved"], 2)
        self.assertEqual(results["failed"], 0)

        # Verify details
        self.assertIn("details", results)
        self.assertIn("1", results["details"])
        self.assertIn("2", results["details"])
        self.assertEqual(results["details"]["1"]["resolution"], "local")
        self.assertEqual(results["details"]["2"]["resolution"], "local")
        self.assertEqual(results["details"]["1"]["status"], "Resolved")
        self.assertEqual(results["details"]["2"]["status"], "Resolved")


if __name__ == "__main__":
    unittest.main()
