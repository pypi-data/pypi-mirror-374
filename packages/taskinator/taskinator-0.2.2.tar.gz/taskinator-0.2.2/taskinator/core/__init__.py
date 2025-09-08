"""
Core functionality for Taskinator.
"""

import dotenv

dotenv.load_dotenv()

from .prd_templates import (
    PRDTemplate,
    SectionMetadata,
    TemplateType,
    PRDTemplateManager,
    template_manager,
    render_template_to_markdown
)

from .prd_creation import (
    PRDCreator,
    PRDCreationState,
    UserCommand
)

__all__ = [
    'PRDTemplate',
    'SectionMetadata', 
    'TemplateType',
    'PRDTemplateManager',
    'template_manager',
    'render_template_to_markdown',
    'PRDCreator',
    'PRDCreationState',
    'UserCommand'
]
