"""
Code generator that creates BaseTask subclasses from analysis results.

This module generates complete Python code for tasks and validators
based on prompt analysis and validator suggestions.
"""

import re
from typing import List, Optional

from .analyzer import AnalysisResult
from .validator_suggester import ValidatorSuggestion


class TaskCodeGenerator:
    """
    Generates BaseTask subclass code from analysis results.

    Creates complete Python files with:
    - Task class inheriting from BaseTask
    - Custom validator classes (if needed)
    - Proper imports and documentation
    """

    def __init__(self) -> None:
        """Initialize the code generator."""
        self.base_imports = ["from typing import Any, Dict, List, Optional, Type", "from validated_llm.base_validator import BaseValidator, ValidationResult", "from validated_llm.tasks.base_task import BaseTask"]

    def generate_task_code(self, analysis: AnalysisResult, suggestions: List[ValidatorSuggestion], task_name: str, task_description: str, prompt_template: str, source_file: Optional[str] = None) -> str:
        """
        Generate complete task code.

        Args:
            analysis: Prompt analysis results
            suggestions: Validator suggestions
            task_name: Name for the generated task class
            task_description: Description of what the task does
            prompt_template: The original prompt template

        Returns:
            Complete Python code as string
        """
        # Generate task class name
        class_name = self._to_class_name(task_name)

        # Prepare imports
        imports = self._generate_imports(suggestions)

        # Generate custom validators (if any)
        custom_validators = self._generate_custom_validators(suggestions)

        # Generate main task class
        task_class = self._generate_task_class(class_name, task_name, task_description, analysis, suggestions, prompt_template)

        # Generate example usage
        example_usage = self._generate_example_usage(class_name, analysis, suggestions)

        # Build header documentation
        header_lines = [
            '"""',
            f"Generated Task: {task_name}",
            "",
            f"Description: {task_description}",
            "",
        ]

        if source_file:
            header_lines.extend(
                [
                    f"Generated from: {source_file}",
                    "",
                ]
            )

        header_lines.extend(
            [
                "This task was automatically generated from prompt analysis.",
                "You may need to customize the validation logic for your specific needs.",
                "",
                "Original prompt:",
                "----------------",
            ]
        )

        # Add the original prompt as a comment
        for line in prompt_template.strip().split("\n"):
            header_lines.append(line)

        header_lines.extend(
            [
                "----------------",
                '"""',
            ]
        )

        # Combine all parts
        code_parts = [
            *header_lines,
            "",
            *imports,
            "",
            *custom_validators,
            task_class,
            "",
            example_usage,
        ]

        return "\n".join(code_parts)

    def _to_class_name(self, task_name: str) -> str:
        """Convert task name to valid Python class name."""
        # Remove special characters and convert to PascalCase
        words = re.findall(r"[a-zA-Z0-9]+", task_name)
        class_name = "".join(word.capitalize() for word in words)

        # Ensure it ends with 'Task'
        if not class_name.endswith("Task"):
            class_name += "Task"

        return class_name

    def _generate_imports(self, suggestions: List[ValidatorSuggestion]) -> List[str]:
        """Generate import statements."""
        imports = self.base_imports.copy()

        # Add imports for built-in validators
        builtin_imports = set()
        for suggestion in suggestions:
            if suggestion.is_builtin and suggestion.import_path != "custom":
                builtin_imports.add(suggestion.import_path)

        for import_path in builtin_imports:
            # Extract validator class from import path
            module_parts = import_path.split(".")
            if len(module_parts) >= 3:  # validated_llm.tasks.module_name
                module_parts[-1]
                class_name = suggestion.validator_type
                imports.append(f"from {import_path} import {class_name}")

        # Add additional imports for custom validators
        custom_imports = set()
        for suggestion in suggestions:
            if not suggestion.is_builtin:
                if "email" in suggestion.validator_type.lower():
                    custom_imports.add("import re")
                elif "url" in suggestion.validator_type.lower():
                    custom_imports.add("import re")
                elif "json" in suggestion.validator_type.lower():
                    custom_imports.add("import json")

        imports.extend(sorted(custom_imports))
        return imports

    def _generate_custom_validators(self, suggestions: List[ValidatorSuggestion]) -> List[str]:
        """Generate custom validator classes."""
        custom_code = []

        for suggestion in suggestions:
            if not suggestion.is_builtin and suggestion.custom_code:
                custom_code.extend([suggestion.custom_code.strip(), "", ""])

        return custom_code

    def _generate_task_class(self, class_name: str, task_name: str, task_description: str, analysis: AnalysisResult, suggestions: List[ValidatorSuggestion], prompt_template: str) -> str:
        """Generate the main task class."""

        # Get primary validator
        primary_validator = suggestions[0] if suggestions else None

        lines = [
            f"class {class_name}(BaseTask):",
            f'    """',
            f"    {task_description}",
            f'    """',
            f"",
            f"    @property",
            f"    def name(self) -> str:",
            f'        return "{task_name}"',
            f"",
            f"    @property",
            f"    def description(self) -> str:",
            f'        return "{task_description}"',
            f"",
            f"    @property",
            f"    def prompt_template(self) -> str:",
            f'        return """{prompt_template}"""',
            f"",
            f"    @property",
            f"    def validator_class(self) -> Type[BaseValidator]:",
        ]

        if primary_validator:
            lines.append(f"        return {primary_validator.validator_type}")
        else:
            lines.append(f"        return BaseValidator")

        # Add custom prompt data preparation if template variables exist
        if analysis.template_variables:
            lines.extend(
                [
                    f"",
                    f"    def get_prompt_data(self, **kwargs: Any) -> Dict[str, Any]:",
                    f'        """Prepare and validate input data for the prompt."""',
                    f"        # Ensure all required variables are provided",
                    f"        required_vars = {analysis.template_variables}",
                    f"        for var in required_vars:",
                    f"            if var not in kwargs:",
                    f'                raise ValueError(f"Missing required parameter: {{var}}")',
                    f"        ",
                    f"        return kwargs",
                ]
            )

        # Add validator creation method if configuration is needed
        if primary_validator and primary_validator.config:
            lines.extend(
                [
                    f"",
                    f"    def create_validator(self, **kwargs: Any) -> BaseValidator:",
                    f'        """Create a configured validator instance."""',
                    f"        config = {primary_validator.config}",
                    f"        config.update(kwargs)",
                    f"        return self.validator_class(**config)",
                ]
            )

        return "\n".join(lines)

    def _generate_example_usage(self, class_name: str, analysis: AnalysisResult, suggestions: List[ValidatorSuggestion]) -> str:
        """Generate example usage code."""

        lines = [
            "def example_usage():",
            '    """',
            f"    Example of how to use the {class_name}.",
            '    """',
            "    from validated_llm.validation_loop import ValidationLoop",
            "",
            f"    # Create the task",
            f"    task = {class_name}()",
            "",
            f"    # Create validator",
            f"    validator = task.create_validator()",
        ]

        if suggestions and hasattr(suggestions[0], "config") and suggestions[0].config:
            lines[-1] += f"  # Configuration: {suggestions[0].config}"

        lines.extend(["", "    # Create validation loop", "    loop = ValidationLoop(default_max_retries=3)", "", "    # Prepare input data"])

        # Generate example input data
        if analysis.template_variables:
            input_data = {}
            for var in analysis.template_variables:
                if "name" in var.lower():
                    input_data[var] = '"John Doe"'
                elif "email" in var.lower():
                    input_data[var] = '"john@example.com"'
                elif "age" in var.lower() or "number" in var.lower():
                    input_data[var] = "25"
                elif "date" in var.lower():
                    input_data[var] = '"2024-01-15"'
                else:
                    input_data[var] = f'"example_{var}"'

            lines.append(f"    input_data = {{")
            for var, value in input_data.items():
                lines.append(f'        "{var}": {value},')
            lines.append(f"    }}")
        else:
            lines.append("    input_data = {}  # Add your input parameters here")

        lines.extend(
            [
                "",
                "    # Execute the task",
                "    try:",
                "        result = loop.execute(",
                "            prompt_template=task.prompt_template,",
                "            validator=validator,",
                "            input_data=input_data",
                "        )",
                "",
                '        if result["success"]:',
                '            print("✅ Task completed successfully!")',
                '            print("Output:", result["output"])',
                "            print(f\"Attempts: {result['attempts']}\")",
                "        else:",
                '            print("❌ Task failed:")',
                '            if result["validation_result"]:',
                '                for error in result["validation_result"].errors:',
                '                    print(f"  - {error}")',
                "",
                "    except Exception as e:",
                '        print(f"❌ Error: {e}")',
                "",
                "",
                'if __name__ == "__main__":',
                "    example_usage()",
            ]
        )

        return "\n".join(lines)

    def generate_validator_code_only(self, suggestion: ValidatorSuggestion) -> str:
        """Generate code for a single custom validator."""
        if suggestion.is_builtin:
            return f"# Built-in validator: {suggestion.validator_type} from {suggestion.import_path}"

        if not suggestion.custom_code:
            return f"# No custom code available for {suggestion.validator_type}"

        imports = ["from typing import Any, Dict, Optional", "from validated_llm.base_validator import BaseValidator, ValidationResult"]

        # Add specific imports based on validator type
        if "email" in suggestion.validator_type.lower() or "url" in suggestion.validator_type.lower():
            imports.append("import re")
        elif "json" in suggestion.validator_type.lower():
            imports.append("import json")

        code_parts = ['"""', f"Custom Validator: {suggestion.validator_type}", "", f"Description: {suggestion.description}", '"""', "", *imports, "", suggestion.custom_code.strip()]

        return "\n".join(code_parts)
