"""
Enhanced JSON Schema validator with detailed error messages and fix suggestions.
"""

import json
from typing import Any, Dict, List, Optional

import jsonschema
from jsonschema import Draft7Validator, ValidationError

from ..base_validator import BaseValidator, ValidationResult
from ..enhanced_validation import EnhancedValidationResult, ErrorCategory, ErrorMessageEnhancer, ErrorSeverity


class EnhancedJSONSchemaValidator(BaseValidator):
    """Enhanced JSON Schema validator with detailed error messages and suggestions.

    This validator provides much more helpful error messages compared to the basic
    JSONSchemaValidator, including fix suggestions, examples, and categorized errors.

    Example:
        ```python
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0},
                "email": {"type": "string", "format": "email"}
            },
            "required": ["name", "age"]
        }

        validator = EnhancedJSONSchemaValidator(schema)
        result = validator.validate('{"name": "John"}')  # Missing age
        print(result.get_feedback_text())  # Detailed error with suggestions
        ```
    """

    def __init__(self, schema: Dict[str, Any], strict_mode: bool = True, format_checker: bool = True):
        """Initialize the enhanced JSON Schema validator.

        Args:
            schema: The JSON Schema to validate against
            strict_mode: If True, treat warnings as errors
            format_checker: If True, enable format checking (email, uri, etc.)
        """
        super().__init__(name="EnhancedJSONSchemaValidator", description=f"Enhanced JSON Schema validation with detailed error messages")

        self.schema = schema
        self.strict_mode = strict_mode

        # Create validator with optional format checking
        if format_checker:
            self.validator = Draft7Validator(schema, format_checker=Draft7Validator.FORMAT_CHECKER)
        else:
            self.validator = Draft7Validator(schema)

    def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate JSON output against the schema with enhanced error messages.

        Args:
            output: The JSON string to validate
            context: Optional validation context

        Returns:
            ValidationResult with enhanced error messages and suggestions
        """
        llm_output = output.strip()

        # Create enhanced result
        enhanced_result = EnhancedValidationResult(is_valid=True)
        enhanced_result.metadata = {"schema": self.schema, "enhanced_validation": True, "validator_type": "EnhancedJSONSchemaValidator"}

        # Try to parse JSON first
        try:
            data = json.loads(llm_output)
        except json.JSONDecodeError as e:
            # Enhanced JSON parsing error
            enhanced_error = ErrorMessageEnhancer.enhance_json_error(str(e), llm_output)
            enhanced_result.errors.append(enhanced_error)
            enhanced_result.is_valid = False

            # Convert to standard ValidationResult for compatibility
            return self._convert_to_standard_result(enhanced_result)

        # Validate against schema with enhanced error messages
        validation_errors = list(self.validator.iter_errors(data))

        if validation_errors:
            for error in validation_errors:
                enhanced_error = self._create_enhanced_schema_error(error)

                if self.strict_mode:
                    enhanced_result.errors.append(enhanced_error)
                else:
                    # In non-strict mode, some errors might be warnings
                    if self._is_critical_error(error):
                        enhanced_result.errors.append(enhanced_error)
                    else:
                        enhanced_result.add_warning(enhanced_error.message, category=enhanced_error.category, suggestion=enhanced_error.suggestion, location=enhanced_error.location)

        # Add validated data to metadata if successful
        if not enhanced_result.has_errors():
            enhanced_result.metadata["validated_data"] = data
            enhanced_result.is_valid = True
        else:
            enhanced_result.is_valid = False

        # Convert to standard ValidationResult for compatibility
        return self._convert_to_standard_result(enhanced_result)

    def _create_enhanced_schema_error(self, error: ValidationError) -> Any:
        """Create an enhanced error from a JSON Schema validation error."""
        field_path = " -> ".join(str(p) for p in error.path) if error.path else "root"
        error_message = error.message
        validator_type = str(error.validator)

        # Determine error category and severity
        if validator_type == "required":
            return ErrorMessageEnhancer.enhance_schema_error(field_path, error_message, expected_type="required field")
        elif validator_type in ["type", "enum"]:
            expected_type = None
            if hasattr(error, "schema") and isinstance(error.schema, dict) and "type" in error.schema:
                expected_type = str(error.schema["type"])
            return ErrorMessageEnhancer.enhance_schema_error(field_path, error_message, expected_type=expected_type)
        elif validator_type in ["minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum"]:
            # Range validation error
            current_value = error.instance if hasattr(error, "instance") else None
            min_val = None
            max_val = None
            if hasattr(error, "schema") and isinstance(error.schema, dict):
                min_val = error.schema.get("minimum")
                max_val = error.schema.get("maximum")
            return ErrorMessageEnhancer.enhance_range_error(current_value, min_val, max_val)
        elif validator_type == "format":
            return self._create_format_error(field_path, error)
        elif validator_type == "pattern":
            return self._create_pattern_error(field_path, error)
        elif validator_type == "additionalProperties":
            return self._create_additional_properties_error(field_path, error)
        else:
            # Generic schema error with enhanced context
            return ErrorMessageEnhancer.enhance_schema_error(field_path, error_message)

    def _create_format_error(self, field_path: str, error: ValidationError) -> Any:
        """Create enhanced error for format validation failures."""
        format_type = "unknown"
        if hasattr(error, "schema") and isinstance(error.schema, dict):
            format_type = error.schema.get("format", "unknown")
        current_value = error.instance if hasattr(error, "instance") else "unknown"

        suggestions = {
            "email": "Use format: user@domain.com",
            "uri": "Use format: https://example.com/path",
            "date": "Use format: YYYY-MM-DD (e.g., 2024-03-15)",
            "time": "Use format: HH:MM:SS (e.g., 14:30:00)",
            "date-time": "Use format: YYYY-MM-DDTHH:MM:SS (e.g., 2024-03-15T14:30:00)",
        }

        from ..enhanced_validation import ValidationError as EnhancedError

        return EnhancedError(
            message=f"Invalid {format_type} format: '{current_value}'",
            category=ErrorCategory.FORMAT,
            severity=ErrorSeverity.HIGH,
            location=field_path,
            suggestion=suggestions.get(format_type, f"Check the required {format_type} format"),
            example=self._get_format_example(format_type),
            fix_actions=[f"Correct the {format_type} format", "Ensure the value matches the expected pattern", "Check for typos or missing components"],
        )

    def _create_pattern_error(self, field_path: str, error: ValidationError) -> Any:
        """Create enhanced error for pattern validation failures."""
        pattern = "unknown"
        if hasattr(error, "schema") and isinstance(error.schema, dict):
            pattern = error.schema.get("pattern", "unknown")
        current_value = error.instance if hasattr(error, "instance") else "unknown"

        from ..enhanced_validation import ValidationError as EnhancedError

        return EnhancedError(
            message=f"Value '{current_value}' does not match required pattern",
            category=ErrorCategory.FORMAT,
            severity=ErrorSeverity.MEDIUM,
            location=field_path,
            suggestion=f"Ensure the value matches the pattern: {pattern}",
            fix_actions=["Check the required pattern format", "Adjust your value to match the pattern", "Remove any invalid characters"],
        )

    def _create_additional_properties_error(self, field_path: str, error: ValidationError) -> Any:
        """Create enhanced error for additional properties."""
        from ..enhanced_validation import ValidationError as EnhancedError

        return EnhancedError(
            message=f"Additional property not allowed: {error.message}",
            category=ErrorCategory.SCHEMA,
            severity=ErrorSeverity.LOW,
            location=field_path,
            suggestion="Remove the extra property or check if it's required in the schema",
            fix_actions=["Remove the additional property", "Check if the property name is correct", "Verify the schema allows this property"],
        )

    def _get_format_example(self, format_type: str) -> str:
        """Get an example for a specific format type."""
        examples = {"email": "john.doe@example.com", "uri": "https://www.example.com/path", "date": "2024-03-15", "time": "14:30:00", "date-time": "2024-03-15T14:30:00Z"}
        return examples.get(format_type, "Valid format required")

    def _is_critical_error(self, error: ValidationError) -> bool:
        """Determine if a validation error is critical."""
        validator_type = str(error.validator)
        return validator_type in ["required", "type", "enum"]

    def _convert_to_standard_result(self, enhanced_result: EnhancedValidationResult) -> ValidationResult:
        """Convert enhanced result to standard ValidationResult for compatibility."""
        # Convert enhanced errors to simple error strings
        error_strings = []
        for error in enhanced_result.errors:
            # Use the formatted LLM message for better feedback
            error_strings.append(error.format_for_llm())

        # Convert enhanced warnings to simple warning strings
        warning_strings = []
        for warning in enhanced_result.warnings:
            warning_strings.append(warning.format_for_llm())

        # Add enhanced metadata
        metadata = enhanced_result.metadata.copy()
        metadata["enhanced_errors"] = [error.to_dict() for error in enhanced_result.errors]
        metadata["enhanced_warnings"] = [{"message": w.message, "category": w.category.value, "suggestion": w.suggestion} for w in enhanced_result.warnings]

        return ValidationResult(is_valid=enhanced_result.is_valid, errors=error_strings, warnings=warning_strings, metadata=metadata)

    def get_validation_instructions(self) -> str:
        """Get enhanced validation instructions for LLM context."""
        return f"""ENHANCED JSON SCHEMA VALIDATION REQUIREMENTS:

Validates JSON data against the following schema:
{json.dumps(self.schema, indent=2)}

The JSON must:
1. Be valid JSON syntax (no trailing commas, proper quotes, balanced brackets)
2. Match the specified schema structure exactly
3. Include all required fields
4. Use correct data types for each field
5. Follow any additional constraints (min/max values, patterns, formats, etc.)

Enhanced error reporting will provide:
- Specific fix suggestions for each error
- Examples of correct formats
- Step-by-step repair instructions
- Categorized errors by severity (critical, high, medium, low)

Common JSON syntax rules:
- Strings must be in double quotes: "text"
- No trailing commas: [1, 2, 3] not [1, 2, 3,]
- Boolean values: true/false (not True/False)
- Numbers: 42 or 3.14 (no quotes for numbers)

This validator provides detailed, actionable feedback to help you fix any issues quickly.
"""
