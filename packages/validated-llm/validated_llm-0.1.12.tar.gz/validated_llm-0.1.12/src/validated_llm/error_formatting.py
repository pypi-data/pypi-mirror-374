"""Enhanced error message formatting for better developer experience."""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class ErrorCategory(Enum):
    """Categories of validation errors for better organization."""

    SYNTAX = "syntax"
    MISSING_REQUIRED = "missing_required"
    TYPE_MISMATCH = "type_mismatch"
    CONSTRAINT_VIOLATION = "constraint_violation"
    FORMAT_ERROR = "format_error"
    EMPTY_OUTPUT = "empty_output"
    STRUCTURE_ERROR = "structure_error"
    VALUE_ERROR = "value_error"


class ErrorSeverity(Enum):
    """Severity levels for validation errors."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ErrorLocation:
    """Location information for validation errors."""

    line: Optional[int] = None
    column: Optional[int] = None
    position: Optional[int] = None
    path: Optional[str] = None  # JSON path, XML XPath, etc.

    def __str__(self) -> str:
        parts = []
        if self.line is not None:
            parts.append(f"line {self.line}")
        if self.column is not None:
            parts.append(f"column {self.column}")
        if self.path:
            parts.append(f"path '{self.path}'")
        return " at " + ", ".join(parts) if parts else ""


@dataclass
class EnhancedValidationError:
    """Enhanced validation error with rich context and suggestions."""

    category: ErrorCategory
    message: str
    severity: ErrorSeverity = ErrorSeverity.ERROR
    location: Optional[ErrorLocation] = None
    context: Optional[str] = None  # surrounding text/code
    expected: Optional[str] = None
    actual: Optional[str] = None
    suggestions: Optional[List[str]] = None
    examples: Optional[List[str]] = None
    documentation_url: Optional[str] = None
    raw_error: Optional[Exception] = None

    def __post_init__(self) -> None:
        if self.suggestions is None:
            self.suggestions = []
        if self.examples is None:
            self.examples = []


class ErrorFormatter:
    """Formats enhanced validation errors into human-readable messages."""

    @staticmethod
    def format_error(error: EnhancedValidationError, include_context: bool = True, max_width: int = 80) -> str:
        """
        Format an enhanced validation error into a human-readable message.

        Args:
            error: The enhanced validation error to format
            include_context: Whether to include context and examples
            max_width: Maximum line width for formatting

        Returns:
            Formatted error message
        """
        lines = []

        # Main error message with location
        severity_symbol = {ErrorSeverity.ERROR: "❌", ErrorSeverity.WARNING: "⚠️", ErrorSeverity.INFO: "ℹ️"}.get(error.severity, "❌")

        location_str = str(error.location) if error.location else ""
        main_line = f"{severity_symbol} {error.message}{location_str}"
        lines.append(main_line)

        # Context section
        if include_context and error.context:
            lines.append("")
            lines.append("📍 Context:")
            context_lines = error.context.strip().split("\n")
            for line in context_lines:
                lines.append(f"   {line}")

        # Expected vs Actual
        if error.expected or error.actual:
            lines.append("")
            if error.expected:
                lines.append(f"✅ Expected: {error.expected}")
            if error.actual:
                lines.append(f"🔍 Actual:   {error.actual}")

        # Suggestions
        if include_context and error.suggestions:
            lines.append("")
            lines.append("💡 Suggestions:")
            for i, suggestion in enumerate(error.suggestions, 1):
                lines.append(f"   {i}. {suggestion}")

        # Examples
        if include_context and error.examples:
            lines.append("")
            lines.append("📝 Valid Examples:")
            for example in error.examples[:3]:  # Limit to 3 examples
                lines.append(f"   • {example}")

        # Documentation link
        if include_context and error.documentation_url:
            lines.append("")
            lines.append(f"📚 Documentation: {error.documentation_url}")

        # Wrap long lines if needed
        if max_width > 0:
            wrapped_lines = []
            for line in lines:
                if len(line) <= max_width:
                    wrapped_lines.append(line)
                else:
                    # Simple word wrapping
                    wrapped_lines.extend(ErrorFormatter._wrap_line(line, max_width))
            lines = wrapped_lines

        return "\n".join(lines)

    @staticmethod
    def _wrap_line(line: str, max_width: int) -> List[str]:
        """Simple word wrapping for long lines."""
        if len(line) <= max_width:
            return [line]

        # Preserve indentation
        indent = len(line) - len(line.lstrip())
        indent_str = line[:indent]
        content = line[indent:]

        words = content.split()
        wrapped_lines = []
        current_line = indent_str

        for word in words:
            if len(current_line) + len(word) + 1 <= max_width:
                if current_line.strip():
                    current_line += " " + word
                else:
                    current_line = indent_str + word
            else:
                if current_line.strip():
                    wrapped_lines.append(current_line)
                current_line = indent_str + "  " + word  # Extra indent for continuation

        if current_line.strip():
            wrapped_lines.append(current_line)

        return wrapped_lines

    @staticmethod
    def format_multiple_errors(errors: List[EnhancedValidationError], max_errors: int = 5) -> str:
        """Format multiple errors with summary."""
        if not errors:
            return "No errors found."

        if len(errors) == 1:
            return ErrorFormatter.format_error(errors[0])

        lines = [f"Found {len(errors)} validation error{'s' if len(errors) > 1 else ''}:\n"]

        # Show first few errors in detail
        shown_errors = errors[:max_errors]
        for i, error in enumerate(shown_errors, 1):
            lines.append(f"Error {i}:")
            lines.append(ErrorFormatter.format_error(error, include_context=True))
            if i < len(shown_errors):
                lines.append("")

        # Summary for remaining errors
        if len(errors) > max_errors:
            remaining = len(errors) - max_errors
            lines.append(f"\n... and {remaining} more error{'s' if remaining > 1 else ''}")

            # Category summary
            category_counts: Dict[ErrorCategory, int] = {}
            for error in errors[max_errors:]:
                category_counts[error.category] = category_counts.get(error.category, 0) + 1

            if category_counts:
                lines.append("Error categories:")
                for category, count in sorted(category_counts.items(), key=lambda x: x[0].value):
                    lines.append(f"  • {category.value}: {count}")

        return "\n".join(lines)


class ContextExtractor:
    """Extracts context around error locations for better error messages."""

    @staticmethod
    def extract_text_context(text: str, position: int, window: int = 30) -> str:
        """
        Extract text context around an error position.

        Args:
            text: The full text
            position: Error position (character index)
            window: Number of characters to show on each side

        Returns:
            Context string with error position marked
        """
        if not text or position < 0:
            return ""

        # Calculate context bounds
        start = max(0, position - window)
        end = min(len(text), position + window)

        # Extract context
        context = text[start:end]

        # Find the relative position in context
        relative_pos = position - start
        if relative_pos < len(context):
            # Add pointer to error position
            context_lines = context.split("\n")
            if len(context_lines) == 1:
                # Single line - add pointer below
                pointer = " " * relative_pos + "^"
                return f"{context}\n{pointer}"
            else:
                # Multi-line - find which line contains the error
                line_start = 0
                for i, line in enumerate(context_lines):
                    line_end = line_start + len(line)
                    if line_start <= relative_pos <= line_end:
                        # Mark this line
                        pointer = " " * (relative_pos - line_start) + "^"
                        context_lines.insert(i + 1, pointer)
                        break
                    line_start = line_end + 1  # +1 for newline

                return "\n".join(context_lines)

        return context

    @staticmethod
    def extract_line_context(text: str, line_number: int, context_lines: int = 2) -> str:
        """
        Extract context around a specific line number.

        Args:
            text: The full text
            line_number: Line number (1-based)
            context_lines: Number of lines to show before and after

        Returns:
            Context with line numbers
        """
        lines = text.split("\n")
        if line_number < 1 or line_number > len(lines):
            return ""

        # Calculate range (convert to 0-based indexing)
        error_line_idx = line_number - 1
        start_idx = max(0, error_line_idx - context_lines)
        end_idx = min(len(lines), error_line_idx + context_lines + 1)

        # Format with line numbers
        context_lines_formatted = []
        for i in range(start_idx, end_idx):
            line_num = i + 1
            marker = ">>> " if i == error_line_idx else "    "
            context_lines_formatted.append(f"{marker}{line_num:3}: {lines[i]}")

        return "\n".join(context_lines_formatted)

    @staticmethod
    def extract_json_path_context(data: Any, json_path: str) -> str:
        """
        Extract context for a JSON path error.

        Args:
            data: The JSON data structure
            json_path: JSON path (e.g., "$.users[0].email")

        Returns:
            Context showing the problematic part of the JSON
        """
        try:
            import json

            # Try to navigate to parent path
            path_parts = json_path.replace("$", "").strip(".").split(".")
            current = data

            for part in path_parts[:-1]:
                if "[" in part and "]" in part:
                    # Array access
                    key, idx_str = part.split("[")
                    idx = int(idx_str.rstrip("]"))
                    if key:
                        current = current[key]
                    current = current[idx]
                else:
                    current = current[part]

            # Show the context at this level
            if isinstance(current, dict):
                relevant_keys = list(current.keys())[:5]  # Show first 5 keys
                return f"Available keys: {relevant_keys}"
            elif isinstance(current, list):
                return f"Array with {len(current)} items"
            else:
                return f"Value: {json.dumps(current, indent=2)[:200]}..."

        except Exception:
            return f"Unable to extract context for path: {json_path}"


def create_enhanced_error(
    category: ErrorCategory,
    message: str,
    text: Optional[str] = None,
    position: Optional[int] = None,
    line: Optional[int] = None,
    column: Optional[int] = None,
    path: Optional[str] = None,
    expected: Optional[str] = None,
    actual: Optional[str] = None,
    suggestions: Optional[List[str]] = None,
    examples: Optional[List[str]] = None,
    documentation_url: Optional[str] = None,
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    raw_error: Optional[Exception] = None,
) -> EnhancedValidationError:
    """
    Convenience function to create enhanced validation errors with automatic context extraction.

    Args:
        category: Error category
        message: Main error message
        text: Source text (for context extraction)
        position: Character position in text
        line: Line number (1-based)
        column: Column number (1-based)
        path: JSON path, XPath, etc.
        expected: Expected value/format
        actual: Actual value/format
        suggestions: List of suggestions to fix the error
        examples: List of valid examples
        documentation_url: Link to relevant documentation
        severity: Error severity level
        raw_error: Original exception if any

    Returns:
        Enhanced validation error with context
    """
    # Create location
    location = None
    if any([line, column, position, path]):
        location = ErrorLocation(line=line, column=column, position=position, path=path)

    # Extract context if text and position/line provided
    context = None
    if text:
        if position is not None:
            context = ContextExtractor.extract_text_context(text, position)
        elif line is not None:
            context = ContextExtractor.extract_line_context(text, line)

    return EnhancedValidationError(
        category=category,
        message=message,
        severity=severity,
        location=location,
        context=context,
        expected=expected,
        actual=actual,
        suggestions=suggestions or [],
        examples=examples or [],
        documentation_url=documentation_url,
        raw_error=raw_error,
    )
