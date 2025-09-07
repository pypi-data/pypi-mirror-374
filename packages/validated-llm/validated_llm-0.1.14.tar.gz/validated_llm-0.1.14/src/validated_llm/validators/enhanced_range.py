"""
Enhanced Range validator with detailed error messages and fix suggestions.
"""

import re
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Union

from ..base_validator import BaseValidator, ValidationResult
from ..enhanced_validation import EnhancedValidationResult, ErrorCategory, ErrorMessageEnhancer, ErrorSeverity


class EnhancedRangeValidator(BaseValidator):
    """Enhanced Range validator with detailed error messages and suggestions.

    This validator provides much more helpful error messages compared to the basic
    RangeValidator, including specific guidance on acceptable ranges and examples.

    Example:
        ```python
        validator = EnhancedRangeValidator(min_value=1, max_value=100, value_type="integer")
        result = validator.validate("150")  # Out of range
        print(result.get_feedback_text())  # Detailed error with suggestions
        ```
    """

    def __init__(
        self,
        min_value: Optional[Union[int, float, Decimal]] = None,
        max_value: Optional[Union[int, float, Decimal]] = None,
        value_type: str = "number",  # "number", "integer", "decimal"
        inclusive_min: bool = True,
        inclusive_max: bool = True,
        extract_all: bool = False,
        required_count: Optional[int] = None,
    ):
        """Initialize the enhanced range validator.

        Args:
            min_value: Minimum allowed value (None for no minimum)
            max_value: Maximum allowed value (None for no maximum)
            value_type: Type of value to validate ("number", "integer", "decimal")
            inclusive_min: Whether min_value is inclusive (>=) or exclusive (>)
            inclusive_max: Whether max_value is inclusive (<=) or exclusive (<)
            extract_all: Whether to extract all values from text or treat as single value
            required_count: Exact number of values required (for extract_all mode)
        """
        super().__init__(name="EnhancedRangeValidator", description=f"Enhanced range validation for {value_type} values with detailed feedback")

        self.value_type = value_type
        self.inclusive_min = inclusive_min
        self.inclusive_max = inclusive_max
        self.extract_all = extract_all
        self.required_count = required_count

        # Convert and validate min/max values
        self.min_value: Any = self._convert_value(min_value) if min_value is not None else None
        self.max_value: Any = self._convert_value(max_value) if max_value is not None else None

        # Validate range configuration
        if self.min_value is not None and self.max_value is not None:
            try:
                if self.min_value > self.max_value:
                    raise ValueError(f"min_value ({self.min_value}) cannot be greater than max_value ({self.max_value})")
            except TypeError:
                pass  # Can't compare different types

    def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate values in output against specified ranges with enhanced error messages.

        Args:
            output: The LLM output containing values to validate
            context: Optional context (unused for range validation)

        Returns:
            ValidationResult with enhanced error messages and suggestions
        """
        enhanced_result = EnhancedValidationResult(is_valid=True)
        enhanced_result.metadata = {"value_type": self.value_type, "min_value": self.min_value, "max_value": self.max_value, "enhanced_validation": True, "values_found": [], "valid_values": [], "invalid_values": []}

        output = output.strip()
        if not output:
            enhanced_result.add_error(
                "Output is empty",
                category=ErrorCategory.CONTENT,
                severity=ErrorSeverity.CRITICAL,
                suggestion="Provide a numeric value in your response",
                example=self._get_example_value(),
                fix_actions=["Add a numeric value to your output", f"Ensure the value is of type {self.value_type}", "Check that your response is not empty"],
            )
            return self._convert_to_standard_result(enhanced_result)

        # Extract and validate values
        if self.extract_all:
            values = self._extract_all_values(output)
        else:
            values = self._extract_single_value(output)

        # Validate each extracted value
        for original_str, converted_value in values:
            enhanced_result.metadata["values_found"].append({"original": original_str, "converted": str(converted_value) if converted_value is not None else None})

            if converted_value is None:
                enhanced_result.add_error(
                    f"Could not parse '{original_str}' as {self.value_type}",
                    category=ErrorCategory.FORMAT,
                    severity=ErrorSeverity.HIGH,
                    suggestion=f"Ensure the value is a valid {self.value_type}",
                    example=self._get_example_value(),
                    fix_actions=[f"Use a valid {self.value_type} format", "Remove any non-numeric characters (except decimal point for numbers)", "Check for typos in the numeric value"],
                )
                enhanced_result.metadata["invalid_values"].append(original_str)
                continue

            # Check range constraints
            is_in_range, range_error = self._check_range(converted_value)

            if is_in_range:
                enhanced_result.metadata["valid_values"].append(str(converted_value))
            else:
                enhanced_result.errors.append(range_error)
                enhanced_result.metadata["invalid_values"].append(str(converted_value))

        # Check required count for extract_all mode
        if self.extract_all and self.required_count is not None:
            valid_count = len(enhanced_result.metadata["valid_values"])
            if valid_count != self.required_count:
                enhanced_result.add_error(
                    f"Expected exactly {self.required_count} valid values, but found {valid_count}",
                    category=ErrorCategory.CONTENT,
                    severity=ErrorSeverity.HIGH,
                    suggestion=f"Provide exactly {self.required_count} valid {self.value_type} values",
                    fix_actions=[
                        f"Add {self.required_count - valid_count} more values" if valid_count < self.required_count else f"Remove {valid_count - self.required_count} values",
                        "Ensure all values are within the acceptable range",
                        "Check that you have the correct number of values",
                    ],
                )

        # Set final validation status
        enhanced_result.is_valid = not enhanced_result.has_errors()

        return self._convert_to_standard_result(enhanced_result)

    def _extract_single_value(self, output: str) -> List[tuple]:
        """Extract a single value from output."""
        try:
            converted = self._convert_value(output)
            return [(output, converted)]
        except (ValueError, InvalidOperation):
            return [(output, None)]

    def _extract_all_values(self, output: str) -> List[tuple]:
        """Extract all numeric values from output."""
        patterns = self._get_parsing_patterns()
        values = []

        for pattern in patterns:
            matches = re.findall(pattern, output)
            for match in matches:
                try:
                    converted = self._convert_value(match)
                    values.append((match, converted))
                except (ValueError, InvalidOperation):
                    values.append((match, None))

        return values

    def _get_parsing_patterns(self) -> List[str]:
        """Get regex patterns for extracting values."""
        if self.value_type == "integer":
            return [r"-?\d+"]
        else:  # number or decimal
            return [
                r"-?\d+\.?\d*",  # Basic number
                r"-?\d{1,3}(?:,\d{3})*(?:\.\d+)?",  # Number with commas
            ]

    def _convert_value(self, value: Any) -> Any:
        """Convert string value to appropriate numeric type."""
        if isinstance(value, str):
            # Remove commas and whitespace
            cleaned = value.replace(",", "").strip()

            if self.value_type == "integer":
                return int(float(cleaned))  # Handle "5.0" -> 5
            elif self.value_type == "decimal":
                return Decimal(cleaned)
            else:  # number
                return float(cleaned)
        return value

    def _check_range(self, value: Any) -> tuple:
        """Check if value is within range and return (is_valid, error_or_none)."""
        # Check minimum constraint
        if self.min_value is not None:
            try:
                if self.inclusive_min:
                    if value < self.min_value:
                        return False, self._create_range_error(value, "below_minimum")
                else:
                    if value <= self.min_value:
                        return False, self._create_range_error(value, "at_or_below_minimum")
            except TypeError:
                return False, self._create_type_comparison_error(value)

        # Check maximum constraint
        if self.max_value is not None:
            try:
                if self.inclusive_max:
                    if value > self.max_value:
                        return False, self._create_range_error(value, "above_maximum")
                else:
                    if value >= self.max_value:
                        return False, self._create_range_error(value, "at_or_above_maximum")
            except TypeError:
                return False, self._create_type_comparison_error(value)

        return True, None

    def _create_range_error(self, value: Any, error_type: str) -> Any:
        """Create an enhanced range error."""
        from ..enhanced_validation import ValidationError as EnhancedError

        # Build descriptive message based on error type
        if error_type == "below_minimum":
            if self.max_value is not None:
                message = f"Value {value} is too small: must be between {self.min_value} and {self.max_value}"
                suggestion = f"Use a value between {self.min_value} and {self.max_value}"
            else:
                message = f"Value {value} is too small: must be at least {self.min_value}"
                suggestion = f"Use a value >= {self.min_value}"
        elif error_type == "above_maximum":
            if self.min_value is not None:
                message = f"Value {value} is too large: must be between {self.min_value} and {self.max_value}"
                suggestion = f"Use a value between {self.min_value} and {self.max_value}"
            else:
                message = f"Value {value} is too large: must be at most {self.max_value}"
                suggestion = f"Use a value <= {self.max_value}"
        else:
            message = f"Value {value} is out of acceptable range"
            suggestion = "Check the acceptable value range for this field"

        # Create fix actions
        fix_actions = ["Check the minimum and maximum allowed values"]

        if self.min_value is not None and self.max_value is not None:
            fix_actions.append(f"Use a value between {self.min_value} and {self.max_value}")
            fix_actions.append(f"Try values like: {self._get_range_examples()}")
        elif self.min_value is not None:
            fix_actions.append(f"Use a value >= {self.min_value}")
        elif self.max_value is not None:
            fix_actions.append(f"Use a value <= {self.max_value}")

        return EnhancedError(message=message, category=ErrorCategory.RANGE, severity=ErrorSeverity.MEDIUM, suggestion=suggestion, example=self._get_example_value(), fix_actions=fix_actions)

    def _create_type_comparison_error(self, value: Any) -> Any:
        """Create error for type comparison issues."""
        from ..enhanced_validation import ValidationError as EnhancedError

        return EnhancedError(
            message=f"Cannot compare {self.value_type} value {value} with range bounds",
            category=ErrorCategory.LOGIC,
            severity=ErrorSeverity.HIGH,
            suggestion="Ensure the value is the correct numeric type",
            fix_actions=[f"Convert the value to {self.value_type} type", "Check for any non-numeric characters", "Ensure proper numeric formatting"],
        )

    def _get_example_value(self) -> str:
        """Get an example value within the acceptable range."""
        if self.min_value is not None and self.max_value is not None:
            # Use midpoint
            mid = (self.min_value + self.max_value) / 2
            if self.value_type == "integer":
                return str(int(mid))
            else:
                return str(round(float(mid), 2))
        elif self.min_value is not None:
            if self.value_type == "integer":
                return str(int(self.min_value) + 1)
            else:
                return str(float(self.min_value) + 1)
        elif self.max_value is not None:
            if self.value_type == "integer":
                return str(int(self.max_value) - 1)
            else:
                return str(float(self.max_value) - 1)
        else:
            return "42" if self.value_type == "integer" else "42.0"

    def _get_range_examples(self) -> str:
        """Get example values within the range."""
        if self.min_value is None or self.max_value is None:
            return self._get_example_value()

        examples = []

        # Add minimum value (if inclusive)
        if self.inclusive_min:
            examples.append(str(self.min_value))

        # Add midpoint
        mid = (self.min_value + self.max_value) / 2
        if self.value_type == "integer":
            examples.append(str(int(mid)))
        else:
            examples.append(str(round(float(mid), 1)))

        # Add maximum value (if inclusive)
        if self.inclusive_max:
            examples.append(str(self.max_value))

        return ", ".join(examples[:3])  # Limit to 3 examples

    def _convert_to_standard_result(self, enhanced_result: EnhancedValidationResult) -> ValidationResult:
        """Convert enhanced result to standard ValidationResult for compatibility."""
        # Convert enhanced errors to simple error strings
        error_strings = []
        for error in enhanced_result.errors:
            error_strings.append(error.format_for_llm())

        # Convert enhanced warnings to simple warning strings
        warning_strings = []
        for warning in enhanced_result.warnings:
            warning_strings.append(warning.format_for_llm())

        # Add enhanced metadata
        metadata = enhanced_result.metadata.copy()
        metadata["enhanced_errors"] = [error.to_dict() for error in enhanced_result.errors]

        return ValidationResult(is_valid=enhanced_result.is_valid, errors=error_strings, warnings=warning_strings, metadata=metadata)

    def get_validation_instructions(self) -> str:
        """Get enhanced validation instructions for LLM context."""
        instructions = f"""ENHANCED RANGE VALIDATION REQUIREMENTS:

Output must contain {self.value_type} value(s) within specified bounds.

VALUE REQUIREMENTS:
- Type: {self.value_type}"""

        # Range requirements
        if self.min_value is not None and self.max_value is not None:
            min_op = "≥" if self.inclusive_min else ">"
            max_op = "≤" if self.inclusive_max else "<"
            instructions += f"""
- Range: {min_op} {self.min_value} and {max_op} {self.max_value}
- Example valid values: {self._get_range_examples()}"""
        elif self.min_value is not None:
            min_op = "≥" if self.inclusive_min else ">"
            instructions += f"""
- Minimum: {min_op} {self.min_value}
- Example: {self._get_example_value()}"""
        elif self.max_value is not None:
            max_op = "≤" if self.inclusive_max else "<"
            instructions += f"""
- Maximum: {max_op} {self.max_value}
- Example: {self._get_example_value()}"""

        if self.extract_all:
            instructions += f"""

EXTRACTION MODE: All numeric values will be validated
"""
            if self.required_count:
                instructions += f"- Required count: exactly {self.required_count} valid values"
        else:
            instructions += """

SINGLE VALUE MODE: Entire output treated as one value"""

        if self.value_type == "integer":
            instructions += """

INTEGER REQUIREMENTS:
- Only whole numbers allowed (no decimals)
- Examples: 42, -17, 0, 1000
- Invalid: 3.14, 42.0, 1.5"""

        instructions += f"""

COMMON ERRORS TO AVOID:
- Values outside the acceptable range
- Non-numeric text (letters, symbols)
- Incorrect decimal formatting for integers
- Missing values when multiple are required

This validator provides detailed feedback with specific fix suggestions for any issues."""

        return instructions
