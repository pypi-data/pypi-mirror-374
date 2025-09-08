"""
Tests for the Nextcloud sync status functionality.
"""

import json
import os
import shutil
import tempfile
import unittest
import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from taskinator.models.task import Task, TaskCollection
from taskinator.plugins.sync.nextcloud.nextcloud_plugin import NextCloudSyncPlugin 
from taskinator.plugins.sync.nextcloud.nextcloud_sync import (
    NextCloudSyncMetadata,
    update_task_sync_metadata,
)
from taskinator.plugins.sync.plugin_base import SyncStatus


class TestNextcloudSyncStatus(unittest.TestCase):
    """Test the Nextcloud sync status functionality."""

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

        # Save tasks to file
        with open(self.tasks_json_path, "w") as f:
            json.dump(self.task_collection.model_dump(), f)

    def tearDown(self):
        """Clean up the test environment."""
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

    @pytest.mark.asyncio
    async def test_get_status_basic(self):
        """Test getting basic sync status."""
        # Create a plugin with mocked components
        plugin = NextCloudSyncPlugin ()
        plugin.client = MagicMock()
        plugin.config = MagicMock()
        plugin.config.host = "https://nextcloud.example.com"
        plugin.config.username = "test_user"
        plugin.config.calendar_id = "personal"

        # Mock read_tasks to return our task collection
        with patch(
            "taskinator.plugins.sync.nextcloud.nextcloud_plugin.read_tasks"
        ) as mock_read_tasks:
            mock_read_tasks.return_value = self.task_collection

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

            # Mock get_task_sync_metadata to return our metadata
            with patch(
                "taskinator.plugins.sync.nextcloud.nextcloud_plugin.get_task_sync_metadata"
            ) as mock_get_metadata:

                def side_effect(task, tasks_dir):
                    if task.id == 1:
                        return metadata1
                    elif task.id == 2:
                        return metadata2
                    return NextCloudSyncMetadata(provider="nextcloud")

                mock_get_metadata.side_effect = side_effect

                # Get status
                status = await plugin.get_status(self.tasks_json_path)

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
        # Create a plugin with mocked components
        plugin = NextCloudSyncPlugin ()
        plugin.client = MagicMock()
        plugin.config = MagicMock()
        plugin.config.host = "https://nextcloud.example.com"
        plugin.config.username = "test_user"
        plugin.config.calendar_id = "personal"

        # Mock read_tasks to return our task collection
        with patch(
            "taskinator.plugins.sync.nextcloud.nextcloud_plugin.read_tasks"
        ) as mock_read_tasks:
            mock_read_tasks.return_value = self.task_collection

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

            # Mock get_task_sync_metadata to return our metadata
            with patch(
                "taskinator.plugins.sync.nextcloud.nextcloud_plugin.get_task_sync_metadata"
            ) as mock_get_metadata:

                def side_effect(task, tasks_dir):
                    if task.id == 1:
                        return metadata1
                    elif task.id == 2:
                        return metadata2
                    return NextCloudSyncMetadata(provider="nextcloud")

                mock_get_metadata.side_effect = side_effect

                # Get status with verbose flag
                status = await plugin.get_status(self.tasks_json_path, verbose=True)

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
                    status["details"]["2"]["title"],
                    "Implement Core Task CRUD Operations",
                )
                self.assertEqual(status["details"]["2"]["status"], "conflict")
                self.assertEqual(status["details"]["2"]["remote_id"], "remote2")

                # Verify connection info
                self.assertIn("connection", status)


if __name__ == "__main__":
    unittest.main()
