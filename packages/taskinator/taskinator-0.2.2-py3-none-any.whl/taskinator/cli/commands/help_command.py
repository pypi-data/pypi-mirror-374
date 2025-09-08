"""
Help command implementation for Taskinator.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

import tomli
from rich.box import ROUNDED, Box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

# Command groups and their commands
COMMAND_GROUPS = {
    "Task Generation": [
        {
            "name": "create-prd",
            "params": "[--name=<name>] [--template=<template>] [--output=<path>] [--update=<path>]",
            "description": "Create a PRD document through guided interactive process",
        },
        {
            "name": "parse-prd",
            "params": "--input=<file.txt> [--tasks=10]",
            "description": "Generate tasks from a PRD document",
        },
        {
            "name": "parse-story",
            "params": "<file_path> [--point-system=<system>] [--prefix=<prefix>]", 
            "description": "Generate tasks from a user story or feature file",
        },
        {
            "name": "generate",
            "params": "",
            "description": "Create individual task files from tasks.json",
        },
    ],
    "Sprint Management": [
        {
            "name": "sprint create",
            "params": "<name> [--goal=<text>] [--start-date=<date>] [--end-date=<date>]",
            "description": "Create a new sprint",
        },
        {
            "name": "sprint list",
            "params": "[--status=<status>]",
            "description": "List all sprints",
        },
        {
            "name": "sprint show",
            "params": "<sprint_id>",
            "description": "Show sprint details including tasks",
        },
        {
            "name": "sprint start",
            "params": "<sprint_id> [--start-date=<date>]",
            "description": "Start a sprint",
        },
        {
            "name": "sprint add-task",
            "params": "<sprint_id> <task_id> [--points=<points>]",
            "description": "Add a task to a sprint with story points",
        },
        {
            "name": "sprint burndown",
            "params": "<sprint_id> [--output=<path>] [--format=<format>]",
            "description": "Generate burndown chart for a sprint",
        },
    ],
    "Task Management": [
        {
            "name": "list",
            "params": "[--status=<status>] [--with-subtasks]",
            "description": "List all tasks with their status",
        },
        {
            "name": "set-status",
            "params": "--id=<id> --status=<status>",
            "description": "Update task status (done, pending, etc.)",
        },
        {
            "name": "update",
            "params": '--from=<id> --prompt="<context>"',
            "description": "Update tasks based on new requirements",
        },
        {
            "name": "add-task",
            "params": '--prompt="<text>" [--dependencies=<ids>]',
            "description": "Add a new task using AI",
        },
        {
            "name": "add-dependency",
            "params": "--id=<id> --depends-on=<id>",
            "description": "Add a dependency to a task",
        },
        {
            "name": "remove-dependency",
            "params": "--id=<id> --depends-on=<id>",
            "description": "Remove a dependency from a task",
        },
    ],
    "Task Analysis & Detail": [
        {
            "name": "analyze-complexity",
            "params": "[--research] [--threshold=5]",
            "description": "Analyze tasks and generate expansion recommendations",
        },
        {
            "name": "complexity-report",
            "params": "[--file=<path>]",
            "description": "Display the complexity analysis report",
        },
        {
            "name": "expand",
            "params": '--id=<id> [--num=5] [--research] [--context="<text>"]',
            "description": "Break down tasks into detailed subtasks",
        },
        {
            "name": "expand --all",
            "params": "[--force] [--research]",
            "description": "Expand all pending tasks with subtasks",
        },
        {
            "name": "clear-subtasks",
            "params": "--id=<id>",
            "description": "Remove subtasks from specified tasks",
        },
    ],
    "Story Point Management": [
        {
            "name": "story point-systems",
            "params": "",
            "description": "Display available story point systems",
        },
        {
            "name": "story explain-points",
            "params": "<point_value> [--system=<system>]",
            "description": "Explain how a story point value affects task generation",
        },
    ],
    "Azure DevOps Integration": [
        {
            "name": "azdo show",
            "params": "<work_item_id> [--parents]",
            "description": "Show information about an Azure DevOps work item",
        },
        {
            "name": "azdo import",
            "params": "<work_item_id> [--include-parents] [--output=<path>]",
            "description": "Import an Azure DevOps work item as Taskinator tasks",
        },
        {
            "name": "azdo tree",
            "params": "<work_item_id> [--up=<levels>] [--down=<levels>]",
            "description": "Show the hierarchy tree of an Azure DevOps work item",
        },
    ],
    "GitLab Integration": [
        {
            "name": "gitlab show",
            "params": "<issue_iid> [--parents]",
            "description": "Show information about a GitLab issue",
        },
        {
            "name": "gitlab import",
            "params": "<issue_iid> [--include-parents] [--output=<path>]",
            "description": "Import a GitLab issue as Taskinator tasks",
        },
        {
            "name": "gitlab tree",
            "params": "<issue_iid> [--up=<levels>] [--down=<levels>]",
            "description": "Show the hierarchy tree of a GitLab issue",
        },
    ],
    "Task Navigation & Viewing": [
        {
            "name": "next",
            "params": "",
            "description": "Show the next task to work on based on dependencies and priority",
        },
        {
            "name": "show",
            "params": "<id>",
            "description": "Display detailed information about a specific task",
        },
    ],
    "Dependency Management": [
        {
            "name": "validate-dependencies",
            "params": "",
            "description": "Identify invalid dependencies without fixing them",
        },
        {
            "name": "fix-dependencies",
            "params": "",
            "description": "Fix invalid dependencies automatically",
        },
    ],
    "Environment Variables": [
        {
            "name": "ANTHROPIC_API_KEY",
            "params": "Your Anthropic API key",
            "description": "Required",
        },
        {
            "name": "MODEL",
            "params": "Claude model to use",
            "description": "Default: claude-3-7-sonnet",
        },
        {
            "name": "MAX_TOKENS",
            "params": "Maximum tokens for responses",
            "description": "Default: 4000",
        },
        {
            "name": "TEMPERATURE",
            "params": "Temperature for model responses",
            "description": "Default: 0.7",
        },
        {
            "name": "PERPLEXITY_API_KEY",
            "params": "Perplexity API key for research",
            "description": "Optional",
        },
        {
            "name": "PERPLEXITY_MODEL",
            "params": "Perplexity model to use",
            "description": "Default: sonar-pro",
        },
        {
            "name": "DEBUG",
            "params": "Enable debug logging",
            "description": "Default: false",
        },
        {
            "name": "LOG_LEVEL",
            "params": "Console output level (debug,info,warn,error)",
            "description": "Default: info",
        },
        {
            "name": "DEFAULT_SUBTASKS",
            "params": "Default number of subtasks to generate",
            "description": "Default: 3",
        },
        {
            "name": "DEFAULT_PRIORITY",
            "params": "Default task priority",
            "description": "Default: medium",
        },
        {
            "name": "PROJECT_NAME",
            "params": "Project name displayed in UI",
            "description": "Default: Current directory name",
        },
    ],
}  # Added a closing bracket here


def print_header():
    """Print the Taskinator header."""
    console.print(
        r"""
  _____         _    _             _             
 |_   _|_ _ ___| | _(_)_ __   __ _| |_ ___  _ __ 
   | |/ _` / __| |/ / | '_ \ / _` | __/ _ \| '__|
   | | (_| \__ \   <| | | | | (_| | || (_) | |   
   |_|\__,_|___/_|\_\_|_| |_|\__,_|\__\___/|_|   
                                                 
"""
    )

    # Try to read version from pyproject.toml
    try:
        pyproject_path = Path(__file__).parents[3] / "pyproject.toml"
        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                pyproject_data = tomli.load(f)
            version = (
                pyproject_data.get("tool", {}).get("poetry", {}).get("version", "0.1.0")
            )
        else:
            version = "0.1.0"
    except Exception:
        # Fallback to default version
        version = "0.1.0"

    # Print project info panel
    # Use current directory name as project name
    project_name = os.path.basename(os.getcwd())

    project_panel = Panel(
        Text("\n   Version: ")
        + Text(version)
        + Text("   Project: ")
        + Text(project_name)
        + Text("\n\n"),
        width=47,
        box=ROUNDED,
    )
    console.print(project_panel)

    # Print CLI title panel
    cli_title_panel = Panel(
        Text("\n   Taskinator CLI\n\n"),
        width=25,
        box=ROUNDED,
    )
    console.print(cli_title_panel)


def print_command_group(group_name: str, commands: List[Dict]):
    """Print a command group with its commands."""
    # Print group header
    group_panel = Panel(
        Text(group_name),
        width=25,
        box=ROUNDED,
    )
    console.print(group_panel)

    # Create commands table (no visible borders)
    table = Table(
        show_header=False,
        box=None,
        padding=(0, 4, 0, 0),
    )

    # Add columns
    table.add_column("Command", style="cyan", width=25)
    table.add_column("Parameters", style="yellow", width=45)
    table.add_column("Description", style="white", width=45)

    # Add rows
    for command in commands:
        table.add_row(
            command["name"],
            command["params"],
            command["description"],
        )

    console.print(table)
    console.print()  # Add a blank line after each group


def help_command():
    """Display help information for all commands."""
    try:
        print_header()

        # Print each command group
        for group_name, commands in COMMAND_GROUPS.items():
            print_command_group(group_name, commands)

    except Exception as e:
        console.print(f"[ERROR] Error displaying help: {str(e)}", style="bold red")
