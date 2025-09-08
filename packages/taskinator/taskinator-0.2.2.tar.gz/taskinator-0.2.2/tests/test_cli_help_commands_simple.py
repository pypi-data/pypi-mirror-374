"""
Simplified tests for validating CLI commands listed in help are accessible.
This test focuses specifically on the expand/expand-task issues.
"""
import pytest
from typer.testing import CliRunner

from taskinator.__main__ import app

# Create a CLI runner
runner = CliRunner()

@pytest.mark.parametrize("command", [
    "expand",
    "expand-task",
])
def test_command_help(command):
    """Test that specific commands respond to --help."""
    result = runner.invoke(app, [command, "--help"])
    assert result.exit_code == 0, f"Command '{command} --help' failed: {result.output}"
    assert "Usage:" in result.output
    assert "Options" in result.output

def test_expand_commands_in_help():
    """Test that both expand and expand-task commands appear in help."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    
    help_output = result.output
    
    # Check that both expand and expand-task commands are in the help
    assert "expand-task" in help_output, "expand-task command is missing from help output"
    assert "expand " in help_output, "expand command is missing from help output"
    
    # Check they have similar descriptions
    assert "Break down tasks into detailed subtasks" in help_output