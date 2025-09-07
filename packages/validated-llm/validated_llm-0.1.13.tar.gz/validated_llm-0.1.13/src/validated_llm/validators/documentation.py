"""
Documentation validator for validating technical documentation completeness and quality.
"""

import re
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from ..base_validator import BaseValidator, ValidationResult
from ..error_formatting import ErrorCategory, create_enhanced_error


class DocumentationType(Enum):
    """Types of documentation for specific validation rules."""

    API = "api"
    README = "readme"
    TECHNICAL_SPEC = "technical_spec"
    USER_GUIDE = "user_guide"
    CHANGELOG = "changelog"
    TUTORIAL = "tutorial"


class DocumentationValidator(BaseValidator):
    """
    Validates technical documentation for completeness, structure, and quality.

    Supports multiple documentation types with specific validation rules for each.
    """

    def __init__(
        self,
        doc_type: DocumentationType = DocumentationType.README,
        min_sections: int = 3,
        require_code_examples: bool = False,
        require_installation_section: bool = False,
        require_usage_section: bool = True,
        require_api_documentation: bool = False,
        check_links: bool = True,
        check_spelling: bool = False,
        min_words_per_section: int = 50,
        required_sections: Optional[List[str]] = None,
        forbidden_sections: Optional[List[str]] = None,
    ):
        """
        Initialize documentation validator.

        Args:
            doc_type: Type of documentation being validated
            min_sections: Minimum number of sections required
            require_code_examples: Whether code examples are required
            require_installation_section: Whether installation section is required
            require_usage_section: Whether usage section is required
            require_api_documentation: Whether API docs are required
            check_links: Whether to validate markdown links
            check_spelling: Whether to check basic spelling (simple checks)
            min_words_per_section: Minimum words per section
            required_sections: List of required section titles
            forbidden_sections: List of forbidden section titles
        """
        self.doc_type = doc_type
        self.min_sections = min_sections
        self.require_code_examples = require_code_examples
        self.require_installation_section = require_installation_section
        self.require_usage_section = require_usage_section
        self.require_api_documentation = require_api_documentation
        self.check_links = check_links
        self.check_spelling = check_spelling
        self.min_words_per_section = min_words_per_section
        self.required_sections = required_sections if required_sections is not None else self._get_default_required_sections()
        self.forbidden_sections = forbidden_sections or []

        # Documentation type specific configurations
        self._setup_type_specific_rules()

    def _get_default_required_sections(self) -> List[str]:
        """Get default required sections based on documentation type."""
        defaults = {
            DocumentationType.API: ["Overview", "Endpoints", "Authentication", "Examples"],
            DocumentationType.README: ["Installation", "Usage", "Examples"],
            DocumentationType.TECHNICAL_SPEC: ["Overview", "Requirements", "Architecture", "Implementation"],
            DocumentationType.USER_GUIDE: ["Getting Started", "Usage", "Examples", "Troubleshooting"],
            DocumentationType.CHANGELOG: ["Unreleased", "Released"],
            DocumentationType.TUTORIAL: ["Prerequisites", "Steps", "Examples", "Next Steps"],
        }
        return defaults.get(self.doc_type, [])

    def _setup_type_specific_rules(self) -> None:
        """Setup validation rules specific to documentation type."""
        if self.doc_type == DocumentationType.API:
            self.require_code_examples = True
            self.require_api_documentation = True
        elif self.doc_type == DocumentationType.README:
            self.require_installation_section = True
            self.require_usage_section = True
        elif self.doc_type == DocumentationType.TUTORIAL:
            self.require_code_examples = True
            self.min_words_per_section = 100

    def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate documentation content.

        Args:
            output: Documentation content to validate
            context: Optional context information

        Returns:
            ValidationResult with validation details
        """
        if not output or not output.strip():
            error = create_enhanced_error(
                category=ErrorCategory.EMPTY_OUTPUT,
                message="Documentation content is empty",
                expected="Non-empty documentation with sections and content",
                suggestions=["Add documentation content with proper markdown formatting", "Include required sections for your documentation type", f"Follow {self.doc_type.value} documentation standards"],
                examples=["# Project Title\n\n## Installation\n\nSteps to install...", "# API Documentation\n\n## Overview\n\nAPI description..."],
            )
            return ValidationResult(is_valid=False, errors=[error.message], warnings=[], metadata={})

        errors: List[str] = []
        warnings: List[str] = []
        metadata: Dict[str, Any] = {}

        # Extract sections from markdown
        sections = self._extract_sections(output)
        metadata["sections_found"] = list(sections.keys())
        metadata["section_count"] = len(sections)

        # Validate section structure
        self._validate_sections(sections, output, errors, warnings, metadata)

        # Validate content quality
        self._validate_content_quality(output, sections, errors, warnings, metadata)

        # Validate links if enabled
        if self.check_links:
            self._validate_links(output, errors, warnings, metadata)

        # Validate code examples if required
        if self.require_code_examples:
            self._validate_code_examples(output, errors, warnings, metadata)

        # Basic spelling check if enabled
        if self.check_spelling:
            self._validate_spelling(output, errors, warnings, metadata)

        # Type-specific validations
        self._validate_type_specific(output, sections, errors, warnings, metadata)

        is_valid = len(errors) == 0

        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings, metadata=metadata)

    def _extract_sections(self, content: str) -> Dict[str, str]:
        """Extract markdown sections and their content."""
        sections: Dict[str, str] = {}
        current_section: Optional[str] = None
        current_content: List[str] = []

        lines = content.split("\n")

        for line in lines:
            # Check for markdown headers (# ## ### etc.)
            header_match = re.match(r"^(#{1,6})\s+(.+)$", line.strip())

            if header_match:
                # Save previous section if exists
                if current_section is not None:
                    sections[current_section] = "\n".join(current_content).strip()

                # Start new section
                title = header_match.group(2).strip()
                current_section = title
                current_content = []
            elif current_section:
                # Add line to current section content
                current_content.append(line)

        # Save last section
        if current_section:
            sections[current_section] = "\n".join(current_content).strip()

        return sections

    def _validate_sections(self, sections: Dict[str, str], content: str, errors: List[str], warnings: List[str], metadata: Dict[str, Any]) -> None:
        """Validate section structure and requirements."""
        section_titles = list(sections.keys())

        # Check minimum sections
        if len(sections) < self.min_sections:
            errors.append(f"Insufficient sections: found {len(sections)}, required {self.min_sections}")

        # Check required sections
        missing_required = []
        for required in self.required_sections:
            # Case-insensitive matching with partial matches
            found = any(required.lower() in title.lower() for title in section_titles)
            if not found:
                missing_required.append(required)

        if missing_required:
            errors.append(f"Missing required sections: {', '.join(missing_required)}")

        # Check forbidden sections
        found_forbidden = []
        for forbidden in self.forbidden_sections:
            found = any(forbidden.lower() in title.lower() for title in section_titles)
            if found:
                found_forbidden.append(forbidden)

        if found_forbidden:
            warnings.append(f"Found discouraged sections: {', '.join(found_forbidden)}")

        # Check section content length
        short_sections = []
        for title, content in sections.items():
            word_count = len(content.split())
            if word_count < self.min_words_per_section:
                short_sections.append(f"{title} ({word_count} words)")

        if short_sections:
            warnings.append(f"Sections with insufficient content: {', '.join(short_sections)}")

        metadata["missing_required_sections"] = missing_required
        metadata["forbidden_sections_found"] = found_forbidden
        metadata["short_sections"] = short_sections

    def _validate_content_quality(self, content: str, sections: Dict[str, str], errors: List[str], warnings: List[str], metadata: Dict[str, Any]) -> None:
        """Validate overall content quality."""
        # Check for table of contents
        has_toc = bool(re.search(r"(table of contents|toc)", content, re.IGNORECASE))
        metadata["has_table_of_contents"] = has_toc

        if len(sections) > 5 and not has_toc:
            warnings.append("Consider adding a table of contents for better navigation")

        # Check for proper markdown formatting
        formatting_issues = []

        # Check for unformatted code (missing backticks)
        unformatted_code = re.findall(r"(?<!`)[a-zA-Z_][a-zA-Z0-9_]*\([^)]*\)(?!`)", content)
        if len(unformatted_code) > 3:
            formatting_issues.append("Multiple function calls not formatted as code")

        # Check for proper list formatting
        improper_lists = re.findall(r"^\s*-\s*[a-z]", content, re.MULTILINE)
        if improper_lists:
            formatting_issues.append("List items should start with capital letters")

        if formatting_issues:
            warnings.extend(formatting_issues)

        metadata["formatting_issues"] = formatting_issues

    def _validate_links(self, content: str, errors: List[str], warnings: List[str], metadata: Dict[str, Any]) -> None:
        """Validate markdown links."""
        # Find all markdown links
        link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
        links = re.findall(link_pattern, content)

        metadata["links_found"] = len(links)

        broken_links = []
        for text, url in links:
            # Basic validation - check for obvious issues
            if not url.strip():
                broken_links.append(f"Empty URL for link '{text}'")
            elif url.startswith("http") and " " in url:
                broken_links.append(f"Invalid URL (contains spaces): '{url}'")
            elif url.startswith("#") and not re.search(r"^#[a-z0-9-]+$", url, re.IGNORECASE):
                broken_links.append(f"Invalid anchor link: '{url}'")

        if broken_links:
            errors.extend(broken_links)

        metadata["broken_links"] = broken_links

        # Check for reference-style links
        ref_links = re.findall(r"\[([^\]]+)\]\[([^\]]*)\]", content)
        ref_definitions = re.findall(r"^\s*\[([^\]]+)\]:\s*(.+)$", content, re.MULTILINE)

        undefined_refs = []
        for text, ref in ref_links:
            ref_key = ref if ref else text
            if not any(ref_key.lower() == defn[0].lower() for defn in ref_definitions):
                undefined_refs.append(ref_key)

        if undefined_refs:
            errors.append(f"Undefined reference links: {', '.join(undefined_refs)}")

    def _validate_code_examples(self, content: str, errors: List[str], warnings: List[str], metadata: Dict[str, Any]) -> None:
        """Validate code examples in documentation."""
        # Find code blocks
        code_blocks = re.findall(r"```(\w*)\n(.*?)\n```", content, re.DOTALL)
        inline_code = re.findall(r"`([^`]+)`", content)

        metadata["code_blocks_found"] = len(code_blocks)
        metadata["inline_code_found"] = len(inline_code)

        if self.require_code_examples and not code_blocks and len(inline_code) < 3:
            errors.append("Code examples are required but none found")

        # Validate code block languages
        missing_language = []
        for lang, code in code_blocks:
            if not lang and len(code.strip()) > 10:
                missing_language.append(code[:30] + "...")

        if missing_language:
            warnings.append(f"Code blocks missing language specification: {len(missing_language)} blocks")

        # Check for common code patterns
        has_installation_code = any("install" in code.lower() or "pip" in code.lower() or "npm" in code.lower() for _, code in code_blocks)
        has_usage_code = any(len(code.strip()) > 50 for _, code in code_blocks if code.strip())

        metadata["has_installation_code"] = has_installation_code
        metadata["has_usage_code"] = has_usage_code

        if self.require_installation_section and not has_installation_code:
            warnings.append("Installation section should include code examples")

    def _validate_spelling(self, content: str, errors: List[str], warnings: List[str], metadata: Dict[str, Any]) -> None:
        """Basic spelling validation (simple common mistakes)."""
        # Simple common spelling mistakes
        common_mistakes = {
            r"\brecieve\b": "receive",
            r"\bthier\b": "their",
            r"\boccur\b": "occur",
            r"\baccomplish\b": "accomplish",
            r"\bperform\b": "perform",
            r"\bfollwing\b": "following",
            r"\bfunctionallity\b": "functionality",
        }

        spelling_issues = []
        for mistake, correction in common_mistakes.items():
            matches = re.findall(mistake, content, re.IGNORECASE)
            if matches:
                spelling_issues.append(f"'{matches[0]}' should be '{correction}'")

        if spelling_issues:
            warnings.extend(spelling_issues[:5])  # Limit to 5 to avoid spam

        metadata["spelling_issues_found"] = len(spelling_issues)

    def _validate_type_specific(self, content: str, sections: Dict[str, str], errors: List[str], warnings: List[str], metadata: Dict[str, Any]) -> None:
        """Perform documentation type-specific validations."""
        if self.doc_type == DocumentationType.API:
            self._validate_api_documentation(content, sections, errors, warnings, metadata)
        elif self.doc_type == DocumentationType.README:
            self._validate_readme(content, sections, errors, warnings, metadata)
        elif self.doc_type == DocumentationType.CHANGELOG:
            self._validate_changelog(content, sections, errors, warnings, metadata)
        elif self.doc_type == DocumentationType.TUTORIAL:
            self._validate_tutorial(content, sections, errors, warnings, metadata)

    def _validate_api_documentation(self, content: str, sections: Dict[str, str], errors: List[str], warnings: List[str], metadata: Dict[str, Any]) -> None:
        """Validate API-specific documentation requirements."""
        # Check for HTTP methods
        http_methods = re.findall(r"\b(GET|POST|PUT|DELETE|PATCH)\b", content)
        metadata["http_methods_found"] = list(set(http_methods))

        if not http_methods:
            warnings.append("No HTTP methods found in API documentation")

        # Check for status codes
        status_codes = re.findall(r"\b(200|201|400|401|403|404|500)\b", content)
        metadata["status_codes_found"] = list(set(status_codes))

        # Check for authentication mentions
        has_auth = bool(re.search(r"(auth|token|key|bearer|basic)", content, re.IGNORECASE))
        metadata["has_authentication_docs"] = has_auth

        if not has_auth:
            warnings.append("API documentation should include authentication information")

    def _validate_readme(self, content: str, sections: Dict[str, str], errors: List[str], warnings: List[str], metadata: Dict[str, Any]) -> None:
        """Validate README-specific requirements."""
        # Check for badges
        badges = re.findall(r"!\[([^\]]*)\]\(([^)]*\.svg[^)]*)\)", content)
        metadata["badges_found"] = len(badges)

        # Check for project description in first paragraph
        first_paragraph = content.split("\n\n")[0] if "\n\n" in content else content[:200]
        if len(first_paragraph.split()) < 10:
            warnings.append("README should start with a clear project description")

        # Check for license mention
        has_license = bool(re.search(r"license", content, re.IGNORECASE))
        metadata["has_license_section"] = has_license

        if not has_license:
            warnings.append("README should include license information")

    def _validate_changelog(self, content: str, sections: Dict[str, str], errors: List[str], warnings: List[str], metadata: Dict[str, Any]) -> None:
        """Validate changelog-specific requirements."""
        # Check for version patterns
        versions = re.findall(r"\b\d+\.\d+\.\d+\b", content)
        metadata["versions_found"] = len(set(versions))

        # Check for date patterns
        dates = re.findall(r"\d{4}-\d{2}-\d{2}", content)
        metadata["dates_found"] = len(dates)

        # Check for change types
        change_types = ["Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"]
        found_types = []
        for change_type in change_types:
            if change_type.lower() in content.lower():
                found_types.append(change_type)

        metadata["change_types_found"] = found_types

        if len(found_types) < 2:
            warnings.append("Changelog should categorize changes (Added, Fixed, etc.)")

    def _validate_tutorial(self, content: str, sections: Dict[str, str], errors: List[str], warnings: List[str], metadata: Dict[str, Any]) -> None:
        """Validate tutorial-specific requirements."""
        # Check for step numbering
        steps = re.findall(r"step\s+\d+", content, re.IGNORECASE)
        metadata["numbered_steps_found"] = len(steps)

        # Check for prerequisite mentions
        has_prereqs = bool(re.search(r"prerequisite|requirement|before.*start", content, re.IGNORECASE))
        metadata["has_prerequisites"] = has_prereqs

        if not has_prereqs:
            warnings.append("Tutorial should include prerequisites or requirements")

        # Check for troubleshooting section
        has_troubleshooting = any("troubleshoot" in title.lower() or "problem" in title.lower() for title in sections.keys())
        metadata["has_troubleshooting"] = has_troubleshooting

        if not has_troubleshooting:
            warnings.append("Tutorial should include troubleshooting or common issues section")

    def get_description(self) -> str:
        """Get description of the documentation validator."""
        return f"Documentation validator for {self.doc_type.value} with {len(self.required_sections)} required sections"
