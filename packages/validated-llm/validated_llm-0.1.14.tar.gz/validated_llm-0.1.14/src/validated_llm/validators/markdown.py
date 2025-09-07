"""
Markdown validation for LLM outputs.
"""

import re
from typing import Any, Dict, List, Optional, Set, Tuple

from validated_llm.base_validator import BaseValidator, ValidationResult


class MarkdownValidator(BaseValidator):
    """
    Validates Markdown syntax and structure in LLM output.

    Features:
    - Syntax validation for common Markdown elements
    - Structure requirements (headings, lists, code blocks, etc.)
    - Link and image validation
    - Table structure validation
    - Custom rules support
    """

    def __init__(
        self,
        name: str = "MarkdownValidator",
        description: str = "Validates Markdown syntax and structure",
        require_headings: bool = False,
        min_headings: int = 0,
        max_heading_level: int = 6,
        require_lists: bool = False,
        require_code_blocks: bool = False,
        require_links: bool = False,
        require_images: bool = False,
        require_tables: bool = False,
        allow_html: bool = True,
        validate_link_urls: bool = False,
        max_line_length: Optional[int] = None,
        required_sections: Optional[List[str]] = None,
    ):
        """
        Initialize the Markdown validator.

        Args:
            name: Validator name
            description: Validator description
            require_headings: Whether document must have headings
            min_headings: Minimum number of headings required
            max_heading_level: Maximum allowed heading level (1-6)
            require_lists: Whether document must have lists
            require_code_blocks: Whether document must have code blocks
            require_links: Whether document must have links
            require_images: Whether document must have images
            require_tables: Whether document must have tables
            allow_html: Whether to allow inline HTML
            validate_link_urls: Whether to validate that links are proper URLs
            max_line_length: Maximum allowed line length
            required_sections: List of required section headings
        """
        super().__init__(name, description)
        self.require_headings = require_headings
        self.min_headings = min_headings
        self.max_heading_level = max_heading_level
        self.require_lists = require_lists
        self.require_code_blocks = require_code_blocks
        self.require_links = require_links
        self.require_images = require_images
        self.require_tables = require_tables
        self.allow_html = allow_html
        self.validate_link_urls = validate_link_urls
        self.max_line_length = max_line_length
        self.required_sections = set(required_sections or [])

        # Markdown patterns
        self.patterns = {
            "heading": re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE),
            "bullet_list": re.compile(r"^[\*\-\+]\s+.+$", re.MULTILINE),
            "ordered_list": re.compile(r"^\d+\.\s+.+$", re.MULTILINE),
            "code_block": re.compile(r"^```[\s\S]*?```$", re.MULTILINE),
            "inline_code": re.compile(r"`[^`]+`"),
            "link": re.compile(r"\[([^\]]+)\]\(([^\)]+)\)"),
            "image": re.compile(r"!\[([^\]]*)\]\(([^\)]+)\)"),
            "table": re.compile(r"^\|.+\|$", re.MULTILINE),
            "html": re.compile(r"<[^>]+>"),
            "bold": re.compile(r"\*\*[^*]+\*\*|__[^_]+__"),
            "italic": re.compile(r"\*[^*]+\*|_[^_]+_"),
            "blockquote": re.compile(r"^>\s+.+$", re.MULTILINE),
            "horizontal_rule": re.compile(r"^[\*\-_]{3,}$", re.MULTILINE),
        }

    def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate Markdown content.

        Args:
            output: The LLM output to validate
            context: Optional context (not used)

        Returns:
            ValidationResult with validation status and details
        """
        errors: list[str] = []
        warnings: list[str] = []
        metadata: dict[str, Any] = {
            "headings": [],
            "heading_levels": [],
            "lists": {"bullet": 0, "ordered": 0},
            "code_blocks": 0,
            "inline_code": 0,
            "links": [],
            "images": [],
            "tables": 0,
            "sections_found": set(),
        }

        if not output:
            errors.append("Output is empty")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings, metadata=metadata)

        lines = output.split("\n")

        # Check line length if specified
        if self.max_line_length:
            for i, line in enumerate(lines, 1):
                if len(line) > self.max_line_length:
                    warnings.append(f"Line {i} exceeds maximum length of {self.max_line_length} characters")

        # Extract and validate headings
        headings = self.patterns["heading"].findall(output)
        for level_str, heading_text in headings:
            level = len(level_str)
            metadata["headings"].append(heading_text.strip())
            metadata["heading_levels"].append(level)

            if level > self.max_heading_level:
                errors.append(f"Heading level {level} exceeds maximum allowed level {self.max_heading_level}: '{heading_text}'")

            # Check for required sections
            if self.required_sections:
                heading_lower = heading_text.strip().lower()
                for required in self.required_sections:
                    if required.lower() in heading_lower:
                        metadata["sections_found"].add(required)

        # Check heading requirements
        if self.require_headings and len(headings) == 0:
            errors.append("Document must contain at least one heading")

        if len(headings) < self.min_headings:
            errors.append(f"Document must contain at least {self.min_headings} heading(s), found {len(headings)}")

        # Check for required sections
        if self.required_sections:
            missing_sections = self.required_sections - metadata["sections_found"]
            if missing_sections:
                errors.append(f"Missing required sections: {', '.join(sorted(missing_sections))}")

        # Extract and count lists
        bullet_lists = self.patterns["bullet_list"].findall(output)
        ordered_lists = self.patterns["ordered_list"].findall(output)
        metadata["lists"]["bullet"] = len(bullet_lists)
        metadata["lists"]["ordered"] = len(ordered_lists)

        if self.require_lists and (len(bullet_lists) + len(ordered_lists)) == 0:
            errors.append("Document must contain at least one list (bullet or ordered)")

        # Extract and count code blocks
        code_blocks = self.patterns["code_block"].findall(output)
        inline_code = self.patterns["inline_code"].findall(output)
        metadata["code_blocks"] = len(code_blocks)
        metadata["inline_code"] = len(inline_code)

        if self.require_code_blocks and len(code_blocks) == 0:
            errors.append("Document must contain at least one code block")

        # Validate code block syntax
        in_code_block = False
        code_block_start = 0
        for i, line in enumerate(lines, 1):
            if line.strip().startswith("```"):
                if not in_code_block:
                    in_code_block = True
                    code_block_start = i
                else:
                    in_code_block = False

        if in_code_block:
            errors.append(f"Unclosed code block starting at line {code_block_start}")

        # Extract and validate links
        links = self.patterns["link"].findall(output)
        for link_text, link_url in links:
            metadata["links"].append({"text": link_text, "url": link_url})

            if self.validate_link_urls:
                if not link_url.startswith(("http://", "https://", "/", "#", "mailto:")):
                    warnings.append(f"Link URL may be invalid: '{link_url}'")

        if self.require_links and len(links) == 0:
            errors.append("Document must contain at least one link")

        # Extract images
        images = self.patterns["image"].findall(output)
        for alt_text, image_url in images:
            metadata["images"].append({"alt": alt_text, "url": image_url})

        if self.require_images and len(images) == 0:
            errors.append("Document must contain at least one image")

        # Check for tables
        table_lines = self.patterns["table"].findall(output)
        if table_lines:
            # Basic table validation
            table_count = self._count_tables(lines)
            metadata["tables"] = table_count

        if self.require_tables and metadata["tables"] == 0:
            errors.append("Document must contain at least one table")

        # Check for HTML if not allowed
        if not self.allow_html:
            html_tags = self.patterns["html"].findall(output)
            if html_tags:
                errors.append(f"HTML tags are not allowed. Found: {', '.join(set(html_tags[:5]))}")

        # Validate list formatting
        self._validate_list_formatting(lines, errors, warnings)

        # Check for common Markdown mistakes
        self._check_common_mistakes(output, warnings)

        # Convert sets to lists for JSON serialization
        metadata["sections_found"] = list(metadata["sections_found"])

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings, metadata=metadata)

    def _count_tables(self, lines: List[str]) -> int:
        """Count the number of tables in the document."""
        table_count = 0
        in_table = False

        for line in lines:
            if self.patterns["table"].match(line):
                if not in_table:
                    # Check if next line is separator line (|----|)
                    in_table = True
            else:
                if in_table and not line.strip():
                    table_count += 1
                    in_table = False

        if in_table:
            table_count += 1

        return table_count

    def _validate_list_formatting(self, lines: List[str], errors: List[str], warnings: List[str]) -> None:
        """Validate list formatting and nesting."""
        list_stack: list[int] = []  # Track list indentation levels

        for i, line in enumerate(lines, 1):
            if not line.strip():
                continue

            # Check for list item
            bullet_match = re.match(r"^(\s*)([\*\-\+])\s+(.+)$", line)
            ordered_match = re.match(r"^(\s*)(\d+)\.\s+(.+)$", line)

            if bullet_match:
                indent, marker, content = bullet_match.groups()
            elif ordered_match:
                indent, number, content = ordered_match.groups()
                marker = "ordered"
            else:
                continue

            indent_level = len(indent)

            # Check for consistent indentation (multiples of 2 or 4)
            if indent_level % 2 != 0:
                warnings.append(f"Line {i}: Inconsistent list indentation (should be multiples of 2 or 4)")

    def _check_common_mistakes(self, output: str, warnings: List[str]) -> None:
        """Check for common Markdown formatting mistakes."""
        # Check for unescaped special characters
        unescaped_asterisks = re.findall(r"(?<!\*)\*(?!\*)", output)
        if len(unescaped_asterisks) % 2 != 0:
            warnings.append("Possible unmatched asterisk (*) for italic formatting")

        # Check for unmatched brackets
        open_brackets = output.count("[")
        close_brackets = output.count("]")
        if open_brackets != close_brackets:
            warnings.append(f"Unmatched brackets: {open_brackets} '[' vs {close_brackets} ']'")

        # Check for unmatched parentheses in link context
        link_pattern = re.compile(r"\[[^\]]+\]\([^\)]*$", re.MULTILINE)
        if link_pattern.search(output):
            warnings.append("Possible unclosed link (missing closing parenthesis)")

    def get_validation_instructions(self) -> str:
        """Get specific validation instructions for Markdown."""
        instructions = """
MARKDOWN VALIDATION REQUIREMENTS:
Your output must be valid Markdown syntax."""

        requirements = []

        if self.require_headings:
            requirements.append(f"- Include at least {self.min_headings} heading(s)")

        if self.max_heading_level < 6:
            requirements.append(f"- Use heading levels 1-{self.max_heading_level} only")

        if self.required_sections:
            requirements.append(f"- Include these sections: {', '.join(sorted(self.required_sections))}")

        if self.require_lists:
            requirements.append("- Include at least one list (bullet or ordered)")

        if self.require_code_blocks:
            requirements.append("- Include at least one code block (```code```)")

        if self.require_links:
            requirements.append("- Include at least one link ([text](url))")

        if self.require_images:
            requirements.append("- Include at least one image (![alt](url))")

        if self.require_tables:
            requirements.append("- Include at least one table")

        if not self.allow_html:
            requirements.append("- Do not use HTML tags")

        if self.max_line_length:
            requirements.append(f"- Keep lines under {self.max_line_length} characters")

        if requirements:
            instructions += "\n" + "\n".join(requirements)

        instructions += """

Markdown syntax examples:
# Heading 1
## Heading 2
### Heading 3

**Bold text** or __bold text__
*Italic text* or _italic text_

- Bullet list item
- Another item
  - Nested item

1. Ordered list
2. Second item

[Link text](https://example.com)
![Image alt text](image.jpg)

```python
# Code block
print("Hello")
```

> Blockquote

| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |

---
(Horizontal rule)
"""

        return instructions
