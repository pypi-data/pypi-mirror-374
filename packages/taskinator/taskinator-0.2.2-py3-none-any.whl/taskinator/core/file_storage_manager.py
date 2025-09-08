"""
File Storage Manager for Taskinator.

This module provides a robust storage system for both JSON and text files,
with bidirectional synchronization and error handling.
"""

import json
import logging
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Union

from taskinator.models.task import Task, TaskCollection
from taskinator.utils.config import get_config

# Set up logging
logger = logging.getLogger(__name__)


class FileStorageManager:
    """
    FileStorageManager class for handling all file storage operations.

    This class encapsulates all storage operations, including reading and writing
    JSON files, generating task files, and reintegrating task files.
    """

    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize the FileStorageManager.

        Args:
            base_dir (Optional[str], optional): Base directory for file operations.
                                               Defaults to current working directory.
        """
        self.base_dir = base_dir or os.getcwd()
        self.config = get_config()

    def read_json(self, file_path: str) -> Dict:
        """
        Read a JSON file and return its contents.

        Args:
            file_path (str): Path to the JSON file

        Returns:
            Dict: JSON file contents

        Raises:
            FileNotFoundError: If the file does not exist
            json.JSONDecodeError: If the file is not valid JSON
            PermissionError: If the file cannot be read due to permissions
        """
        try:
            logger.info(f"Reading JSON file: {file_path}")
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in file {file_path}: {str(e)}")
            raise
        except PermissionError:
            logger.error(f"Permission denied when reading file: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error reading JSON file {file_path}: {str(e)}")
            raise

    def write_json(self, file_path: str, data: Dict) -> None:
        """
        Write data to a JSON file.

        Args:
            file_path (str): Path to the JSON file
            data (Dict): Data to write

        Raises:
            PermissionError: If the file cannot be written due to permissions
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            logger.info(f"Writing JSON file: {file_path}")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except PermissionError:
            logger.error(f"Permission denied when writing file: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error writing JSON file {file_path}: {str(e)}")
            raise

    def read_tasks(self, tasks_path: str) -> TaskCollection:
        """
        Read tasks from a JSON file.

        Args:
            tasks_path (str): Path to the tasks.json file

        Returns:
            TaskCollection: Collection of tasks

        Raises:
            FileNotFoundError: If the file does not exist
            json.JSONDecodeError: If the file is not valid JSON
            PermissionError: If the file cannot be read due to permissions
        """
        try:
            data = self.read_json(tasks_path)
            tasks = TaskCollection.model_validate(data)
            logger.info(f"Successfully read tasks from {tasks_path}")
            return tasks
        except Exception as e:
            logger.error(f"Error reading tasks from {tasks_path}: {str(e)}")
            raise

    def write_tasks(self, tasks_path: str, tasks: TaskCollection) -> None:
        """
        Write tasks to a JSON file.

        Args:
            tasks_path (str): Path to the tasks.json file
            tasks (TaskCollection): Collection of tasks

        Raises:
            PermissionError: If the file cannot be written due to permissions
        """
        try:
            # Ensure metadata contains proper project name
            if tasks.metadata:
                # If project name is not explicitly set or is default value, use directory name
                if ("project_name" not in tasks.metadata or 
                    tasks.metadata["project_name"] == "Taskinator" or 
                    tasks.metadata["project_name"] == ""):
                    # Get the directory where we're writing the file
                    project_dir = os.path.dirname(os.path.dirname(tasks_path))
                    dir_name = os.path.basename(project_dir)
                    
                    # Only update if the directory name is not "taskinator" itself
                    if dir_name.lower() != "taskinator":
                        tasks.metadata["project_name"] = dir_name
                    
                # Mark the project name as explicitly set to avoid overrides
                tasks.metadata["project_name_set"] = True
            
            self.write_json(tasks_path, tasks.model_dump())
            logger.info(f"Successfully wrote tasks to {tasks_path}")
        except Exception as e:
            logger.error(f"Error writing tasks to {tasks_path}: {str(e)}")
            raise

    def generate_task_files(
        self, tasks_path: str, output_dir: Optional[str] = None, base_dir: Optional[str] = None
    ) -> None:
        """
        Generate task files from tasks.json.

        Args:
            tasks_path (str): Path to the tasks.json file
            output_dir (Optional[str], optional): Output directory for task files.
                                                 Defaults to "tasks".
            base_dir (Optional[str], optional): Base directory for file operations.
                                                Defaults to self.base_dir.
        """
        try:
            # Read tasks
            tasks = self.read_tasks(tasks_path)

            # Determine output directory
            output_dir = output_dir or "tasks"
            effective_base_dir = base_dir or self.base_dir
            
            # Handle both absolute and relative paths for output_dir
            if os.path.isabs(output_dir):
                output_path = output_dir
            else:
                output_path = os.path.join(effective_base_dir, output_dir)
                
            logger.info(f"Using output path: {output_path}")

            # Create output directory if it doesn't exist
            os.makedirs(output_path, exist_ok=True)

            # Generate task files
            for task in tasks.tasks:
                # Handle both numeric and UUID-style task IDs
                if isinstance(task.id, int) or (isinstance(task.id, str) and task.id.isdigit()):
                    # For numeric IDs, use zero-padded format
                    task_file_name = f"task_{int(task.id):03d}.txt"
                else:
                    # For UUID or other string IDs, use the ID directly
                    task_file_name = f"task_{task.id}.txt"
                    
                task_file_path = os.path.join(output_path, task_file_name)

                with open(task_file_path, "w", encoding="utf-8") as f:
                    # Write task header
                    f.write(f"# Task ID: {task.id}\n")
                    f.write(f"# Title: {task.title}\n")
                    f.write(f"# Status: {task.status}\n")

                    # Write dependencies
                    if task.dependencies:
                        deps_str = ", ".join(str(d) for d in task.dependencies)
                        f.write(f"# Dependencies: {deps_str}\n")
                    else:
                        f.write("# Dependencies: None\n")

                    # Write priority
                    f.write(f"# Priority: {task.priority}\n")

                    # Write description
                    f.write(f"# Description: {task.description}\n")

                    # Write details
                    f.write("# Details:\n")
                    if task.details:
                        f.write(f"{task.details}\n\n")
                    else:
                        f.write("None\n\n")

                    # Write test strategy
                    f.write("# Test Strategy:\n")
                    if task.test_strategy:
                        f.write(f"{task.test_strategy}\n")
                    else:
                        f.write("None\n")
                    
                    # Add subtasks section for backward compatibility
                    if task.subtasks:
                        f.write("\n# Subtasks:\n")
                        for subtask in task.subtasks:
                            f.write(f"- {subtask.id}: {subtask.title}\n")
                            f.write(f"  Description: {subtask.description}\n")
                            f.write(f"  Status: {subtask.status}\n")
                            if subtask.dependencies:
                                deps_str = ", ".join(str(d) for d in subtask.dependencies)
                                f.write(f"  Dependencies: {deps_str}\n")
                            f.write("\n")

                logger.info(f"Generated: {os.path.basename(task_file_path)}")
                
                # Generate subtask files
                if task.subtasks:
                    for subtask in task.subtasks:
                        # Create subtask filename based on parent task ID and subtask ID
                        # For example, if task.id is "1" and subtask.id is "1.1",
                        # the filename will be "task_001_001.txt"
                        
                        # Extract the numeric part after the dot in subtask ID
                        if "." in str(subtask.id):
                            subtask_num = str(subtask.id).split(".")[-1]
                            try:
                                subtask_num = int(subtask_num)
                                subtask_file_name = f"task_{int(task.id):03d}_{int(subtask_num):03d}.txt"
                            except ValueError:
                                # If conversion fails, use the full subtask ID
                                subtask_file_name = f"task_{task.id}_{subtask.id}.txt"
                        else:
                            # If there's no dot in the subtask ID, use the full ID
                            subtask_file_name = f"task_{task.id}_{subtask.id}.txt"
                        
                        subtask_file_path = os.path.join(output_path, subtask_file_name)
                        
                        with open(subtask_file_path, "w", encoding="utf-8") as f:
                            # Write subtask header
                            f.write(f"# Subtask ID: {subtask.id}\n")
                            f.write(f"# Parent Task: {task.id} - {task.title}\n")
                            f.write(f"# Title: {subtask.title}\n")
                            f.write(f"# Status: {subtask.status}\n")
                            
                            # Write dependencies
                            if subtask.dependencies:
                                deps_str = ", ".join(str(d) for d in subtask.dependencies)
                                f.write(f"# Dependencies: {deps_str}\n")
                            else:
                                f.write("# Dependencies: None\n")
                            
                            # Write priority (inherit from parent if not set)
                            priority = getattr(subtask, "priority", task.priority)
                            f.write(f"# Priority: {priority}\n")
                            
                            # Write description
                            f.write(f"# Description: {subtask.description}\n")
                            
                            # Write details
                            f.write("# Details:\n")
                            if hasattr(subtask, 'details') and subtask.details:
                                f.write(f"{subtask.details}\n\n")
                            else:
                                f.write(f"This is a subtask of '{task.title}'.\n\n")
                                f.write(f"Parent task description: {task.description}\n\n")
                            
                            # Write test strategy
                            f.write("# Test Strategy:\n")
                            if hasattr(subtask, 'test_strategy') and subtask.test_strategy:
                                f.write(f"{subtask.test_strategy}\n")
                            else:
                                f.write("Follow the test strategy of the parent task.\n")
                        
                        logger.info(f"Generated: {os.path.basename(subtask_file_path)}")
        
            logger.info(f"Successfully generated task files in {output_path}")
        except Exception as e:
            logger.error(f"Error generating task files: {str(e)}")
            raise

    def reintegrate_task_files(
        self, tasks_path: str, input_dir: Optional[str] = None
    ) -> TaskCollection:
        """
        Reintegrate task files into tasks.json.

        Args:
            tasks_path (str): Path to the tasks.json file
            input_dir (Optional[str], optional): Input directory for task files.
                                               Defaults to "tasks".
        """
        try:
            # Read tasks
            tasks = self.read_tasks(tasks_path)

            # Determine input directory
            input_dir = input_dir or "tasks"
            input_path = os.path.join(self.base_dir, input_dir)

            # Check if input directory exists
            if not os.path.exists(input_path):
                logger.error(f"Input directory does not exist: {input_path}")
                raise FileNotFoundError(f"Input directory does not exist: {input_path}")

            # Get task files
            task_files = [
                f
                for f in os.listdir(input_path)
                if f.startswith("task_") and f.endswith(".txt")
            ]

            # Reintegrate task files
            for task_file in task_files:
                task_file_path = os.path.join(input_path, task_file)

                # Extract task ID from filename
                task_id_str = task_file.replace("task_", "").replace(".txt", "")
                
                # Try to convert to int if it's a numeric ID, otherwise use as string
                try:
                    # Only convert to int if it's all digits (after stripping leading zeros)
                    if task_id_str.lstrip("0").isdigit():
                        task_id = int(task_id_str.lstrip("0"))
                    else:
                        # For UUID or other string IDs, use as is
                        task_id = task_id_str
                except ValueError:
                    logger.warning(f"Invalid task ID in filename: {task_file}")
                    continue

                # Find task in collection
                task = next((t for t in tasks.tasks if str(t.id) == str(task_id)), None)
                if not task:
                    logger.warning(f"Task {task_id} not found in tasks.json")
                    continue

                # Parse task file
                with open(task_file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Parse sections
                sections = {}
                current_section = None
                section_content = []

                for line in content.split("\n"):
                    if line.startswith("# "):
                        # Save previous section
                        if current_section:
                            sections[current_section] = "\n".join(
                                section_content
                            ).strip()

                        # Start new section
                        parts = line[2:].split(":", 1)
                        if len(parts) == 2:
                            current_section = parts[0].strip()
                            section_content = [parts[1].strip()]
                        else:
                            current_section = parts[0].strip()
                            section_content = []
                    else:
                        section_content.append(line)

                # Save last section
                if current_section:
                    sections[current_section] = "\n".join(section_content).strip()

                # Update task
                if "Status" in sections:
                    task.status = sections["Status"]

                if "Details" in sections:
                    task.details = sections["Details"]

                if "Test Strategy" in sections:
                    task.test_strategy = sections["Test Strategy"]

                logger.info(f"Reintegrated: {task_file}")

            # Write updated tasks
            self.write_tasks(tasks_path, tasks)
            logger.info(f"Successfully reintegrated task files into {tasks_path}")
            
            # Return the updated tasks
            return tasks
        except Exception as e:
            logger.error(f"Error reintegrating task files: {str(e)}")
            raise

    def backup_tasks(self, tasks_path: str, backup_dir: Optional[str] = None) -> str:
        """
        Create a backup of the tasks.json file.

        Args:
            tasks_path (str): Path to the tasks.json file
            backup_dir (Optional[str], optional): Backup directory.
                                                Defaults to "backups".

        Returns:
            str: Path to the backup file
        """
        try:
            # Determine backup directory
            backup_dir = backup_dir or "backups"
            backup_path = os.path.join(self.base_dir, backup_dir)

            # Create backup directory if it doesn't exist
            os.makedirs(backup_path, exist_ok=True)

            # Create backup filename with timestamp
            import datetime

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"tasks_{timestamp}.json"
            backup_file_path = os.path.join(backup_path, backup_file)

            # Copy tasks.json to backup
            shutil.copy2(tasks_path, backup_file_path)

            logger.info(f"Created backup: {backup_file}")
            return backup_file_path
        except Exception as e:
            logger.error(f"Error creating backup: {str(e)}")
            raise
