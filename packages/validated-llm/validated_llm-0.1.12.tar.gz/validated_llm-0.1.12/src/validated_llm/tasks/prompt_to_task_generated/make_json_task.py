"""
Generated Task: Generated Task

Description: Automatically generated task from prompt analysis

Generated from: tools/prompt_to_task/examples/make-json.txt

This task was automatically generated from prompt analysis.
You may need to customize the validation logic for your specific needs.

Original prompt:
----------------
# Sample Prompts for Testing prompt-to-task Tool

This file contains example prompts to test the conversion tool.

## JSON Generation Prompt

Generate a JSON object representing a customer profile with the following information:

Customer Name: {customer_name}
Email: {email}
Age: {age}
City: {city}

The output should be valid JSON with these required fields:
- "name": customer's full name
- "email": valid email address
- "age": integer between 18 and 100
- "city": customer's city
- "id": unique customer ID (generate random)

Example output:
{
    "id": "cust_12345",
    "name": "John Smith",
    "email": "john@example.com",
    "age": 35,
    "city": "New York"
}

## CSV Generation Prompt

Generate a CSV report for sales data with the following columns:
Date, Product, Quantity, Price, Total

Input data:
Products: {products}
Date Range: {date_range}

Requirements:
- Include header row
- Date format: YYYY-MM-DD
- Price format: 2 decimal places
- Calculate Total = Quantity * Price
- Minimum 5 rows of data

## List Generation Prompt

Create a numbered list of action items for {project_name}:

Project: {project_name}
Priority: {priority}
Due Date: {due_date}

Requirements:
- 5-10 action items
- Each item should be specific and actionable
- Include responsible person where applicable
- Format: "1. Action item description"

## Email Generation Prompt

Compose a professional email for the following:

To: {recipient}
Subject: {subject}
Purpose: {purpose}
Tone: {tone}

The email should:
- Include proper greeting and closing
- Be 50-200 words
- Use {tone} tone throughout
- Include clear call to action
- Be professionally formatted
----------------
"""

from typing import Any, Dict, Type

from validated_llm.base_validator import BaseValidator
from validated_llm.tasks.base_task import BaseTask
from validated_llm.tasks.json_generation import JSONSchemaValidator


class GeneratedTask(BaseTask):
    """
    Automatically generated task from prompt analysis
    """

    @property
    def name(self) -> str:
        return "Generated Task"

    @property
    def description(self) -> str:
        return "Automatically generated task from prompt analysis"

    @property
    def prompt_template(self) -> str:
        return """# Sample Prompts for Testing prompt-to-task Tool

This file contains example prompts to test the conversion tool.

## JSON Generation Prompt

Generate a JSON object representing a customer profile with the following information:

Customer Name: {customer_name}
Email: {email}
Age: {age}
City: {city}

The output should be valid JSON with these required fields:
- "name": customer's full name
- "email": valid email address
- "age": integer between 18 and 100
- "city": customer's city
- "id": unique customer ID (generate random)

Example output:
{
    "id": "cust_12345",
    "name": "John Smith",
    "email": "john@example.com",
    "age": 35,
    "city": "New York"
}

## CSV Generation Prompt

Generate a CSV report for sales data with the following columns:
Date, Product, Quantity, Price, Total

Input data:
Products: {products}
Date Range: {date_range}

Requirements:
- Include header row
- Date format: YYYY-MM-DD
- Price format: 2 decimal places
- Calculate Total = Quantity * Price
- Minimum 5 rows of data

## List Generation Prompt

Create a numbered list of action items for {project_name}:

Project: {project_name}
Priority: {priority}
Due Date: {due_date}

Requirements:
- 5-10 action items
- Each item should be specific and actionable
- Include responsible person where applicable
- Format: "1. Action item description"

## Email Generation Prompt

Compose a professional email for the following:

To: {recipient}
Subject: {subject}
Purpose: {purpose}
Tone: {tone}

The email should:
- Include proper greeting and closing
- Be 50-200 words
- Use {tone} tone throughout
- Include clear call to action
- Be professionally formatted
"""

    @property
    def validator_class(self) -> Type[BaseValidator]:
        return JSONSchemaValidator

    def get_prompt_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Prepare and validate input data for the prompt."""
        # Ensure all required variables are provided
        required_vars = ["customer_name", "email", "age", "city", "products", "date_range", "project_name", "priority", "due_date", "recipient", "subject", "purpose", "tone"]
        for var in required_vars:
            if var not in kwargs:
                raise ValueError(f"Missing required parameter: {var}")

        return kwargs

    def create_validator(self, **kwargs: Any) -> BaseValidator:
        """Create a configured validator instance."""
        config = {
            "schema": {
                "type": "object",
                "properties": {
                    "Age": {"type": "string"},
                    "Subject": {"type": "string"},
                    "following": {"type": "string"},
                    "age": {"type": "string"},
                    "information": {"type": "string"},
                    "name": {"type": "string"},
                    "I": {"type": "string"},
                    "fields": {"type": "string"},
                    "Format": {"type": "string"},
                    "output": {"type": "string"},
                    "city": {"type": "string"},
                    "Requirements": {"type": "string"},
                    "Tone": {"type": "string"},
                    "email": {"type": "string"},
                    "format": {"type": "string"},
                    "Priority": {"type": "string"},
                    "Purpose": {"type": "string"},
                    "data": {"type": "string"},
                    "should": {"type": "string"},
                    "City": {"type": "string"},
                    "id": {"type": "string"},
                    "columns": {"type": "string"},
                    "Range": {"type": "string"},
                    "Date": {"type": "string"},
                    "Project": {"type": "string"},
                    "Email": {"type": "string"},
                },
                "required": [
                    "Age",
                    "Subject",
                    "following",
                    "age",
                    "information",
                    "name",
                    "I",
                    "fields",
                    "Format",
                    "output",
                    "city",
                    "Requirements",
                    "Tone",
                    "email",
                    "format",
                    "Priority",
                    "Purpose",
                    "data",
                    "should",
                    "City",
                    "id",
                    "columns",
                    "Range",
                    "Date",
                    "Project",
                    "Email",
                ],
            },
            "name": "generated_json_validator",
            "description": "Validates generated JSON against schema",
            "strict_mode": True,
        }
        config.update(kwargs)
        # Only pass valid keys to JSONSchemaValidator and ensure correct types
        valid_keys = {"name", "description", "schema", "strict_mode"}
        filtered_config = {k: v for k, v in config.items() if k in valid_keys}
        name = str(filtered_config.get("name", "generated_json_validator"))
        description = str(filtered_config.get("description", "Validates generated JSON against schema"))
        schema = filtered_config.get("schema", config["schema"])
        if not isinstance(schema, dict):
            schema = None
        strict_mode = filtered_config.get("strict_mode", True)
        if not isinstance(strict_mode, bool):
            strict_mode = True
        return JSONSchemaValidator(
            name=name,
            description=description,
            schema=schema,
            strict_mode=strict_mode,
        )


def example_usage() -> None:
    """
    Example of how to use the GeneratedTask.
    """
    from validated_llm.validation_loop import ValidationLoop

    # Create the task
    task = GeneratedTask()

    # Create validator
    validator = (
        task.create_validator()
    )  # Configuration: {'schema': {'type': 'object', 'properties': {'Age': {'type': 'string'}, 'Subject': {'type': 'string'}, 'following': {'type': 'string'}, 'age': {'type': 'string'}, 'information': {'type': 'string'}, 'name': {'type': 'string'}, 'I': {'type': 'string'}, 'fields': {'type': 'string'}, 'Format': {'type': 'string'}, 'output': {'type': 'string'}, 'city': {'type': 'string'}, 'Requirements': {'type': 'string'}, 'Tone': {'type': 'string'}, 'email': {'type': 'string'}, 'format': {'type': 'string'}, 'Priority': {'type': 'string'}, 'Purpose': {'type': 'string'}, 'data': {'type': 'string'}, 'should': {'type': 'string'}, 'City': {'type': 'string'}, 'id': {'type': 'string'}, 'columns': {'type': 'string'}, 'Range': {'type': 'string'}, 'Date': {'type': 'string'}, 'Project': {'type': 'string'}, 'Email': {'type': 'string'}}, 'required': ['Age', 'Subject', 'following', 'age', 'information', 'name', 'I', 'fields', 'Format', 'output', 'city', 'Requirements', 'Tone', 'email', 'format', 'Priority', 'Purpose', 'data', 'should', 'City', 'id', 'columns', 'Range', 'Date', 'Project', 'Email']}}

    # Create validation loop
    loop = ValidationLoop(default_max_retries=3)

    # Prepare input data
    input_data = {
        "customer_name": "John Doe",
        "email": "john@example.com",
        "age": 25,
        "city": "example_city",
        "products": "example_products",
        "date_range": "2024-01-15",
        "project_name": "John Doe",
        "priority": "example_priority",
        "due_date": "2024-01-15",
        "recipient": "example_recipient",
        "subject": "example_subject",
        "purpose": "example_purpose",
        "tone": "example_tone",
    }

    # Execute the task
    try:
        result = loop.execute(prompt_template=task.prompt_template, validator=validator, input_data=input_data)

        if result["success"]:
            print("✅ Task completed successfully!")
            print("Output:", result["output"])
            print(f"Attempts: {result['attempts']}")
        else:
            print("❌ Task failed:")
            if result["validation_result"]:
                for error in result["validation_result"].errors:
                    print(f"  - {error}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    example_usage()
