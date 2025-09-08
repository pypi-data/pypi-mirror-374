# Taskinator

A Python CLI task management tool for software development projects, inspired by task-master.

## Features

- Task generation from PRD documents
- Task management with dependencies
- Task analysis and complexity assessment
- AI-powered task expansion and breakdown
- Dependency validation and management
- Beautiful CLI interface with rich formatting

## Installation

```bash
# Using Poetry
poetry install

# Using pip
pip install .
```

## Configuration

Create a `.env` file in your project root with the following variables:

```
ANTHROPIC_API_KEY=your_anthropic_api_key
MODEL=claude-3-7-sonnet
MAX_TOKENS=4000
TEMPERATURE=0.7
PERPLEXITY_API_KEY=your_perplexity_api_key  # Optional
PERPLEXITY_MODEL=sonar-pro  # Optional
DEBUG=false
LOG_LEVEL=info
DEFAULT_SUBTASKS=3
DEFAULT_PRIORITY=medium
PROJECT_NAME=Taskinator
```

## Usage

```bash
# Show help
taskinator --help

# List all tasks
taskinator list

# Show the next task to work on
taskinator next

# Add a new task
taskinator add-task --prompt="Implement user authentication"

# Set task status
taskinator set-status --id=1 --status=done

# Expand a task into subtasks
taskinator expand --id=1 --num=3
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
