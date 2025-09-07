"""
JSON generation LLM validation tasks.

This module contains tasks for generating JSON output with schema validation.
"""

import json
from typing import Any, Dict, List, Optional, Type

import jsonschema

from ..base_validator import BaseValidator, ValidationResult
from .base_task import BaseTask


class JSONGenerationTask(BaseTask):
    """
    Base class for JSON generation tasks.

    Provides common functionality for tasks that generate JSON output
    with schema validation.
    """

    @property
    def validator_class(self) -> Type[BaseValidator]:
        return JSONSchemaValidator


class PersonJSONTask(JSONGenerationTask):
    """Task for generating person data as JSON."""

    @property
    def name(self) -> str:
        return "Person JSON Generation"

    @property
    def description(self) -> str:
        return "Generate JSON object representing a person from text description"

    @property
    def prompt_template(self) -> str:
        return """
Generate a JSON object representing a person with the following information from the input: {input_text}

The JSON should have this exact structure:
{{
  "name": "string - person's full name",
  "age": number - person's age in years,
  "occupation": "string - person's job or profession",
  "location": "string - city or location",
  "interests": ["array", "of", "strings", "representing", "hobbies"]
}}

OUTPUT REQUIREMENTS:
- Output ONLY the JSON object, no additional text
- Do not wrap in markdown code blocks
- Ensure valid JSON syntax
- All fields are required

Example input: "John Smith is a 35-year-old software engineer from San Francisco who enjoys hiking, photography, and cooking."
Example output:
{{
  "name": "John Smith",
  "age": 35,
  "occupation": "software engineer",
  "location": "San Francisco",
  "interests": ["hiking", "photography", "cooking"]
}}

Your response:"""

    def create_validator(self, **kwargs: Any) -> BaseValidator:
        """Create validator with person schema."""
        person_schema = {
            "type": "object",
            "required": ["name", "age", "occupation", "location", "interests"],
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number", "minimum": 0, "maximum": 150},
                "occupation": {"type": "string"},
                "location": {"type": "string"},
                "interests": {"type": "array", "items": {"type": "string"}, "minItems": 1},
            },
        }

        # Allow schema override
        schema = kwargs.get("schema", person_schema)
        return JSONSchemaValidator(name="person_json_validator", description="Validates person JSON against schema", schema=schema, **{k: v for k, v in kwargs.items() if k != "schema"})


class ProductCatalogTask(JSONGenerationTask):
    """Task for generating product catalog data as JSON."""

    @property
    def name(self) -> str:
        return "Product Catalog JSON Generation"

    @property
    def description(self) -> str:
        return "Generate JSON product catalog from text descriptions"

    @property
    def prompt_template(self) -> str:
        return """
Generate a JSON product catalog from the following product descriptions: {product_descriptions}

The JSON should be an object with a "products" array, where each product has this structure:
{{
  "products": [
    {{
      "id": "string - unique product identifier",
      "name": "string - product name",
      "category": "string - product category",
      "price": {{
        "currency": "USD",
        "amount": number
      }},
      "specifications": {{
        "dimensions": "string - product dimensions",
        "weight": "string - product weight",
        "material": "string - primary material"
      }},
      "availability": {{
        "in_stock": boolean,
        "quantity": number,
        "shipping_time": "string - estimated shipping time"
      }}
    }}
  ]
}}

OUTPUT REQUIREMENTS:
- Output ONLY the JSON object, no additional text
- Do not wrap in markdown code blocks
- Ensure valid JSON syntax with proper nesting
- All fields are required for each product
- Generate reasonable values for missing information

Your response:"""

    def create_validator(self, **kwargs: Any) -> BaseValidator:
        """Create validator with product catalog schema."""
        product_schema = {
            "type": "object",
            "required": ["products"],
            "properties": {
                "products": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["id", "name", "category", "price", "specifications", "availability"],
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "category": {"type": "string"},
                            "price": {"type": "object", "required": ["currency", "amount"], "properties": {"currency": {"type": "string"}, "amount": {"type": "number", "minimum": 0}}},
                            "specifications": {
                                "type": "object",
                                "required": ["dimensions", "weight", "material"],
                                "properties": {"dimensions": {"type": "string"}, "weight": {"type": "string"}, "material": {"type": "string"}},
                            },
                            "availability": {
                                "type": "object",
                                "required": ["in_stock", "quantity", "shipping_time"],
                                "properties": {"in_stock": {"type": "boolean"}, "quantity": {"type": "number", "minimum": 0}, "shipping_time": {"type": "string"}},
                            },
                        },
                    },
                }
            },
        }

        # Allow schema override
        schema = kwargs.get("schema", product_schema)
        return JSONSchemaValidator(name="product_catalog_validator", description="Validates product catalog JSON against schema", schema=schema, **{k: v for k, v in kwargs.items() if k != "schema"})


class JSONSchemaValidator(BaseValidator):
    """Validates LLM output against a JSON schema."""

    def __init__(self, name: str = "json_schema_validator", description: str = "Validates JSON output against provided schema", schema: Optional[Dict[str, Any]] = None, strict_mode: bool = True):
        """
        Initialize the JSON schema validator.

        Args:
            name: Validator name
            description: Validator description
            schema: JSON schema to validate against
            strict_mode: If True, requires exact schema compliance
        """
        super().__init__(name=name, description=description)
        self.schema = schema
        self.strict_mode = strict_mode

    def validate(self, content: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate content against JSON schema."""
        errors = []
        warnings: List[str] = []

        # Check if content is valid JSON
        try:
            data = json.loads(content.strip())
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON syntax: {str(e)}")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

        # Validate against schema
        if self.schema is None:
            errors.append("No JSON schema provided for validation.")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        try:
            jsonschema.validate(instance=data, schema=self.schema)
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation failed: {e.message}")
            if hasattr(e, "path") and e.path:
                errors.append(f"Error location: {'.'.join(str(p) for p in e.path)}")
        except jsonschema.SchemaError as e:
            errors.append(f"Invalid schema: {str(e)}")

        # Additional checks for common JSON issues
        if isinstance(data, str):
            warnings.append("Output is a JSON string, expected object/array")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)
