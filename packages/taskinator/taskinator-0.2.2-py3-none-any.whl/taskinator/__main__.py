"""
Main entry point for the Taskinator CLI application.
"""

import os
import sys
import asyncio
from typing import Dict, List, Optional, Tuple

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from taskinator.cli.commands import (
    add_dependency_command,
    add_task_command,
    analyze_complexity_command,
    clear_subtasks_command,
    complexity_report_command,
    create_prd_command,
    expand_command,
    fix_dependencies_command,
    generate_command,
    help_command,
    init_command,
    list_command,
    next_command,
    parse_prd_command,
    pdd_convert_command,
    pdd_to_tasks_command,
    remove_dependency_command,
    set_status_command,
    show_command,
    update_command,
    validate_dependencies_command,
)
from taskinator.cli.commands.discuss_command import discuss_command
from taskinator.cli.commands.export_gherkin_command import export_gherkin_command
from taskinator.cli.commands.import_gherkin_command import import_gherkin_command
from taskinator.cli.commands.add_bdd_scenario_command import add_bdd_scenario_command
from taskinator.cli.commands.stack_command import stack_command
from taskinator.cli.commands.story_commands import (
    parse_story_command,
    story_point_systems_command,
    story_point_system_explain_command,
)

# Conditionally import Azure DevOps commands if available
try:
    from taskinator.plugins.integrations.azure.commands import (
        azure_devops_show_command,
        azure_devops_import_command,
        azure_devops_tree_command,
        AZURE_DEVOPS_AVAILABLE,
    )
except ImportError:
    AZURE_DEVOPS_AVAILABLE = False

# Conditionally import GitLab commands if available  
try:
    from taskinator.plugins.integrations.gitlab.commands import (
        gitlab_show_command,
        gitlab_import_command,
        gitlab_tree_command,
        GITLAB_AVAILABLE,
    )
except ImportError:
    GITLAB_AVAILABLE = False
from taskinator.cli.commands.sprint_commands import (
    sprint_create_command,
    sprint_list_command,
    sprint_show_command,
    sprint_start_command,
    sprint_complete_command,
    sprint_cancel_command,
    sprint_add_task_command,
    sprint_remove_task_command,
    sprint_set_points_command,
    sprint_update_progress_command,
    sprint_burndown_command,
)
from taskinator.plugins.sync.sync_command import (
    setup_command as setup_sync_command,
    status_command as sync_status_command,
    sync_command as sync_command_async,
    push_command as sync_push_command,
    pull_command as sync_pull_command,
    resolve_command,
)
from taskinator.utils.config import load_config
from taskinator.utils.ui import display_banner

# Create Typer app
app = typer.Typer(
    help="Taskinator - A Python CLI task management tool for software development projects",
    add_completion=True,
    no_args_is_help=False,  # We'll handle this ourselves
)

# Create Sprint subcommand group
sprint_app = typer.Typer(help="Sprint management commands")
app.add_typer(sprint_app, name="sprint")

console = Console()

# Load configuration
config = load_config()


@app.callback(invoke_without_command=True)
def callback(ctx: typer.Context):
    """
    Taskinator - A Python CLI task management tool for software development projects.
    """
    # If no command is provided, show help
    if ctx.invoked_subcommand is None:
        help_command()
        raise typer.Exit()


@app.command("list")
def list_tasks(
    status: Optional[str] = typer.Option(
        None, "--status", help="Filter tasks by status (done, pending, etc.)"
    ),
    with_subtasks: bool = typer.Option(
        False, "--with-subtasks", help="Include subtasks in the listing"
    ),
    priority: Optional[str] = typer.Option(
        None, "--priority", help="Filter tasks by priority (high, medium, low)"
    ),
    with_hierarchy: bool = typer.Option(
        False, "--with-hierarchy", help="Display document hierarchy relationships"
    ),
):
    """List all tasks with their status."""
    display_banner()
    list_command(status, with_subtasks, priority, with_hierarchy)


@app.command("next")
def next_task():
    """Show the next task to work on based on dependencies and priority."""
    display_banner()
    next_command()


@app.command("show")
def show_task(task_id: str = typer.Argument(..., help="Task ID to show")):
    """Display detailed information about a specific task."""
    display_banner()
    show_command(task_id)


@app.command("set-status")
def set_status(
    id: str = typer.Option(..., help="Task ID to update"),
    status: str = typer.Option(
        ...,
        help="New status (done, pending, in-progress, blocked, deferred, cancelled)",
    ),
):
    """Update task status (done, pending, etc.)."""
    display_banner()
    set_status_command(id, status)


@app.command("parse-prd")
def parse_prd(
    prd_file: str = typer.Argument(..., help="Path to the PRD document"),
    tasks: int = typer.Option(10, help="Number of tasks to generate"),
):
    """Generate tasks from a PRD document."""
    display_banner()
    parse_prd_command(prd_file, tasks)


@app.command("create-prd")
def create_prd(
    name: Optional[str] = typer.Option(None, help="Project or feature name (used for filename generation)"),
    template: str = typer.Option("standard", help="PRD template to use (standard, minimal, feature)"),
    output: Optional[str] = typer.Option(None, help="Custom output path (defaults to docs/[name]-prd.md)"),
    update: Optional[str] = typer.Option(None, help="Path to an existing PRD to update instead of creating new"),
):
    """Create a PRD document through guided interactive process."""
    display_banner()
    create_prd_command(name, template, output, update)


@app.command("generate")
def generate():
    """Create individual task files from tasks.json."""
    display_banner()
    generate_command()


@app.command("reintegrate")
def reintegrate():
    """Reintegrate task files back into tasks.json."""
    display_banner()
    reintegrate_command()


@app.command("update")
def update(
    from_id: str = typer.Option(..., "--from", help="Task ID to start updating from"),
    prompt: str = typer.Option(..., help="Context for updating tasks"),
):
    """Update tasks based on new requirements."""
    display_banner()
    update_command(from_id, prompt)


@app.command("add-task")
def add_task(
    prompt: str = typer.Option(..., help="Text description for the new task"),
    dependencies: Optional[str] = typer.Option(
        None, help="Comma-separated list of task IDs this task depends on"
    ),
    priority: str = typer.Option("medium", help="Task priority (high, medium, low)"),
):
    """Add a new task using AI."""
    display_banner()
    add_task_command(prompt, dependencies, priority)


@app.command("add-dependency")
def add_dependency(
    id: str = typer.Option(..., help="Task ID to add dependency to"),
    depends_on: str = typer.Option(..., help="Task ID that this task depends on"),
):
    """Add a dependency to a task."""
    display_banner()
    add_dependency_command(id, depends_on)


@app.command("remove-dependency")
def remove_dependency(
    id: str = typer.Option(..., help="Task ID to remove dependency from"),
    depends_on: str = typer.Option(..., help="Task ID to remove from dependencies"),
):
    """Remove a dependency from a task."""
    display_banner()
    remove_dependency_command(id, depends_on)


@app.command("analyze-complexity")
def analyze_complexity(
    research: bool = typer.Option(False, help="Use research for better analysis"),
    threshold: int = typer.Option(5, help="Complexity threshold for expansion"),
):
    """Analyze tasks and generate expansion recommendations."""
    display_banner()

    # Import asyncio to handle the async function
    import asyncio

    # Run the async function in an event loop
    try:
        # Get or create an event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # If no event loop exists in this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Run the async function
        loop.run_until_complete(analyze_complexity_command(research, threshold))
    except Exception as e:
        console.print(
            f"[ERROR] Error running analyze-complexity command: {str(e)}",
            style="bold red",
        )


@app.command("complexity-report")
def complexity_report(
    file: Optional[str] = typer.Option(None, help="Path to complexity report file"),
):
    """Display the complexity analysis report."""
    display_banner()
    complexity_report_command(file)


@app.command("expand-task")
def expand_task(
    id: Optional[str] = typer.Option(None, help="Task ID to expand"),
    num: int = typer.Option(
        None, help="Number of subtasks to generate (default from config)"
    ),
    research: bool = typer.Option(False, help="Use research for better expansion"),
    all: bool = typer.Option(False, help="Expand all pending tasks"),
    force: bool = typer.Option(False, help="Force expansion even if already expanded"),
):
    """Break down tasks into detailed subtasks."""
    display_banner()
    expand_command(id, num, research, all, force)
    
# Add an alias for expand-task as expand for backwards compatibility
@app.command("expand")
def expand_alias(
    id: Optional[str] = typer.Option(None, help="Task ID to expand"),
    num: int = typer.Option(
        None, help="Number of subtasks to generate (default from config)"
    ),
    research: bool = typer.Option(False, help="Use research for better expansion"),
    all: bool = typer.Option(False, help="Expand all pending tasks"),
    force: bool = typer.Option(False, help="Force expansion even if already expanded"),
):
    """Break down tasks into detailed subtasks (alias for expand-task)."""
    display_banner()
    expand_command(id, num, research, all, force)


@app.command("expand-all")
def expand_all(
    num: int = typer.Option(
        None, help="Number of subtasks to generate (default from config)"
    ),
    research: bool = typer.Option(False, help="Use research for better expansion"),
    force: bool = typer.Option(False, help="Force expansion even if already expanded"),
):
    """Break down all pending tasks into detailed subtasks."""
    display_banner()
    expand_command(None, num, research, True, force)


@app.command("validate-dependencies")
def validate_dependencies():
    """Identify invalid dependencies without fixing them."""
    display_banner()
    validate_dependencies_command()


@app.command("fix-dependencies")
def fix_dependencies():
    """Fix invalid dependencies automatically."""
    display_banner()
    fix_dependencies_command()


@app.command("export-csv")
def export_csv(
    output: str = typer.Option("tasks/export.csv", help="Path to the output CSV file"),
):
    """Export tasks to a CSV file."""
    display_banner()
    export_csv(output)


@app.command("export-markdown")
def export_markdown(
    output: str = typer.Option(
        "tasks/tasks.md", help="Path to the output Markdown file"
    ),
):
    """Export tasks to a Markdown file."""
    display_banner()
    export_markdown(output)


@app.command("export-gherkin")
def export_gherkin(
    output_dir: Optional[str] = typer.Option(
        None, 
        "--output", "-o", 
        help="Output directory for feature files (defaults to ./features)"
    ),
    project_name: Optional[str] = typer.Option(
        None,
        "--project", "-p",
        help="Project name for the feature file (defaults to 'Project')"
    ),
    individual: bool = typer.Option(
        True,
        "--individual/--combined", "-i",
        help="Export each task to its own feature file (default: True)"
    ),
    tasks_path: Optional[str] = typer.Option(
        None,
        "--tasks-file", "-f",
        help="Path to tasks.json file (defaults to ./tasks/tasks.json)"
    )
):
    """Export tasks to Gherkin feature files for BDD testing."""
    display_banner()
    export_gherkin_command(output_dir, project_name, individual, tasks_path)


@app.command("import-gherkin")
def import_gherkin(
    features_dir: Optional[str] = typer.Option(
        None,
        "--features", "-f",
        help="Directory containing .feature files (defaults to ./features or ./tasks/features)"
    ),
    tasks_path: Optional[str] = typer.Option(
        None,
        "--tasks-file", "-t",
        help="Path to tasks.json file (defaults to ./tasks/tasks.json)"
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run", "-n",
        help="Show what would be changed without making actual modifications"
    )
):
    """Import/sync Gherkin feature files back to Taskinator tasks."""
    display_banner()
    import_gherkin_command(features_dir, tasks_path, dry_run)


@app.command("init")
def init(
    name: Optional[str] = typer.Option(None, "--name", help="Project name"),
    compat: bool = typer.Option(False, "--compat", help="Initialize in compatibility mode for Task Master"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Automatically answer yes to all prompts"),
):
    """Initialize a new project with a basic task structure."""
    display_banner()
    init_command(name, compat=compat, yes=yes)


@app.command("help")
def help():
    """Display help information."""
    help_command()


@app.command("clear-subtasks")
def clear_subtasks(id: str = typer.Option(..., help="Task ID to clear subtasks from")):
    """Remove subtasks from specified tasks."""
    display_banner()
    clear_subtasks_command(id)


# Create a sync command group
sync_app = typer.Typer(help="Sync commands", invoke_without_command=True)
app.add_typer(sync_app, name="sync")

# Create a stack command group
stack_app = typer.Typer(help="Technology stack management commands")
app.add_typer(stack_app, name="stack")

# Create a story command group
story_app = typer.Typer(help="User story and feature management commands")
app.add_typer(story_app, name="story")

# Create an Azure DevOps command group
azdo_app = typer.Typer(help="Azure DevOps integration commands")
app.add_typer(azdo_app, name="azdo")

# Create a GitLab command group
gitlab_app = typer.Typer(help="GitLab integration commands")
app.add_typer(gitlab_app, name="gitlab")


@sync_app.callback()
def sync_callback(
    ctx: typer.Context,
    direction: str = typer.Option(
        "bidirectional", help="Sync direction (push, pull, or bidirectional)"
    ),
    provider: Optional[str] = typer.Option(None, help="Sync provider"),
) -> None:
    """Synchronize tasks with remote providers."""
    # Only run the sync command if no subcommand is specified
    if ctx.invoked_subcommand is None:
        display_banner()
        asyncio.run(sync_command_async(os.getcwd(), provider, direction))


@sync_app.command("resolve")
def sync_resolve_command(
    resolution: str = typer.Option(
        "local", help="Resolution strategy (local, remote, or interactive)"
    ),
    task_id: Optional[str] = typer.Option(None, help="Task ID to resolve conflicts for"),
    provider: Optional[str] = typer.Option(None, help="Sync provider"),
) -> None:
    """Resolve sync conflicts."""
    display_banner()
    asyncio.run(resolve_command(os.getcwd(), provider, task_id, resolution))


@sync_app.command("setup")
def sync_setup(
    provider: str = typer.Argument(..., help="Sync provider to set up"),
    non_interactive: bool = typer.Option(False, "--non-interactive", help="Run in non-interactive mode using environment variables"),
):
    """Set up sync provider."""
    display_banner()
    asyncio.run(setup_sync_command(os.getcwd(), provider, non_interactive=non_interactive))


@sync_app.command("status")
def sync_status(
    provider: Optional[str] = typer.Option(
        None, help="Sync provider to show status for"
    ),
    verbose: bool = typer.Option(False, help="Show verbose output"),
):
    """Show sync status."""
    display_banner()
    asyncio.run(sync_status_command(os.getcwd(), provider, verbose=verbose))


@sync_app.command("push")
def sync_push(
    provider: Optional[str] = typer.Option(None, help="Sync provider to push to"),
):
    """Push tasks to remote provider."""
    display_banner()
    asyncio.run(sync_push_command(os.getcwd(), provider))


@sync_app.command("pull")
def sync_pull(
    provider: Optional[str] = typer.Option(None, help="Sync provider to pull from"),
):
    """Pull tasks from remote provider."""
    display_banner()
    asyncio.run(sync_pull_command(os.getcwd(), provider))


# Sprint commands
@sprint_app.command("create")
def sprint_create(
    name: str = typer.Argument(..., help="Sprint name"),
    goal: Optional[str] = typer.Option(None, help="Sprint goal"),
    start_date: Optional[str] = typer.Option(None, help="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = typer.Option(None, help="End date (YYYY-MM-DD)"),
    capacity: Optional[float] = typer.Option(None, help="Team capacity in story points"),
):
    """Create a new sprint."""
    display_banner()
    sprint_create_command(name, goal, start_date, end_date, capacity)


@sprint_app.command("list")
def sprint_list(
    status: Optional[str] = typer.Option(
        None, help="Filter sprints by status (planned, active, completed, cancelled)"
    ),
):
    """List all sprints."""
    display_banner()
    sprint_list_command(status)


@sprint_app.command("show")
def sprint_show(
    sprint_id: str = typer.Argument(..., help="Sprint ID to show"),
):
    """Show sprint details including tasks."""
    display_banner()
    sprint_show_command(sprint_id)


@sprint_app.command("start")
def sprint_start(
    sprint_id: str = typer.Argument(..., help="Sprint ID to start"),
    start_date: Optional[str] = typer.Option(None, help="Start date (YYYY-MM-DD)"),
):
    """Start a sprint."""
    display_banner()
    sprint_start_command(sprint_id, start_date)


@sprint_app.command("complete")
def sprint_complete(
    sprint_id: str = typer.Argument(..., help="Sprint ID to complete"),
    notes: Optional[str] = typer.Option(None, help="Retrospective notes"),
):
    """Complete a sprint."""
    display_banner()
    sprint_complete_command(sprint_id, notes)


@sprint_app.command("cancel")
def sprint_cancel(
    sprint_id: str = typer.Argument(..., help="Sprint ID to cancel"),
):
    """Cancel a sprint."""
    display_banner()
    sprint_cancel_command(sprint_id)


@sprint_app.command("add-task")
def sprint_add_task(
    sprint_id: str = typer.Argument(..., help="Sprint ID"),
    task_id: str = typer.Argument(..., help="Task ID to add to the sprint"),
    points: Optional[float] = typer.Option(None, help="Story points estimation"),
):
    """Add a task to a sprint."""
    display_banner()
    sprint_add_task_command(sprint_id, task_id, points)


@sprint_app.command("remove-task")
def sprint_remove_task(
    task_id: str = typer.Argument(..., help="Task ID to remove from the sprint"),
):
    """Remove a task from its sprint."""
    display_banner()
    sprint_remove_task_command(task_id)


@sprint_app.command("set-points")
def sprint_set_points(
    task_id: str = typer.Argument(..., help="Task ID to update"),
    points: float = typer.Argument(..., help="Story points estimation"),
):
    """Set story points for a task."""
    display_banner()
    sprint_set_points_command(task_id, points)


@sprint_app.command("update-progress")
def sprint_update_progress(
    sprint_id: str = typer.Argument(..., help="Sprint ID to update"),
    date: Optional[str] = typer.Option(None, help="Date for the entry (YYYY-MM-DD)"),
):
    """Record daily progress for a sprint."""
    display_banner()
    sprint_update_progress_command(sprint_id, date)


@sprint_app.command("burndown")
def sprint_burndown(
    sprint_id: str = typer.Argument(..., help="Sprint ID to show burndown for"),
    output: Optional[str] = typer.Option(None, help="Output file path for burndown chart"),
    format: str = typer.Option("text", help="Output format (text, json)"),
):
    """Generate burndown chart for a sprint."""
    display_banner()
    sprint_burndown_command(sprint_id, output, format)


@app.command("pdd")
def pdd():
    """Process Design Document (PDD) commands."""
    display_banner()
    console.print("Use one of the PDD subcommands: convert, to-tasks")


@app.command("pdd:convert")
def pdd_convert(
    input_file: str = typer.Argument(..., help="Path to the PDD file"),
    output_file: Optional[str] = typer.Option(
        None, "--output", "-o", help="Path to the output SOP file"
    ),
    format: str = typer.Option(
        "markdown", "--format", "-f", help="Output format (markdown, json, yaml)"
    ),
    output_dir: Optional[str] = typer.Option(
        None, "--dir", "-d", help="Directory to output SOP files"
    ),
):
    """Convert a PDD to SOP documents."""
    display_banner()
    pdd_convert_command(input_file, output_file, format, output_dir)


@app.command("pdd:to-tasks")
def pdd_to_tasks(
    input_file: str = typer.Argument(..., help="Path to the PDD file"),
    tasks_file: Optional[str] = typer.Option(
        None, "--tasks", "-t", help="Path to the tasks.json file"
    ),
    num_tasks: int = typer.Option(5, "--num", "-n", help="Number of tasks to generate"),
    priority: str = typer.Option(
        "medium", "--priority", "-p", help="Priority for the generated tasks"
    ),
):
    """Convert a PDD to tasks."""
    display_banner()
    pdd_to_tasks_command(input_file, tasks_file, num_tasks, priority)


@app.command("discuss")
def discuss(
    task_id: Optional[str] = typer.Argument(None, help="Optional task ID to discuss (e.g., '1' or '1.1')"),
    comment: Optional[str] = typer.Option(None, "--comment", help="Non-interactive comment for direct processing"),
):
    """Interactive discussion interface for task modifications."""
    display_banner()
    discuss_command(task_id, comment)


@app.command("add-bdd-scenario")
def add_bdd_scenario(
    task_id: str = typer.Argument(..., help="Task ID to add BDD scenario to"),
    scenario_title: Optional[str] = typer.Option(
        None,
        "--title", "-t",
        help="Title for the BDD scenario"
    ),
    interactive: bool = typer.Option(
        True,
        "--interactive/--non-interactive",
        help="Use interactive mode to create the scenario"
    ),
    tasks_path: Optional[str] = typer.Option(
        None,
        "--tasks-file", "-f",
        help="Path to tasks.json file (defaults to ./tasks/tasks.json)"
    )
):
    """Add a BDD scenario to a specific task."""
    display_banner()
    add_bdd_scenario_command(task_id, scenario_title, interactive, tasks_path)


@stack_app.command("suggest")
def stack_suggest(
    prd_file: Optional[str] = typer.Option(None, "--prd", help="PRD file to analyze for stack suggestions"),
    interactive: bool = typer.Option(True, "--interactive/--non-interactive", help="Run in interactive mode"),
):
    """Generate basic technology stack suggestions based on project requirements."""
    display_banner()
    stack_command("suggest", os.getcwd(), interactive, prd_file)


@stack_app.command("recommend")
def stack_recommend(
    prd_file: Optional[str] = typer.Option(None, "--prd", help="PRD file to analyze for stack recommendations"),
    research: bool = typer.Option(False, "--research", help="Use Perplexity for enhanced research (requires PERPLEXITY_API_KEY)"),
    interactive: bool = typer.Option(True, "--interactive/--non-interactive", help="Run in interactive mode"),
):
    """Generate enhanced technology stack recommendations with optional research."""
    display_banner()
    stack_command("recommend", os.getcwd(), interactive, prd_file, research)


@stack_app.command("discuss")
def stack_discuss():
    """Interactive discussion about technology stack choices."""
    display_banner()
    stack_command("discuss", os.getcwd(), True)


@stack_app.command("compile")
def stack_compile(
    interactive: bool = typer.Option(True, "--interactive/--non-interactive", help="Run in interactive mode"),
):
    """Compile stack.suggest into a definitive stack.lock file."""
    display_banner()
    stack_command("compile", os.getcwd(), interactive)


@stack_app.command("lock")
def stack_lock(
    interactive: bool = typer.Option(True, "--interactive/--non-interactive", help="Run in interactive mode"),
):
    """Alias for compile - create stack.lock from suggestions."""
    display_banner()
    stack_command("lock", os.getcwd(), interactive)


@stack_app.command("show")
def stack_show():
    """Show current technology stack status."""
    display_banner()
    stack_command("show", os.getcwd(), False)


@stack_app.command("status")
def stack_status():
    """Alias for show - display stack status."""
    display_banner()
    stack_command("show", os.getcwd(), False)


# Add Azure DevOps commands if available
if 'AZURE_DEVOPS_AVAILABLE' in locals() and AZURE_DEVOPS_AVAILABLE:
    @azdo_app.command("show")
    def azdo_show(
        work_item_id: int = typer.Argument(..., help="Azure DevOps Work Item ID"),
        parents: bool = typer.Option(False, "--parents", help="Show parent items"),
    ):
        """Show information about an Azure DevOps work item."""
        display_banner()
        azure_devops_show_command(work_item_id, parents)

    @azdo_app.command("import")
    def azdo_import(
        work_item_id: int = typer.Argument(..., help="Azure DevOps Work Item ID"),
        include_parents: bool = typer.Option(False, "--include-parents", help="Include parent items"),
        output: Optional[str] = typer.Option(None, "--output", help="Output path for tasks"),
    ):
        """Import an Azure DevOps work item as Taskinator tasks."""
        display_banner()
        azure_devops_import_command(work_item_id, include_parents, output)

    @azdo_app.command("tree")
    def azdo_tree(
        work_item_id: int = typer.Argument(..., help="Azure DevOps Work Item ID"),
        levels_up: Optional[int] = typer.Option(None, "--up", help="Levels to traverse up"),
        levels_down: Optional[int] = typer.Option(None, "--down", help="Levels to traverse down"),
    ):
        """Show the hierarchy tree of an Azure DevOps work item."""
        display_banner()
        azure_devops_tree_command(work_item_id, levels_up, levels_down)


# Add GitLab commands if available
if 'GITLAB_AVAILABLE' in locals() and GITLAB_AVAILABLE:
    @gitlab_app.command("show")
    def gitlab_show(
        issue_iid: int = typer.Argument(..., help="GitLab Issue Internal ID"),
        parents: bool = typer.Option(False, "--parents", help="Show parent issues"),
    ):
        """Show information about a GitLab issue."""
        display_banner()
        gitlab_show_command(issue_iid, parents)

    @gitlab_app.command("import")
    def gitlab_import(
        issue_iid: int = typer.Argument(..., help="GitLab Issue Internal ID"),
        include_parents: bool = typer.Option(False, "--include-parents", help="Include parent issues"),
        output: Optional[str] = typer.Option(None, "--output", help="Output path for tasks"),
    ):
        """Import a GitLab issue as Taskinator tasks."""
        display_banner()
        gitlab_import_command(issue_iid, include_parents, output)

    @gitlab_app.command("tree")
    def gitlab_tree(
        issue_iid: int = typer.Argument(..., help="GitLab Issue Internal ID"),
        levels_up: Optional[int] = typer.Option(None, "--up", help="Levels to traverse up"),
        levels_down: Optional[int] = typer.Option(None, "--down", help="Levels to traverse down"),
    ):
        """Show the hierarchy tree of a GitLab issue."""
        display_banner()
        gitlab_tree_command(issue_iid, levels_up, levels_down)


@app.command("parse-story")
def parse_story(
    file_path: str = typer.Argument(..., help="Path to the story/feature file"),
    point_system: Optional[str] = typer.Option(
        None, "--point-system", help="Story point system to use (fibonacci, powers_of_two, linear, tshirt, modified_fibonacci)"
    ),
    ai_assist: bool = typer.Option(
        True, "--ai-assist/--no-ai-assist", help="Use AI to enhance task generation"
    ),
    analyze_codebase: bool = typer.Option(
        False, "--analyze-codebase", help="Analyze codebase for context"
    ),
    task_prefix: Optional[str] = typer.Option(
        None, "--prefix", help="Prefix for generated task IDs"
    ),
    output: Optional[str] = typer.Option(
        None, "--output", help="Path to write tasks to (defaults to tasks.json)"
    ),
):
    """Parse a user story or feature file and generate tasks."""
    display_banner()
    parse_story_command(file_path, point_system, ai_assist, analyze_codebase, task_prefix, output)


@story_app.command("point-systems")
def story_point_systems():
    """Display available story point systems."""
    display_banner()
    story_point_systems_command()


@story_app.command("explain-points")
def story_explain_points(
    point_value: str = typer.Argument(..., help="Story point value to explain"),
    system: str = typer.Option(
        "fibonacci", "--system", help="Story point system to use (fibonacci, powers_of_two, linear, tshirt, modified_fibonacci)"
    ),
):
    """Explain how a story point value affects task generation."""
    display_banner()
    story_point_system_explain_command(point_value, system)


if __name__ == "__main__":
    app()
