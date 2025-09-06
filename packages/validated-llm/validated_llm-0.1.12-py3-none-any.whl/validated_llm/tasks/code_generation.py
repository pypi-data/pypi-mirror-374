"""
Code generation tasks for creating functions, classes, and complete programs.
"""

from typing import Any, Dict, Optional, Type

from validated_llm.base_validator import BaseValidator
from validated_llm.config import get_task_config
from validated_llm.tasks import BaseTask
from validated_llm.validators.syntax import SyntaxValidator


class CodeGenerationTask(BaseTask):
    """Task for generating code in various programming languages.

    This task generates syntactically correct code based on specifications,
    including functions, classes, or complete programs.

    Example:
        ```python
        task = CodeGenerationTask(language="python")

        result = ValidationLoop(task=task).execute(
            function_name="calculate_fibonacci",
            function_description="Calculate the nth Fibonacci number recursively",
            parameters="n: int",
            return_type="int",
            include_docstring=True,
            include_type_hints=True
        )
        ```
    """

    def __init__(self, language: Optional[str] = None, code_type: str = "function", strict_syntax: bool = True):
        """Initialize the code generation task.

        Args:
            language: Programming language to generate (python, javascript, etc.)
            code_type: Type of code to generate (function, class, program)
            strict_syntax: Whether to enforce strict syntax validation
        """
        # Load config defaults
        config = get_task_config("CodeGenerationTask")

        # Apply config defaults if not explicitly set
        if language is None:
            language = config.get("language", "python")

        self.language = language
        self.code_type = code_type
        self.strict_syntax = strict_syntax
        self._validator = SyntaxValidator(language=language, strict_mode=strict_syntax)

    @property
    def name(self) -> str:
        """Human-readable name for this task."""
        return f"{self.language.title()} {self.code_type.title()} Generation"

    @property
    def description(self) -> str:
        """Description of what this task does."""
        return f"Generate syntactically correct {self.code_type} code in {self.language}"

    @property
    def prompt_template(self) -> str:
        """Get the prompt template for code generation."""
        base_template = """Generate {code_type} code in {language} based on the following specifications:

{specifications}

Requirements:
1. The code must be syntactically correct {language}
2. Follow {language} best practices and idioms
3. Use clear, descriptive variable and function names
4. Include appropriate error handling where needed
"""

        if self.code_type == "function":
            return (
                base_template
                + """
5. Function name: {function_name}
6. Parameters: {parameters}
7. Return type: {return_type}
8. Description: {function_description}
{docstring_requirement}
{type_hints_requirement}

Generate only the function code, no additional explanation."""
            )

        elif self.code_type == "class":
            return (
                base_template
                + """
5. Class name: {class_name}
6. Methods: {methods}
7. Properties: {properties}
8. Description: {class_description}
{inheritance_info}
{docstring_requirement}

Generate only the class code, no additional explanation."""
            )

        else:  # program
            return (
                base_template
                + """
5. Program purpose: {program_purpose}
6. Input/Output: {io_description}
7. Main functionality: {main_functionality}
{imports_requirement}

Generate a complete, runnable program."""
            )

    @property
    def validator_class(self) -> Type[BaseValidator]:
        """Get the validator class for syntax validation."""
        return type(self._validator)

    def prepare_prompt_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Prepare data for the prompt template."""
        # Load config defaults
        config = get_task_config("CodeGenerationTask")

        data = {"language": self.language, "code_type": self.code_type, "specifications": self._build_specifications(**kwargs)}

        # Add language-specific requirements
        if self.language == "python":
            # Use config defaults if not specified
            include_docstring = kwargs.get("include_docstring", config.get("include_docstrings", True))
            include_type_hints = kwargs.get("include_type_hints", config.get("include_type_hints", True))

            data["docstring_requirement"] = "9. Include a comprehensive docstring" if include_docstring else ""
            data["type_hints_requirement"] = "10. Use type hints for all parameters and return values" if include_type_hints else ""
        else:
            data["docstring_requirement"] = "9. Include appropriate documentation comments" if kwargs.get("include_docstring", True) else ""
            data["type_hints_requirement"] = ""

        # Code type specific data
        if self.code_type == "function":
            data.update(
                {
                    "function_name": kwargs.get("function_name", "process_data"),
                    "parameters": kwargs.get("parameters", "data: Any"),
                    "return_type": kwargs.get("return_type", "Any"),
                    "function_description": kwargs.get("function_description", "Process the input data and return results"),
                }
            )

        elif self.code_type == "class":
            data.update(
                {
                    "class_name": kwargs.get("class_name", "DataProcessor"),
                    "methods": kwargs.get("methods", "process(), validate(), save()"),
                    "properties": kwargs.get("properties", "data, config, results"),
                    "class_description": kwargs.get("class_description", "A class for processing and validating data"),
                    "inheritance_info": (f"9. Inherit from: {kwargs.get('base_class')}" if kwargs.get("base_class") else ""),
                }
            )

        else:  # program
            data.update(
                {
                    "program_purpose": kwargs.get("program_purpose", "A command-line utility for data processing"),
                    "io_description": kwargs.get("io_description", "Read from stdin or file, output to stdout"),
                    "main_functionality": kwargs.get("main_functionality", "Parse arguments, process data, display results"),
                    "imports_requirement": ("9. Include all necessary import statements" if self.language in ["python", "javascript", "typescript"] else ""),
                }
            )

        return data

    def _build_specifications(self, **kwargs: Any) -> str:
        """Build detailed specifications from kwargs."""
        specs = []

        # Add custom specifications if provided
        if "specifications" in kwargs:
            specs.append(kwargs["specifications"])

        # Add algorithm details if provided
        if "algorithm" in kwargs:
            specs.append(f"Algorithm: {kwargs['algorithm']}")

        # Add examples if provided
        if "examples" in kwargs:
            specs.append(f"Examples:\n{kwargs['examples']}")

        # Add constraints if provided
        if "constraints" in kwargs:
            specs.append(f"Constraints: {kwargs['constraints']}")

        # Add performance requirements if provided
        if "performance" in kwargs:
            specs.append(f"Performance requirements: {kwargs['performance']}")

        return "\n".join(specs) if specs else "Create well-structured, efficient code"

    def configure_validator(self) -> Dict[str, Any]:
        """Configure the syntax validator."""
        return {"language": self.language, "strict_mode": self.strict_syntax}


class FunctionGenerationTask(CodeGenerationTask):
    """Specialized task for generating functions."""

    def __init__(self, language: str = "python", **kwargs: Any) -> None:
        super().__init__(language=language, code_type="function", **kwargs)


class ClassGenerationTask(CodeGenerationTask):
    """Specialized task for generating classes."""

    def __init__(self, language: str = "python", **kwargs: Any) -> None:
        super().__init__(language=language, code_type="class", **kwargs)


class ProgramGenerationTask(CodeGenerationTask):
    """Specialized task for generating complete programs."""

    def __init__(self, language: str = "python", **kwargs: Any) -> None:
        super().__init__(language=language, code_type="program", **kwargs)
