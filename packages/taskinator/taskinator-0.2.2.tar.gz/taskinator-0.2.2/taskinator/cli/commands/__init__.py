"""
Command implementations for the Taskinator CLI.
"""

from taskinator.cli.commands.analyze_complexity_command import (
    analyze_complexity_command,
)

# Import standalone commands that have been moved to the commands directory
from taskinator.cli.commands.help_command import help_command
from taskinator.cli.commands.list_command import list_command
from taskinator.cli.commands.next_command import next_command

# Import PRD commands
from taskinator.cli.commands.create_prd_command import create_prd_command

# Import PDD commands
from taskinator.cli.commands.pdd_command import convert_command as pdd_convert_command
from taskinator.cli.commands.pdd_command import to_tasks_command as pdd_to_tasks_command
from taskinator.cli.commands.set_status_command import set_status_command
from taskinator.cli.commands.show_command import show_command
from taskinator.cli.commands.sync_command import pull_command as sync_pull_command
from taskinator.cli.commands.sync_command import push_command as sync_push_command
from taskinator.cli.commands.sync_command import resolve_command as sync_resolve_command
from taskinator.cli.commands.sync_command import setup_command as setup_sync_command
from taskinator.cli.commands.sync_command import status_command as sync_status_command
from taskinator.cli.commands.sync_command import (
    sync_command,
)

# Import commands that are still in the original commands.py file
from taskinator.cli.commands_original import (  # analyze_complexity_command,  # Removed as it's now in its own file
    add_dependency_command,
    add_task_command,
    clear_subtasks_command,
    complexity_report_command,
    expand_command,
    export_csv,
    export_markdown,
    fix_dependencies_command,
    generate_command,
    init_command,
    parse_prd_command,
    reintegrate_command,
    remove_dependency_command,
    update_command,
    validate_dependencies_command,
)

__all__ = [
    "help_command",
    "list_command",
    "next_command",
    "show_command",
    "set_status_command",
    "add_dependency_command",
    "add_task_command",
    "analyze_complexity_command",
    "clear_subtasks_command",
    "complexity_report_command",
    "create_prd_command",
    "expand_command",
    "fix_dependencies_command",
    "generate_command",
    "reintegrate_command",
    "init_command",
    "parse_prd_command",
    "remove_dependency_command",
    "update_command",
    "validate_dependencies_command",
    "export_csv",
    "export_markdown",
    "sync_command",
    "setup_sync_command",
    "sync_status_command",
    "sync_resolve_command",
    "sync_push_command",
    "sync_pull_command",
    "pdd_convert_command",
    "pdd_to_tasks_command",
]
