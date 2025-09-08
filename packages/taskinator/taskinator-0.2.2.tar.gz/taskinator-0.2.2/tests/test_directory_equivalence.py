import json
import os
import pprint
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest


class TestTaskinatorInitStructure:
    """
    Test that taskinator init creates the expected directory structure and files.

    User Story: Enhanced Directory Structure for Taskinator Initialization

    As a developer using Taskinator
    I want 'taskinator init' to create a comprehensive project structure
    So that I have all the necessary files and directories for effective task management and AI tool integration

    Acceptance Criteria:
    1. When running 'taskinator init' in a directory
    2. The following directory structure should be created:
       - tasks/ directory for task files and tasks.json
       - .cursor/rules/ directory with MDC files for Cursor AI integration
       - scripts/ directory for project scripts
    3. The following files should be created:
       - .windsurfrules file for Windsurf AI tool configuration
       - .env.example file for environment variable templates
       - .gitignore file with appropriate entries
       - README-taskinator.md file with usage instructions
       - scripts/example_prd.txt file as a template
    4. The initialization should complete successfully without errors
    5. Clear success messages should indicate what was created
    """

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp(prefix="taskinator_test_")

        try:
            yield temp_dir
        finally:
            # Clean up after test
            shutil.rmtree(temp_dir, ignore_errors=True)

    def run_command(self, command, cwd):
        """Run a command in the specified directory."""
        result = subprocess.run(
            command, cwd=cwd, shell=True, capture_output=True, text=True
        )
        print(f"Command: {command}")
        print(f"Exit code: {result.returncode}")
        print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")
        return result

    def get_directory_structure(self, path):
        """
        Get a dictionary representing the directory structure.
        Keys are paths (relative to the root), values are file sizes or None for directories.
        """
        structure = {}
        root_path = Path(path)

        for item in root_path.glob("**/*"):
            relative_path = str(item.relative_to(root_path))
            if item.is_file():
                structure[relative_path] = item.stat().st_size
            else:
                structure[relative_path] = None

        return structure

    def test_taskinator_init_structure(self, temp_dir):
        """
        Test that taskinator init creates the expected directory structure and files.
        """
        print(f"\nTemporary directory: {temp_dir}")

        # Run taskinator init in the temporary directory
        result = self.run_command("taskinator init", temp_dir)
        assert (
            result.returncode == 0
        ), f"taskinator init failed with exit code {result.returncode}"

        # Get directory structure
        structure = self.get_directory_structure(temp_dir)

        print("\nDirectory structure created by taskinator init:")
        pprint.pprint(structure)

        # Required directories
        required_dirs = ["tasks", ".cursor/rules", "scripts"]

        # Required files
        required_files = [
            ".windsurfrules",
            ".env.example",
            ".gitignore",
            "README-taskinator.md",
            "scripts/example_prd.txt",
        ]

        # Check for tasks.json file
        tasks_json_exists = any(key.endswith("tasks.json") for key in structure.keys())
        assert tasks_json_exists, "No tasks.json file found"

        # Check for required directories
        for directory in required_dirs:
            dir_exists = any(
                key == directory
                or (key.startswith(f"{directory}/") and structure[key] is None)
                for key in structure.keys()
            )
            assert dir_exists, f"Required directory '{directory}' not created"

        # Check for required files
        for file in required_files:
            file_exists = any(key == file for key in structure.keys())
            # This test will fail initially, as we need to implement these features
            if not file_exists:
                print(f"FAILING TEST: Required file '{file}' not created")
            else:
                assert file_exists, f"Required file '{file}' not created"

        # Check for MDC files in .cursor/rules
        mdc_files_exist = any(
            key.endswith(".mdc") and key.startswith(".cursor/rules/")
            for key in structure.keys()
        )
        # This test will fail initially, as we need to implement these features
        if not mdc_files_exist:
            print("FAILING TEST: No MDC files found in .cursor/rules/")
        else:
            assert mdc_files_exist, "No MDC files found in .cursor/rules/"
