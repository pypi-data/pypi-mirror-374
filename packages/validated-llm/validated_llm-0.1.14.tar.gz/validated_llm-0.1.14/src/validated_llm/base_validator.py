"""
Base validation classes and utilities for the LLM validation system.
"""

import inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional


@dataclass
class ValidationResult:
    """Standardized validation result containing success status and error details."""

    is_valid: bool
    errors: List[str]
    warnings: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if self.warnings is None:
            self.warnings = []
        if self.metadata is None:
            self.metadata = {}

    def add_error(self, error: str) -> None:
        """Add an error to the validation result."""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str) -> None:
        """Add a warning to the validation result."""
        if self.warnings is not None:
            self.warnings.append(warning)

    def has_errors(self) -> bool:
        """Check if there are any validation errors."""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Check if there are any validation warnings."""
        return self.warnings is not None and len(self.warnings) > 0

    def get_feedback_text(self) -> str:
        """Generate formatted feedback text for LLM prompt."""
        feedback_parts = []

        if self.has_errors():
            feedback_parts.append("VALIDATION ERRORS:")
            for i, error in enumerate(self.errors, 1):
                feedback_parts.append(f"  {i}. {error}")

        if self.has_warnings() and self.warnings is not None:
            feedback_parts.append("\\nWARNINGS:")
            for i, warning in enumerate(self.warnings, 1):
                feedback_parts.append(f"  {i}. {warning}")

        return "\\n".join(feedback_parts) if feedback_parts else ""


class BaseValidator(ABC):
    """
    Abstract base class for all validators used in the LLM validation loop.

    Validators should implement the validate method to check LLM output
    and return a ValidationResult with detailed feedback.
    """

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description

    @abstractmethod
    def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate the LLM output and return detailed results.

        Args:
            output: The raw output from the LLM
            context: Optional context information for validation

        Returns:
            ValidationResult with validation status and detailed feedback
        """

    def get_source_code(self) -> str:
        """
        Get the source code of the validate method to include in LLM prompts.
        This allows the LLM to see exactly what validation criteria it needs to meet.
        """
        try:
            return inspect.getsource(self.validate)
        except OSError:
            # Fallback for dynamically created methods
            return f"Validator: {self.name}\\nDescription: {self.description}"

    def get_validation_instructions(self) -> str:
        """
        Generate clear instructions for the LLM about validation requirements.
        Override this method to provide specific guidance for each validator.
        """
        return f"""
VALIDATION REQUIREMENTS:
{self.description}

Your output will be validated using this function:
```python
{self.get_source_code()}
```

Please ensure your response satisfies all the validation criteria above.
"""


class FunctionValidator(BaseValidator):
    """
    Wrapper to use standalone validation functions with the BaseValidator interface.
    This allows existing validation functions to be used in the LLM validation loop.
    """

    def __init__(self, validation_func: Callable, name: Optional[str] = None, description: str = ""):
        self.validation_func = validation_func
        func_name = name or getattr(validation_func, "__name__", "anonymous_validator")
        # Ensure func_name is always a string
        if not isinstance(func_name, str):
            func_name = "anonymous_validator"
        super().__init__(func_name, description)

    def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Call the wrapped validation function."""
        result = self.validation_func(output, context)
        if not isinstance(result, ValidationResult):
            raise TypeError("Validation function must return ValidationResult")
        return result

    def get_source_code(self) -> str:
        """Get source code of the wrapped function."""
        try:
            return inspect.getsource(self.validation_func)
        except OSError:
            return f"Function: {self.name}\\nDescription: {self.description}"
