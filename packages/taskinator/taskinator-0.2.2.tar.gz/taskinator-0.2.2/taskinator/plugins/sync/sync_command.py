"""
Sync command for Taskinator.

This module provides the sync command for Taskinator's CLI.
"""

import importlib
import json
import logging
import os
import asyncio
from typing import Any, Dict, List, Optional, TypeVar, Union, cast

from taskinator.plugins.sync.nextcloud.nextcloud_client import RateLimitExceeded

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from taskinator.core.task_manager import get_tasks_path

# Set up logging
log = logging.getLogger(__name__)
console = Console()

# Define a generic type variable for the return type
T = TypeVar('T')


async def with_retry_async(
    func, *args, max_retries=3, base_delay=1.0, max_delay=60.0, **kwargs
) -> T:
    """Helper function to retry async operations with exponential backoff.
    
    Args:
        func: The async function to call
        args: Positional arguments to pass to func
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        kwargs: Keyword arguments to pass to func
        
    Returns:
        The result of the function call
        
    Raises:
        RateLimitExceeded: If rate limit is exceeded after max_retries
        Exception: Any other exception raised by the function
    """
    import asyncio
    import random
    
    last_exception = None
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except RateLimitExceeded as e:
            last_exception = e
            # Only retry if we haven't reached max_retries
            if attempt < max_retries - 1:
                # Calculate delay with exponential backoff and jitter
                delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
                if hasattr(e, 'retry_after') and e.retry_after:
                    delay = max(delay, float(e.retry_after))
                    
                log.warning(
                    f"Rate limit exceeded, retrying in {delay:.2f} seconds "
                    f"(attempt {attempt + 1}/{max_retries})"
                )
                await asyncio.sleep(delay)
            else:
                # We've reached max_retries, raise the exception
                raise
    
    # This should not be reached, but just in case
    if last_exception:
        raise last_exception
    raise RuntimeError("Unexpected error in with_retry_async")


def discover_sync_plugins():
    """Discover available sync plugins.

    Returns:
        Dict[str, Any]: Dictionary of plugin name to plugin instance
    """
    plugins = {}

    try:
        # Get the sync plugins directory
        plugins_dir = os.path.join(os.path.dirname(__file__))

        # Find all directories in the plugins directory (excluding __pycache__)
        plugin_dirs = [
            d
            for d in os.listdir(plugins_dir)
            if os.path.isdir(os.path.join(plugins_dir, d)) and not d.startswith("__")
        ]

        # Import each plugin
        for plugin_dir in plugin_dirs:
            try:
                # Check if the plugin has an __init__.py with get_plugin function
                module_name = f"taskinator.plugins.sync.{plugin_dir}"
                module = importlib.import_module(module_name)

                if hasattr(module, "get_plugin"):
                    plugin = module.get_plugin()
                    plugins[plugin_dir] = plugin
                    log.debug(f"Loaded sync plugin: {plugin_dir}")
            except Exception as e:
                log.error(f"Error loading sync plugin {plugin_dir}: {str(e)}")
    except Exception as e:
        log.error(f"Error discovering sync plugins: {str(e)}")

    return plugins


async def status_command(
    project_directory: str,
    provider: Optional[str] = None,
    verbose: bool = False,
    **kwargs,
) -> None:
    """
    Show sync status for the configured sync provider.
    
    Args:
        project_directory: The project directory
        provider: The sync provider to use
        verbose: Whether to show verbose output
        **kwargs: Additional parameters
    """
    console.print(
        Panel(
            "Checking sync status...",
            title="Sync Status",
            style="blue",
        )
    )
    
    try:
        # Get the configured sync plugin
        plugin = await get_sync_plugin(project_directory, provider)
        if plugin:
            # Get sync status with retry
            await with_retry_async(
                plugin.status_command,
                project_directory,
                verbose=verbose,
                max_retries=3,
                base_delay=1.0,
                max_delay=15.0,
                **kwargs
            )
        else:
            console.print("[ERROR] No configured sync plugin found", style="bold red")
    except RateLimitExceeded as e:
        console.print(f"[ERROR] Rate limit exceeded: {str(e)}", style="bold red")
        console.print("Try again in a few minutes or use --provider to specify a different provider.")
    except Exception as e:
        console.print(f"[ERROR] Failed to check status: {str(e)}", style="bold red")


async def sync_command(
    project_directory: str,
    provider: Optional[str] = None,
    direction: str = "bidirectional",
    **kwargs,
) -> None:
    """
    Synchronize tasks with the configured sync provider.
    
    Args:
        project_directory: The project directory
        provider: The sync provider to use
        direction: The sync direction (push, pull, or bidirectional)
        **kwargs: Additional parameters
    """
    console.print(
        Panel(
            f"Synchronizing tasks with configured provider ({direction})...",
            title="Sync",
            style="blue",
        )
    )
    
    try:
        # Get the configured sync plugin
        plugin = await get_sync_plugin(project_directory, provider)
        if plugin:
            # Sync tasks with retry
            await with_retry_async(
                plugin.sync_command,
                project_directory,
                direction=direction,
                max_retries=3,
                base_delay=2.0,
                max_delay=30.0,
                **kwargs
            )
        else:
            console.print("[ERROR] Failed to sync: No configured sync plugin found", style="bold red")
    except RateLimitExceeded as e:
        console.print(f"[ERROR] Rate limit exceeded: {str(e)}", style="bold red")
        console.print("Try again in a few minutes or use --provider to specify a different provider.")
    except Exception as e:
        console.print(f"[ERROR] Failed to sync: {str(e)}", style="bold red")


async def push_command(
    project_directory: str,
    provider: Optional[str] = None,
    **kwargs,
) -> None:
    """
    Push tasks to the configured sync provider.
    
    Args:
        project_directory: The project directory
        provider: The sync provider to use
        **kwargs: Additional parameters
    """
    console.print(
        Panel(
            "Pushing tasks to configured provider...",
            title="Sync Push",
            style="blue",
        )
    )
    
    try:
        # Get the configured sync plugin
        plugin = await get_sync_plugin(project_directory, provider)
        if plugin:
            # Push tasks with retry
            await with_retry_async(
                plugin.push_command,
                project_directory,
                max_retries=3,
                base_delay=2.0,
                max_delay=30.0,
                **kwargs
            )
        else:
            console.print("[ERROR] Failed to push: No configured sync plugin found", style="bold red")
    except RateLimitExceeded as e:
        console.print(f"[ERROR] Rate limit exceeded: {str(e)}", style="bold red")
        console.print("Try again in a few minutes or use --provider to specify a different provider.")
    except Exception as e:
        console.print(f"[ERROR] Failed to push: {str(e)}", style="bold red")


async def pull_command(
    project_directory: str,
    provider: Optional[str] = None,
    **kwargs,
) -> None:
    """
    Pull tasks from the configured sync provider.
    
    Args:
        project_directory: The project directory
        provider: The sync provider to use
        **kwargs: Additional parameters
    """
    console.print(
        Panel(
            "Pulling tasks from configured provider...",
            title="Sync Pull",
            style="blue",
        )
    )
    
    try:
        # Get the configured sync plugin
        plugin = await get_sync_plugin(project_directory, provider)
        if plugin:
            # Pull tasks with retry
            await with_retry_async(
                plugin.pull_command,
                project_directory,
                max_retries=3, 
                base_delay=2.0,
                max_delay=30.0,
                **kwargs
            )
        else:
            console.print("[ERROR] Failed to pull: No configured sync plugin found", style="bold red")
    except RateLimitExceeded as e:
        console.print(f"[ERROR] Rate limit exceeded: {str(e)}", style="bold red")
        console.print("Try again in a few minutes or use --provider to specify a different provider.")
    except Exception as e:
        console.print(f"[ERROR] Failed to pull: {str(e)}", style="bold red")


async def setup_command(
    project_directory: str, provider: str, non_interactive: bool = False, **kwargs
) -> None:
    """
    Set up sync for the specified provider.
    
    Args:
        project_directory: The project directory
        provider: The sync provider to set up
        non_interactive: Whether to run in non-interactive mode (use environment variables only)
        **kwargs: Additional parameters
    """
    console.print(
        Panel(
            f"Setting up {provider} sync...",
            title="Sync Setup",
            style="blue",
        )
    )
    
    # Discover sync plugins
    plugins = discover_sync_plugins()
    
    if not plugins:
        console.print("[ERROR] No sync plugins found", style="bold red")
        return
    
    # Check if the specified provider is available
    if provider not in plugins:
        console.print(f"[ERROR] Provider {provider} not found", style="bold red")
        console.print(f"Available providers: {', '.join(plugins.keys())}")
        return
    
    # Set up the specified provider
    plugin = plugins[provider]
    try:
        await plugin.setup_command(project_directory, **kwargs)
    except Exception as e:
        console.print(f"[ERROR] Failed to set up {provider} sync: {str(e)}", style="bold red")


async def resolve_command(
    project_directory: str,
    provider: Optional[str] = None,
    task_id: Optional[str] = None,
    resolution: str = "local",
    **kwargs,
) -> None:
    """
    Resolve sync conflicts for the configured sync provider.
    
    Args:
        project_directory: The project directory
        provider: The sync provider to use
        task_id: Optional task ID to resolve conflicts for
        resolution: Resolution strategy (local, remote, or interactive)
        **kwargs: Additional parameters
    """
    console.print(
        Panel(
            f"Resolving sync conflicts using {resolution} strategy...",
            title="Sync Resolve",
            style="blue",
        )
    )
    
    try:
        # Get the configured sync plugin
        plugin = await get_sync_plugin(project_directory, provider)
        if plugin:
            # Resolve conflicts with retry
            await with_retry_async(
                plugin.resolve_command,
                project_directory,
                task_id=task_id, 
                resolution=resolution,
                max_retries=3,
                base_delay=2.0,
                max_delay=30.0,
                **kwargs
            )
        else:
            console.print("[ERROR] No configured sync plugin found", style="bold red")
    except RateLimitExceeded as e:
        console.print(f"[ERROR] Rate limit exceeded: {str(e)}", style="bold red")
        console.print("Try again in a few minutes or use --provider to specify a different provider.")
    except Exception as e:
        console.print(f"[ERROR] Failed to resolve conflicts: {str(e)}", style="bold red")


async def get_sync_plugin(project_directory: str, provider: Optional[str] = None):
    """
    Get the sync plugin to use.
    
    Args:
        project_directory: The project directory
        provider: The sync provider to use
        
    Returns:
        The sync plugin to use
    """
    # Discover sync plugins
    plugins = discover_sync_plugins()
    
    if not plugins:
        console.print("[ERROR] No sync plugins found", style="bold red")
        return None
    
    # If provider is specified, use that provider
    if provider:
        if provider not in plugins:
            console.print(f"[ERROR] Provider {provider} not found", style="bold red")
            return None
        
        plugin = plugins[provider]
        return plugin
    
    # Otherwise, get the configured plugin
    plugin_name = get_configured_sync_plugin(project_directory)
    
    if not plugin_name or plugin_name not in plugins:
        console.print("[ERROR] No configured sync plugin found", style="bold red")
        return None
    
    return plugins[plugin_name]


def get_configured_sync_plugin(project_directory: str) -> Optional[str]:
    """
    Get the configured sync plugin for the project.
    
    Args:
        project_directory: The project directory
        
    Returns:
        The name of the configured sync plugin, or None if no plugin is configured
    """
    # Look for a .taskinator/sync.json file in the project directory
    sync_config_path = os.path.join(project_directory, ".taskinator", "config.json")
    
    if not os.path.exists(sync_config_path):
        return None
    
    try:
        with open(sync_config_path, "r") as f:
            config = json.load(f)
            # Check for sync.nextcloud configuration
            if "sync" in config and "nextcloud" in config["sync"]:
                return "nextcloud"
            return None
    except Exception as e:
        console.print(f"[ERROR] Failed to load sync configuration: {str(e)}", style="bold red")
        return None


def sync_status_standalone(
    project_directory: str,
    provider: Optional[str] = None,
    verbose: bool = False,
    **kwargs,
) -> None:
    """Show sync status.

    Args:
        project_directory: The project directory
        provider: Sync provider to show status for
        verbose: Show detailed information
        **kwargs: Additional parameters
    """
    # Get available plugins
    plugins = discover_sync_plugins()

    if not plugins:
        console.print("[WARNING] No sync plugins found.", style="yellow")
        return

    # If a specific provider is requested
    if provider:
        if provider not in plugins:
            console.print(
                f"[ERROR] Sync provider '{provider}' not found.", style="bold red"
            )
            console.print(f"Available providers: {', '.join(plugins.keys())}")
            return

        # Use the specified provider
        plugin = plugins[provider]
        status = plugin.get_status(project_directory, verbose=verbose, **kwargs)

        # Display status
        _display_sync_status(provider, status, verbose)
    else:
        # Use all available providers
        for plugin_name, plugin in plugins.items():
            console.print(f"[INFO] Sync status for {plugin_name}:")
            status = plugin.get_status(project_directory, verbose=verbose, **kwargs)

            # Display status
            _display_sync_status(plugin_name, status, verbose)


def _display_sync_status(
    provider: str, status: Dict[str, Any], verbose: bool = False
) -> None:
    """Display sync status.

    Args:
        provider: Sync provider name
        status: Sync status
        verbose: Show detailed information
    """
    # Create a table for the status
    table = Table(
        title=f"{provider.capitalize()} Sync Status",
        show_header=True,
        header_style="bold",
    )
    table.add_column("Metric", style="dim")
    table.add_column("Count")

    # Add rows for each status
    table.add_row("Total Tasks", str(status["total"]))
    table.add_row("Synced", str(status["synced"]))
    table.add_row("Pending", str(status["pending"]))
    table.add_row("Conflicts", str(status["conflict"]))
    table.add_row("Errors", str(status["error"]))
    table.add_row("Not Synced", str(status["not_synced"]))

    console.print(table)

    # Show detailed information if requested
    if verbose and "details" in status:
        console.print("\nDetailed Sync Information:", style="bold")

        # Create a table for detailed information
        detail_table = Table(show_header=True, header_style="bold")
        detail_table.add_column("Task ID", style="dim")
        detail_table.add_column("Title")
        detail_table.add_column("Status")
        detail_table.add_column("Last Synced")
        detail_table.add_column("Remote ID")

        # Add rows for each task
        for task_id, details in status["details"].items():
            detail_table.add_row(
                str(task_id),
                details.get("title", ""),
                details.get("status", ""),
                details.get("last_sync", "Never"),
                details.get("remote_id", "None"),
            )

        console.print(detail_table)

    # Show conflicts if any
    if status["conflict"] > 0:
        console.print(
            "\n[WARNING] There are sync conflicts. Use 'taskinator sync:resolve' to resolve them.",
            style="yellow",
        )


def sync_resolve_standalone(
    project_directory: str,
    provider: Optional[str] = None,
    task_id: Optional[str] = None,
    resolution: str = "local",
    **kwargs,
) -> None:
    """Resolve sync conflicts.

    Args:
        project_directory: The project directory
        provider: Sync provider to resolve conflicts for
        task_id: Task ID to resolve conflicts for
        resolution: Resolution strategy (local or remote)
        **kwargs: Additional parameters
    """
    # Get available plugins
    plugins = discover_sync_plugins()

    if not plugins:
        console.print("[WARNING] No sync plugins found.", style="yellow")
        return

    # If a specific provider is requested
    if provider:
        if provider not in plugins:
            console.print(
                f"[ERROR] Sync provider '{provider}' not found.", style="bold red"
            )
            console.print(f"Available providers: {', '.join(plugins.keys())}")
            return

        # Use the specified provider
        plugin = plugins[provider]
        results = plugin.resolve_conflicts(
            project_directory, task_id, resolution=resolution, **kwargs
        )

        # Display results
        _display_resolve_results(provider, results)
    else:
        # Use all available providers
        for plugin_name, plugin in plugins.items():
            console.print(f"[INFO] Resolving conflicts for {plugin_name}:")
            results = plugin.resolve_conflicts(
                project_directory, task_id, resolution=resolution, **kwargs
            )

            # Display results
            _display_resolve_results(plugin_name, results)


def _display_resolve_results(provider: str, results: Dict[str, Any]) -> None:
    """Display conflict resolution results.

    Args:
        provider: Sync provider name
        results: Resolution results
    """
    # Create a table for the results
    table = Table(
        title=f"{provider.capitalize()} Conflict Resolution",
        show_header=True,
        header_style="bold",
    )
    table.add_column("Metric", style="dim")
    table.add_column("Count")

    # Add rows for each metric
    table.add_row("Total Conflicts", str(results.get("total", 0)))
    table.add_row("Resolved", str(results.get("resolved", 0)))
    table.add_row("Failed", str(results.get("failed", 0)))

    console.print(table)

    # Show detailed information if available
    if "details" in results and results["details"]:
        console.print("\nResolution Details:", style="bold")

        # Create a table for detailed information
        detail_table = Table(show_header=True, header_style="bold")
        detail_table.add_column("Task ID", style="dim")
        detail_table.add_column("Title")
        detail_table.add_column("Resolution")
        detail_table.add_column("Status")

        # Add rows for each task
        for task_id, details in results["details"].items():
            detail_table.add_row(
                str(task_id),
                details.get("title", ""),
                details.get("resolution", ""),
                details.get("status", ""),
            )

        console.print(detail_table)
