"""
Enhanced validation system with detailed error messages and fix suggestions.

This module provides improved ValidationResult with actionable feedback,
detailed context, and automatic fix suggestions for common validation failures.
"""

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class ErrorSeverity(Enum):
    """Severity levels for validation errors."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ErrorCategory(Enum):
    """Categories of validation errors for better organization."""

    SYNTAX = "syntax"  # JSON parsing, XML syntax, etc.
    SCHEMA = "schema"  # Schema violations, missing fields
    FORMAT = "format"  # Date format, email format, etc.
    RANGE = "range"  # Value out of bounds
    LOGIC = "logic"  # Business logic violations
    STRUCTURE = "structure"  # Incorrect data structure
    CONTENT = "content"  # Content-related issues


@dataclass
class ValidationError:
    """Enhanced validation error with detailed context and suggestions."""

    message: str
    category: ErrorCategory
    severity: ErrorSeverity = ErrorSeverity.HIGH
    location: Optional[str] = None
    suggestion: Optional[str] = None
    example: Optional[str] = None
    code: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    fix_actions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "location": self.location,
            "suggestion": self.suggestion,
            "example": self.example,
            "code": self.code,
            "context": self.context,
            "fix_actions": self.fix_actions,
        }

    def format_for_llm(self) -> str:
        """Format error for LLM feedback with actionable guidance."""
        parts = [f"❌ {self.message}"]

        if self.location:
            parts.append(f"📍 Location: {self.location}")

        if self.suggestion:
            parts.append(f"💡 Suggestion: {self.suggestion}")

        if self.example:
            parts.append(f"📝 Example: {self.example}")

        if self.fix_actions:
            parts.append("🔧 Fix actions:")
            for action in self.fix_actions:
                parts.append(f"   • {action}")

        return "\n".join(parts)

    def format_for_human(self) -> str:
        """Format error for human-readable output."""
        severity_icons = {ErrorSeverity.CRITICAL: "🚨", ErrorSeverity.HIGH: "⚠️", ErrorSeverity.MEDIUM: "⚡", ErrorSeverity.LOW: "ℹ️", ErrorSeverity.INFO: "💡"}

        icon = severity_icons.get(self.severity, "❌")
        header = f"{icon} {self.category.value.upper()}: {self.message}"

        details = []
        if self.location:
            details.append(f"Location: {self.location}")
        if self.suggestion:
            details.append(f"Suggestion: {self.suggestion}")
        if self.example:
            details.append(f"Example: {self.example}")

        result = header
        if details:
            result += "\n  " + "\n  ".join(details)

        return result


@dataclass
class ValidationWarning:
    """Enhanced validation warning with context."""

    message: str
    category: ErrorCategory = ErrorCategory.CONTENT
    suggestion: Optional[str] = None
    location: Optional[str] = None

    def format_for_llm(self) -> str:
        """Format warning for LLM feedback."""
        parts = [f"⚠️ {self.message}"]

        if self.location:
            parts.append(f"📍 Location: {self.location}")

        if self.suggestion:
            parts.append(f"💡 Suggestion: {self.suggestion}")

        return "\n".join(parts)


@dataclass
class EnhancedValidationResult:
    """Enhanced validation result with detailed errors and suggestions."""

    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationWarning] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    performance_stats: Optional[Dict[str, Any]] = None

    def add_error(
        self,
        message: str,
        category: ErrorCategory,
        severity: ErrorSeverity = ErrorSeverity.HIGH,
        location: Optional[str] = None,
        suggestion: Optional[str] = None,
        example: Optional[str] = None,
        fix_actions: Optional[List[str]] = None,
    ) -> None:
        """Add an enhanced error to the validation result."""
        error = ValidationError(message=message, category=category, severity=severity, location=location, suggestion=suggestion, example=example, fix_actions=fix_actions or [])
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, message: str, category: ErrorCategory = ErrorCategory.CONTENT, suggestion: Optional[str] = None, location: Optional[str] = None) -> None:
        """Add a warning to the validation result."""
        warning = ValidationWarning(message=message, category=category, suggestion=suggestion, location=location)
        self.warnings.append(warning)

    def has_errors(self) -> bool:
        """Check if there are any validation errors."""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Check if there are any validation warnings."""
        return len(self.warnings) > 0

    def get_errors_by_category(self, category: ErrorCategory) -> List[ValidationError]:
        """Get errors filtered by category."""
        return [error for error in self.errors if error.category == category]

    def get_errors_by_severity(self, severity: ErrorSeverity) -> List[ValidationError]:
        """Get errors filtered by severity."""
        return [error for error in self.errors if error.severity == severity]

    def get_feedback_text(self) -> str:
        """Generate enhanced feedback text for LLM prompt."""
        if not self.has_errors() and not self.has_warnings():
            return ""

        feedback_parts = []

        if self.has_errors():
            # Group errors by severity
            critical_errors = self.get_errors_by_severity(ErrorSeverity.CRITICAL)
            high_errors = self.get_errors_by_severity(ErrorSeverity.HIGH)
            other_errors = [e for e in self.errors if e.severity not in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]]

            feedback_parts.append("🚨 VALIDATION ERRORS FOUND:")
            feedback_parts.append("")

            # Show critical errors first
            if critical_errors:
                feedback_parts.append("🔴 CRITICAL ISSUES (Fix these first):")
                for i, error in enumerate(critical_errors, 1):
                    feedback_parts.append(f"{i}. {error.format_for_llm()}")
                feedback_parts.append("")

            # Show high priority errors
            if high_errors:
                feedback_parts.append("🟠 HIGH PRIORITY ISSUES:")
                for i, error in enumerate(high_errors, 1):
                    feedback_parts.append(f"{i}. {error.format_for_llm()}")
                feedback_parts.append("")

            # Show other errors
            if other_errors:
                feedback_parts.append("🟡 OTHER ISSUES:")
                for i, error in enumerate(other_errors, 1):
                    feedback_parts.append(f"{i}. {error.format_for_llm()}")
                feedback_parts.append("")

        if self.has_warnings():
            feedback_parts.append("⚠️ WARNINGS:")
            for i, warning in enumerate(self.warnings, 1):
                feedback_parts.append(f"{i}. {warning.format_for_llm()}")
            feedback_parts.append("")

        # Add summary and guidance
        if self.has_errors():
            error_count = len(self.errors)
            critical_count = len(self.get_errors_by_severity(ErrorSeverity.CRITICAL))

            feedback_parts.append(f"📊 SUMMARY: {error_count} error(s) found")
            if critical_count > 0:
                feedback_parts.append(f"⚠️ Focus on fixing {critical_count} critical issue(s) first")

            feedback_parts.append("")
            feedback_parts.append("💡 NEXT STEPS:")
            feedback_parts.append("1. Review the specific errors and suggestions above")
            feedback_parts.append("2. Make the recommended changes to your output")
            feedback_parts.append("3. Ensure you follow the exact format requirements")
            feedback_parts.append("4. Test your changes against the validation criteria")

        return "\n".join(feedback_parts)

    def get_human_readable_summary(self) -> str:
        """Get a human-readable summary of validation results."""
        if self.is_valid:
            summary = "✅ Validation passed successfully"
            if self.has_warnings():
                summary += f" ({len(self.warnings)} warning(s))"
            return summary

        parts = []
        error_count = len(self.errors)
        warning_count = len(self.warnings)

        # Error summary by severity
        critical = len(self.get_errors_by_severity(ErrorSeverity.CRITICAL))
        high = len(self.get_errors_by_severity(ErrorSeverity.HIGH))
        medium = len(self.get_errors_by_severity(ErrorSeverity.MEDIUM))

        parts.append(f"❌ Validation failed: {error_count} error(s)")

        severity_parts = []
        if critical > 0:
            severity_parts.append(f"{critical} critical")
        if high > 0:
            severity_parts.append(f"{high} high")
        if medium > 0:
            severity_parts.append(f"{medium} medium")

        if severity_parts:
            parts.append(f"   Severity breakdown: {', '.join(severity_parts)}")

        if warning_count > 0:
            parts.append(f"   Plus {warning_count} warning(s)")

        return "\n".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "is_valid": self.is_valid,
            "errors": [error.to_dict() for error in self.errors],
            "warnings": [{"message": w.message, "category": w.category.value, "suggestion": w.suggestion, "location": w.location} for w in self.warnings],
            "metadata": self.metadata,
            "performance_stats": self.performance_stats,
        }


class ErrorMessageEnhancer:
    """Utility class for enhancing error messages with suggestions and context."""

    @staticmethod
    def enhance_json_error(original_error: str, attempted_json: str) -> ValidationError:
        """Enhance JSON parsing errors with specific suggestions."""
        error_msg = original_error.lower()

        # Common JSON error patterns
        if "trailing comma" in error_msg or "extra comma" in error_msg:
            return ValidationError(
                message="Invalid JSON: Trailing comma detected",
                category=ErrorCategory.SYNTAX,
                severity=ErrorSeverity.HIGH,
                suggestion="Remove the extra comma before closing brackets/braces",
                example='{"name": "John", "age": 30} ✅ (not {"name": "John", "age": 30,} ❌)',
                fix_actions=["Find the trailing comma in your JSON", "Remove the comma before the closing ] or }", "Ensure commas only separate items, not end them"],
            )

        elif "unterminated string" in error_msg or "unclosed string" in error_msg:
            return ValidationError(
                message="Invalid JSON: Unterminated string literal",
                category=ErrorCategory.SYNTAX,
                severity=ErrorSeverity.CRITICAL,
                suggestion="Add missing closing quote for string values",
                example='"name": "John Doe" ✅ (not "name": "John Doe ❌)',
                fix_actions=["Find the string missing its closing quote", 'Add the missing " character', "Ensure all string values are properly quoted"],
            )

        elif "invalid character" in error_msg:
            return ValidationError(
                message="Invalid JSON: Unexpected character in JSON",
                category=ErrorCategory.SYNTAX,
                severity=ErrorSeverity.HIGH,
                suggestion="Check for unescaped special characters or invalid syntax",
                example='Use "text": "It\'s working" or "text": "It\\"s working"',
                fix_actions=["Look for unescaped quotes or special characters", "Escape special characters with backslash (\\)", "Ensure proper JSON structure with {}, [], and quotes"],
            )

        else:
            return ValidationError(
                message=f"Invalid JSON: {original_error}",
                category=ErrorCategory.SYNTAX,
                severity=ErrorSeverity.HIGH,
                suggestion="Check JSON syntax and structure",
                example='Valid JSON: {"key": "value", "number": 123, "array": [1, 2, 3]}',
                fix_actions=["Validate your JSON syntax", "Ensure all strings are properly quoted", "Check for balanced brackets and braces", "Remove any trailing commas"],
            )

    @staticmethod
    def enhance_schema_error(field_path: str, schema_error: str, expected_type: Optional[str] = None) -> ValidationError:
        """Enhance JSON schema validation errors with specific guidance."""
        if "required" in schema_error.lower():
            missing_field = field_path.split(" -> ")[-1] if " -> " in field_path else field_path
            return ValidationError(
                message=f"Missing required field: {missing_field}",
                category=ErrorCategory.SCHEMA,
                severity=ErrorSeverity.CRITICAL,
                location=field_path,
                suggestion=f"Add the required '{missing_field}' field to your JSON",
                example=f'"{missing_field}": "your_value_here"',
                fix_actions=[f"Add the '{missing_field}' field to your JSON object", "Ensure the field has an appropriate value", "Check the schema requirements for field type and format"],
            )

        elif "type" in schema_error.lower() and expected_type:
            return ValidationError(
                message=f"Incorrect type for field '{field_path}': expected {expected_type}",
                category=ErrorCategory.SCHEMA,
                severity=ErrorSeverity.HIGH,
                location=field_path,
                suggestion=f"Change the value to be of type {expected_type}",
                example=f'"{field_path}": {ErrorMessageEnhancer._get_type_example(expected_type)}',
                fix_actions=[f"Convert the value to {expected_type} type", "Remove quotes for numbers and booleans", "Add quotes for string values", "Use [] for arrays and {} for objects"],
            )

        else:
            return ValidationError(
                message=f"Schema violation at {field_path}: {schema_error}",
                category=ErrorCategory.SCHEMA,
                severity=ErrorSeverity.HIGH,
                location=field_path,
                suggestion="Review the schema requirements for this field",
                fix_actions=["Check the expected data type and format", "Ensure the value meets schema constraints", "Verify required fields are present"],
            )

    @staticmethod
    def enhance_range_error(value: Any, min_val: Any = None, max_val: Any = None) -> ValidationError:
        """Enhance range validation errors with specific bounds information."""
        if min_val is not None and max_val is not None:
            message = f"Value {value} is out of range: must be between {min_val} and {max_val}"
            suggestion = f"Use a value between {min_val} and {max_val} (inclusive)"
        elif min_val is not None:
            message = f"Value {value} is too small: must be at least {min_val}"
            suggestion = f"Use a value >= {min_val}"
        elif max_val is not None:
            message = f"Value {value} is too large: must be at most {max_val}"
            suggestion = f"Use a value <= {max_val}"
        else:
            message = f"Value {value} is out of acceptable range"
            suggestion = "Check the acceptable value range for this field"

        return ValidationError(
            message=message,
            category=ErrorCategory.RANGE,
            severity=ErrorSeverity.MEDIUM,
            suggestion=suggestion,
            fix_actions=["Check the minimum and maximum allowed values", "Adjust your value to fall within the acceptable range", "Consider if the constraint makes sense for your use case"],
        )

    @staticmethod
    def _get_type_example(type_name: str) -> str:
        """Get an example value for a given type."""
        examples = {"string": '"example text"', "integer": "42", "number": "3.14", "boolean": "true", "array": "[1, 2, 3]", "object": '{"key": "value"}'}
        return examples.get(type_name.lower(), '"value"')
