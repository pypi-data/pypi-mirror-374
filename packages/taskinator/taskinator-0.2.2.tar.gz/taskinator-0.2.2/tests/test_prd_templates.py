"""Tests for PRD template system."""

import pytest
from taskinator.core.prd_templates import (
    PRDTemplate,
    SectionMetadata,
    TemplateType,
    PRDTemplateManager,
    template_manager,
    render_template_to_markdown
)


class TestSectionMetadata:
    """Test SectionMetadata class."""
    
    def test_section_metadata_creation(self):
        """Test creating a section metadata object."""
        section = SectionMetadata(
            title="Test Section",
            description="A test section",
            prompt="Enter test data",
            required=True,
            examples=["Example 1"],
            validation_rules=["Must not be empty"],
            order=1
        )
        
        assert section.title == "Test Section"
        assert section.description == "A test section"
        assert section.prompt == "Enter test data"
        assert section.required is True
        assert section.examples == ["Example 1"]
        assert section.validation_rules == ["Must not be empty"]
        assert section.order == 1
    
    def test_section_metadata_defaults(self):
        """Test section metadata with default values."""
        section = SectionMetadata(
            title="Test Section",
            description="A test section", 
            prompt="Enter test data"
        )
        
        assert section.required is True
        assert section.examples == []
        assert section.validation_rules == []
        assert section.order == 0


class TestPRDTemplate:
    """Test PRDTemplate class."""
    
    def setup_method(self):
        """Set up test template."""
        sections = {
            "overview": SectionMetadata(
                title="Overview",
                description="Project overview",
                prompt="Describe your project",
                required=True,
                order=1
            ),
            "details": SectionMetadata(
                title="Details", 
                description="Project details",
                prompt="Provide details",
                required=False,
                order=2
            )
        }
        
        self.template = PRDTemplate(
            name="Test Template",
            description="A test template",
            sections=sections
        )
    
    def test_template_creation(self):
        """Test creating a PRD template."""
        assert self.template.name == "Test Template"
        assert self.template.description == "A test template"
        assert len(self.template.sections) == 2
        assert "overview" in self.template.sections
        assert "details" in self.template.sections
    
    def test_get_ordered_sections(self):
        """Test getting sections in order."""
        ordered = self.template.get_ordered_sections()
        assert len(ordered) == 2
        assert ordered[0][0] == "overview"
        assert ordered[1][0] == "details"
    
    def test_get_required_sections(self):
        """Test getting required sections."""
        required = self.template.get_required_sections()
        assert required == ["overview"]
    
    def test_get_optional_sections(self):
        """Test getting optional sections."""
        optional = self.template.get_optional_sections()
        assert optional == ["details"]


class TestPRDTemplateManager:
    """Test PRDTemplateManager class."""
    
    def setup_method(self):
        """Set up template manager."""
        self.manager = PRDTemplateManager()
    
    def test_get_template_by_type(self):
        """Test getting template by type enum."""
        template = self.manager.get_template(TemplateType.STANDARD)
        assert template.name == "Standard PRD Template"
        assert "project_overview" in template.sections
    
    def test_get_template_by_name(self):
        """Test getting template by string name."""
        template = self.manager.get_template_by_name("minimal")
        assert template.name == "Minimal PRD Template"
        assert "project_overview" in template.sections
    
    def test_list_templates(self):
        """Test listing available templates."""
        templates = self.manager.list_templates()
        assert len(templates) == 3
        
        template_names = [name for name, desc in templates]
        assert "standard" in template_names
        assert "minimal" in template_names
        assert "feature" in template_names
    
    def test_validate_template_name(self):
        """Test template name validation."""
        assert self.manager.validate_template_name("standard") is True
        assert self.manager.validate_template_name("minimal") is True
        assert self.manager.validate_template_name("feature") is True
        assert self.manager.validate_template_name("invalid") is False
    
    def test_invalid_template_name_raises_error(self):
        """Test that invalid template name raises error."""
        with pytest.raises(ValueError):
            self.manager.get_template_by_name("invalid")


class TestTemplateContent:
    """Test that templates have expected content and structure."""
    
    def setup_method(self):
        """Set up template manager."""
        self.manager = template_manager
    
    def test_standard_template_structure(self):
        """Test standard template has expected sections."""
        template = self.manager.get_template(TemplateType.STANDARD)
        
        expected_sections = [
            "project_overview",
            "user_requirements", 
            "functional_requirements",
            "technical_requirements",
            "implementation_details",
            "success_criteria",
            "risks_and_mitigation"
        ]
        
        for section in expected_sections:
            assert section in template.sections
        
        # Check required sections
        required = template.get_required_sections()
        assert "project_overview" in required
        assert "user_requirements" in required
        assert "functional_requirements" in required
        assert "technical_requirements" in required
        assert "success_criteria" in required
        
        # Check optional sections
        optional = template.get_optional_sections()
        assert "implementation_details" in optional
        assert "risks_and_mitigation" in optional
    
    def test_minimal_template_structure(self):
        """Test minimal template has expected sections."""
        template = self.manager.get_template(TemplateType.MINIMAL)
        
        expected_sections = [
            "project_overview",
            "user_requirements",
            "functional_requirements", 
            "success_criteria"
        ]
        
        for section in expected_sections:
            assert section in template.sections
        
        # All sections should be required in minimal template
        required = template.get_required_sections()
        assert len(required) == len(expected_sections)
    
    def test_feature_template_structure(self):
        """Test feature template has expected sections."""
        template = self.manager.get_template(TemplateType.FEATURE)
        
        expected_sections = [
            "feature_overview",
            "user_story", 
            "acceptance_criteria",
            "technical_considerations",
            "edge_cases"
        ]
        
        for section in expected_sections:
            assert section in template.sections
        
        # Check required sections
        required = template.get_required_sections()
        assert "feature_overview" in required
        assert "user_story" in required
        assert "acceptance_criteria" in required
        
        # Check optional sections
        optional = template.get_optional_sections()
        assert "technical_considerations" in optional
        assert "edge_cases" in optional


class TestMarkdownRendering:
    """Test markdown rendering functionality."""
    
    def test_render_complete_template(self):
        """Test rendering template with all content filled."""
        template = template_manager.get_template(TemplateType.MINIMAL)
        
        content = {
            "project_overview": "This is a test project overview.",
            "user_requirements": "Test users need this functionality.",
            "functional_requirements": "1. Feature A\n2. Feature B",
            "success_criteria": "Success is measured by user adoption."
        }
        
        markdown = render_template_to_markdown(template, content)
        
        assert "# Minimal PRD" in markdown
        assert "## Project Overview" in markdown
        assert "This is a test project overview." in markdown
        assert "## User Requirements" in markdown
        assert "Test users need this functionality." in markdown
        assert "## Core Features" in markdown
        assert "1. Feature A" in markdown
        assert "## Success Criteria" in markdown
        assert "Success is measured by user adoption." in markdown
    
    def test_render_partial_template(self):
        """Test rendering template with some missing content."""
        template = template_manager.get_template(TemplateType.MINIMAL)
        
        content = {
            "project_overview": "This is a test project overview.",
            "functional_requirements": "1. Feature A\n2. Feature B"
            # Missing user_requirements and success_criteria
        }
        
        markdown = render_template_to_markdown(template, content)
        
        assert "# Minimal PRD" in markdown
        assert "This is a test project overview." in markdown
        assert "1. Feature A" in markdown
        assert "*[To be completed]*" in markdown
    
    def test_render_empty_template(self):
        """Test rendering template with no content."""
        template = template_manager.get_template(TemplateType.MINIMAL)
        content = {}
        
        markdown = render_template_to_markdown(template, content)
        
        assert "# Minimal PRD" in markdown
        assert "*[To be completed]*" in markdown
        # Should have placeholder for each section
        assert markdown.count("*[To be completed]*") == len(template.sections)


if __name__ == "__main__":
    pytest.main([__file__])