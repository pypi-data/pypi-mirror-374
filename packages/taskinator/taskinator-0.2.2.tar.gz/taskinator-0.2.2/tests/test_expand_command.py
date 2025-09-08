"""
Tests for expand command including the alias functionality.
"""
import os
import pytest
from typer.testing import CliRunner

from taskinator.__main__ import app

runner = CliRunner()

def test_expand_alias_exists():
    """Test that the 'expand' command exists as an alias for 'expand-task'."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    
    # Check that both commands are present in help output
    help_text = result.output
    assert "expand-task" in help_text, "expand-task command not found in help output"
    assert "expand " in help_text, "expand command not found in help output"
    
def test_expand_alias_has_help():
    """Test that both 'expand' and 'expand-task' commands have help output."""
    # Check expand-task
    result_task = runner.invoke(app, ["expand-task", "--help"])
    assert result_task.exit_code == 0
    assert len(result_task.output) > 0
    
    # Check expand alias
    result_alias = runner.invoke(app, ["expand", "--help"])
    assert result_alias.exit_code == 0
    assert len(result_alias.output) > 0
    
    # Both should have similar content
    assert "Break down tasks into detailed subtasks" in result_task.output
    assert "Break down tasks into detailed subtasks" in result_alias.output
    
def test_expand_alias_has_options():
    """Test that both 'expand' and 'expand-task' commands have the same options."""
    result_task = runner.invoke(app, ["expand-task", "--help"])
    result_alias = runner.invoke(app, ["expand", "--help"])
    
    # Check for command options in both outputs
    for option in ["--id", "--num", "--research", "--all", "--force"]:
        assert option in result_task.output, f"Option {option} missing from expand-task help"
        assert option in result_alias.output, f"Option {option} missing from expand help"