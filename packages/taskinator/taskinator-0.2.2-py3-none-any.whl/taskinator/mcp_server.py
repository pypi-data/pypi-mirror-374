#!/usr/bin/env python3
"""
MCP server for Taskinator.
Provides an interface for AI assistants to interact with Taskinator functionality.
"""

import os
import sys
import logging
import asyncio
from typing import Optional, Dict, Any, List

from fastmcp import FastMCP

# Import Taskinator functionality
from taskinator.core.task_manager import (
    add_dependency,
    add_task,
    analyze_task_complexity,
    clear_subtasks,
    expand_all_tasks,
    expand_task,
    fix_dependencies,
    generate_task_files,
    list_tasks,
    get_task,
    get_next_task,
    parse_prd,
    reintegrate_task_files,
    remove_dependency,
    set_task_status,
    update_tasks,
    validate_dependencies,
)
from taskinator.utils.config import get_config, get_config_value

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("taskinator-mcp")

class TaskinatorMCPServer:
    """Main MCP server class that integrates with Taskinator."""
    
    def __init__(self):
        """Initialize the MCP server."""
        self.options = {
            "name": "Taskinator MCP Server",
            "instructions": """
            This server provides access to Taskinator functionality.
            Taskinator is a task management system for breaking down complex projects into manageable tasks.
            You can use these tools to manage tasks, analyze complexity, and track progress.
            """
        }
        
        self.server = FastMCP(**self.options)
        self.initialized = False
        
        # Bind methods
        # Bind methods
        self.init = self.init
        self.start = self.start
        self.stop = self.stop
        
    async def init(self):
        """Initialize the MCP server with necessary tools."""
        if self.initialized:
            return self
        
        # Register all Taskinator tools
        self._register_taskinator_tools()
        
        self.initialized = True
        return self
    
    async def start(self):
        """Start the MCP server."""
        if not self.initialized:
            await self.init()
        
        # Start the FastMCP server
        await self.server.start(
            transportType="stdio",
            timeout=120000  # 2 minutes timeout (in milliseconds)
        )
        
        return self
    
    async def stop(self):
        """Stop the MCP server."""
        if self.server:
            await self.server.stop()
    
    def _register_taskinator_tools(self):
        """Register all Taskinator tools with the MCP server."""
        # Register each tool
        self._register_list_tasks_tool()
        self._register_show_task_tool()
        self._register_next_task_tool()
        self._register_set_task_status_tool()
        self._register_parse_prd_tool()
        self._register_update_tool()
        self._register_generate_tool()
        self._register_expand_task_tool()
        self._register_add_task_tool()
        self._register_analyze_tool()
        self._register_clear_subtasks_tool()
        self._register_expand_all_tool()
        self._register_add_dependency_tool()
        self._register_remove_dependency_tool()
        self._register_validate_dependencies_tool()
        self._register_fix_dependencies_tool()
    
    def _register_list_tasks_tool(self):
        """Register the list_tasks tool."""
        @self.server.tool()
        async def get_tasks(
            status: Optional[str] = None,
            with_subtasks: bool = False,
            project_root: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Get all tasks from Taskinator, optionally filtering by status and including subtasks.
            
            Args:
                status: Filter tasks by status (e.g., 'pending', 'done')
                with_subtasks: Include subtasks nested within their parent tasks in the response
                project_root: The directory of the project. Must be an absolute path.
            
            Returns:
                A dictionary containing the list of tasks and metadata
            """
            try:
                logger.info(f"Getting tasks with filters: status={status}, with_subtasks={with_subtasks}")
                
                # Get project root from args or use current directory
                root_folder = project_root or os.getcwd()
                
                # Get tasks path from config
                tasks_path = get_config_value("tasks_file_path", root_folder)
                
                # Get tasks
                result = list_tasks(
                    tasks_json_path=tasks_path,
                    status=status,
                    with_subtasks=with_subtasks
                )
                
                logger.info(f"Retrieved {len(result.get('tasks', []))} tasks")
                return result
            except Exception as e:
                logger.error(f"Error getting tasks: {str(e)}")
                raise ValueError(f"Error getting tasks: {str(e)}")
    
    def _register_show_task_tool(self):
        """Register the show_task tool."""
        @self.server.tool()
        async def get_task(
            task_id: str,
            project_root: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Get detailed information about a specific task.
            
            Args:
                task_id: The ID of the task to show
                project_root: The directory of the project. Must be an absolute path.
            
            Returns:
                A dictionary containing the task details
            """
            try:
                logger.info(f"Getting task details for task ID: {task_id}")
                
                # Get project root from args or use current directory
                root_folder = project_root or os.getcwd()
                
                # Get tasks path from config
                tasks_path = get_config_value("tasks_file_path", root_folder)
                
                # Get task
                result = get_task(task_id, tasks_path)
                
                logger.info(f"Retrieved task: {task_id}")
                return result
            except Exception as e:
                logger.error(f"Error getting task: {str(e)}")
                raise ValueError(f"Error getting task: {str(e)}")
    
    def _register_next_task_tool(self):
        """Register the next_task tool."""
        @self.server.tool()
        async def next_task(
            project_root: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Get the next task to work on based on dependencies and priority.
            
            Args:
                project_root: The directory of the project. Must be an absolute path.
            
            Returns:
                A dictionary containing the next task to work on
            """
            try:
                logger.info("Getting next task to work on")
                
                # Get project root from args or use current directory
                root_folder = project_root or os.getcwd()
                
                # Get tasks path from config
                tasks_path = get_config_value("tasks_file_path", root_folder)
                
                # Get next task
                result = get_next_task(tasks_path)
                
                logger.info(f"Retrieved next task: {result.get('id', 'None')}")
                return result
            except Exception as e:
                logger.error(f"Error getting next task: {str(e)}")
                raise ValueError(f"Error getting next task: {str(e)}")
    
    def _register_set_task_status_tool(self):
        """Register the set_task_status tool."""
        @self.server.tool()
        async def set_task_status(
            task_id: str,
            status: str,
            project_root: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Update task status (done, pending, etc.).
            
            Args:
                task_id: The ID of the task to update
                status: The new status for the task
                project_root: The directory of the project. Must be an absolute path.
            
            Returns:
                A dictionary containing the updated task
            """
            try:
                logger.info(f"Setting task {task_id} status to {status}")
                
                # Get project root from args or use current directory
                root_folder = project_root or os.getcwd()
                
                # Get tasks path from config
                tasks_path = get_config_value("tasks_file_path", root_folder)
                
                # Set task status
                result = set_task_status(task_id, status, tasks_path)
                
                logger.info(f"Updated task {task_id} status to {status}")
                return result
            except Exception as e:
                logger.error(f"Error setting task status: {str(e)}")
                raise ValueError(f"Error setting task status: {str(e)}")
    
    def _register_parse_prd_tool(self):
        """Register the parse_prd tool."""
        @self.server.tool()
        async def parse_prd(
            prd_path: str,
            num_tasks: int = 10,
            project_root: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Generate tasks from a PRD document.
            
            Args:
                prd_path: Path to the PRD document
                num_tasks: Number of tasks to generate
                project_root: The directory of the project. Must be an absolute path.
            
            Returns:
                A dictionary containing the generated tasks
            """
            try:
                logger.info(f"Parsing PRD from {prd_path} to generate {num_tasks} tasks")
                
                # Get project root from args or use current directory
                root_folder = project_root or os.getcwd()
                
                # Resolve the PRD path - if it's relative, make it relative to project root
                if not os.path.isabs(prd_path):
                    prd_path = os.path.join(root_folder, prd_path)
                
                # Check if the PRD file exists
                if not os.path.exists(prd_path):
                    raise ValueError(f"PRD file not found: {prd_path}")
                
                # Get tasks path from config
                tasks_path = get_config_value("tasks_file_path", root_folder)
                
                # Parse PRD
                result = parse_prd(prd_path, tasks_path, num_tasks)
                
                logger.info(f"Generated {len(result.get('tasks', []))} tasks from PRD")
                return result
            except Exception as e:
                logger.error(f"Error parsing PRD: {str(e)}")
                raise ValueError(f"Error parsing PRD: {str(e)}")
    
    def _register_update_tool(self):
        """Register the update tool."""
        @self.server.tool()
        async def update(
            from_id: str,
            prompt: str,
            project_root: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Update tasks based on new requirements.
            
            Args:
                from_id: The ID of the task to update from
                prompt: The prompt describing the updates
                project_root: The directory of the project. Must be an absolute path.
            
            Returns:
                A dictionary containing the updated tasks
            """
            try:
                logger.info(f"Updating tasks from {from_id} with prompt: {prompt}")
                
                # Get project root from args or use current directory
                root_folder = project_root or os.getcwd()
                
                # Get tasks path from config
                tasks_path = get_config_value("tasks_file_path", root_folder)
                
                # Update tasks
                result = update_tasks(from_id, prompt, tasks_path)
                
                logger.info(f"Updated tasks from {from_id}")
                return result
            except Exception as e:
                logger.error(f"Error updating tasks: {str(e)}")
                raise ValueError(f"Error updating tasks: {str(e)}")
    
    def _register_generate_tool(self):
        """Register the generate tool."""
        @self.server.tool()
        async def generate(
            project_root: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Create individual task files from tasks.json.
            
            Args:
                project_root: The directory of the project. Must be an absolute path.
            
            Returns:
                A dictionary containing the result of the generation
            """
            try:
                logger.info("Generating task files")
                
                # Get project root from args or use current directory
                root_folder = project_root or os.getcwd()
                
                # Get tasks path from config
                tasks_path = get_config_value("tasks_file_path", root_folder)
                
                # Generate task files
                result = generate_task_files(tasks_path)
                
                logger.info("Generated task files")
                return {"success": True, "message": "Task files generated successfully"}
            except Exception as e:
                logger.error(f"Error generating task files: {str(e)}")
                raise ValueError(f"Error generating task files: {str(e)}")
    
    def _register_expand_task_tool(self):
        """Register the expand_task tool."""
        @self.server.tool()
        async def expand_task(
            task_id: str,
            num_subtasks: Optional[int] = None,
            research: bool = False,
            force: bool = False,
            project_root: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Break down a task into detailed subtasks.
            
            Args:
                task_id: The ID of the task to expand
                num_subtasks: Number of subtasks to generate
                research: Whether to perform research for better subtask generation
                force: Whether to force expansion even if the task already has subtasks
                project_root: The directory of the project. Must be an absolute path.
            
            Returns:
                A dictionary containing the expanded task
            """
            try:
                logger.info(f"Expanding task {task_id} into {num_subtasks} subtasks")
                
                # Get project root from args or use current directory
                root_folder = project_root or os.getcwd()
                
                # Get tasks path from config
                tasks_path = get_config_value("tasks_file_path", root_folder)
                
                # Expand task
                result = expand_task(
                    task_id,
                    tasks_path,
                    num_subtasks=num_subtasks,
                    research=research,
                    force=force
                )
                
                logger.info(f"Expanded task {task_id}")
                return result
            except Exception as e:
                logger.error(f"Error expanding task: {str(e)}")
                raise ValueError(f"Error expanding task: {str(e)}")
    
    def _register_add_task_tool(self):
        """Register the add_task tool."""
        @self.server.tool()
        async def add_task(
            prompt: str,
            dependencies: Optional[str] = None,
            priority: str = "medium",
            project_root: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Add a new task using AI.
            
            Args:
                prompt: Description of the task to add
                dependencies: Comma-separated list of task IDs this task depends on
                priority: Priority of the task (low, medium, high)
                project_root: The directory of the project. Must be an absolute path.
            
            Returns:
                A dictionary containing the added task
            """
            try:
                logger.info(f"Adding new task with prompt: {prompt}")
                
                # Get project root from args or use current directory
                root_folder = project_root or os.getcwd()
                
                # Get tasks path from config
                tasks_path = get_config_value("tasks_file_path", root_folder)
                
                # Parse dependencies
                deps_list = None
                if dependencies:
                    deps_list = [dep.strip() for dep in dependencies.split(",")]
                
                # Add task
                result = add_task(prompt, tasks_path, deps_list, priority)
                
                logger.info(f"Added new task: {result.get('id', 'Unknown')}")
                return result
            except Exception as e:
                logger.error(f"Error adding task: {str(e)}")
                raise ValueError(f"Error adding task: {str(e)}")
    
    def _register_analyze_tool(self):
        """Register the analyze tool."""
        @self.server.tool()
        async def analyze(
            research: bool = False,
            threshold: int = 5,
            project_root: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Analyze tasks and generate expansion recommendations.
            
            Args:
                research: Whether to perform research for better analysis
                threshold: Complexity threshold for recommending expansion
                project_root: The directory of the project. Must be an absolute path.
            
            Returns:
                A dictionary containing the analysis results
            """
            try:
                logger.info(f"Analyzing tasks with threshold {threshold}")
                
                # Get project root from args or use current directory
                root_folder = project_root or os.getcwd()
                
                # Get tasks path from config
                tasks_path = get_config_value("tasks_file_path", root_folder)
                
                # Analyze tasks
                result = analyze_task_complexity(tasks_path, research, threshold)
                
                logger.info("Completed task analysis")
                return result
            except Exception as e:
                logger.error(f"Error analyzing tasks: {str(e)}")
                raise ValueError(f"Error analyzing tasks: {str(e)}")
    
    def _register_clear_subtasks_tool(self):
        """Register the clear_subtasks tool."""
        @self.server.tool()
        async def clear_subtasks(
            task_id: str,
            project_root: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Remove subtasks from a specified task.
            
            Args:
                task_id: The ID of the task to clear subtasks from
                project_root: The directory of the project. Must be an absolute path.
            
            Returns:
                A dictionary containing the result of the operation
            """
            try:
                logger.info(f"Clearing subtasks from task {task_id}")
                
                # Get project root from args or use current directory
                root_folder = project_root or os.getcwd()
                
                # Get tasks path from config
                tasks_path = get_config_value("tasks_file_path", root_folder)
                
                # Clear subtasks
                result = clear_subtasks(task_id, tasks_path)
                
                logger.info(f"Cleared subtasks from task {task_id}")
                return {"success": True, "message": f"Subtasks cleared from task {task_id}"}
            except Exception as e:
                logger.error(f"Error clearing subtasks: {str(e)}")
                raise ValueError(f"Error clearing subtasks: {str(e)}")
    
    def _register_expand_all_tool(self):
        """Register the expand_all tool."""
        @self.server.tool()
        async def expand_all(
            project_root: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Expand all tasks that need expansion based on complexity analysis.
            
            Args:
                project_root: The directory of the project. Must be an absolute path.
            
            Returns:
                A dictionary containing the result of the operation
            """
            try:
                logger.info("Expanding all tasks based on complexity analysis")
                
                # Get project root from args or use current directory
                root_folder = project_root or os.getcwd()
                
                # Get tasks path from config
                tasks_path = get_config_value("tasks_file_path", root_folder)
                
                # Expand all tasks
                result = expand_all_tasks(tasks_path)
                
                logger.info("Expanded all tasks")
                return result
            except Exception as e:
                logger.error(f"Error expanding all tasks: {str(e)}")
                raise ValueError(f"Error expanding all tasks: {str(e)}")
    
    def _register_add_dependency_tool(self):
        """Register the add_dependency tool."""
        @self.server.tool()
        async def add_dependency(
            task_id: str,
            depends_on: str,
            project_root: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Add a dependency to a task.
            
            Args:
                task_id: The ID of the task to add a dependency to
                depends_on: The ID of the task that task_id depends on
                project_root: The directory of the project. Must be an absolute path.
            
            Returns:
                A dictionary containing the result of the operation
            """
            try:
                logger.info(f"Adding dependency {depends_on} to task {task_id}")
                
                # Get project root from args or use current directory
                root_folder = project_root or os.getcwd()
                
                # Get tasks path from config
                tasks_path = get_config_value("tasks_file_path", root_folder)
                
                # Add dependency
                result = add_dependency(task_id, depends_on, tasks_path)
                
                logger.info(f"Added dependency {depends_on} to task {task_id}")
                return {"success": True, "message": f"Added dependency {depends_on} to task {task_id}"}
            except Exception as e:
                logger.error(f"Error adding dependency: {str(e)}")
                raise ValueError(f"Error adding dependency: {str(e)}")
    
    def _register_remove_dependency_tool(self):
        """Register the remove_dependency tool."""
        @self.server.tool()
        async def remove_dependency(
            task_id: str,
            depends_on: str,
            project_root: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Remove a dependency from a task.
            
            Args:
                task_id: The ID of the task to remove a dependency from
                depends_on: The ID of the task that task_id depends on
                project_root: The directory of the project. Must be an absolute path.
            
            Returns:
                A dictionary containing the result of the operation
            """
            try:
                logger.info(f"Removing dependency {depends_on} from task {task_id}")
                
                # Get project root from args or use current directory
                root_folder = project_root or os.getcwd()
                
                # Get tasks path from config
                tasks_path = get_config_value("tasks_file_path", root_folder)
                
                # Remove dependency
                result = remove_dependency(task_id, depends_on, tasks_path)
                
                logger.info(f"Removed dependency {depends_on} from task {task_id}")
                return {"success": True, "message": f"Removed dependency {depends_on} from task {task_id}"}
            except Exception as e:
                logger.error(f"Error removing dependency: {str(e)}")
                raise ValueError(f"Error removing dependency: {str(e)}")
    
    def _register_validate_dependencies_tool(self):
        """Register the validate_dependencies tool."""
        @self.server.tool()
        async def validate_dependencies(
            project_root: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Identify invalid dependencies without fixing them.
            
            Args:
                project_root: The directory of the project. Must be an absolute path.
            
            Returns:
                A dictionary containing the validation results
            """
            try:
                logger.info("Validating dependencies")
                
                # Get project root from args or use current directory
                root_folder = project_root or os.getcwd()
                
                # Get tasks path from config
                tasks_path = get_config_value("tasks_file_path", root_folder)
                
                # Validate dependencies
                result = validate_dependencies(tasks_path)
                
                logger.info("Validated dependencies")
                return result
            except Exception as e:
                logger.error(f"Error validating dependencies: {str(e)}")
                raise ValueError(f"Error validating dependencies: {str(e)}")
    
    def _register_fix_dependencies_tool(self):
        """Register the fix_dependencies tool."""
        @self.server.tool()
        async def fix_dependencies(
            project_root: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Fix invalid dependencies automatically.
            
            Args:
                project_root: The directory of the project. Must be an absolute path.
            
            Returns:
                A dictionary containing the fix results
            """
            try:
                logger.info("Fixing dependencies")
                
                # Get project root from args or use current directory
                root_folder = project_root or os.getcwd()
                
                # Get tasks path from config
                tasks_path = get_config_value("tasks_file_path", root_folder)
                
                # Fix dependencies
                result = fix_dependencies(tasks_path)
                
                logger.info("Fixed dependencies")
                return result
            except Exception as e:
                logger.error(f"Error fixing dependencies: {str(e)}")
                raise ValueError(f"Error fixing dependencies: {str(e)}")


async def start_server():
    """Start the MCP server."""
    server = TaskinatorMCPServer()
    
    # Handle graceful shutdown
    try:
        await server.start()
    except Exception as e:
        logger.error(f"Failed to start MCP server: {str(e)}")
        sys.exit(1)
    finally:
        await server.stop()


def main():
    """Main entry point for the MCP server."""
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
