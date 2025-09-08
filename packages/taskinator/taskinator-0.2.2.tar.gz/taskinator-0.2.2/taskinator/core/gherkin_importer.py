"""
Gherkin importer for synchronizing BDD feature files back to Taskinator tasks.
"""

import os
import re
from typing import Dict, List, Optional, Tuple

from rich.console import Console

from taskinator.core.file_storage import read_tasks, write_tasks
from taskinator.models.task import Task, TaskCollection

console = Console()


def parse_gherkin_file(feature_path: str) -> Dict:
    """
    Parse a Gherkin feature file and extract structured information.
    
    Args:
        feature_path: Path to the .feature file
        
    Returns:
        Dict: Parsed feature information
    """
    try:
        with open(feature_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        parsed = {
            'feature': None,
            'scenarios': [],
            'background': None,
            'metadata': {}
        }
        
        lines = content.split('\n')
        current_scenario = None
        current_section = None
        
        for line in lines:
            line = line.rstrip()
            
            # Skip comments and empty lines
            if not line.strip() or line.strip().startswith('#'):
                # Extract metadata from comments
                if line.strip().startswith('# Task ID:'):
                    parsed['metadata']['task_id'] = line.split('Task ID:')[1].strip()
                continue
            
            # Feature declaration
            if line.startswith('Feature:'):
                parsed['feature'] = {
                    'title': line.replace('Feature:', '').strip(),
                    'description': []
                }
                current_section = 'feature_description'
                continue
            
            # Background section
            elif line.startswith('  Background:'):
                parsed['background'] = {'steps': []}
                current_section = 'background'
                continue
            
            # Scenario declaration
            elif line.startswith('  Scenario:'):
                if current_scenario:
                    parsed['scenarios'].append(current_scenario)
                
                current_scenario = {
                    'title': line.replace('Scenario:', '').strip(),
                    'steps': [],
                    'task_id': None
                }
                current_section = 'scenario'
                continue
            
            # Steps (Given, When, Then, And, But)
            elif line.strip().startswith(('Given ', 'When ', 'Then ', 'And ', 'But ')):
                step = line.strip()
                
                if current_section == 'background' and parsed['background']:
                    parsed['background']['steps'].append(step)
                elif current_section == 'scenario' and current_scenario:
                    current_scenario['steps'].append(step)
                continue
            
            # Feature description lines
            elif current_section == 'feature_description' and line.startswith('  '):
                parsed['feature']['description'].append(line.strip())
                continue
            
            # Data tables or other content
            elif line.strip().startswith('|'):
                if current_scenario:
                    if 'data_table' not in current_scenario:
                        current_scenario['data_table'] = []
                    current_scenario['data_table'].append(line.strip())
                continue
        
        # Add the last scenario if exists
        if current_scenario:
            parsed['scenarios'].append(current_scenario)
        
        return parsed
        
    except Exception as e:
        console.print(f"[ERROR] Failed to parse Gherkin file {feature_path}: {str(e)}", style="bold red")
        raise


def extract_task_info_from_scenario(scenario: Dict) -> Optional[Dict]:
    """
    Extract task information from a parsed Gherkin scenario.
    
    Args:
        scenario: Parsed scenario dictionary
        
    Returns:
        Dict: Extracted task information or None
    """
    try:
        task_info = {
            'title': None,
            'dependencies': [],
            'test_strategy': [],
            'acceptance_criteria': []
        }
        
        # Extract task title from scenario title
        title = scenario.get('title', '')
        if title.startswith('Implement '):
            task_info['title'] = title.replace('Implement ', '').strip()
        else:
            task_info['title'] = title
        
        # Parse steps to extract information
        for step in scenario.get('steps', []):
            step_lower = step.lower()
            
            # Extract dependencies from Given steps
            if step_lower.startswith('given ') and ('task' in step_lower or 'completed' in step_lower):
                # Parse dependencies like "Given task 1, task 2 are completed"
                dep_match = re.findall(r'task (\d+)', step_lower)
                task_info['dependencies'].extend(dep_match)
            
            # Extract test strategy from Then/And steps
            elif step_lower.startswith(('then ', 'and ')) and any(word in step_lower for word in ['test', 'should', 'verify']):
                task_info['test_strategy'].append(step.replace('Then ', '').replace('And ', '').strip())
            
            # Extract acceptance criteria
            elif step_lower.startswith(('then ', 'and ')):
                task_info['acceptance_criteria'].append(step.replace('Then ', '').replace('And ', '').strip())
        
        # Extract subtasks from data tables
        if 'data_table' in scenario:
            task_info['subtasks'] = []
            for row in scenario['data_table']:
                # Simple parsing for | subtask_title |
                if '|' in row:
                    subtask_title = row.replace('|', '').strip()
                    if subtask_title:
                        task_info['subtasks'].append(subtask_title)
        
        return task_info
        
    except Exception as e:
        console.print(f"[ERROR] Failed to extract task info from scenario: {str(e)}", style="bold red")
        return None


def sync_feature_to_task(feature_path: str, task: Task) -> bool:
    """
    Synchronize changes from a feature file back to a task.
    
    Args:
        feature_path: Path to the modified feature file
        task: Task object to update
        
    Returns:
        bool: True if task was modified, False otherwise
    """
    try:
        parsed_feature = parse_gherkin_file(feature_path)
        modified = False
        
        # Find the relevant scenario for this task
        target_scenario = None
        for scenario in parsed_feature.get('scenarios', []):
            scenario_title = scenario.get('title', '').lower()
            task_title = task.title.lower()
            
            # Match by title similarity
            if task_title in scenario_title or scenario_title in task_title:
                target_scenario = scenario
                break
        
        if not target_scenario:
            console.print(f"[WARNING] No matching scenario found for task {task.id} in {feature_path}", style="yellow")
            return False
        
        # Extract task information from the scenario
        task_info = extract_task_info_from_scenario(target_scenario)
        if not task_info:
            return False
        
        # Update task fields if they've changed
        if task_info['title'] and task_info['title'] != task.title:
            console.print(f"[INFO] Updating task {task.id} title: '{task.title}' -> '{task_info['title']}'", style="blue")
            task.title = task_info['title']
            modified = True
        
        # Update dependencies
        new_deps = [str(dep) for dep in task_info['dependencies']]
        if new_deps != task.dependencies:
            console.print(f"[INFO] Updating task {task.id} dependencies: {task.dependencies} -> {new_deps}", style="blue")
            task.dependencies = new_deps
            modified = True
        
        # Update test strategy if available
        if task_info['test_strategy']:
            new_test_strategy = '\n'.join(task_info['test_strategy'])
            if hasattr(task, 'test_strategy'):
                if task.test_strategy != new_test_strategy:
                    console.print(f"[INFO] Updating task {task.id} test strategy", style="blue")
                    task.test_strategy = new_test_strategy
                    modified = True
            else:
                console.print(f"[INFO] Adding test strategy to task {task.id}", style="blue")
                task.test_strategy = new_test_strategy
                modified = True
        
        return modified
        
    except Exception as e:
        console.print(f"[ERROR] Failed to sync feature to task: {str(e)}", style="bold red")
        return False


def import_features_to_tasks(
    tasks_path: str, 
    features_dir: str
) -> Tuple[int, int]:
    """
    Import/sync all feature files in a directory back to tasks.
    
    Args:
        tasks_path: Path to tasks.json file
        features_dir: Directory containing .feature files
        
    Returns:
        Tuple[int, int]: (number_of_tasks_modified, total_features_processed)
    """
    try:
        # Read current tasks
        task_collection = read_tasks(tasks_path)
        tasks_by_id = {str(task.id): task for task in task_collection.tasks}
        
        # Find all feature files
        feature_files = []
        if os.path.isdir(features_dir):
            for filename in os.listdir(features_dir):
                if filename.endswith('.feature'):
                    feature_files.append(os.path.join(features_dir, filename))
        else:
            console.print(f"[ERROR] Features directory not found: {features_dir}", style="bold red")
            return 0, 0
        
        if not feature_files:
            console.print(f"[WARNING] No .feature files found in {features_dir}", style="yellow")
            return 0, 0
        
        modified_count = 0
        processed_count = 0
        
        # Process each feature file
        for feature_path in feature_files:
            try:
                processed_count += 1
                console.print(f"[INFO] Processing {os.path.basename(feature_path)}...", style="blue")
                
                # Check if this is a task-specific feature file
                task_id = None
                filename = os.path.basename(feature_path)
                
                # Try to extract task ID from filename (e.g., task_1_setup.feature)
                match = re.search(r'task_(\d+)_', filename)
                if match:
                    task_id = match.group(1)
                
                if task_id and task_id in tasks_by_id:
                    # Sync specific task
                    if sync_feature_to_task(feature_path, tasks_by_id[task_id]):
                        modified_count += 1
                else:
                    # Try to match scenarios to tasks by title
                    parsed_feature = parse_gherkin_file(feature_path)
                    for scenario in parsed_feature.get('scenarios', []):
                        task_info = extract_task_info_from_scenario(scenario)
                        if task_info and task_info['title']:
                            # Find matching task by title
                            for task in task_collection.tasks:
                                if task.title.lower() == task_info['title'].lower():
                                    if sync_feature_to_task(feature_path, task):
                                        modified_count += 1
                                    break
                
            except Exception as e:
                console.print(f"[ERROR] Failed to process {feature_path}: {str(e)}", style="bold red")
                continue
        
        # Write updated tasks if any were modified
        if modified_count > 0:
            write_tasks(tasks_path, task_collection)
            console.print(f"[SUCCESS] Updated {modified_count} tasks from {processed_count} feature files", style="green")
        else:
            console.print(f"[INFO] No tasks were modified from {processed_count} feature files", style="blue")
        
        return modified_count, processed_count
        
    except Exception as e:
        console.print(f"[ERROR] Failed to import features to tasks: {str(e)}", style="bold red")
        raise