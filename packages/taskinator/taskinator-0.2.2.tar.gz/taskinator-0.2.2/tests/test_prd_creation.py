"""Tests for PRD creation business logic."""

import os
import tempfile
import pytest
from pathlib import Path

from taskinator.core.prd_creation import (
    PRDCreator,
    PRDCreationState,
    UserCommand,
    TemplateType
)


class TestPRDCreator:
    """Test PRDCreator class."""
    
    def setup_method(self):
        """Set up test PRD creator."""
        self.name = "Test Project"
        self.temp_dir = Path(tempfile.mkdtemp())
        self.output_path = str(self.temp_dir / "test-project-prd.md")
        self.creator = PRDCreator(
            name=self.name,
            template_type=TemplateType.MINIMAL,
            output_path=self.output_path
        )
    
    def test_initialization(self):
        """Test PRDCreator initialization."""
        assert self.creator.name == "Test Project"
        assert self.creator.template_type == TemplateType.MINIMAL
        assert self.creator.output_path == self.output_path
        assert self.creator.state == PRDCreationState.INITIALIZED
        assert self.creator.current_section_index == 0
        assert len(self.creator.sections_list) > 0
        assert len(self.creator.completion_status) == len(self.creator.sections_list)
    
    def test_default_output_path(self):
        """Test default output path generation."""
        # Cleanup potential docs directory created by other tests
        if os.path.exists("docs"):
            # Only cleanup if it was created by this test
            if not os.path.exists("docs/.test_marker"):
                os.makedirs("docs", exist_ok=True)
                with open("docs/.test_marker", "w") as f:
                    f.write("Test marker file")
        
        creator = PRDCreator(name="Test Project", template_type=TemplateType.MINIMAL)
        assert creator.output_path == "docs/test-project-prd.md"
        
        # Cleanup
        if os.path.exists("docs/.test_marker"):
            os.remove("docs/.test_marker")
            try:
                os.rmdir("docs")
            except OSError:
                pass  # Directory not empty, leave it
    
    def test_get_welcome_message(self):
        """Test welcome message generation."""
        message = self.creator.get_welcome_message()
        assert "Welcome to the Taskinator PRD Creator" in message
        assert "Test Project" in message
        assert "Minimal PRD Template" in message
    
    def test_get_help_message(self):
        """Test help message generation."""
        message = self.creator.get_help_message()
        assert "/help" in message
        assert "/skip" in message
        assert "/back" in message
        assert "/preview" in message
        assert "/edit" in message
        assert "/finish" in message
        assert "/save" in message
    
    def test_start(self):
        """Test starting the PRD creation process."""
        section_key, section = self.creator.start()
        assert section_key == "project_overview"
        assert section.title == "Project Overview"
        assert self.creator.state == PRDCreationState.IN_PROGRESS
    
    def test_handle_help_command(self):
        """Test handling help command."""
        response = self.creator.handle_input("/help")
        assert response["type"] == "help"
        assert "/help" in response["message"]
    
    def test_handle_skip_command(self):
        """Test handling skip command."""
        # Start from first section
        self.creator.start()
        
        # Skip to next section
        response = self.creator.handle_input("/skip")
        assert response["type"] == "next_section"
        assert self.creator.current_section_index == 1
    
    def test_skip_last_section(self):
        """Test handling skip command on the last section."""
        # Move to the last section
        self.creator.current_section_index = len(self.creator.sections_list) - 1
        
        # Try to skip beyond the last section
        response = self.creator.handle_input("/skip")
        assert response["type"] == "info"
        assert "last section" in response["message"]
    
    def test_handle_back_command(self):
        """Test handling back command."""
        # Start from second section
        self.creator.start()
        self.creator.current_section_index = 1
        
        # Go back to first section
        response = self.creator.handle_input("/back")
        assert response["type"] == "previous_section"
        assert self.creator.current_section_index == 0
    
    def test_back_first_section(self):
        """Test handling back command on the first section."""
        # Start from first section
        self.creator.start()
        
        # Try to go back from the first section
        response = self.creator.handle_input("/back")
        assert response["type"] == "info"
        assert "first section" in response["message"]
    
    def test_handle_preview_command(self):
        """Test handling preview command."""
        # Add some content
        self.creator.start()
        self.creator.content["project_overview"] = "Test project overview."
        self.creator.completion_status["project_overview"] = True
        
        # Preview the PRD
        response = self.creator.handle_input("/preview")
        assert response["type"] == "preview"
        assert "# Minimal PRD" in response["markdown"]
        assert "Test project overview" in response["markdown"]
        assert response["completion_stats"]["completed"] == 1
    
    def test_handle_edit_command_no_args(self):
        """Test handling edit command with no arguments."""
        response = self.creator.handle_input("/edit")
        assert response["type"] == "info"
        assert "Please specify a section number" in response["message"]
    
    def test_handle_edit_command_by_index(self):
        """Test handling edit command with section index."""
        self.creator.start()
        
        # Edit section 2 (index 1)
        response = self.creator.handle_input("/edit 2")
        assert response["type"] == "edit_section"
        assert self.creator.current_section_index == 1
    
    def test_handle_edit_command_by_name(self):
        """Test handling edit command with section name."""
        self.creator.start()
        
        # Edit section by name (should be case insensitive)
        response = self.creator.handle_input("/edit user requirements")
        assert response["type"] == "edit_section"
        assert "User Requirements" in response["message"]
    
    def test_handle_edit_invalid_section(self):
        """Test handling edit command with invalid section."""
        response = self.creator.handle_input("/edit invalid section")
        assert response["type"] == "error"
        assert "not found" in response["message"]
    
    def test_handle_finish_with_missing_required(self):
        """Test finishing with missing required sections."""
        # Start without filling any sections
        self.creator.start()
        
        # Try to finish (should warn about missing sections)
        response = self.creator.handle_input("/finish")
        assert response["type"] == "warning"
        assert "required sections are missing" in response["message"]
    
    def test_handle_finish_complete(self):
        """Test finishing with all required sections."""
        # Fill all required sections
        self.creator.start()
        for key in self.creator.template.get_required_sections():
            self.creator.content[key] = f"Content for {key}"
            self.creator.completion_status[key] = True
        
        # Now finish should work
        response = self.creator.handle_input("/finish")
        assert response["type"] == "finished"
        assert "PRD creation complete" in response["message"]
    
    def test_handle_save_command(self):
        """Test handling save command."""
        # Add some content
        self.creator.start()
        self.creator.content["project_overview"] = "Test project overview."
        
        # Save the PRD
        response = self.creator.handle_input("/save")
        assert response["type"] == "saved"
        assert "saved successfully" in response["message"]
        assert os.path.exists(self.output_path)
        
        # Check file content
        with open(self.output_path, "r") as f:
            content = f.read()
            assert "# Minimal PRD" in content
            assert "Test project overview" in content
    
    def test_handle_section_content(self):
        """Test handling section content input."""
        # Start from first section
        section_key, _ = self.creator.start()
        
        # Add content for the section
        response = self.creator.handle_input("This is the project overview.")
        
        # Should store content and update completion status
        assert section_key in self.creator.content
        assert self.creator.content[section_key] == "This is the project overview."
        assert self.creator.completion_status[section_key] is True
        
        # Should advance to next section automatically
        assert self.creator.current_section_index == 1
        assert response["suggestion"] == "next"
    
    def test_handle_empty_content(self):
        """Test handling empty content input."""
        # Start from first section
        section_key, _ = self.creator.start()
        
        # Add empty content
        response = self.creator.handle_input("")
        
        # Should store empty content and mark as incomplete
        assert section_key in self.creator.content
        assert self.creator.content[section_key] == ""
        assert self.creator.completion_status[section_key] is False
    
    def test_get_progress_summary(self):
        """Test getting progress summary."""
        # Fill some sections
        self.creator.start()
        self.creator.content["project_overview"] = "Test content"
        self.creator.completion_status["project_overview"] = True
        
        # Get progress summary
        summary = self.creator.get_progress_summary()
        
        assert summary["total"] == len(self.creator.sections_list)
        assert summary["completed"] == 1
        assert len(summary["completed_sections"]) == 1
        assert "Project Overview" in summary["completed_sections"]
        assert len(summary["incomplete_sections"]) == len(self.creator.sections_list) - 1
    
    @pytest.mark.parametrize("content,expected_errors", [
        # Valid content (2 paragraphs)
        ("Paragraph 1.\n\nParagraph 2 with purpose mentioned.", []),
        
        # Invalid content (1 paragraph, missing purpose)
        ("Single paragraph without key information.", ["Content should be 2-3 paragraphs.", 
                                                      "Content should mention project purpose."]),
        
        # Valid content (3 paragraphs with purpose)
        ("P1.\n\nP2 with purpose mentioned.\n\nP3.", [])
    ])
    def test_validation_rules(self, content, expected_errors):
        """Test content validation rules."""
        # Add validation rules to the first section
        section_key = self.creator.sections_list[0]
        self.creator.template.sections[section_key].validation_rules = [
            "Should be 2-3 paragraphs",
            "Must include project purpose"
        ]
        
        # Start and submit content
        self.creator.start()
        response = self.creator.handle_input(content)
        
        # Check validation results
        if expected_errors:
            assert "validation_errors" in response
            assert len(response["validation_errors"]) == len(expected_errors)
            for error in expected_errors:
                assert error in response["validation_errors"]
        else:
            assert not response.get("validation_errors")
    
    def test_save_and_load_progress(self):
        """Test saving and loading progress."""
        # Fill some content
        self.creator.start()
        self.creator.content["project_overview"] = "Test content"
        self.creator.completion_status["project_overview"] = True
        self.creator.current_section_index = 1
        
        # Save progress to temporary file
        progress_file = str(self.temp_dir / "progress.json")
        success = self.creator.save_progress(progress_file)
        assert success is True
        
        # Load progress in a new creator
        new_creator = PRDCreator.load_progress(progress_file)
        assert new_creator is not None
        assert new_creator.name == self.creator.name
        assert new_creator.content == self.creator.content
        assert new_creator.current_section_index == self.creator.current_section_index
        assert new_creator.completion_status == self.creator.completion_status
    
    def test_load_existing_prd(self):
        """Test loading content from an existing PRD file."""
        # Create a sample PRD file
        prd_content = """# Sample PRD
        
## Project Overview
This is a test project overview.

## User Requirements
These are the user requirements.

## Core Features
1. Feature A
2. Feature B

## Success Criteria
Success criteria here.
"""
        
        existing_prd_path = str(self.temp_dir / "existing-prd.md")
        with open(existing_prd_path, "w") as f:
            f.write(prd_content)
        
        # Create PRDCreator with the existing PRD
        creator = PRDCreator(
            name="Existing Project",
            template_type=TemplateType.MINIMAL,
            update_path=existing_prd_path
        )
        
        # Check that content was loaded
        assert "project_overview" in creator.content
        assert "This is a test project overview" in creator.content["project_overview"]
        assert "user_requirements" in creator.content
        assert "These are the user requirements" in creator.content["user_requirements"]
        
        # Check completion status
        assert creator.completion_status["project_overview"] is True
        assert creator.completion_status["user_requirements"] is True


if __name__ == "__main__":
    pytest.main([__file__])