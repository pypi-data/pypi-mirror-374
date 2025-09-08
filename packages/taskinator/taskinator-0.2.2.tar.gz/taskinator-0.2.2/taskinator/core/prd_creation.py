"""PRD Creation Business Logic for Taskinator

This module provides the business logic for PRD creation workflow management,
including section navigation, input collection, state management, and validation.
"""

import os
import json
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from .prd_templates import (
    PRDTemplate,
    SectionMetadata,
    TemplateType,
    template_manager,
    render_template_to_markdown
)


class PRDCreationState(Enum):
    """Possible states for PRD creation workflow."""
    INITIALIZED = auto()
    IN_PROGRESS = auto()
    REVIEWING = auto()
    EDITING = auto()
    COMPLETED = auto()
    SAVED = auto()


class UserCommand(Enum):
    """Commands a user can issue during PRD creation."""
    HELP = "help"
    SKIP = "skip"
    BACK = "back"
    PREVIEW = "preview"
    EDIT = "edit"
    FINISH = "finish"
    SAVE = "save"


class PRDCreator:
    """Manages the PRD creation workflow, section navigation, and state management."""
    
    def __init__(
        self,
        name: str,
        template_type: TemplateType = TemplateType.STANDARD,
        output_path: Optional[str] = None,
        update_path: Optional[str] = None
    ):
        """Initialize PRD Creator with project settings.
        
        Args:
            name: Project or feature name (used for filename generation)
            template_type: PRD template type to use
            output_path: Custom output path (defaults to docs/[name]-prd.md)
            update_path: Path to an existing PRD to update instead of creating new
        """
        self.name = name
        self.template_type = template_type
        self.template = template_manager.get_template(template_type)
        
        # Default output path
        if not output_path:
            # Create docs directory if it doesn't exist
            docs_dir = Path("docs")
            if not docs_dir.exists():
                docs_dir.mkdir(parents=True)
            self.output_path = f"docs/{self.name.lower().replace(' ', '-')}-prd.md"
        else:
            self.output_path = output_path
        
        # Initialize content storage
        self.content: Dict[str, str] = {}
        
        # Load existing content if updating
        if update_path and os.path.exists(update_path):
            self._load_existing_prd(update_path)
        
        # State management
        self.state = PRDCreationState.INITIALIZED
        self.current_section_index = 0
        self.sections_list = [key for key, _ in self.template.get_ordered_sections()]
        self.completion_status: Dict[str, bool] = {key: False for key in self.sections_list}
        self.validation_errors: Dict[str, List[str]] = {}
        
        # Mark sections as complete if content exists
        for section_key, content in self.content.items():
            if content.strip():
                self.completion_status[section_key] = True
    
    def _load_existing_prd(self, file_path: str) -> None:
        """Load content from an existing PRD file.
        
        Attempts to parse markdown headings and content to populate the PRD template.
        
        Args:
            file_path: Path to existing PRD markdown file
        """
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            current_section = None
            content_buffer = []
            
            # Process the markdown file line by line
            for line in lines:
                # Skip the title line
                if line.startswith('# '):
                    continue
                
                # Check if line is a section heading
                if line.startswith('## '):
                    # Save previous section content if exists
                    if current_section and content_buffer:
                        self.content[current_section] = ''.join(content_buffer).strip()
                        content_buffer = []
                    
                    # Get new section title and find corresponding section key
                    section_title = line[3:].strip()
                    current_section = self._find_section_key_by_title(section_title)
                    continue
                
                # Add line to current section content
                if current_section:
                    # Skip the "To be completed" placeholder
                    if "*[To be completed]*" in line:
                        continue
                    content_buffer.append(line)
            
            # Don't forget to save the last section
            if current_section and content_buffer:
                self.content[current_section] = ''.join(content_buffer).strip()
        
        except Exception as e:
            # If loading fails, just start with empty content
            self.content = {}
            print(f"Warning: Could not load existing PRD: {e}")
    
    def _find_section_key_by_title(self, title: str) -> Optional[str]:
        """Find section key by its title.
        
        Args:
            title: The section title to search for
            
        Returns:
            The section key or None if not found
        """
        for key, metadata in self.template.sections.items():
            if metadata.title == title:
                return key
        return None
    
    def start(self) -> Tuple[str, SectionMetadata]:
        """Start or resume the PRD creation process.
        
        Returns:
            Tuple of (section_key, section_metadata) for the current section
        """
        self.state = PRDCreationState.IN_PROGRESS
        section_key = self.sections_list[self.current_section_index]
        return section_key, self.template.sections[section_key]
    
    def get_welcome_message(self) -> str:
        """Get welcome message and instructions for PRD creation.
        
        Returns:
            Formatted welcome message with instructions
        """
        message = [
            f"Welcome to the Taskinator PRD Creator!",
            f"",
            f"You're using the {self.template.name} to create a PRD for '{self.name}'.",
            f"",
            f"Instructions:",
            f"- I'll guide you through each section of the PRD",
            f"- Type your response after each prompt",
            f"- Use commands like /help, /skip, /back, /preview, /edit, /finish",
            f"",
            f"Let's get started with the first section!"
        ]
        return "\n".join(message)
    
    def get_help_message(self) -> str:
        """Get help message with available commands.
        
        Returns:
            Formatted help message string
        """
        message = [
            f"Available commands:",
            f"",
            f"/help - Show this help message",
            f"/skip - Skip current section and move to the next",
            f"/back - Go back to the previous section",
            f"/preview - Show current PRD draft",
            f"/edit [section] - Edit a specific section",
            f"/finish - Complete the PRD creation process",
            f"/save - Save current progress as draft",
            f"",
            f"Just type your content to respond to the current prompt."
        ]
        return "\n".join(message)
    
    def handle_input(self, user_input: str) -> Dict[str, Any]:
        """Process user input and update state accordingly.
        
        Args:
            user_input: User input text or command
            
        Returns:
            Dictionary with response data and next actions
        """
        # Check if input is a command
        if user_input.startswith("/"):
            return self._handle_command(user_input[1:])  # Remove the leading slash
        
        # Handle regular input (section content)
        return self._handle_section_content(user_input)
    
    def _handle_command(self, command_text: str) -> Dict[str, Any]:
        """Handle command input.
        
        Args:
            command_text: Command without the leading slash
            
        Returns:
            Response data including message and next action
        """
        # Parse command and arguments
        parts = command_text.strip().split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Handle each command
        if command == UserCommand.HELP.value:
            return {
                "type": "help",
                "message": self.get_help_message()
            }
        
        elif command == UserCommand.SKIP.value:
            return self._handle_skip_command()
        
        elif command == UserCommand.BACK.value:
            return self._handle_back_command()
        
        elif command == UserCommand.PREVIEW.value:
            return self._handle_preview_command()
        
        elif command == UserCommand.EDIT.value:
            return self._handle_edit_command(args)
        
        elif command == UserCommand.FINISH.value:
            return self._handle_finish_command()
        
        elif command == UserCommand.SAVE.value:
            return self._handle_save_command()
        
        else:
            return {
                "type": "error",
                "message": f"Unknown command: {command}. Type /help for available commands."
            }
    
    def _handle_skip_command(self) -> Dict[str, Any]:
        """Handle skip command to move to next section.
        
        Returns:
            Response data with next section
        """
        # Move to next section
        if self.current_section_index < len(self.sections_list) - 1:
            self.current_section_index += 1
            section_key = self.sections_list[self.current_section_index]
            section = self.template.sections[section_key]
            
            return {
                "type": "next_section",
                "section_key": section_key,
                "section": section,
                "message": f"Moving to section: {section.title}"
            }
        else:
            # Already at the last section
            return {
                "type": "info",
                "message": "This is the last section. Use /finish to complete the PRD or /edit to revise a section."
            }
    
    def _handle_back_command(self) -> Dict[str, Any]:
        """Handle back command to move to previous section.
        
        Returns:
            Response data with previous section
        """
        # Move to previous section
        if self.current_section_index > 0:
            self.current_section_index -= 1
            section_key = self.sections_list[self.current_section_index]
            section = self.template.sections[section_key]
            
            return {
                "type": "previous_section",
                "section_key": section_key,
                "section": section,
                "message": f"Moving back to section: {section.title}",
                "current_content": self.content.get(section_key, "")
            }
        else:
            # Already at the first section
            return {
                "type": "info",
                "message": "This is the first section. There are no previous sections."
            }
    
    def _handle_preview_command(self) -> Dict[str, Any]:
        """Handle preview command to show current PRD draft.
        
        Returns:
            Response data with preview markdown
        """
        self.state = PRDCreationState.REVIEWING
        markdown = render_template_to_markdown(self.template, self.content)
        
        # Get completion stats
        total_sections = len(self.sections_list)
        completed_sections = sum(1 for key in self.sections_list if self.completion_status.get(key, False))
        
        return {
            "type": "preview",
            "markdown": markdown,
            "completion_stats": {
                "total": total_sections,
                "completed": completed_sections,
                "percentage": int((completed_sections / total_sections) * 100)
            },
            "message": f"PRD Preview ({completed_sections}/{total_sections} sections complete)"
        }
    
    def _handle_edit_command(self, args: List[str]) -> Dict[str, Any]:
        """Handle edit command to edit a specific section.
        
        Args:
            args: Command arguments (section name or index)
            
        Returns:
            Response data with section to edit
        """
        self.state = PRDCreationState.EDITING
        
        # No args provided, show available sections
        if not args:
            sections_list = [
                f"{i+1}. {self.template.sections[key].title}" 
                for i, key in enumerate(self.sections_list)
            ]
            return {
                "type": "info",
                "message": "Please specify a section number to edit:\n" + "\n".join(sections_list)
            }
        
        # Try to parse section index
        try:
            section_index = int(args[0]) - 1  # Convert to 0-based index
            if 0 <= section_index < len(self.sections_list):
                self.current_section_index = section_index
                section_key = self.sections_list[self.current_section_index]
                section = self.template.sections[section_key]
                
                return {
                    "type": "edit_section",
                    "section_key": section_key,
                    "section": section,
                    "message": f"Editing section: {section.title}",
                    "current_content": self.content.get(section_key, "")
                }
            else:
                return {
                    "type": "error",
                    "message": f"Invalid section number. Please choose a number between 1 and {len(self.sections_list)}."
                }
        except ValueError:
            # Not a number, try to find by name
            section_name = " ".join(args).lower()
            for i, key in enumerate(self.sections_list):
                if section_name in self.template.sections[key].title.lower():
                    self.current_section_index = i
                    section_key = self.sections_list[self.current_section_index]
                    section = self.template.sections[section_key]
                    
                    return {
                        "type": "edit_section",
                        "section_key": section_key,
                        "section": section,
                        "message": f"Editing section: {section.title}",
                        "current_content": self.content.get(section_key, "")
                    }
            
            return {
                "type": "error",
                "message": f"Section '{section_name}' not found. Use /edit to see available sections."
            }
    
    def _handle_finish_command(self) -> Dict[str, Any]:
        """Handle finish command to complete PRD creation.
        
        Returns:
            Response data with completion status
        """
        # Check for required sections
        missing_required = []
        for section_key in self.template.get_required_sections():
            if not self.content.get(section_key, "").strip():
                missing_required.append(self.template.sections[section_key].title)
        
        # If required sections are missing, notify user
        if missing_required:
            return {
                "type": "warning",
                "message": (f"The following required sections are missing or empty:\n"
                           f"{', '.join(missing_required)}\n\n"
                           f"You should complete these sections before finishing.")
            }
        
        # All required sections are complete
        self.state = PRDCreationState.COMPLETED
        markdown = render_template_to_markdown(self.template, self.content)
        
        return {
            "type": "finished",
            "markdown": markdown,
            "message": f"PRD creation complete! Ready to save to {self.output_path}"
        }
    
    def _handle_save_command(self) -> Dict[str, Any]:
        """Handle save command to save current progress.
        
        Returns:
            Response data with save status
        """
        try:
            # Create the markdown content
            markdown = render_template_to_markdown(self.template, self.content)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.output_path) or '.', exist_ok=True)
            
            # Write the file
            with open(self.output_path, 'w') as f:
                f.write(markdown)
            
            self.state = PRDCreationState.SAVED
            
            return {
                "type": "saved",
                "path": self.output_path,
                "message": f"PRD saved successfully to {self.output_path}"
            }
        except Exception as e:
            return {
                "type": "error",
                "message": f"Error saving PRD: {str(e)}"
            }
    
    def _handle_section_content(self, content: str) -> Dict[str, Any]:
        """Handle user input for current section content.
        
        Args:
            content: User input content
            
        Returns:
            Response data with next actions
        """
        # Get current section
        section_key = self.sections_list[self.current_section_index]
        section = self.template.sections[section_key]
        
        # Store the content
        self.content[section_key] = content
        
        # Mark section as complete if content is not empty
        if content.strip():
            self.completion_status[section_key] = True
        else:
            self.completion_status[section_key] = False
        
        # Validate content if validation rules exist
        validation_errors = []
        for rule in section.validation_rules:
            # Simple validation rule examples
            if rule == "Should be 2-3 paragraphs":
                paragraphs = [p for p in content.split("\n\n") if p.strip()]
                if not (2 <= len(paragraphs) <= 3):
                    validation_errors.append("Content should be 2-3 paragraphs.")
            
            elif rule == "Must include project purpose":
                if "purpose" not in content.lower():
                    validation_errors.append("Content should mention project purpose.")
            
            # Add more validation rules as needed
        
        # Store validation errors
        if validation_errors:
            self.validation_errors[section_key] = validation_errors
        else:
            self.validation_errors.pop(section_key, None)
        
        # Prepare response
        response = {
            "type": "content_updated",
            "section_key": section_key,
            "validation_errors": validation_errors
        }
        
        # Suggest next action
        if validation_errors:
            response["message"] = (
                f"Content saved with {len(validation_errors)} validation issues:\n" +
                "\n".join(f"- {error}" for error in validation_errors) +
                "\n\nYou can revise your answer or continue to the next section."
            )
            response["suggestion"] = "revise"
        else:
            # Move to next section automatically if there are more sections
            if self.current_section_index < len(self.sections_list) - 1:
                self.current_section_index += 1
                next_section_key = self.sections_list[self.current_section_index]
                next_section = self.template.sections[next_section_key]
                
                response["next_section_key"] = next_section_key
                response["next_section"] = next_section
                response["message"] = f"Content saved! Moving to next section: {next_section.title}"
                response["suggestion"] = "next"
            else:
                # This was the last section
                response["message"] = (
                    "Content saved! This was the last section. "
                    "Use /preview to review your PRD or /edit to make changes."
                )
                response["suggestion"] = "preview"
        
        return response
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get summary of PRD creation progress.
        
        Returns:
            Dictionary with progress data
        """
        total_sections = len(self.sections_list)
        completed_sections = sum(1 for key in self.sections_list if self.completion_status.get(key, False))
        
        # Get lists of completed and incomplete sections
        completed = []
        incomplete = []
        
        for key in self.sections_list:
            section_title = self.template.sections[key].title
            if self.completion_status.get(key, False):
                completed.append(section_title)
            else:
                incomplete.append(section_title)
        
        return {
            "total": total_sections,
            "completed": completed_sections,
            "completed_sections": completed,
            "incomplete_sections": incomplete,
            "percentage": int((completed_sections / total_sections) * 100)
        }
    
    def get_current_section(self) -> Tuple[str, SectionMetadata]:
        """Get the current section key and metadata.
        
        Returns:
            Tuple of (section_key, section_metadata) for the current section
        """
        section_key = self.sections_list[self.current_section_index]
        return section_key, self.template.sections[section_key]
    
    def save_progress(self, path: Optional[str] = None) -> bool:
        """Save progress to a JSON file for later restoration.
        
        Args:
            path: File path to save progress (defaults to .taskinator/prd_progress.json)
            
        Returns:
            True if saved successfully, False otherwise
        """
        if not path:
            # Create .taskinator directory if it doesn't exist
            os.makedirs(".taskinator", exist_ok=True)
            path = ".taskinator/prd_progress.json"
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
            
            data = {
                "name": self.name,
                "template_type": self.template_type.value,
                "output_path": self.output_path,
                "content": self.content,
                "current_section_index": self.current_section_index,
                "completion_status": self.completion_status
            }
            
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving progress: {e}")
            return False
    
    @classmethod
    def load_progress(cls, path: str) -> Optional['PRDCreator']:
        """Load previously saved PRD creation progress.
        
        Args:
            path: File path to load progress from
            
        Returns:
            PRDCreator instance with restored state or None if loading failed
        """
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            
            # Create instance with minimal initialization
            template_type = TemplateType(data.get("template_type", "standard"))
            creator = cls(
                name=data.get("name", "Unnamed Project"),
                template_type=template_type,
                output_path=data.get("output_path")
            )
            
            # Restore state
            creator.content = data.get("content", {})
            creator.current_section_index = data.get("current_section_index", 0)
            creator.completion_status = data.get("completion_status", {})
            
            return creator
        except Exception:
            return None