"""Tests for enhanced JSON schema detection with nested structures."""

import pytest

from tools.prompt_to_task.analyzer import PromptAnalyzer
from tools.prompt_to_task.validator_suggester import ValidatorSuggester


class TestNestedJSONDetection:
    """Test cases for detecting nested JSON structures in prompts."""

    def test_detect_nested_object(self) -> None:
        """Test detection of nested objects in JSON."""
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
            },
            "preferences": {
                "language": "en",
                "notifications": true
            }
        }
        ```
        """

        analyzer = PromptAnalyzer()
        result = analyzer.analyze(prompt)

        assert result.output_format == "json"
        assert result.json_schema is not None

        # Check that nested structure is detected
        schema = result.json_schema
        assert schema["type"] == "object"
        assert "contact" in schema["properties"]
        assert schema["properties"]["contact"]["type"] == "object"
        assert "address" in schema["properties"]["contact"]["properties"]
        assert schema["properties"]["contact"]["properties"]["address"]["type"] == "object"

        # Check that ValidatorSuggester recommends JSONSchemaValidator
        suggester = ValidatorSuggester()
        suggestions = suggester.suggest_validators(result)

        assert len(suggestions) > 0
        primary = suggestions[0]
        assert primary.validator_type == "JSONSchemaValidator"
        assert primary.import_path == "validated_llm.validators.json_schema"
        assert primary.confidence >= 0.89  # Allow for floating point precision

    def test_detect_array_of_objects(self) -> None:
        """Test detection of arrays containing objects."""
        prompt = """
        Generate a list of products in JSON format:

        ```json
        [
            {
                "id": 1,
                "name": "Product A",
                "price": 29.99,
                "categories": ["electronics", "gadgets"],
                "specs": {
                    "weight": "200g",
                    "dimensions": "10x5x2cm"
                }
            },
            {
                "id": 2,
                "name": "Product B",
                "price": 49.99,
                "categories": ["home", "kitchen"],
                "specs": {
                    "weight": "500g",
                    "dimensions": "20x15x10cm"
                }
            }
        ]
        ```
        """

        analyzer = PromptAnalyzer()
        result = analyzer.analyze(prompt)

        assert result.output_format == "json"
        assert result.json_schema is not None

        # Check array of objects detection
        schema = result.json_schema
        assert schema["type"] == "array"
        assert schema["items"]["type"] == "object"
        assert "specs" in schema["items"]["properties"]
        assert schema["items"]["properties"]["specs"]["type"] == "object"
        assert "categories" in schema["items"]["properties"]
        assert schema["items"]["properties"]["categories"]["type"] == "array"

    def test_detect_mixed_nested_structures(self) -> None:
        """Test detection of mixed nested arrays and objects."""
        prompt = """
        Create a course catalog in JSON:

        ```json
        {
            "school": "Tech University",
            "semester": "Fall 2024",
            "courses": [
                {
                    "code": "CS101",
                    "title": "Introduction to Programming",
                    "instructor": {
                        "name": "Dr. Smith",
                        "email": "smith@university.edu"
                    },
                    "schedule": [
                        {
                            "day": "Monday",
                            "time": "10:00-11:30",
                            "room": "A101"
                        },
                        {
                            "day": "Wednesday",
                            "time": "10:00-11:30",
                            "room": "A101"
                        }
                    ]
                }
            ]
        }
        ```
        """

        analyzer = PromptAnalyzer()
        result = analyzer.analyze(prompt)

        assert result.output_format == "json"
        assert result.json_schema is not None

        # Verify complex nested structure
        schema = result.json_schema
        assert schema["type"] == "object"
        assert "courses" in schema["properties"]
        assert schema["properties"]["courses"]["type"] == "array"

        # Check nested course structure
        course_schema = schema["properties"]["courses"]["items"]
        assert course_schema["type"] == "object"
        assert "instructor" in course_schema["properties"]
        assert course_schema["properties"]["instructor"]["type"] == "object"
        assert "schedule" in course_schema["properties"]
        assert course_schema["properties"]["schedule"]["type"] == "array"
        assert course_schema["properties"]["schedule"]["items"]["type"] == "object"

        # Verify JSONSchemaValidator is recommended
        suggester = ValidatorSuggester()
        suggestions = suggester.suggest_validators(result)
        primary = suggestions[0]
        assert primary.validator_type == "JSONSchemaValidator"

    def test_detect_json_without_code_blocks(self) -> None:
        """Test JSON detection when example is not in code blocks."""
        prompt = """
        Generate a configuration file with the following structure:

        The output should be JSON with this format:
        {
            "server": {
                "host": "localhost",
                "port": 8080,
                "ssl": {
                    "enabled": true,
                    "cert": "/path/to/cert.pem"
                }
            },
            "database": {
                "type": "postgresql",
                "connection": {
                    "host": "db.example.com",
                    "port": 5432
                }
            }
        }
        """

        analyzer = PromptAnalyzer()
        result = analyzer.analyze(prompt)

        assert result.output_format == "json"
        assert result.json_schema is not None

        # Check nested detection even without code blocks
        schema = result.json_schema
        assert "server" in schema["properties"]
        assert schema["properties"]["server"]["type"] == "object"
        assert "ssl" in schema["properties"]["server"]["properties"]

    def test_detect_json_from_descriptions(self) -> None:
        """Test JSON schema inference from textual descriptions."""
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

        assert result.output_format == "json"
        assert result.json_schema is not None

        schema = result.json_schema
        assert schema["properties"]["id"]["type"] == "number"
        assert schema["properties"]["emails"]["type"] == "array"
        assert schema["properties"]["profile"]["type"] == "object"
        # Experience should be nested under profile
        assert "experience" in schema["properties"]["profile"]["properties"]
        assert schema["properties"]["profile"]["properties"]["experience"]["type"] == "array"
        assert schema["properties"]["profile"]["properties"]["experience"]["items"]["type"] == "object"

    def test_simple_json_uses_basic_validator(self) -> None:
        """Test that simple JSON structures use the basic JSONValidator."""
        prompt = """
        Generate a simple user object:

        ```json
        {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "active": true
        }
        ```
        """

        analyzer = PromptAnalyzer()
        result = analyzer.analyze(prompt)

        suggester = ValidatorSuggester()
        suggestions = suggester.suggest_validators(result)

        # Should recommend simple JSONValidator for flat structure
        primary = suggestions[0]
        assert primary.validator_type == "JSONValidator"
        assert primary.import_path == "validated_llm.tasks.json_generation"

    def test_confidence_levels(self) -> None:
        """Test confidence levels for different JSON complexity."""
        # Very clear nested JSON
        complex_prompt = """
        Generate complex nested JSON:
        ```json
        {
            "data": {
                "items": [
                    {"nested": {"deep": {"value": 1}}}
                ]
            }
        }
        ```
        """

        analyzer = PromptAnalyzer()
        suggester = ValidatorSuggester()

        result = analyzer.analyze(complex_prompt)
        suggestions = suggester.suggest_validators(result)
        assert suggestions[0].confidence >= 0.89  # Allow for floating point precision

        # Simple JSON
        simple_prompt = "Return JSON with name and age fields"
        result = analyzer.analyze(simple_prompt)
        suggestions = suggester.suggest_validators(result)
        assert suggestions[0].confidence < 0.9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
