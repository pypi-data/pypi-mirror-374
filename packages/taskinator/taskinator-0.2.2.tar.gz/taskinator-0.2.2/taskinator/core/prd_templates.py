"""PRD Template System for Taskinator

This module defines PRD templates as structured data, providing different
template options for various project types and complexity levels.
"""

from typing import Dict, List, Any, Optional
from enum import Enum


class TemplateType(Enum):
    """Available PRD template types."""
    STANDARD = "standard"
    MINIMAL = "minimal" 
    FEATURE = "feature"


class SectionMetadata:
    """Metadata for a PRD section."""
    
    def __init__(
        self,
        title: str,
        description: str,
        prompt: str,
        required: bool = True,
        examples: Optional[List[str]] = None,
        validation_rules: Optional[List[str]] = None,
        order: int = 0
    ):
        self.title = title
        self.description = description
        self.prompt = prompt
        self.required = required
        self.examples = examples or []
        self.validation_rules = validation_rules or []
        self.order = order


class PRDTemplate:
    """A PRD template with structured sections."""
    
    def __init__(self, name: str, description: str, sections: Dict[str, SectionMetadata]):
        self.name = name
        self.description = description
        self.sections = sections
        
    def get_ordered_sections(self) -> List[tuple[str, SectionMetadata]]:
        """Get sections ordered by their order field."""
        return sorted(self.sections.items(), key=lambda x: x[1].order)
    
    def get_required_sections(self) -> List[str]:
        """Get list of required section keys."""
        return [key for key, section in self.sections.items() if section.required]
    
    def get_optional_sections(self) -> List[str]:
        """Get list of optional section keys."""
        return [key for key, section in self.sections.items() if not section.required]


def _create_standard_template() -> PRDTemplate:
    """Create the standard comprehensive PRD template."""
    sections = {
        "project_overview": SectionMetadata(
            title="Project Overview",
            description="High-level project context and purpose",
            prompt="Describe your project's main purpose, background, and goals (2-3 paragraphs).",
            required=True,
            examples=[
                "This feature adds a new dashboard to help users track their project metrics...",
                "The mobile app redesign aims to improve user engagement by streamlining navigation..."
            ],
            validation_rules=["Should be 2-3 paragraphs", "Must include project purpose"],
            order=1
        ),
        
        "user_requirements": SectionMetadata(
            title="User Requirements", 
            description="Target users and their needs",
            prompt="Who are your target users and what specific needs does this project address?",
            required=True,
            examples=[
                "Target users are software developers who need to track task completion...",
                "Primary users are project managers requiring visibility into team progress..."
            ],
            validation_rules=["Must identify target users", "Should include user needs"],
            order=2
        ),
        
        "functional_requirements": SectionMetadata(
            title="Functional Requirements",
            description="Core features and capabilities",
            prompt="What are the main features and capabilities this project must provide?",
            required=True,
            examples=[
                "1. User authentication and authorization\n2. Task creation and management\n3. Progress tracking dashboard"
            ],
            validation_rules=["Should be numbered or bulleted list", "Must include core features"],
            order=3
        ),
        
        "technical_requirements": SectionMetadata(
            title="Technical Requirements",
            description="Technical constraints and specifications",
            prompt="What are the technical requirements, constraints, and platform considerations?",
            required=True,
            examples=[
                "- Platform: Web application with mobile responsive design\n- Technology: Python/Django backend, React frontend"
            ],
            validation_rules=["Should include platform/technology details"],
            order=4
        ),
        
        "implementation_details": SectionMetadata(
            title="Implementation Details",
            description="Development approach and considerations", 
            prompt="Describe the development approach, testing strategy, and implementation considerations.",
            required=False,
            examples=[
                "Development will follow agile methodology with 2-week sprints...",
                "Testing strategy includes unit tests, integration tests, and user acceptance testing..."
            ],
            order=5
        ),
        
        "success_criteria": SectionMetadata(
            title="Success Criteria",
            description="Measurable success indicators",
            prompt="How will you measure the success of this project? What are the key metrics?",
            required=True,
            examples=[
                "- User adoption rate > 70% within 3 months\n- Task completion time reduced by 25%"
            ],
            validation_rules=["Should include measurable metrics"],
            order=6
        ),
        
        "risks_and_mitigation": SectionMetadata(
            title="Risks & Mitigation",
            description="Potential risks and mitigation strategies",
            prompt="What are the main risks for this project and how will you mitigate them?",
            required=False,
            examples=[
                "Risk: User adoption challenges\nMitigation: Comprehensive onboarding and training program"
            ],
            order=7
        )
    }
    
    return PRDTemplate(
        name="Standard PRD Template",
        description="Comprehensive PRD template suitable for most projects",
        sections=sections
    )


def _create_minimal_template() -> PRDTemplate:
    """Create the minimal PRD template with core sections only."""
    sections = {
        "project_overview": SectionMetadata(
            title="Project Overview",
            description="Brief project description and goals",
            prompt="Briefly describe what this project does and why it's needed (1-2 paragraphs).",
            required=True,
            examples=[
                "This tool helps developers manage their daily tasks more efficiently..."
            ],
            order=1
        ),
        
        "user_requirements": SectionMetadata(
            title="User Requirements",
            description="Target users and main needs",
            prompt="Who will use this and what problem does it solve for them?",
            required=True,
            examples=[
                "Software developers who struggle with task prioritization and tracking..."
            ],
            order=2
        ),
        
        "functional_requirements": SectionMetadata(
            title="Core Features",
            description="Essential features and capabilities",
            prompt="What are the 3-5 most important features this project must have?",
            required=True,
            examples=[
                "1. Create and manage tasks\n2. Set priorities\n3. Track progress"
            ],
            order=3
        ),
        
        "success_criteria": SectionMetadata(
            title="Success Criteria", 
            description="How success will be measured",
            prompt="How will you know if this project is successful?",
            required=True,
            examples=[
                "Users can complete their daily task management 50% faster"
            ],
            order=4
        )
    }
    
    return PRDTemplate(
        name="Minimal PRD Template",
        description="Streamlined template for quick PRD creation",
        sections=sections
    )


def _create_feature_template() -> PRDTemplate:
    """Create the feature-focused PRD template."""
    sections = {
        "feature_overview": SectionMetadata(
            title="Feature Overview", 
            description="Feature description and context",
            prompt="Describe this specific feature and how it fits into the larger product.",
            required=True,
            examples=[
                "The export functionality allows users to download their data in multiple formats..."
            ],
            order=1
        ),
        
        "user_story": SectionMetadata(
            title="User Story",
            description="User perspective on the feature",
            prompt="Write a user story: As a [user type], I want [feature] so that [benefit].",
            required=True,
            examples=[
                "As a project manager, I want to export task reports so that I can share progress with stakeholders."
            ],
            validation_rules=["Must follow 'As a... I want... so that...' format"],
            order=2
        ),
        
        "acceptance_criteria": SectionMetadata(
            title="Acceptance Criteria",
            description="Specific criteria for feature completion",
            prompt="What specific conditions must be met for this feature to be considered complete?",
            required=True,
            examples=[
                "- User can select export format (PDF, CSV, JSON)\n- Export completes within 30 seconds\n- All task data is included"
            ],
            order=3
        ),
        
        "technical_considerations": SectionMetadata(
            title="Technical Considerations",
            description="Implementation and technical notes",
            prompt="Are there any specific technical requirements or constraints for this feature?",
            required=False,
            examples=[
                "Must work with existing authentication system\nShould handle up to 10,000 tasks per export"
            ],
            order=4
        ),
        
        "edge_cases": SectionMetadata(
            title="Edge Cases",
            description="Unusual scenarios to consider",
            prompt="What edge cases or unusual scenarios should be handled?",
            required=False,
            examples=[
                "- No tasks to export\n- Very large datasets\n- Network interruptions during export"
            ],
            order=5
        )
    }
    
    return PRDTemplate(
        name="Feature PRD Template",
        description="Focused template for individual feature PRDs",
        sections=sections
    )


class PRDTemplateManager:
    """Manages PRD templates and provides access to them."""
    
    def __init__(self):
        self._templates = {
            TemplateType.STANDARD: _create_standard_template(),
            TemplateType.MINIMAL: _create_minimal_template(),
            TemplateType.FEATURE: _create_feature_template()
        }
    
    def get_template(self, template_type: TemplateType) -> PRDTemplate:
        """Get a specific template by type."""
        return self._templates[template_type]
    
    def get_template_by_name(self, name: str) -> PRDTemplate:
        """Get a template by string name."""
        template_type = TemplateType(name.lower())
        return self.get_template(template_type)
    
    def list_templates(self) -> List[tuple[str, str]]:
        """Get list of available templates with their descriptions."""
        return [
            (template_type.value, template.description)
            for template_type, template in self._templates.items()
        ]
    
    def validate_template_name(self, name: str) -> bool:
        """Check if a template name is valid."""
        try:
            TemplateType(name.lower())
            return True
        except ValueError:
            return False


def render_template_to_markdown(template: PRDTemplate, content: Dict[str, str]) -> str:
    """Render a completed PRD template to markdown format."""
    lines = [f"# {template.name.replace(' Template', '')}\n"]
    
    for section_key, section_meta in template.get_ordered_sections():
        lines.append(f"## {section_meta.title}\n")
        
        if section_key in content and content[section_key].strip():
            lines.append(f"{content[section_key].strip()}\n")
        else:
            lines.append("*[To be completed]*\n")
    
    return "\n".join(lines)


# Global template manager instance
template_manager = PRDTemplateManager()