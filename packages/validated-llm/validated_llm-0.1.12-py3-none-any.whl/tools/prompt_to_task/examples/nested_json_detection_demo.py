#!/usr/bin/env python3
"""
Demonstration of enhanced JSON schema detection with nested structures.

This example shows how the PromptAnalyzer can now detect:
- Nested objects
- Arrays of objects
- Complex JSON structures from textual descriptions
"""

import json

from tools.prompt_to_task.analyzer import PromptAnalyzer
from tools.prompt_to_task.validator_suggester import ValidatorSuggester


def demo_nested_object_detection() -> None:
    """Demonstrate detection of nested objects in JSON."""
    print("=== Nested Object Detection ===\n")

    prompt = """
    Generate a user profile in JSON format:

    ```json
    {
        "id": 123,
        "name": "John Doe",
        "contact": {
            "email": "john@example.com",
            "phone": "+1234567890",
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "zipCode": "10001"
            }
        }
    }
    ```
    """

    analyzer = PromptAnalyzer()
    result = analyzer.analyze(prompt)

    print(f"Output format: {result.output_format}")
    print(f"JSON Schema detected:")
    print(json.dumps(result.json_schema, indent=2))

    # Check validator suggestion
    suggester = ValidatorSuggester()
    suggestions = suggester.suggest_validators(result)
    print(f"\nSuggested validator: {suggestions[0].validator_type if suggestions else 'None'}")
    print()


def demo_array_of_objects_detection() -> None:
    """Demonstrate detection of arrays containing objects."""
    print("=== Array of Objects Detection ===\n")

    prompt = """
    Create a product catalog with multiple items:

    ```json
    [
        {
            "id": "P001",
            "name": "Laptop",
            "price": 999.99,
            "specs": {
                "cpu": "Intel i7",
                "ram": "16GB"
            },
            "categories": ["electronics", "computers"]
        },
        {
            "id": "P002",
            "name": "Mouse",
            "price": 29.99,
            "specs": {
                "type": "wireless",
                "dpi": 1600
            },
            "categories": ["electronics", "accessories"]
        }
    ]
    ```
    """

    analyzer = PromptAnalyzer()
    result = analyzer.analyze(prompt)

    print(f"Output format: {result.output_format}")
    print(f"JSON Schema detected:")
    print(json.dumps(result.json_schema, indent=2))

    # Check if it recommends JSONSchemaValidator
    suggester = ValidatorSuggester()
    suggestions = suggester.suggest_validators(result)
    if suggestions:
        print(f"\nSuggested validator: {suggestions[0].validator_type}")
        print(f"Confidence: {suggestions[0].confidence:.2f}")
    print()


def demo_textual_description_detection() -> None:
    """Demonstrate JSON schema inference from textual descriptions."""
    print("=== Textual Description Detection ===\n")

    prompt = """
    Create a JSON response with the following fields:
    - id (number): Unique identifier
    - name (string): Full name of the person
    - emails (array): List of email addresses
    - profile (object): User profile containing:
        - bio (string): Short biography
        - skills (array): List of skills
        - experience (array of objects): Work experience with company, role, and years
    """

    analyzer = PromptAnalyzer()
    result = analyzer.analyze(prompt)

    print(f"Output format: {result.output_format}")
    print(f"JSON Schema detected:")
    print(json.dumps(result.json_schema, indent=2))

    # Verify nested structure
    if result.json_schema:
        profile_props = result.json_schema.get("properties", {}).get("profile", {}).get("properties", {})
        if "experience" in profile_props:
            exp_schema = profile_props["experience"]
            print(f"\nExperience field correctly detected as: {exp_schema['type']}")
            if exp_schema["type"] == "array" and "items" in exp_schema:
                print(f"  Items type: {exp_schema['items'].get('type', 'unknown')}")
    print()


def demo_simple_vs_complex_json() -> None:
    """Demonstrate different validator suggestions for simple vs complex JSON."""
    print("=== Simple vs Complex JSON Validator Selection ===\n")

    # Simple JSON
    simple_prompt = """
    Generate a user object:
    ```json
    {"id": 1, "name": "John", "email": "john@example.com"}
    ```
    """

    # Complex JSON
    complex_prompt = """
    Generate a company structure:
    ```json
    {
        "company": {
            "name": "TechCorp",
            "departments": [
                {
                    "name": "Engineering",
                    "manager": {"id": 1, "name": "Alice"},
                    "employees": [
                        {"id": 2, "name": "Bob", "skills": ["Python", "Go"]}
                    ]
                }
            ]
        }
    }
    ```
    """

    analyzer = PromptAnalyzer()
    suggester = ValidatorSuggester()

    # Analyze simple JSON
    simple_result = analyzer.analyze(simple_prompt)
    simple_suggestions = suggester.suggest_validators(simple_result)

    # Analyze complex JSON
    complex_result = analyzer.analyze(complex_prompt)
    complex_suggestions = suggester.suggest_validators(complex_result)

    print("Simple JSON:")
    print(f"  Suggested validator: {simple_suggestions[0].validator_type if simple_suggestions else 'None'}")

    print("\nComplex JSON:")
    print(f"  Suggested validator: {complex_suggestions[0].validator_type if complex_suggestions else 'None'}")
    print(f"  Has nested structure: {complex_result.json_schema is not None}")
    print()


if __name__ == "__main__":
    print("Enhanced JSON Schema Detection Demo")
    print("=" * 50)
    print()

    demo_nested_object_detection()
    demo_array_of_objects_detection()
    demo_textual_description_detection()
    demo_simple_vs_complex_json()

    print("\nDemo complete! The enhanced detection now supports:")
    print("- Nested objects and arrays")
    print("- Arrays of objects")
    print("- JSON schema inference from textual descriptions")
    print("- Intelligent validator selection based on complexity")
