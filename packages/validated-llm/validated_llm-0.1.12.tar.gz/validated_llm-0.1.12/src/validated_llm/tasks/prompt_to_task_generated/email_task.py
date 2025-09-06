"""
Generated Task: Generated Task

Description: Automatically generated task from prompt analysis

Generated from: tools/prompt_to_task/examples/email.txt

This task was automatically generated from prompt analysis.
You may need to customize the validation logic for your specific needs.

Original prompt:
----------------
Generate a professional email for {recipient_name} regarding {subject_matter}.

The email should include:
- A proper greeting using the recipient's name
- A clear introduction stating the purpose
- Main body with {num_points} key points
- A professional closing
- Your signature as {sender_name} from {company_name}

Requirements:
- The tone should be {tone_style} (formal/casual/friendly)
- Email length should be between 150-300 words
- Include a clear call-to-action if {include_cta} is true
- Make sure to address any concerns about {main_concern}

Format the output as plain text with proper email structure.
----------------
"""

import re
from typing import Any, Dict, Optional, Type

from validated_llm.base_validator import BaseValidator, ValidationResult
from validated_llm.tasks.base_task import BaseTask


class EmailValidator(BaseValidator):
    """Validates email addresses."""

    def __init__(self) -> None:
        super().__init__(name="email_validator", description="Validates email format")
        self.email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    def validate(self, content: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        errors = []

        email = content.strip()
        if not self.email_pattern.match(email):
            errors.append(f"Invalid email format: {email}")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=[], metadata={"email": email})


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
        return """Generate a professional email for {recipient_name} regarding {subject_matter}.

The email should include:
- A proper greeting using the recipient's name
- A clear introduction stating the purpose
- Main body with {num_points} key points
- A professional closing
- Your signature as {sender_name} from {company_name}

Requirements:
- The tone should be {tone_style} (formal/casual/friendly)
- Email length should be between 150-300 words
- Include a clear call-to-action if {include_cta} is true
- Make sure to address any concerns about {main_concern}

Format the output as plain text with proper email structure.
"""

    @property
    def validator_class(self) -> Type[BaseValidator]:
        return EmailValidator

    def get_prompt_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Prepare and validate input data for the prompt."""
        # Ensure all required variables are provided
        required_vars = ["recipient_name", "subject_matter", "num_points", "sender_name", "company_name", "tone_style", "include_cta", "main_concern"]
        for var in required_vars:
            if var not in kwargs:
                raise ValueError(f"Missing required parameter: {var}")

        return kwargs


def example_usage() -> None:
    """
    Example of how to use the GeneratedTask.
    """
    from validated_llm.validation_loop import ValidationLoop

    # Create the task
    task = GeneratedTask()

    # Create validator
    validator = task.create_validator()

    # Create validation loop
    loop = ValidationLoop(default_max_retries=3)

    # Prepare input data
    input_data = {
        "recipient_name": "John Doe",
        "subject_matter": "example_subject_matter",
        "num_points": "example_num_points",
        "sender_name": "John Doe",
        "company_name": "John Doe",
        "tone_style": "example_tone_style",
        "include_cta": "example_include_cta",
        "main_concern": "example_main_concern",
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
