"""
Validator suggestion engine that recommends appropriate validators
based on prompt analysis results.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .analyzer import AnalysisResult


@dataclass
class ValidatorSuggestion:
    """A suggested validator configuration."""

    # Validator type/name
    validator_type: str

    # Import path for the validator
    import_path: str

    # Configuration parameters
    config: Dict[str, Any]

    # Confidence in this suggestion (0.0 to 1.0)
    confidence: float

    # Human-readable description
    description: str

    # Whether this is a built-in validator or needs custom code
    is_builtin: bool = True

    # Custom validator code (if needed)
    custom_code: Optional[str] = None


class ValidatorSuggester:
    """
    Suggests appropriate validators based on prompt analysis.

    This engine maps detected patterns to existing validators or
    suggests custom validator implementations.
    """

    def __init__(self) -> None:
        """Initialize the validator suggester."""
        self.builtin_validators = {
            "json": {"validator_type": "JSONValidator", "import_path": "validated_llm.tasks.json_generation", "description": "Validates JSON output against schema"},
            "csv": {"validator_type": "CSVValidator", "import_path": "validated_llm.tasks.csv_generation", "description": "Validates CSV format and structure"},
        }

    def suggest_validators(self, analysis: AnalysisResult) -> list[ValidatorSuggestion]:
        """
        Suggest validators based on prompt analysis.

        Args:
            analysis: Result from PromptAnalyzer

        Returns:
            List of validator suggestions, ordered by confidence
        """
        suggestions = []

        # Primary validator based on detected format
        primary_suggestion = self._suggest_primary_validator(analysis)
        if primary_suggestion:
            suggestions.append(primary_suggestion)

        # Additional validators based on validation hints
        additional_suggestions = self._suggest_additional_validators(analysis)
        suggestions.extend(additional_suggestions)

        # Sort by confidence (highest first)
        suggestions.sort(key=lambda x: x.confidence, reverse=True)

        return suggestions

    def _suggest_primary_validator(self, analysis: AnalysisResult) -> Optional[ValidatorSuggestion]:
        """Suggest the primary validator based on output format."""

        if analysis.output_format == "json":
            return self._suggest_json_validator(analysis)
        elif analysis.output_format == "csv":
            return self._suggest_csv_validator(analysis)
        elif analysis.output_format == "list":
            return self._suggest_list_validator(analysis)
        elif analysis.output_format == "text":
            return self._suggest_text_validator(analysis)
        else:
            return self._suggest_generic_validator(analysis)

    def _suggest_json_validator(self, analysis: AnalysisResult) -> ValidatorSuggestion:
        """Suggest JSON validator configuration."""
        config = {}

        if analysis.json_schema:
            schema = analysis.json_schema
            config["schema"] = schema

            # Check if schema has nested structures
            has_nested = self._has_nested_structure(schema)

            # Higher confidence for detected schemas, especially with nested structures
            if has_nested:
                confidence = 0.95
                description = "Validates complex JSON with nested objects/arrays against detected schema"
                # Use JSONSchemaValidator for complex schemas
                validator_type = "JSONSchemaValidator"
                import_path = "validated_llm.validators.json_schema"
            else:
                confidence = 0.9
                description = "Validates JSON output against detected schema"
                # Use simpler JSONValidator for flat structures
                validator_type = "JSONValidator"
                import_path = "validated_llm.tasks.json_generation"
        else:
            # Create basic schema from template variables
            if analysis.template_variables or []:
                basic_schema: dict[str, Any] = {"type": "object", "properties": {}, "required": analysis.template_variables or []}
                for var in analysis.template_variables or []:
                    basic_schema["properties"][var] = {"type": "string"}
                config["schema"] = basic_schema
                confidence = 0.7
                description = "Validates JSON output with basic schema from template variables"
                validator_type = "JSONValidator"
                import_path = "validated_llm.tasks.json_generation"
            else:
                confidence = 0.5
                description = "Validates basic JSON format"
                validator_type = "JSONValidator"
                import_path = "validated_llm.tasks.json_generation"

        # Adjust confidence based on analysis confidence
        confidence = min(confidence, analysis.confidence + 0.1)

        return ValidatorSuggestion(validator_type=validator_type, import_path=import_path, config=config, confidence=confidence, description=description, is_builtin=True)

    def _has_nested_structure(self, schema: Dict[str, Any]) -> bool:
        """Check if a JSON schema has nested objects or arrays."""
        # Check root level
        if schema.get("type") == "array":
            items = schema.get("items", {})
            if items.get("type") == "object":
                return True

        # Check properties
        properties = schema.get("properties", {})
        for prop_name, prop_schema in properties.items():
            if isinstance(prop_schema, dict):
                prop_type = prop_schema.get("type")
                if prop_type == "object":
                    return True
                elif prop_type == "array":
                    # Array of objects is considered nested
                    items = prop_schema.get("items", {})
                    if isinstance(items, dict) and items.get("type") == "object":
                        return True

        return False

    def _suggest_csv_validator(self, analysis: AnalysisResult) -> ValidatorSuggestion:
        """Suggest CSV validator configuration."""
        config = {}

        if analysis.csv_columns:
            config["expected_columns"] = analysis.csv_columns
            confidence = 0.8
        else:
            confidence = 0.5

        # Adjust confidence based on analysis confidence
        confidence = min(confidence, analysis.confidence + 0.1)

        return ValidatorSuggestion(
            validator_type="CSVValidator", import_path="validated_llm.tasks.csv_generation", config=config, confidence=confidence, description="Validates CSV format and column structure", is_builtin=True
        )

    def _suggest_list_validator(self, analysis: AnalysisResult) -> ValidatorSuggestion:
        """Suggest validator for list output."""
        # This would need a custom validator since we don't have a built-in list validator
        custom_code = self._generate_list_validator_code(analysis)

        config = {}
        if analysis.list_pattern:
            config["expected_pattern"] = analysis.list_pattern

        return ValidatorSuggestion(
            validator_type="ListValidator",
            import_path="custom",  # Indicates custom validator
            config=config,
            confidence=0.6,
            description="Validates list format and item structure",
            is_builtin=False,
            custom_code=custom_code,
        )

    def _suggest_text_validator(self, analysis: AnalysisResult) -> ValidatorSuggestion:
        """Suggest validator for text output."""
        custom_code = self._generate_text_validator_code(analysis)

        config = {"min_length": 10, "max_length": 5000}  # Default minimum  # Default maximum

        # Extract length constraints from validation hints
        for hint in analysis.validation_hints or []:
            if "length" in hint.lower():
                # Try to extract numeric values
                import re

                numbers = re.findall(r"\d+", hint)
                if numbers:
                    if "min" in hint.lower():
                        config["min_length"] = int(numbers[0])
                    elif "max" in hint.lower():
                        config["max_length"] = int(numbers[0])

        return ValidatorSuggestion(validator_type="TextValidator", import_path="custom", config=config, confidence=0.4, description="Validates text length and basic format", is_builtin=False, custom_code=custom_code)

    def _suggest_generic_validator(self, analysis: AnalysisResult) -> ValidatorSuggestion:
        """Suggest a generic validator when format is unclear."""
        custom_code = self._generate_generic_validator_code(analysis)

        return ValidatorSuggestion(validator_type="GenericValidator", import_path="custom", config={}, confidence=0.3, description="Basic validation for unknown output format", is_builtin=False, custom_code=custom_code)

    def _suggest_additional_validators(self, analysis: AnalysisResult) -> list[ValidatorSuggestion]:
        """Suggest additional validators based on validation hints."""
        suggestions = []

        # Look for specific validation requirements in hints
        for hint in analysis.validation_hints or []:
            hint_lower = hint.lower()

            # Email validation
            if "email" in hint_lower:
                suggestions.append(
                    ValidatorSuggestion(
                        validator_type="EmailValidator", import_path="custom", config={}, confidence=0.7, description="Validates email format", is_builtin=False, custom_code=self._generate_email_validator_code()
                    )
                )

            # URL validation
            if "url" in hint_lower or "http" in hint_lower:
                suggestions.append(
                    ValidatorSuggestion(validator_type="URLValidator", import_path="custom", config={}, confidence=0.7, description="Validates URL format", is_builtin=False, custom_code=self._generate_url_validator_code())
                )

            # Length validation
            if "length" in hint_lower and ("min" in hint_lower or "max" in hint_lower):
                import re

                numbers = re.findall(r"\d+", hint)
                if numbers:
                    config = {}
                    if "min" in hint_lower:
                        config["min_length"] = int(numbers[0])
                    if "max" in hint_lower:
                        config["max_length"] = int(numbers[-1])

                    suggestions.append(
                        ValidatorSuggestion(
                            validator_type="LengthValidator",
                            import_path="custom",
                            config=config,
                            confidence=0.8,
                            description="Validates content length",
                            is_builtin=False,
                            custom_code=self._generate_length_validator_code(),
                        )
                    )

        return suggestions

    def _generate_list_validator_code(self, analysis: AnalysisResult) -> str:
        """Generate custom list validator code."""
        return '''
class ListValidator(BaseValidator):
    """Validates list output format."""

    def __init__(self, min_items: int = 1, max_items: int = 100, item_pattern: Optional[str] = None):
        super().__init__(name="list_validator", description="Validates list format and structure")
        self.min_items = min_items
        self.max_items = max_items
        self.item_pattern = item_pattern

    def validate(self, content: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        errors = []
        warnings = []

        lines = [line.strip() for line in content.strip().split('\\n') if line.strip()]

        # Check item count
        if len(lines) < self.min_items:
            errors.append(f"Too few items: {len(lines)} (minimum: {self.min_items})")
        elif len(lines) > self.max_items:
            warnings.append(f"Many items: {len(lines)} (recommended max: {self.max_items})")

        # Check item format
        for i, line in enumerate(lines, 1):
            if not (line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '*', '-')) or
                    line[0].isdigit()):
                warnings.append(f"Line {i} doesn't follow list format")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metadata={"item_count": len(lines)}
        )
'''

    def _generate_text_validator_code(self, analysis: AnalysisResult) -> str:
        """Generate custom text validator code."""
        return '''
class TextValidator(BaseValidator):
    """Validates text output."""

    def __init__(self, min_length: int = 10, max_length: int = 5000):
        super().__init__(name="text_validator", description="Validates text length and format")
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, content: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        errors = []
        warnings = []

        content_length = len(content.strip())

        if content_length < self.min_length:
            errors.append(f"Content too short: {content_length} characters (minimum: {self.min_length})")
        elif content_length > self.max_length:
            warnings.append(f"Content quite long: {content_length} characters (recommended max: {self.max_length})")

        # Check for empty content
        if not content.strip():
            errors.append("Content is empty")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metadata={"character_count": content_length, "word_count": len(content.split())}
        )
'''

    def _generate_generic_validator_code(self, analysis: AnalysisResult) -> str:
        """Generate generic validator code."""
        return '''
class GenericValidator(BaseValidator):
    """Generic validator for unknown output formats."""

    def __init__(self):
        super().__init__(name="generic_validator", description="Basic validation for any output")

    def validate(self, content: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        errors = []
        warnings = []

        # Basic checks
        if not content.strip():
            errors.append("Output is empty")

        if len(content.strip()) < 5:
            warnings.append("Output seems very short")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metadata={"length": len(content)}
        )
'''

    def _generate_email_validator_code(self) -> str:
        """Generate email validator code."""
        return '''
import re

class EmailValidator(BaseValidator):
    """Validates email addresses."""

    def __init__(self):
        super().__init__(name="email_validator", description="Validates email format")
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$')

    def validate(self, content: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        errors = []

        email = content.strip()
        if not self.email_pattern.match(email):
            errors.append(f"Invalid email format: {email}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=[],
            metadata={"email": email}
        )
'''

    def _generate_url_validator_code(self) -> str:
        """Generate URL validator code."""
        return '''
import re

class URLValidator(BaseValidator):
    """Validates URL format."""

    def __init__(self):
        super().__init__(name="url_validator", description="Validates URL format")
        self.url_pattern = re.compile(r'^https?://[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}')

    def validate(self, content: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        errors = []

        url = content.strip()
        if not self.url_pattern.match(url):
            errors.append(f"Invalid URL format: {url}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=[],
            metadata={"url": url}
        )
'''

    def _generate_length_validator_code(self) -> str:
        """Generate length validator code."""
        return '''
class LengthValidator(BaseValidator):
    """Validates content length."""

    def __init__(self, min_length: Optional[int] = None, max_length: Optional[int] = None):
        super().__init__(name="length_validator", description="Validates content length")
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, content: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        errors = []
        warnings = []

        length = len(content.strip())

        if self.min_length is not None and length < self.min_length:
            errors.append(f"Content too short: {length} characters (minimum: {self.min_length})")

        if self.max_length is not None and length > self.max_length:
            errors.append(f"Content too long: {length} characters (maximum: {self.max_length})")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metadata={"length": length}
        )
'''
