"""
Generated Task: Generated Task

Description: Automatically generated task from prompt analysis

Generated from: tools/prompt_to_task/examples/story.txt

This task was automatically generated from prompt analysis.
You may need to customize the validation logic for your specific needs.

Original prompt:
----------------
Transform the following story into a structured scene breakdown:

Story: {story_text}

For each scene, provide:
1. Scene number
2. Location/Setting
3. Time of day
4. Characters present
5. Key actions or events
6. Emotional tone
7. Important dialogue snippets

Output format should be:
SCENE [number]: [title]
Location: [setting]
Time: [time of day]
Characters: [list of characters]
Action: [what happens]
Tone: [emotional atmosphere]
Key Dialogue: "[important quotes]"
---

Create between {min_scenes} and {max_scenes} scenes based on the story complexity.
Ensure each scene advances the plot and maintains narrative continuity.
----------------
"""

from typing import Any, Dict, Optional, Type

from validated_llm.base_validator import BaseValidator, ValidationResult
from validated_llm.tasks.base_task import BaseTask


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

        lines = [line.strip() for line in content.strip().split("\n") if line.strip()]

        # Check item count
        if len(lines) < self.min_items:
            errors.append(f"Too few items: {len(lines)} (minimum: {self.min_items})")
        elif len(lines) > self.max_items:
            warnings.append(f"Many items: {len(lines)} (recommended max: {self.max_items})")

        # Check item format
        for i, line in enumerate(lines, 1):
            if not (line.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "*", "-")) or line[0].isdigit()):
                warnings.append(f"Line {i} doesn't follow list format")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings, metadata={"item_count": len(lines)})


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
        return """Transform the following story into a structured scene breakdown:

Story: {story_text}

For each scene, provide:
1. Scene number
2. Location/Setting
3. Time of day
4. Characters present
5. Key actions or events
6. Emotional tone
7. Important dialogue snippets

Output format should be:
SCENE [number]: [title]
Location: [setting]
Time: [time of day]
Characters: [list of characters]
Action: [what happens]
Tone: [emotional atmosphere]
Key Dialogue: "[important quotes]"
---

Create between {min_scenes} and {max_scenes} scenes based on the story complexity.
Ensure each scene advances the plot and maintains narrative continuity.
"""

    @property
    def validator_class(self) -> Type[BaseValidator]:
        return ListValidator

    def get_prompt_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Prepare and validate input data for the prompt."""
        # Ensure all required variables are provided
        required_vars = ["story_text", "min_scenes", "max_scenes"]
        for var in required_vars:
            if var not in kwargs:
                raise ValueError(f"Missing required parameter: {var}")

        return kwargs

    def create_validator(self, **kwargs: Any) -> BaseValidator:
        """Create a configured validator instance."""
        config = {"expected_pattern": "Scene number"}
        config.update(kwargs)
        return self.validator_class(**config)


def example_usage() -> None:
    """
    Example of how to use the GeneratedTask.
    """
    from validated_llm.validation_loop import ValidationLoop

    # Create the task
    task = GeneratedTask()

    # Create validator
    validator = task.create_validator()  # Configuration: {'expected_pattern': 'Scene number'}

    # Create validation loop
    loop = ValidationLoop(default_max_retries=3)

    # Prepare input data
    input_data = {
        "story_text": "example_story_text",
        "min_scenes": "example_min_scenes",
        "max_scenes": "example_max_scenes",
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
