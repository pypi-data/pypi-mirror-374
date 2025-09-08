"""
Gherkin exporter for converting Taskinator tasks to BDD feature files.
"""

import os
from datetime import datetime
from typing import List, Optional

from rich.console import Console

from taskinator.core.file_storage import read_tasks
from taskinator.models.task import Task, TaskCollection

console = Console()


def generate_bdd_scenarios_for_task(task: Task) -> List[str]:
    """
    Generate BDD scenarios based on actual functional usage of the implemented feature.
    
    Args:
        task: Task object to generate scenarios for
        
    Returns:
        List[str]: List of Gherkin scenario strings focused on user interactions
    """
    scenarios = []
    
    # Analyze task title and description to understand the actual functionality
    title_lower = task.title.lower()
    description = getattr(task, 'description', '') or ''
    desc_lower = description.lower()
    
    # Create realistic scenarios based on what the feature actually does
    if 'hamilton' in title_lower and 'dag' in title_lower:
        # Hamilton DAG scenarios - workflow orchestration
        scenarios.extend([
            """  Scenario: Process a prompt through the Hamilton DAG workflow
    Given I submit a prompt for processing
    When the Hamilton DAG orchestrates the workflow
    Then the prompt should be classified correctly
    And the workflow should route through appropriate nodes
    And I should receive the processed result
    And execution metrics should be captured""",
            
            """  Scenario: Handle workflow errors in DAG execution
    Given the Hamilton DAG is processing a complex prompt
    When an error occurs in one of the DAG nodes
    Then the error should be caught and logged
    And the workflow should fail gracefully
    And I should receive meaningful error information
    And the system should remain stable""",
            
            """  Scenario: Monitor DAG execution with observability
    Given multiple prompts are being processed
    When I check the observability dashboard
    Then I should see real-time execution metrics
    And I should see the workflow decision paths
    And performance data should be available for each node"""
        ])
    
    elif 'agno' in title_lower or 'agent' in title_lower:
        # AI Agent scenarios - agent discovery and execution
        scenarios.extend([
            """  Scenario: Discover and execute with appropriate AI agent
    Given I have a specific task requirement
    When the Agno framework analyzes the request
    Then it should identify the best-suited agent
    And execute the task using that agent
    And return the results with confidence scores""",
            
            """  Scenario: Handle agent selection for different task types
    Given I have various types of requests
    When the agent framework processes each request
    Then each should be routed to the appropriate specialist agent
    And the selection reasoning should be transparent
    And execution should be optimized for the task type"""
        ])
    
    elif 'routing' in title_lower or 'muscle-mem' in title_lower:
        # Intelligent routing scenarios - caching and optimization
        scenarios.extend([
            """  Scenario: Cache and retrieve frequently used patterns
    Given I submit a prompt similar to previous requests
    When the intelligent routing system processes it
    Then it should check the pattern cache
    And retrieve cached results if available
    And improve response time significantly""",
            
            """  Scenario: Route new requests to appropriate processing path
    Given I submit a novel prompt request
    When the routing system analyzes it
    Then it should identify the best processing path
    And route to appropriate agents or cached patterns
    And learn from the interaction for future requests"""
        ])
    
    elif 'parallel' in title_lower or 'execution' in title_lower:
        # Parallel execution scenarios
        scenarios.extend([
            """  Scenario: Execute multiple tasks in parallel
    Given I have multiple independent requests
    When the parallel execution framework processes them
    Then tasks should be executed concurrently where possible
    And resource allocation should be optimized
    And all results should be returned correctly""",
            
            """  Scenario: Manage resource allocation for concurrent tasks
    Given high system load with many concurrent requests
    When the execution framework manages the workload
    Then system performance should remain stable
    And resource limits should be respected
    And no task should be starved of resources"""
        ])
    
    elif 'observability' in title_lower or 'monitoring' in title_lower:
        # Observability scenarios
        scenarios.extend([
            """  Scenario: Monitor system performance and health
    Given the system is processing various requests
    When I access the observability dashboard
    Then I should see real-time performance metrics
    And system health indicators should be accurate
    And I should be able to identify performance bottlenecks""",
            
            """  Scenario: Track request flows and execution paths
    Given requests are being processed through the system
    When I examine the observability data
    Then I should see complete request tracing
    And execution paths should be clearly visible
    And timing information should be available for optimization"""
        ])
    
    else:
        # Generic functional scenarios based on description
        feature_name = task.title
        
        scenarios.append(f"""  Scenario: Use {feature_name} for its intended purpose
    Given the {feature_name.lower()} is available
    When I interact with it using typical inputs
    Then it should perform its core functionality correctly
    And provide the expected results
    And handle edge cases appropriately""")
        
        # Add test strategy based scenarios if available
        if hasattr(task, 'test_strategy') and task.test_strategy:
            test_lines = [line.strip() for line in task.test_strategy.split('\n') 
                         if line.strip() and not line.startswith('#')]
            if test_lines:
                scenarios.append(f"""  Scenario: Validate {feature_name} behavior
    Given the {feature_name.lower()} is functioning
    When I test its various capabilities
    Then {test_lines[0].lower() if test_lines else 'it should pass all tests'}
    And all validation checks should succeed""")
    
    return scenarios


def task_to_gherkin_feature(task: Task) -> str:
    """
    Convert a single task to a complete Gherkin feature focused on actual usage.
    
    Args:
        task: Task object to convert
        
    Returns:
        str: Complete Gherkin feature string representing the implemented capability
    """
    title_lower = task.title.lower()
    description = getattr(task, 'description', '') or ''
    
    # Create proper feature title and user story based on actual functionality
    if 'hamilton' in title_lower and 'dag' in title_lower:
        feature_title = "Hamilton DAG Workflow Orchestration"
        user_story = """  As a developer using the Intelligent Prompt-to-Artifact Engine
  I want the Hamilton DAG orchestration layer to manage prompt processing workflows
  So that I can reliably transform prompts into artifacts with full observability and error handling"""
        background = """  Background:
    Given the Hamilton DAG driver is properly configured
    And all required dependencies are available
    And the observability system is active"""
    
    elif 'agno' in title_lower or 'agent' in title_lower:
        feature_title = "Agno AI Agent Framework"
        user_story = """  As a user of the intelligent system
  I want the Agno framework to automatically select and execute the best AI agent for my requests
  So that I can get optimal results without having to choose agents manually"""
        background = """  Background:
    Given the Agno AI agent framework is initialized
    And multiple specialized agents are available
    And agent selection algorithms are functioning"""
    
    elif 'routing' in title_lower or 'muscle-mem' in title_lower:
        feature_title = "Intelligent Routing System (muscle-mem)"
        user_story = """  As a user submitting requests to the system
  I want the intelligent routing system to cache and optimize my request processing
  So that I get faster responses and the system learns from usage patterns"""
        background = """  Background:
    Given the muscle-mem caching system is active
    And pattern recognition algorithms are trained
    And the routing decision engine is functioning"""
    
    elif 'parallel' in title_lower or 'execution' in title_lower:
        feature_title = "Parallel Execution Framework"
        user_story = """  As a user with multiple concurrent requests
  I want the system to execute my tasks in parallel when possible
  So that I can achieve better performance and throughput"""
        background = """  Background:
    Given the parallel execution framework is configured
    And sufficient system resources are available
    And task scheduling algorithms are active"""
    
    elif 'burr' in title_lower or 'state machine' in title_lower:
        feature_title = "Burr State Machine for Complex Workflows"
        user_story = """  As a user with complex multi-step workflows
  I want the Burr state machine to manage workflow states and transitions
  So that I can handle complex business logic with proper state management"""
        background = """  Background:
    Given the Burr state machine is initialized
    And workflow state definitions are loaded
    And state transition rules are configured"""
    
    elif 'dspy' in title_lower or 'optimization' in title_lower:
        feature_title = "DSPy Optimization Framework"
        user_story = """  As a user of AI-powered features
  I want the DSPy framework to optimize prompts and model interactions
  So that I can get better results with improved efficiency and accuracy"""
        background = """  Background:
    Given the DSPy optimization framework is configured
    And optimization algorithms are trained
    And performance metrics are being tracked"""
    
    elif 'observability' in title_lower or 'monitoring' in title_lower:
        feature_title = "Comprehensive Observability System"
        user_story = """  As a system operator or developer
  I want comprehensive observability into system performance and behavior
  So that I can monitor, debug, and optimize the system effectively"""
        background = """  Background:
    Given the observability system is deployed
    And metrics collection is active
    And dashboards are configured and accessible"""
    
    elif 'security' in title_lower or 'enterprise' in title_lower:
        feature_title = "Security Framework and Enterprise Features"
        user_story = """  As an enterprise user or administrator
  I want robust security controls and enterprise-grade features
  So that I can deploy the system safely in production environments"""
        background = """  Background:
    Given security policies are configured
    And authentication systems are active
    And enterprise features are enabled"""
    
    elif 'testing' in title_lower or 'documentation' in title_lower:
        feature_title = "End-to-End Testing and Documentation"
        user_story = """  As a developer or user of the system
  I want comprehensive testing coverage and clear documentation
  So that I can understand, use, and maintain the system confidently"""
        background = """  Background:
    Given the testing framework is set up
    And documentation is accessible
    And test environments are available"""
    
    else:
        # Generic approach - extract the actual capability from description
        feature_title = task.title
        if description:
            goal = description.split('.')[0] if '.' in description else description[:100]
            user_story = f"""  As a user of the system
  I want to use {task.title.lower()}
  So that {goal.lower()}"""
        else:
            user_story = f"""  As a user
  I want to interact with {task.title.lower()}
  So that I can accomplish my intended goals"""
        
        background = """  Background:
    Given the system is properly configured
    And all required components are available
    And the feature is accessible"""
    
    feature_content = f"""Feature: {feature_title}
{user_story}

{background}"""
    
    # Add scenarios
    scenarios = generate_bdd_scenarios_for_task(task)
    if hasattr(task, 'bdd_scenarios') and task.bdd_scenarios:
        # Add custom BDD scenarios if they exist
        scenarios.extend(task.bdd_scenarios)
    
    for scenario in scenarios:
        feature_content += f"\n\n{scenario}"
    
    return feature_content


def tasks_to_gherkin_feature(tasks: List[Task], project_name: str = "Project") -> str:
    """
    Convert a list of tasks to a complete Gherkin feature file.
    
    Args:
        tasks: List of Task objects
        project_name: Name of the project for the feature
        
    Returns:
        str: Complete Gherkin feature file content
    """
    feature_content = f"""Feature: {project_name} Implementation
  As a development team
  I want to implement all project tasks
  So that the project requirements are fulfilled

  Background:
    Given a development environment is set up
    And all necessary dependencies are installed
    And the project repository is accessible

"""
    
    # Sort tasks by ID for consistent output
    sorted_tasks = sorted(tasks, key=lambda t: t.id)
    
    for task in sorted_tasks:
        feature_content += task_to_gherkin_scenario(task) + "\n"
    
    return feature_content


def export_tasks_to_gherkin(
    tasks_path: str, 
    output_dir: str = None, 
    project_name: str = None
) -> str:
    """
    Export all tasks to a Gherkin feature file.
    
    Args:
        tasks_path: Path to tasks.json file
        output_dir: Directory to write the feature file (defaults to tasks dir)
        project_name: Name of the project (defaults to "Project")
        
    Returns:
        str: Path to the generated feature file
    """
    try:
        # Read tasks
        task_collection = read_tasks(tasks_path)
        tasks = task_collection.tasks
        
        if not tasks:
            console.print("[WARNING] No tasks found to export", style="yellow")
            return None
        
        # Set defaults
        if output_dir is None:
            # Default to ./features directory (standard BDD location)
            project_root = os.path.dirname(os.path.dirname(tasks_path))  # Go up from tasks/ to project root
            output_dir = os.path.join(project_root, "features")
        
        if project_name is None:
            project_name = "Project"
        
        # Generate feature content
        feature_content = tasks_to_gherkin_feature(tasks, project_name)
        
        # Write to file
        os.makedirs(output_dir, exist_ok=True)
        feature_filename = f"{project_name.lower().replace(' ', '_')}_implementation.feature"
        feature_path = os.path.join(output_dir, feature_filename)
        
        with open(feature_path, 'w', encoding='utf-8') as f:
            f.write(f"# Generated by Taskinator on {datetime.now().isoformat()}\n")
            f.write(f"# Tasks exported from: {tasks_path}\n\n")
            f.write(feature_content)
        
        console.print(f"[SUCCESS] Exported {len(tasks)} tasks to {feature_path}", style="green")
        return feature_path
        
    except Exception as e:
        console.print(f"[ERROR] Failed to export tasks to Gherkin: {str(e)}", style="bold red")
        raise


def export_task_to_individual_feature(
    task: Task, 
    output_dir: str, 
    project_name: str = "Project"
) -> str:
    """
    Export a single task to its own feature file.
    
    Args:
        task: Task object to export
        output_dir: Directory to write the feature file
        project_name: Name of the project
        
    Returns:
        str: Path to the generated feature file
    """
    try:
        # Generate complete feature content using the new approach
        feature_content = task_to_gherkin_feature(task)
        
        # Write to file
        os.makedirs(output_dir, exist_ok=True)
        safe_title = task.title.lower().replace(' ', '_').replace('/', '_').replace('-', '_')
        feature_filename = f"{safe_title}.feature"
        feature_path = os.path.join(output_dir, feature_filename)
        
        with open(feature_path, 'w', encoding='utf-8') as f:
            f.write(f"# Generated by Taskinator on {datetime.now().isoformat()}\n")
            f.write(f"# Task ID: {task.id}\n")
            f.write(f"# This feature represents the capability implemented by the task\n\n")
            f.write(feature_content)
        
        return feature_path
        
    except Exception as e:
        console.print(f"[ERROR] Failed to export task {task.id} to Gherkin: {str(e)}", style="bold red")
        raise


def export_tasks_to_individual_features(
    tasks_path: str, 
    output_dir: str = None, 
    project_name: str = None
) -> List[str]:
    """
    Export each task to its own individual feature file.
    
    Args:
        tasks_path: Path to tasks.json file
        output_dir: Directory to write feature files (defaults to tasks/features)
        project_name: Name of the project
        
    Returns:
        List[str]: Paths to all generated feature files
    """
    try:
        # Read tasks
        task_collection = read_tasks(tasks_path)
        tasks = task_collection.tasks
        
        if not tasks:
            console.print("[WARNING] No tasks found to export", style="yellow")
            return []
        
        # Set defaults
        if output_dir is None:
            # Default to ./features directory (standard BDD location)
            project_root = os.path.dirname(os.path.dirname(tasks_path))  # Go up from tasks/ to project root
            output_dir = os.path.join(project_root, "features")
        
        if project_name is None:
            project_name = "Project"
        
        # Export each task
        feature_paths = []
        for task in tasks:
            feature_path = export_task_to_individual_feature(task, output_dir, project_name)
            feature_paths.append(feature_path)
        
        console.print(f"[SUCCESS] Exported {len(tasks)} tasks to individual feature files in {output_dir}", style="green")
        return feature_paths
        
    except Exception as e:
        console.print(f"[ERROR] Failed to export tasks to individual features: {str(e)}", style="bold red")
        raise