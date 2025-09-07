"""
Mapping between Langchain output parsers and validated-llm validators.

This module provides conversion between Langchain's output parsing
approach and validated-llm's validation system.
"""

from typing import Any, Callable, Dict, Optional, Type, Union

from validated_llm.base_validator import BaseValidator, ValidationResult


class OutputParserMapper:
    """Maps Langchain output parsers to validated-llm validators."""

    def __init__(self) -> None:
        """Initialize the parser mapper."""
        self.parser_map = self._build_parser_map()

    def _build_parser_map(self) -> Dict[str, Union[Callable[[Any], Type[BaseValidator]], Callable[[], Type[BaseValidator]], Type[BaseValidator], None]]:
        """Build mapping of Langchain parser types to validators.

        Returns:
            Dictionary mapping parser class names to validator classes
        """
        from validated_llm.validators import DateTimeValidator, EmailValidator, RegexValidator

        # Map Langchain parser types to our validators
        return {
            "PydanticOutputParser": self._create_pydantic_validator,
            "StructuredOutputParser": self._create_json_validator,
            "ListOutputParser": self._create_list_validator,
            "DatetimeOutputParser": DateTimeValidator,
            "CommaSeparatedListOutputParser": self._create_csv_validator,
            "OutputFixingParser": None,  # Built into ValidationLoop
            "RetryOutputParser": None,  # Built into ValidationLoop
        }

    def _create_pydantic_validator(self, parser: Any) -> Type[BaseValidator]:
        """Create a validator from a Pydantic output parser.

        Args:
            parser: Langchain PydanticOutputParser instance

        Returns:
            A validator class that validates against the Pydantic model
        """

        class PydanticModelValidator(BaseValidator):
            def __init__(self) -> None:
                super().__init__(name="PydanticModelValidator", description="Validates against Pydantic model")
                self.model = parser.pydantic_object

            def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
                """Validate output matches Pydantic model."""
                import json

                try:
                    # Parse JSON
                    data = json.loads(output)

                    # Validate with Pydantic model
                    validated = self.model(**data)

                    return ValidationResult(is_valid=True, errors=[], warnings=[], metadata={"parsed_data": validated.dict()})
                except json.JSONDecodeError as e:
                    return ValidationResult(is_valid=False, errors=[f"Invalid JSON: {str(e)}"], warnings=[])
                except Exception as e:
                    return ValidationResult(is_valid=False, errors=[f"Validation failed: {str(e)}"], warnings=[])

        return PydanticModelValidator

    def _create_json_validator(self) -> Type[BaseValidator]:
        """Create a JSON validator for structured output parsing.

        Returns:
            A validator class for JSON validation
        """
        from validated_llm.validators import RegexValidator

        # Use RegexValidator as a placeholder since JSONValidator doesn't exist
        return RegexValidator

    def _create_list_validator(self) -> Type[BaseValidator]:
        """Create a validator for list outputs.

        Returns:
            A validator class for list validation
        """

        class ListValidator(BaseValidator):
            def __init__(self) -> None:
                super().__init__(name="ListValidator", description="Validates list format output")

            def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
                """Validate output is a proper list."""
                lines = output.strip().split("\n")

                # Check if it looks like a list
                is_list = all(line.strip().startswith(("-", "*", "•", "1", "2", "3", "4", "5", "6", "7", "8", "9")) for line in lines if line.strip())

                if is_list and len(lines) > 0:
                    return ValidationResult(is_valid=True, errors=[], warnings=[], metadata={"items": [line.strip().lstrip("-*•0123456789. ") for line in lines]})
                else:
                    return ValidationResult(is_valid=False, errors=["Output is not formatted as a list"], warnings=[])

        return ListValidator

    def _create_csv_validator(self) -> Type[BaseValidator]:
        """Create a validator for comma-separated values.

        Returns:
            A validator class for CSV validation
        """

        class CSVValidator(BaseValidator):
            def __init__(self) -> None:
                super().__init__(name="CSVValidator", description="Validates comma-separated values output")

            def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
                """Validate output is comma-separated."""
                items = [item.strip() for item in output.split(",")]

                if len(items) > 0 and all(items):
                    return ValidationResult(is_valid=True, errors=[], warnings=[], metadata={"items": items})
                else:
                    return ValidationResult(is_valid=False, errors=["Output is not valid comma-separated values"], warnings=[])

        return CSVValidator

    def convert_parser(self, langchain_parser: Any) -> Optional[Type[BaseValidator]]:
        """Convert a Langchain output parser to a validator.

        Args:
            langchain_parser: Langchain output parser instance

        Returns:
            Corresponding validator class or None if built into ValidationLoop
        """
        parser_type = type(langchain_parser).__name__

        if parser_type in self.parser_map:
            validator_factory = self.parser_map[parser_type]
            if validator_factory is None:
                return None  # Built into ValidationLoop
            elif callable(validator_factory) and not isinstance(validator_factory, type):
                # It's a method that creates validators - call with appropriate args
                if parser_type == "PydanticOutputParser":
                    return self._create_pydantic_validator(langchain_parser)
                elif parser_type == "StructuredOutputParser":
                    return self._create_json_validator()
                elif parser_type == "ListOutputParser":
                    return self._create_list_validator()
                elif parser_type == "CommaSeparatedListOutputParser":
                    return self._create_csv_validator()
                else:
                    # Shouldn't reach here with current mapping
                    from validated_llm.validators import RegexValidator

                    return RegexValidator
            else:
                # It's already a validator class
                return validator_factory
        else:
            # Default to regex validator for unknown parsers
            from validated_llm.validators import RegexValidator

            return RegexValidator
