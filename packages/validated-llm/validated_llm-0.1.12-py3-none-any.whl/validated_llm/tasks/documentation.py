"""
Documentation generation tasks for technical writing and content creation.
"""

from typing import Any, Dict, List, Optional

from ..base_validator import BaseValidator
from ..validators.documentation import DocumentationType, DocumentationValidator
from .base_task import BaseTask


class DocumentationTask(BaseTask):
    """
    Base task for generating technical documentation with validation.

    Supports multiple documentation types: API docs, README files,
    technical specifications, user guides, changelogs, and tutorials.
    """

    def __init__(
        self,
        doc_type: DocumentationType = DocumentationType.README,
        project_name: str = "Your Project",
        project_description: str = "A software project",
        include_installation: bool = True,
        include_usage: bool = True,
        include_examples: bool = True,
        include_api_docs: bool = False,
        include_contributing: bool = False,
        include_license: bool = True,
        target_audience: str = "developers",
        min_sections: int = 3,
        require_code_examples: bool = True,
        **validator_kwargs: Any,
    ):
        """
        Initialize documentation task.

        Args:
            doc_type: Type of documentation to generate
            project_name: Name of the project
            project_description: Brief project description
            include_installation: Include installation section
            include_usage: Include usage section
            include_examples: Include examples section
            include_api_docs: Include API documentation
            include_contributing: Include contributing guidelines
            include_license: Include license information
            target_audience: Target audience for documentation
            min_sections: Minimum number of sections required
            require_code_examples: Whether code examples are required
            **validator_kwargs: Additional validator configuration
        """
        self.doc_type = doc_type
        self.project_name = project_name
        self.project_description = project_description
        self.include_installation = include_installation
        self.include_usage = include_usage
        self.include_examples = include_examples
        self.include_api_docs = include_api_docs
        self.include_contributing = include_contributing
        self.include_license = include_license
        self.target_audience = target_audience

        # Create validator with type-specific configuration
        validator_config = {
            "doc_type": doc_type,
            "min_sections": min_sections,
            "require_code_examples": require_code_examples,
            "require_installation_section": include_installation,
            "require_usage_section": include_usage,
            "require_api_documentation": include_api_docs,
            **validator_kwargs,
        }

        self._validator = DocumentationValidator(**validator_config)

        # Build and cache prompt template
        self._prompt_template = self._build_prompt_template()

    def _build_prompt_template(self) -> str:
        """Build the prompt template based on documentation type and requirements."""
        base_prompt = self._get_base_prompt()

        # Add type-specific instructions
        type_instructions = self._get_type_specific_instructions()

        # Add section requirements
        section_requirements = self._get_section_requirements()

        # Add formatting guidelines
        formatting_guidelines = self._get_formatting_guidelines()

        # Add examples
        examples = self._get_examples()

        prompt = f"""
{base_prompt}

{type_instructions}

{section_requirements}

{formatting_guidelines}

{examples}

Generate comprehensive {self.doc_type.value} documentation for "{self.project_name}":
{self.project_description}

Target audience: {self.target_audience}

Please follow the structure and requirements specified above.
"""

        return prompt.strip()

    @property
    def prompt_template(self) -> str:
        """Get the prompt template for this documentation task."""
        return self._prompt_template

    def _get_base_prompt(self) -> str:
        """Get base prompt for documentation generation."""
        return f"""
You are a technical writer creating high-quality {self.doc_type.value} documentation.
Your goal is to create clear, comprehensive, and well-structured documentation that helps users understand and use the project effectively.

Project: {self.project_name}
Description: {self.project_description}
Documentation Type: {self.doc_type.value}
"""

    def _get_type_specific_instructions(self) -> str:
        """Get instructions specific to the documentation type."""
        instructions = {
            DocumentationType.API: """
API Documentation Requirements:
- Document all endpoints with HTTP methods
- Include request/response examples
- Specify authentication requirements
- Document error codes and responses
- Include rate limiting information
- Provide SDKs or client library examples
""",
            DocumentationType.README: """
README Requirements:
- Start with a clear project description
- Include badges for build status, version, etc.
- Provide installation instructions
- Show basic usage examples
- Include contribution guidelines
- Add license information
- Provide contact/support information
""",
            DocumentationType.TECHNICAL_SPEC: """
Technical Specification Requirements:
- Define system requirements clearly
- Include architecture diagrams (describe them)
- Specify implementation details
- Document APIs and interfaces
- Include performance requirements
- Address security considerations
- Provide deployment guidelines
""",
            DocumentationType.USER_GUIDE: """
User Guide Requirements:
- Write for non-technical users
- Include step-by-step instructions
- Provide screenshots descriptions
- Address common use cases
- Include troubleshooting section
- Provide FAQ section
- Use clear, simple language
""",
            DocumentationType.CHANGELOG: """
Changelog Requirements:
- Follow Keep a Changelog format
- Group changes by type (Added, Changed, Fixed, etc.)
- Include version numbers and dates
- Use semantic versioning
- List breaking changes prominently
- Include links to commits or issues
""",
            DocumentationType.TUTORIAL: """
Tutorial Requirements:
- Break down into clear steps
- Include prerequisites
- Provide complete code examples
- Explain each step thoroughly
- Include troubleshooting tips
- Add "next steps" section
- Test all instructions
""",
        }

        return instructions.get(self.doc_type, "")

    def _get_section_requirements(self) -> str:
        """Get required sections based on configuration."""
        sections = []

        if self.doc_type == DocumentationType.README:
            sections.extend(
                [
                    "# Project Title",
                    "## Description",
                ]
            )

            if self.include_installation:
                sections.append("## Installation")

            if self.include_usage:
                sections.append("## Usage")

            if self.include_examples:
                sections.append("## Examples")

            if self.include_api_docs:
                sections.append("## API Documentation")

            if self.include_contributing:
                sections.append("## Contributing")

            if self.include_license:
                sections.append("## License")

        elif self.doc_type == DocumentationType.API:
            sections.extend(["# API Documentation", "## Overview", "## Authentication", "## Endpoints", "## Examples", "## Error Handling", "## Rate Limiting"])

        elif self.doc_type == DocumentationType.TECHNICAL_SPEC:
            sections.extend(["# Technical Specification", "## Overview", "## Requirements", "## Architecture", "## Implementation", "## Testing", "## Deployment"])

        elif self.doc_type == DocumentationType.USER_GUIDE:
            sections.extend(["# User Guide", "## Getting Started", "## Basic Usage", "## Advanced Features", "## Troubleshooting", "## FAQ"])

        elif self.doc_type == DocumentationType.TUTORIAL:
            sections.extend(["# Tutorial", "## Prerequisites", "## Step-by-Step Instructions", "## Examples", "## Troubleshooting", "## Next Steps"])

        if sections:
            return f"""
Required Structure:
The documentation must include these sections:

{chr(10).join(sections)}

Each section should contain substantial content relevant to its purpose.
"""

        return ""

    def _get_formatting_guidelines(self) -> str:
        """Get markdown formatting guidelines."""
        return """
Formatting Guidelines:
- Use proper markdown headers (# ## ###)
- Format code with syntax highlighting ```language
- Use bullet points for lists
- Include links in [text](url) format
- Use **bold** for emphasis and `code` for inline code
- Add blank lines between sections
- Keep line length reasonable (80-100 characters)
- Use tables for structured data when appropriate
"""

    def _get_examples(self) -> str:
        """Get examples based on documentation type."""
        examples = {
            DocumentationType.README: """
Example Structure:
```markdown
# Project Name

Brief description of what the project does.

## Installation

```bash
pip install project-name
```

## Usage

```python
import project_name

result = project_name.do_something()
print(result)
```

## License

MIT License
```
""",
            DocumentationType.API: """
Example Endpoint Documentation:
```markdown
## GET /api/users

Retrieve a list of users.

### Parameters
- `limit` (optional): Maximum number of users to return
- `offset` (optional): Number of users to skip

### Response
```json
{
  "users": [
    {"id": 1, "name": "John Doe", "email": "john@example.com"}
  ],
  "total": 1
}
```

### Example Request
```bash
curl -X GET "https://api.example.com/users?limit=10" \
     -H "Authorization: Bearer YOUR_TOKEN"
```
```
""",
        }

        return examples.get(self.doc_type, "")

    def prepare_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Prepare data for the documentation generation prompt."""
        return {
            "project_name": self.project_name,
            "project_description": self.project_description,
            "doc_type": self.doc_type.value,
            "target_audience": self.target_audience,
            "include_installation": self.include_installation,
            "include_usage": self.include_usage,
            "include_examples": self.include_examples,
            "include_api_docs": self.include_api_docs,
            "include_contributing": self.include_contributing,
            "include_license": self.include_license,
            **kwargs,
        }

    @property
    def validator_class(self) -> type:
        """Return the validator class for this task."""
        return DocumentationValidator

    def get_validator(self) -> BaseValidator:
        """Get the configured validator instance."""
        return self._validator


class APIDocumentationTask(DocumentationTask):
    """Specialized task for generating API documentation."""

    def __init__(self, **kwargs: Any):
        kwargs.setdefault("doc_type", DocumentationType.API)
        kwargs.setdefault("include_api_docs", True)
        kwargs.setdefault("require_code_examples", True)
        super().__init__(**kwargs)


class ReadmeTask(DocumentationTask):
    """Specialized task for generating README files."""

    def __init__(self, **kwargs: Any):
        kwargs.setdefault("doc_type", DocumentationType.README)
        kwargs.setdefault("include_installation", True)
        kwargs.setdefault("include_usage", True)
        kwargs.setdefault("include_examples", True)
        kwargs.setdefault("include_license", True)
        super().__init__(**kwargs)


class TechnicalSpecTask(DocumentationTask):
    """Specialized task for generating technical specifications."""

    def __init__(self, **kwargs: Any):
        kwargs.setdefault("doc_type", DocumentationType.TECHNICAL_SPEC)
        kwargs.setdefault("min_sections", 5)
        kwargs.setdefault("require_code_examples", False)
        super().__init__(**kwargs)


class UserGuideTask(DocumentationTask):
    """Specialized task for generating user guides."""

    def __init__(self, **kwargs: Any):
        kwargs.setdefault("doc_type", DocumentationType.USER_GUIDE)
        kwargs.setdefault("target_audience", "end users")
        kwargs.setdefault("include_examples", True)
        super().__init__(**kwargs)


class TutorialTask(DocumentationTask):
    """Specialized task for generating tutorials."""

    def __init__(self, **kwargs: Any):
        kwargs.setdefault("doc_type", DocumentationType.TUTORIAL)
        kwargs.setdefault("require_code_examples", True)
        kwargs.setdefault("min_sections", 4)
        super().__init__(**kwargs)


class ChangelogTask(DocumentationTask):
    """Specialized task for generating changelogs."""

    def __init__(self, **kwargs: Any):
        kwargs.setdefault("doc_type", DocumentationType.CHANGELOG)
        kwargs.setdefault("require_code_examples", False)
        kwargs.setdefault("min_sections", 2)
        super().__init__(**kwargs)
