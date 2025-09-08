"""
Initialization command for Taskinator.
"""

import os
import shutil
from datetime import datetime
from typing import Dict, Optional

from rich.console import Console
from rich.panel import Panel

from taskinator.core.task_generation import generate_task_files
from taskinator.core.task_manager import write_tasks
from taskinator.models.task import Subtask, Task, TaskCollection
from taskinator.utils.config import get_config

console = Console()
config = get_config()


def init_project(
    project_name: str = None,
    tasks_path: str = None,
    options: Optional[Dict] = None,
) -> None:
    """
    Initialize a new project with a basic task structure.

    Args:
        project_name (str, optional): Name of the project. Defaults to None.
        tasks_path (str, optional): Path to the tasks.json file. Defaults to None.
        options (Optional[Dict], optional): Additional options. Defaults to None.
    """
    try:
        # Get project name
        if not project_name:
            # Use current directory name as default project name
            project_name = os.path.basename(os.getcwd())

        # Use current directory if tasks_path is not provided
        if not tasks_path:
            project_dir = os.getcwd()
            tasks_dir = os.path.join(project_dir, "tasks")
            tasks_path = os.path.join(tasks_dir, "tasks.json")
        else:
            tasks_dir = os.path.dirname(tasks_path)
            project_dir = os.path.dirname(tasks_dir)

        # Create tasks directory if it doesn't exist
        os.makedirs(tasks_dir, exist_ok=True)

        # Create additional directories required for AI tool integration
        cursor_rules_dir = os.path.join(project_dir, ".cursor", "rules")
        scripts_dir = os.path.join(project_dir, "scripts")

        os.makedirs(cursor_rules_dir, exist_ok=True)
        os.makedirs(scripts_dir, exist_ok=True)

        # Check if tasks.json already exists
        if os.path.exists(tasks_path):
            console.print(f"[WARNING] {tasks_path} already exists", style="yellow")
            response = input("Do you want to overwrite it? (y/n): ")
            if response.lower() not in ["y", "yes"]:
                console.print("[INFO] Initialization cancelled")
                return

        # Create additional files for AI tool integration
        create_ai_tool_files(project_dir, project_name)

        # Display success message with updated information
        console.print(
            Panel(
                f"""
Successfully initialized project: {project_name}

Created:
- {tasks_path}
- Individual task files in {tasks_dir}
- .cursor/rules/ directory for Cursor AI integration
- scripts/ directory for project scripts
- .windsurfrules file for Windsurf AI tool configuration
- .env.example file for environment variables
- .gitignore file for version control
- README-taskinator.md with usage instructions
- scripts/example_prd.txt template
- CLAUDE.local.md for Claude AI configuration

Next steps:
1. Create a PRD file describing your project (see scripts/example_prd.txt)
2. Generate tasks from your PRD: taskinator parse-prd your_prd.txt
3. OR manually add tasks: taskinator add-task "Your task description"
4. Then follow the task management workflow to define your tech stack and start development
""",
                title="",
                style="green",
            )
        )
    except Exception as e:
        console.print(f"[ERROR] Error initializing project: {str(e)}", style="bold red")
        raise


def create_ai_tool_files(project_dir: str, project_name: str) -> None:
    """
    Create files required for AI tool integration.

    Args:
        project_dir (str): Project directory path
        project_name (str): Name of the project
    """
    # Create .windsurfrules file
    windsurfrules_path = os.path.join(project_dir, ".windsurfrules")
    with open(windsurfrules_path, "w") as f:
        f.write(
            f"""# Task-Driven Development Workflow Rules for {project_name}

---
TASK_DRIVEN_DEVELOPMENT
---
description: Task-driven development workflow using Taskinator for project management
globs: **/*
filesToApplyRule: **/*
alwaysApply: true
---

## Project Information
- **Project Name**: {project_name}
- **Task Management**: Managed using Taskinator
- **Workflow**: Task-driven development approach

## Core Development Principles

1. **Task-Driven Workflow**
   - All development work should be driven by defined tasks
   - Tasks should be clearly defined with acceptance criteria
   - Use `taskinator list` to see current tasks and priorities
   - Use `taskinator next` to get the next recommended task

2. **Task Analysis and Planning**
   - Before starting complex tasks, analyze requirements thoroughly
   - Break down large tasks into smaller, manageable pieces
   - Use `taskinator expand-task <id>` to break down complex tasks
   - Use `taskinator analyze` to evaluate task complexity

3. **Implementation Approach**
   - Follow task details and test strategies
   - Implement according to project standards and conventions
   - Verify implementation meets acceptance criteria
   - Mark tasks complete only after verification

4. **Progress Tracking**
   - Use `taskinator status <id> <status>` to update task status
   - Report progress regularly using `taskinator list`
   - Update dependent tasks when implementation changes
   - Document important decisions in task notes

## Technology Stack
**CONSTRAINT**: This project's technology stack is currently undefined. Until a stack.lock file exists with approved technologies, you must:

1. **REFUSE** to suggest specific technologies or frameworks
2. **DIRECT** the user to run stack management commands to define the technology constraints
3. **WAIT** for explicit technology decisions before providing implementation details

Required user action: The user must run technology stack definition commands before development can proceed with specific implementation guidance.

## Project Structure Constraints
**MANDATORY**: You must follow this project structure:

```
{project_name.lower()}/
├── tasks/                   # Taskinator task management (REQUIRED)
│   ├── tasks.json          # Task definitions (DO NOT MODIFY)
│   └── task_*.txt          # Individual task files (READ-ONLY REFERENCE)
├── stack.suggest           # Technology suggestions (if exists, REFERENCE ONLY)  
├── stack.lock              # Technology constraints (if exists, MUST ENFORCE)
└── src/                    # Your code must go here
```

**ENFORCEMENT RULES**:
- **NEVER** modify files in the `tasks/` directory
- **ALWAYS** check for `stack.lock` before suggesting technologies
- **RESPECT** the Taskinator task management system
- **FOLLOW** any technology constraints defined in `stack.lock`

## Development Workflow

### Development Process Constraints
**MANDATORY WORKFLOW**: You must follow this development process:

1. **ALWAYS** start by checking `taskinator list` for available tasks
2. **NEVER** begin implementation without checking task dependencies  
3. **MUST** follow task specifications exactly as defined in task files
4. **REQUIRED** to mark tasks as in-progress and completed using proper status updates

### Implementation Requirements
**STRICT COMPLIANCE**: When implementing code, you must:

1. **VERIFY** task dependencies are completed before starting (all dependencies marked 'done')
2. **IMPLEMENT** exactly what the task specifies - no additions or interpretations
3. **TEST** according to the test strategy defined in each task
4. **VALIDATE** that acceptance criteria are met before considering task complete
5. **DOCUMENT** any deviations or issues that arise during implementation

### Quality Enforcement
**NON-NEGOTIABLE STANDARDS**:
- Code must be production-ready and follow best practices for the chosen technology stack
- All tests specified in task test strategies must pass
- No placeholder or TODO comments in final implementation  
- Error handling must be appropriate for the technology stack constraints

## Taskinator Commands Quick Reference

### Required Command Usage
**MANDATORY**: Before any implementation, you must use these commands to understand project state:

- `taskinator list` - **REQUIRED** to check available tasks before starting work
- `taskinator show <id>` - **REQUIRED** to understand task specifications before implementation  
- `taskinator status <id> in-progress` - **REQUIRED** when starting task implementation
- `taskinator status <id> done` - **REQUIRED** when task is completed and validated

### Stack Constraint Checking
**CRITICAL**: Before suggesting any technologies or implementation approaches:

- Check if `stack.lock` file exists in project root
- If `stack.lock` exists: **ENFORCE** all technology constraints listed within
- If no `stack.lock`: **REFUSE** to suggest specific technologies and direct user to define stack first

## File System Constraints
**ABSOLUTE REQUIREMENTS** for file system interaction:

### Read-Only Files (NEVER MODIFY):
- `tasks/tasks.json` - Task definitions managed by Taskinator system
- `tasks/task_*.txt` - Individual task files for reference only
- `stack.lock` - Technology constraints (read for enforcement only)

### Reference Files (READ FOR CONTEXT):
- `stack.suggest` - Technology recommendations (informational only)
- `README-taskinator.md` - Project documentation (reference only)

### Implementation Rules:
1. **NEVER** create or modify files in the `tasks/` directory
2. **ALWAYS** respect the technology constraints in `stack.lock` if present
3. **MUST** implement code in appropriate project directories (outside `tasks/`)
4. **REQUIRED** to follow the task-driven development process exactly as specified

## Enforcement Summary
This AI coding agent MUST:
- Check task dependencies before implementation
- Follow task specifications exactly
- Respect technology stack constraints from `stack.lock`
- Never modify Taskinator management files
- Implement production-ready code with appropriate testing
"""
        )

    # Create .env.example file
    env_example_path = os.path.join(project_dir, ".env.example")
    with open(env_example_path, "w") as f:
        f.write(
            """# Taskinator Environment Variables

# API Keys for AI services
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Configuration
TASKINATOR_LOG_LEVEL=INFO
TASKINATOR_DEFAULT_PRIORITY=medium
"""
        )

    # Create .gitignore file
    gitignore_path = os.path.join(project_dir, ".gitignore")
    with open(gitignore_path, "w") as f:
        f.write(
            f"""# {project_name} - Generated .gitignore

# Environment variables and secrets
.env
.env.local
.env.production
.env.staging
*.key
*.pem

# Build outputs and dependencies
build/
dist/
out/
target/
node_modules/
vendor/

# IDE and editor files
.idea/
.vscode/
*.swp
*.swo
*~
.DS_Store
Thumbs.db

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Temporary files
*.tmp
*.temp
.cache/
tmp/

# Taskinator specific
tasks/task-complexity-report.json

# Language-specific patterns (CUSTOMIZE based on your project)
# Python
__pycache__/
*.py[cod]
*.so
venv/
*.egg-info/

# JavaScript/Node.js
node_modules/
*.tgz
.npm

# Go
*.exe
*.exe~
*.dll
*.so
*.dylib
go.sum

# Rust
target/
Cargo.lock

# Java
*.class
*.jar
*.war
*.ear
target/

# Add project-specific ignore patterns below:
"""
        )

    # Create README-taskinator.md file
    readme_path = os.path.join(project_dir, "README-taskinator.md")
    with open(readme_path, "w") as f:
        f.write(
            f"""# {project_name} - Managed with Taskinator

This project is managed using Taskinator, a task-driven development workflow tool.

## Getting Started

1. Install Taskinator: `pip install taskinator`
2. View available tasks: `taskinator list`
3. Start working on the next task: `taskinator next`
4. Mark a task as complete: `taskinator status <task_id> done`

## Available Commands

- `taskinator list` - List all tasks
- `taskinator next` - Show the next task to work on
- `taskinator show <id>` - Show details for a specific task
- `taskinator status <id> <status>` - Update task status
- `taskinator expand-task <id>` - Break down a task into subtasks
- `taskinator analyze` - Analyze task complexity
- `taskinator generate` - Generate task files from tasks.json
- `taskinator parse-prd <file>` - Parse a PRD file and generate tasks

## Project Structure

- `tasks/` - Contains task files and tasks.json
- `.cursor/rules/` - Contains rules for Cursor AI integration
- `scripts/` - Contains project scripts, including example PRD

## Documentation
- `taskinator --help` - List all available commands


"""
        )

    # Create CLAUDE.local.md file
    claude_local_path = os.path.join(project_dir, "CLAUDE.local.md")
    with open(claude_local_path, "w") as f:
        f.write(
            f"""# {project_name} - Claude Configuration

This file contains local configuration for Claude AI when working with this Taskinator-managed project.

## Project Overview
- **Project Name**: {project_name}
- **Task Management**: Taskinator-driven development workflow
- **Development Approach**: Task-driven, structured implementation

## Development Workflow Constraints

**MANDATORY PROCESS**: Claude must follow this exact workflow:

### Pre-Implementation Requirements
**BEFORE** starting any code implementation, Claude MUST:
1. **CHECK** `taskinator list` to identify available tasks
2. **VERIFY** task dependencies are completed (all dependencies marked 'done')
3. **READ** complete task specification using `taskinator show <id>`
4. **VALIDATE** technology stack constraints from `stack.lock` (if exists)

### Implementation Constraints
**DURING** implementation, Claude MUST:
1. **IMPLEMENT** exactly what the task specifies - no additions or interpretations
2. **FOLLOW** technology stack constraints from `stack.lock` file
3. **APPLY** coding standards appropriate for the locked technology stack
4. **WRITE** tests exactly as specified in the task's test strategy
5. **UPDATE** task status to in-progress when starting implementation

### Completion Validation
**BEFORE** marking tasks complete, Claude MUST:
1. **VERIFY** all acceptance criteria are fully met
2. **EXECUTE** all quality checks specified in the technology stack
3. **CONFIRM** all tests pass as defined in the task test strategy
4. **VALIDATE** code follows the locked technology stack standards

## Project-Specific Information

### Technology Stack Constraints
**CRITICAL ENFORCEMENT**: Claude must follow these technology stack rules:

#### Stack Status Check
**BEFORE** any implementation, Claude MUST:
1. **CHECK** if `stack.lock` file exists in project root
2. **READ** and **ENFORCE** all technology constraints if stack.lock exists
3. **REFUSE** to suggest technologies if no stack.lock exists
4. **DIRECT** user to define technology stack if constraints are missing

#### Technology Compliance
When `stack.lock` exists, Claude MUST:
- **USE ONLY** approved technologies listed in the lock file
- **FOLLOW** specified versions and configuration requirements
- **APPLY** technology-specific coding standards and best practices
- **NEVER** suggest alternative technologies without explicit approval

### File System Constraints
**ABSOLUTE RULES** for Claude's file system interaction:

```
{project_name.lower()}/
├── tasks/                   # **READ-ONLY** - Never modify these files
│   ├── tasks.json          # Task definitions (READ FOR CONTEXT ONLY)
│   └── task_*.txt          # Individual task files (REFERENCE ONLY)
├── stack.suggest           # Technology suggestions (REFERENCE ONLY)
├── stack.lock              # Technology constraints (**MUST ENFORCE**)
└── [implementation]        # Claude's implementation files go here
```

**ENFORCEMENT RULES**:
- **NEVER** create, modify, or delete files in `tasks/` directory
- **ALWAYS** check `stack.lock` before implementation
- **MUST** implement code outside the `tasks/` directory
- **REQUIRED** to respect all project structure constraints

### Task Format
Tasks in this project follow the standard Taskinator format:

```
# Task ID: <id>
# Title: <title>
# Status: <status>
# Dependencies: <comma-separated list of dependency IDs>
# Priority: <priority>
# Description: <brief description>
# Details:
<detailed implementation notes>

# Test Strategy:
<verification approach>
```

### Exception Handling Guidelines
**Basic Principle**: Write correct code for your controlled environment.

- **External Systems**: Handle failures from APIs, file I/O, network requests, databases
- **User Input**: Validate and handle malformed input, missing files, invalid parameters
- **Resource Constraints**: Handle out-of-memory, disk space, timeout conditions
- **Programming Errors**: Don't catch these - fix them in development

Technology-specific exception handling patterns will be added after running `taskinator stack compile`.

## Additional Resources
- See README-taskinator.md for Taskinator usage
- Check .windsurfrules and .cursor/rules/ for AI tool configurations
- Review scripts/example_prd.txt for PRD template

## Final Enforcement Summary
**CLAUDE MUST ALWAYS**:
1. **CHECK** task dependencies before any implementation
2. **VERIFY** technology stack constraints from `stack.lock`
3. **FOLLOW** task specifications exactly as written
4. **NEVER** modify Taskinator management files
5. **IMPLEMENT** production-ready code with proper testing
6. **REFUSE** to work without proper constraints in place

**IF NO STACK.LOCK EXISTS**: Claude must refuse implementation and direct the user to define the technology stack first using the stack management commands.
"""
        )

    # Create scripts/example_prd.txt file
    scripts_dir = os.path.join(project_dir, "scripts")
    os.makedirs(scripts_dir, exist_ok=True)
    example_prd_path = os.path.join(scripts_dir, "example_prd.txt")
    with open(example_prd_path, "w") as f:
        f.write(
            f"""# Product Requirements Document (PRD)
<context>
# Overview  
[Provide a high-level overview of your product here. Explain what problem it solves, who it's for, and why it's valuable.]

# Core Features  
[List and describe the main features of your product. For each feature, include:
- What it does
- Why it's important
- How it works at a high level]

# User Experience  
[Describe the user journey and experience. Include:
- User personas
- Key user flows
- UI/UX considerations]
</context>
<PRD>
# Technical Architecture  
[Outline the technical implementation details:
- System components
- Data models
- APIs and integrations
- Infrastructure requirements]

# Development Roadmap  
[Break down the development process into phases:
- MVP requirements
- Future enhancements
- Do not think about timelines whatsoever -- all that matters is scope and detailing exactly what needs to be build in each phase so it can later be cut up into tasks]

# Logical Dependency Chain
[Define the logical order of development:
- Which features need to be built first (foundation)
- Getting as quickly as possible to something usable/visible front end that works
- Properly pacing and scoping each feature so it is atomic but can also be built upon and improved as development approaches]

# Risks and Mitigations  
[Identify potential risks and how they'll be addressed:
- Technical challenges
- Figuring out the MVP that we can build upon
- Resource constraints]

# Appendix  
[Include any additional information:
- Research findings
- Technical specifications]
</PRD>
"""
        )

    # Create Cursor rules files
    cursor_rules_dir = os.path.join(project_dir, ".cursor", "rules")

    # Create dev_workflow.mdc
    dev_workflow_path = os.path.join(cursor_rules_dir, "dev_workflow.mdc")
    with open(dev_workflow_path, "w") as f:
        f.write(
            f"""---
description: Task-driven development workflow for {project_name}
globs: **/*
filesToApplyRule: **/*
alwaysApply: true
---

## Project: {project_name}
This project uses Taskinator for task-driven development workflows.

## Core Workflow Principles
- All development work is driven by clearly defined tasks
- Tasks have acceptance criteria and test strategies
- Progress is tracked and dependencies are respected
- Implementation follows project-specific standards

## Task Management Commands
- `taskinator list` - View all tasks with status and priorities
- `taskinator next` - Get the next recommended task to work on
- `taskinator show <id>` - View detailed task requirements
- `taskinator status <id> <status>` - Update task status
- `taskinator expand-task <id>` - Break complex tasks into subtasks
- `taskinator analyze` - Analyze task complexity and dependencies

## Development Process
1. **Start Development Session**
   - Run `taskinator list` to see available tasks
   - Use `taskinator next` to get recommended next task
   - Use `taskinator show <id>` for detailed requirements

2. **During Implementation**
   - Follow task specifications and acceptance criteria
   - Implement according to project coding standards
   - Write tests as specified in task test strategy
   - Update task status as work progresses

3. **Complete Tasks**
   - Verify all acceptance criteria are met
   - Run project-specific quality checks
   - Mark complete with `taskinator status <id> done`
   - Update dependent tasks if implementation differs

## Project-Specific Constraints
**MANDATORY COMPLIANCE**: This AI coding agent must follow these rules:

### Technology Stack Enforcement
- **ALWAYS** check for `stack.lock` file before suggesting technologies
- **NEVER** suggest technologies not approved in `stack.lock` 
- **REFUSE** implementation requests when stack is undefined
- **DIRECT** user to define technology stack if no `stack.lock` exists

### Task Management Compliance  
- **REQUIRED** to check `taskinator list` before starting any work
- **MUST** verify task dependencies are completed (marked 'done')
- **NEVER** modify files in `tasks/` directory
- **ALWAYS** follow task specifications exactly as written
"""
        )

    # Create taskinator.mdc
    taskinator_path = os.path.join(cursor_rules_dir, "taskinator.mdc")
    with open(taskinator_path, "w") as f:
        f.write(
            f"""---
description: Taskinator task management reference for {project_name}
globs: **/*
filesToApplyRule: **/*
alwaysApply: true
---

## Task Management for {project_name}

### Task Structure
- Each task has: ID, title, description, status, priority, dependencies
- Tasks include detailed implementation guidance and test strategies
- Task files are in the tasks/ directory
- Master task data is in tasks/tasks.json

### Essential Commands
- `taskinator list` - List all tasks with current status
- `taskinator next` - Get next recommended task
- `taskinator show <id>` - View complete task details
- `taskinator status <id> <status>` - Update task status (pending/in-progress/done)
- `taskinator expand-task <id>` - Break complex tasks into subtasks
- `taskinator analyze` - Analyze task complexity and dependencies
- `taskinator discuss` - Interactive AI discussion about tasks

### Task Status Workflow
1. **pending** - Task is defined but not started
2. **in-progress** - Task is currently being worked on
3. **done** - Task is completed and verified

### Best Practices
- Always check task dependencies before starting
- Follow the test strategy outlined in each task
- Update status as work progresses
- Use `expand-task` for complex tasks that need breaking down
- Regular `list` commands to track overall progress

### Project-Specific Task Guidelines
**STRICT ENFORCEMENT**: This AI agent must follow these task management rules:

#### Before Starting Any Task:
1. **VERIFY** all task dependencies are marked as 'done' 
2. **READ** the complete task specification using `taskinator show <id>`
3. **CHECK** for technology constraints in `stack.lock` file
4. **REFUSE** to proceed if stack is undefined or dependencies are incomplete

#### During Task Implementation:
1. **FOLLOW** task specifications exactly - no additions or interpretations
2. **IMPLEMENT** only what is specified in the task details
3. **TEST** according to the test strategy defined in the task
4. **ENFORCE** technology stack constraints from `stack.lock`

#### Task Completion Requirements:
1. **VALIDATE** all acceptance criteria are met
2. **ENSURE** all tests pass as specified in test strategy  
3. **CONFIRM** code follows technology stack standards
4. **MARK** task as completed only after full validation
"""
        )
