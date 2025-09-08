"""
Tests for the file storage system.
"""

import json
import os
import shutil
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from taskinator.core.file_storage_manager import FileStorageManager
from taskinator.models.task import Subtask, Task, TaskCollection


class TestFileStorage(unittest.TestCase):
    """Test the file storage system."""

    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for tests
        self.test_dir = tempfile.mkdtemp()
        self.tasks_dir = os.path.join(self.test_dir, "tasks")
        self.tasks_json_path = os.path.join(self.tasks_dir, "tasks.json")

        # Create a file storage manager
        self.file_storage = FileStorageManager(self.tasks_dir)

        # Create a sample task collection
        self.tasks = TaskCollection(
            tasks=[
                Task(
                    id=1,
                    title="Task 1",
                    description="Description for Task 1",
                    status="pending",
                    priority="high",
                    dependencies=[],
                    details="Implementation details for Task 1",
                    test_strategy="Test strategy for Task 1",
                    subtasks=[
                        Subtask(
                            id="1.1",
                            title="Subtask 1.1",
                            description="Description for Subtask 1.1",
                            status="pending",
                            dependencies=[],
                        ),
                        Subtask(
                            id="1.2",
                            title="Subtask 1.2",
                            description="Description for Subtask 1.2",
                            status="pending",
                            dependencies=["1.1"],
                        ),
                    ],
                ),
                Task(
                    id=2,
                    title="Task 2",
                    description="Description for Task 2",
                    status="pending",
                    priority="medium",
                    dependencies=["1"],
                    details="Implementation details for Task 2",
                    test_strategy="Test strategy for Task 2",
                    subtasks=[],
                ),
            ],
            metadata={
                "project_name": "Test Project",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "version": "0.1.0",
            },
        )

    def tearDown(self):
        """Clean up the test environment."""
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

    def test_read_write_tasks(self):
        """Test reading and writing tasks."""
        # Write tasks to file
        self.file_storage.write_tasks(self.tasks_json_path, self.tasks)

        # Verify the file exists
        self.assertTrue(os.path.exists(self.tasks_json_path))

        # Read tasks from file
        read_tasks = self.file_storage.read_tasks(self.tasks_json_path)

        # Verify the tasks match
        self.assertEqual(len(read_tasks.tasks), len(self.tasks.tasks))
        self.assertEqual(read_tasks.tasks[0].id, self.tasks.tasks[0].id)
        self.assertEqual(read_tasks.tasks[0].title, self.tasks.tasks[0].title)
        self.assertEqual(
            read_tasks.tasks[0].description, self.tasks.tasks[0].description
        )
        self.assertEqual(read_tasks.tasks[0].status, self.tasks.tasks[0].status)
        self.assertEqual(read_tasks.tasks[0].priority, self.tasks.tasks[0].priority)
        self.assertEqual(
            read_tasks.tasks[0].dependencies, self.tasks.tasks[0].dependencies
        )
        self.assertEqual(read_tasks.tasks[0].details, self.tasks.tasks[0].details)
        self.assertEqual(
            read_tasks.tasks[0].test_strategy, self.tasks.tasks[0].test_strategy
        )

        # Verify subtasks
        self.assertEqual(
            len(read_tasks.tasks[0].subtasks), len(self.tasks.tasks[0].subtasks)
        )
        self.assertEqual(
            read_tasks.tasks[0].subtasks[0].id, self.tasks.tasks[0].subtasks[0].id
        )
        self.assertEqual(
            read_tasks.tasks[0].subtasks[0].title, self.tasks.tasks[0].subtasks[0].title
        )

        # Verify metadata
        self.assertEqual(
            read_tasks.metadata["project_name"], self.tasks.metadata["project_name"]
        )
        self.assertEqual(read_tasks.metadata["version"], self.tasks.metadata["version"])

    def test_generate_task_files(self):
        """Test generating task files."""
        # Write tasks to file
        self.file_storage.write_tasks(self.tasks_json_path, self.tasks)

        # Generate task files
        self.file_storage.generate_task_files(self.tasks_json_path, None, self.tasks_dir)

        # Verify task files exist
        task1_file = os.path.join(self.tasks_dir, "task_001.txt")
        task2_file = os.path.join(self.tasks_dir, "task_002.txt")
        self.assertTrue(os.path.exists(task1_file))
        self.assertTrue(os.path.exists(task2_file))

        # Verify task file content
        with open(task1_file, "r") as f:
            content = f.read()
            self.assertIn("Task ID: 1", content)
            self.assertIn("Title: Task 1", content)
            self.assertIn("Status: pending", content)
            self.assertIn("Priority: high", content)
            self.assertIn("Description: Description for Task 1", content)
            self.assertIn("Implementation details for Task 1", content)
            self.assertIn("Test strategy for Task 1", content)
            self.assertIn("Subtasks:", content)
            self.assertIn("1.1: Subtask 1.1", content)
            self.assertIn("1.2: Subtask 1.2", content)

    def test_reintegrate_task_files(self):
        """Test reintegrating task files."""
        # Write tasks to file and generate task files
        self.file_storage.write_tasks(self.tasks_json_path, self.tasks)
        self.file_storage.generate_task_files(self.tasks_json_path, None, self.tasks_dir)

        # Modify a task file
        task1_file = os.path.join(self.tasks_dir, "task_001.txt")
        with open(task1_file, "r") as f:
            content = f.read()

        # Change the title and status
        modified_content = content.replace("Title: Task 1", "Title: Modified Task 1")
        modified_content = modified_content.replace(
            "Status: pending", "Status: in-progress"
        )

        with open(task1_file, "w") as f:
            f.write(modified_content)

        # Reintegrate task files
        updated_tasks = self.file_storage.reintegrate_task_files(self.tasks_json_path)

        # Verify the changes were applied
        self.assertEqual(updated_tasks.tasks[0].title, "Modified Task 1")
        self.assertEqual(updated_tasks.tasks[0].status, "in-progress")

        # Read tasks from file to verify changes were saved
        read_tasks = self.file_storage.read_tasks(self.tasks_json_path)
        self.assertEqual(read_tasks.tasks[0].title, "Modified Task 1")
        self.assertEqual(read_tasks.tasks[0].status, "in-progress")

    def test_error_handling(self):
        """Test error handling."""
        # Test reading a non-existent file
        non_existent_path = os.path.join(self.test_dir, "non_existent_file.json")
        with self.assertRaises(FileNotFoundError):
            self.file_storage.read_tasks(non_existent_path)

        # Test writing to a read-only directory
        if os.name != "nt":  # Skip on Windows
            read_only_dir = os.path.join(self.test_dir, "read_only")
            os.makedirs(read_only_dir)
            os.chmod(read_only_dir, 0o444)  # Read-only

            file_storage = FileStorageManager(read_only_dir)
            with self.assertRaises(Exception):
                file_storage.write_tasks(os.path.join(read_only_dir, "tasks.json"), self.tasks)

    def test_utility_methods(self):
        """Test utility methods."""
        # Test checking if a file exists
        test_file = os.path.join(self.test_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("Test content")

        self.assertTrue(os.path.exists(test_file))
        self.assertFalse(os.path.exists(os.path.join(self.test_dir, "non_existent.txt")))

        # Test reading and writing JSON files
        json_file = os.path.join(self.test_dir, "test.json")
        data = {"test": "data"}
        
        # Write JSON file
        self.file_storage.write_json(json_file, data)
        self.assertTrue(os.path.exists(json_file))
        
        # Read JSON file
        read_data = self.file_storage.read_json(json_file)
        self.assertEqual(read_data, data)


if __name__ == "__main__":
    unittest.main()
