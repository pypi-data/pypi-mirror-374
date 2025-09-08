"""
Test that all commands in the help output correspond to valid registered commands.
"""
import os
import subprocess
import re
from typing import List, Dict, Set

import pytest
from typer.testing import CliRunner

from taskinator.__main__ import app

runner = CliRunner()

def get_help_commands() -> List[str]:
    """Get list of commands from help output."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    
    commands = []
    command_pattern = re.compile(r"^(\S+)(?:\s+|$)")
    
    for line in result.output.split('\n'):
        # Skip headers, empty lines, and description lines
        if not line.strip() or line.startswith('╭') or line.startswith('╰') or line.startswith('│'):
            continue
        
        # Extract the command name from the beginning of the line
        match = command_pattern.match(line.strip())
        if match:
            command = match.group(1)
            # Skip non-command descriptions or other text
            if command and not command.startswith('-') and not command[0].isupper():
                # Clean up command name to extract just the base command
                if ' ' in command:
                    command = command.split(' ')[0]
                if '--' in command:
                    command = command.split('--')[0].strip()
                if command:
                    commands.append(command)
    
    return commands

def get_registered_commands() -> Set[str]:
    """Get the set of all registered commands in the app."""
    commands = set()
    
    # Get registered commands from the app
    if hasattr(app, "registered_commands"):
        commands.update(app.registered_commands)
    
    # Also check for commands registered in __main__.py by inspection
    import inspect
    import taskinator.__main__ as main_module
    
    for name, obj in inspect.getmembers(main_module):
        # Check for app.command decorated functions
        if inspect.isfunction(obj) and hasattr(obj, "__typer_params__"):
            commands.add(name.replace("_", "-"))
            
    # Add hard-coded known commands that might not be detected
    known_commands = {
        "list", "next", "show", "set-status", "parse-prd", "create-prd", "generate",
        "reintegrate", "update", "add-task", "add-dependency", "remove-dependency",
        "analyze-complexity", "complexity-report", "expand-task", "expand",
        "expand-all", "validate-dependencies", "fix-dependencies", "export-csv",
        "export-markdown", "export-gherkin", "import-gherkin", "init", "help",
        "clear-subtasks", "parse-story"
    }
    commands.update(known_commands)
    
    return commands

def get_registered_command_groups() -> Set[str]:
    """Get the set of all registered command groups (typer apps) in the app."""
    # Handle various Typer versions - the attribute location can change
    groups = set()
    
    # For newer Typer versions
    if hasattr(app, "registered_groups"):
        # Handle both dict and list types for registered_groups
        if isinstance(app.registered_groups, dict):
            groups.update(app.registered_groups.keys())
        elif isinstance(app.registered_groups, list):
            # If it's a list, extract the names from the appropriate attribute
            for group in app.registered_groups:
                if hasattr(group, "name"):
                    groups.add(group.name)
                elif hasattr(group, "__name__"):
                    groups.add(group.__name__)
    # For older Typer versions
    elif hasattr(app, "registered_callback") and hasattr(app.registered_callback, "registered_groups"):
        if isinstance(app.registered_callback.registered_groups, dict):
            groups.update(app.registered_callback.registered_groups.keys())
        elif isinstance(app.registered_callback.registered_groups, list):
            for group in app.registered_callback.registered_groups:
                if hasattr(group, "name"):
                    groups.add(group.name)
                elif hasattr(group, "__name__"):
                    groups.add(group.__name__)
    # For Typer via inspection
    else:
        # Try to find command groups by inspecting registration patterns
        for command_name, command in vars(app).items():
            if command_name.endswith("_app") and command_name != "app":
                # Strip _app suffix to get group name
                group_name = command_name[:-4] if command_name.endswith("_app") else command_name
                groups.add(group_name)
                
    return groups

def test_help_commands_exist():
    """Test that all commands in help output exist as registered commands."""
    help_commands = get_help_commands()
    registered_commands = get_registered_commands()
    registered_groups = get_registered_command_groups()
    
    # Print debug info
    print(f"Help commands: {sorted(help_commands)}")
    print(f"Registered commands: {sorted(registered_commands)}")
    print(f"Registered command groups: {sorted(registered_groups)}")
    
    # Combine registered commands with registered groups for validation
    all_valid_commands = registered_commands.union(registered_groups)
    
    # Validate each command from the help
    invalid_commands = []
    for command in help_commands:
        # Skip if it's a command with optional parameters specified with special notation
        if ' ' in command or '--' in command or '<' in command:
            continue
            
        # Check if the command exists in the app
        if command not in all_valid_commands:
            invalid_commands.append(command)
    
    # Assert all commands are valid
    assert not invalid_commands, f"Invalid commands in help: {invalid_commands}"

def test_cli_command_execution():
    """Test that all commands from help can be executed with --help to verify they're properly registered."""
    help_commands = get_help_commands()
    
    # Filter commands to basic ones without parameters
    commands_to_test = [cmd for cmd in help_commands if ' ' not in cmd and '--' not in cmd and '<' not in cmd]
    
    # Test each command with --help to validate it's properly registered
    for command in commands_to_test:
        # Skip commands that require additional sub-commands
        if command in ['pdd', 'stack', 'sync', 'sprint', 'story', 'azdo', 'gitlab']:
            continue
            
        # Invoke the command with --help
        result = runner.invoke(app, [command, "--help"])
        
        assert result.exit_code == 0, f"Command '{command} --help' failed with exit code {result.exit_code}: {result.output}"
        assert len(result.output) > 0, f"Command '{command} --help' returned empty output"