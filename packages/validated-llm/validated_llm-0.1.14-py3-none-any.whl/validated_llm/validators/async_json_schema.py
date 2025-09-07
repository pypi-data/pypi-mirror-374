"""
Async JSON Schema validator for validating JSON data against a schema.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional

import jsonschema
from jsonschema import Draft7Validator, ValidationError

from ..async_validator import AsyncBaseValidator
from ..base_validator import ValidationResult


class AsyncJSONSchemaValidator(AsyncBaseValidator):
    """Async validator that uses JSON Schema to validate JSON data.

    This validator supports JSON Schema draft 7 and provides detailed
    error messages for schema violations. Validation runs in a thread pool
    to avoid blocking the event loop.

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

        validator = AsyncJSONSchemaValidator(schema)
        result = await validator.validate_async('{"name": "John", "age": 30}')
        ```
    """

    def __init__(self, schema: Dict[str, Any], strict_mode: bool = True, format_checker: bool = True):
        """Initialize the async JSON Schema validator.

        Args:
            schema: The JSON Schema to validate against
            strict_mode: If True, treat warnings as errors
            format_checker: If True, enable format checking (email, uri, etc.)
        """
        super().__init__(name="AsyncJSONSchemaValidator", description=f"Validates JSON data against schema with {len(schema.get('properties', {}))} properties")

        self.schema = schema
        self.strict_mode = strict_mode

        # Create validator with optional format checking
        if format_checker:
            self.validator = Draft7Validator(schema, format_checker=Draft7Validator.FORMAT_CHECKER)
        else:
            self.validator = Draft7Validator(schema)

    async def validate_async(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate JSON output against the schema asynchronously.

        Args:
            output: The JSON string to validate
            context: Optional validation context

        Returns:
            ValidationResult containing any errors or warnings
        """
        # Run the validation in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._validate_sync, output, context)

    def _validate_sync(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Synchronous validation logic (to be run in thread pool)."""
        llm_output = output
        errors: List[str] = []
        warnings: List[str] = []
        metadata = {"schema": self.schema, "async_validation": True}

        # Try to parse JSON
        try:
            data = json.loads(llm_output.strip())
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON: {str(e)}")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings, metadata=metadata)

        # Validate against schema
        validation_errors = list(self.validator.iter_errors(data))

        if validation_errors:
            for error in validation_errors:
                error_msg = self._format_validation_error(error)
                if self.strict_mode:
                    errors.append(error_msg)
                else:
                    # In non-strict mode, some errors might be warnings
                    if self._is_critical_error(error):
                        errors.append(error_msg)
                    else:
                        warnings.append(error_msg)

        # Add validated data to metadata
        if not errors:
            metadata["validated_data"] = data

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings, metadata=metadata)

    def _format_validation_error(self, error: ValidationError) -> str:
        """Format a JSON Schema validation error into a readable message.

        Args:
            error: The validation error

        Returns:
            Formatted error message
        """
        path = " -> ".join(str(p) for p in error.path) if error.path else "root"
        return f"Schema violation at {path}: {error.message}"

    def _is_critical_error(self, error: ValidationError) -> bool:
        """Determine if a validation error is critical.

        In non-strict mode, some errors (like additional properties)
        might be treated as warnings.

        Args:
            error: The validation error

        Returns:
            True if the error is critical
        """
        # Required property missing is always critical
        if str(error.validator) == "required":
            return True

        # Type mismatch is critical
        if str(error.validator) in ["type", "enum"]:
            return True

        # Additional properties might be warnings in non-strict mode
        if str(error.validator) == "additionalProperties":
            return False

        # Default to critical
        return True

    def get_validation_instructions(self) -> str:
        """Get a description of this validator for LLM context."""
        return f"""ASYNC JSON SCHEMA VALIDATION REQUIREMENTS:

Validates JSON data against the following schema:
{json.dumps(self.schema, indent=2)}

The JSON must:
1. Be valid JSON syntax
2. Match the specified schema structure
3. Include all required fields
4. Use correct data types for each field
5. Follow any additional constraints (min/max values, patterns, etc.)

This validator runs asynchronously for better performance.
Strict mode: {self.strict_mode}
"""
