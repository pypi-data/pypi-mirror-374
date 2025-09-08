"""
Sync command for Taskinator.

This module provides the sync command for Taskinator's CLI.
"""

import logging
import os
from typing import Optional

from rich.console import Console

from taskinator.core.task_manager import get_tasks_path
from taskinator.plugins.sync.sync_command import pull_command as pull_standalone
from taskinator.plugins.sync.sync_command import push_command as push_standalone
from taskinator.plugins.sync.sync_command import resolve_command as resolve_standalone
from taskinator.plugins.sync.sync_command import setup_command as setup_standalone
from taskinator.plugins.sync.sync_command import status_command as status_standalone
from taskinator.plugins.sync.sync_command import sync_command as sync_standalone

# Set up logging
log = logging.getLogger(__name__)
console = Console()


def sync_command(
    provider: Optional[str] = None,
    direction: str = "bidirectional",
    force: bool = False,
    debug: bool = False,
    **kwargs,
) -> None:
    """Synchronize tasks with remote providers.

    Args:
        provider: Sync provider to use
        direction: Direction of synchronization
        force: Force update of all tasks, even if no changes detected
        debug: Enable debug logging
        **kwargs: Additional parameters
    """
    try:
        # Set up debug logging if requested
        if debug:
            logging.getLogger("taskinator.plugins.sync").setLevel(logging.DEBUG)
            log.debug("Debug logging enabled for sync")

        # Get tasks path
        tasks_path = get_tasks_path()

        # Call the standalone sync command
        sync_standalone(tasks_path, provider, direction, force=force, **kwargs)
    except Exception as e:
        console.print(f"[ERROR] Error syncing tasks: {str(e)}", style="bold red")


def setup_command(provider: Optional[str] = None, non_interactive: bool = False, **kwargs) -> None:
    """Set up sync provider.

    Args:
        provider: Sync provider to set up
        non_interactive: Whether to run in non-interactive mode (use environment variables only)
        **kwargs: Additional parameters
    """
    try:
        # Get tasks path
        tasks_path = get_tasks_path()

        # Call the standalone setup command
        setup_standalone(tasks_path, provider, non_interactive=non_interactive, **kwargs)
    except Exception as e:
        console.print(
            f"[ERROR] Error setting up sync provider: {str(e)}", style="bold red"
        )


def status_command(provider: Optional[str] = None, **kwargs) -> None:
    """Show sync status.

    Args:
        provider: Sync provider to show status for
        **kwargs: Additional parameters
    """
    try:
        # Get tasks path
        tasks_path = get_tasks_path()

        # Call the standalone status command
        status_standalone(tasks_path, provider, **kwargs)
    except Exception as e:
        console.print(f"[ERROR] Error showing sync status: {str(e)}", style="bold red")


def resolve_command(
    provider: Optional[str] = None,
    task_id: Optional[str] = None,
    resolution: str = "local",
    **kwargs,
) -> None:
    """Resolve sync conflicts.

    Args:
        provider: Sync provider to resolve conflicts for
        task_id: Optional task ID to resolve conflicts for
        resolution: Resolution strategy ('local' or 'remote')
        **kwargs: Additional parameters
    """
    try:
        # Get tasks path
        tasks_path = get_tasks_path()

        # Call the standalone resolve command
        resolve_standalone(tasks_path, provider, task_id, resolution, **kwargs)
    except Exception as e:
        console.print(
            f"[ERROR] Error resolving sync conflicts: {str(e)}", style="bold red"
        )


def push_command(provider: Optional[str] = None, **kwargs) -> None:
    """Push tasks to remote providers.

    Args:
        provider: Sync provider to push to
        **kwargs: Additional parameters
    """
    try:
        # Get tasks path
        tasks_path = get_tasks_path()

        # Call the standalone push command
        push_standalone(tasks_path, provider, **kwargs)
    except Exception as e:
        console.print(f"[ERROR] Error pushing tasks: {str(e)}", style="bold red")


def pull_command(provider: Optional[str] = None, **kwargs) -> None:
    """Pull tasks from remote providers.

    Args:
        provider: Sync provider to pull from
        **kwargs: Additional parameters
    """
    try:
        # Get tasks path
        tasks_path = get_tasks_path()

        # Call the standalone pull command
        pull_standalone(tasks_path, provider, **kwargs)
    except Exception as e:
        console.print(f"[ERROR] Error pulling tasks: {str(e)}", style="bold red")
