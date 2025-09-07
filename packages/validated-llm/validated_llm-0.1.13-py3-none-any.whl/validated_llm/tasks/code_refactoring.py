"""
Code refactoring task for improving existing code while preserving functionality.
"""

from typing import Any, Dict, Optional, Type

from validated_llm.base_validator import BaseValidator
from validated_llm.tasks import BaseTask
from validated_llm.validators.refactoring import RefactoringValidator


class CodeRefactoringTask(BaseTask):
    """Task for refactoring code to improve quality while preserving functionality.

    This task takes existing code and refactors it to improve:
    - Readability and maintainability
    - Performance and efficiency
    - Code structure and organization
    - Adherence to best practices
    - Reduction of complexity

    Example:
        ```python
        task = CodeRefactoringTask(language="python")

        result = ValidationLoop(task=task).execute(
            original_code=messy_function_code,
            refactoring_goals="reduce complexity, improve naming",
            preserve_api=True,
            target_complexity=8
        )
        ```
    """

    def __init__(self, language: str = "python", check_complexity: bool = True, check_naming: bool = True, check_structure: bool = True, max_complexity: int = 10, refactoring_style: str = "clean_code"):
        """Initialize the code refactoring task.

        Args:
            language: Programming language of the code
            check_complexity: Whether to validate complexity improvements
            check_naming: Whether to check naming conventions
            check_structure: Whether to check structural improvements
            max_complexity: Maximum allowed cyclomatic complexity
            refactoring_style: Style of refactoring ("clean_code", "performance", "functional")
        """
        self.language = language
        self.check_complexity = check_complexity
        self.check_naming = check_naming
        self.check_structure = check_structure
        self.max_complexity = max_complexity
        self.refactoring_style = refactoring_style

        # Validator will be configured with original code during execution
        self._validator_config = {"language": language, "check_complexity": check_complexity, "check_naming": check_naming, "check_structure": check_structure, "max_complexity": max_complexity}

    @property
    def name(self) -> str:
        """Human-readable name for this task."""
        return f"{self.language.title()} Code Refactoring"

    @property
    def description(self) -> str:
        """Description of what this task does."""
        return f"Refactor {self.language} code to improve quality while preserving functionality"

    @property
    def prompt_template(self) -> str:
        """Get the prompt template for code refactoring."""
        style_instructions = self._get_style_instructions()

        return f"""Refactor the following {self.language} code to improve its quality:

```{self.language}
{{original_code}}
```

REFACTORING REQUIREMENTS:
1. Preserve ALL original functionality - the refactored code must behave identically
2. Maintain the same public API (function/class signatures)
3. Improve code quality according to these goals:
   {{refactoring_goals}}

{style_instructions}

SPECIFIC IMPROVEMENTS TO FOCUS ON:
{{improvement_focus}}

CONSTRAINTS:
- Maximum cyclomatic complexity: {self.max_complexity}
- Follow {self.language} best practices and idioms
- Add helpful comments and docstrings where appropriate
- Organize imports properly (if applicable)
{{additional_constraints}}

Generate only the refactored code, no explanations."""

    @property
    def validator_class(self) -> Type[BaseValidator]:
        """Get the validator class for refactoring validation."""
        return RefactoringValidator

    def prepare_prompt_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Prepare data for the prompt template."""
        original_code = kwargs.get("original_code", "")

        # Store original code for validator configuration
        self._original_code = original_code

        # Default refactoring goals
        default_goals = ["Reduce code complexity", "Improve variable and function naming", "Extract repeated code into functions", "Improve error handling", "Enhance code readability"]

        refactoring_goals = kwargs.get("refactoring_goals", ", ".join(default_goals))
        if isinstance(refactoring_goals, list):
            refactoring_goals = ", ".join(refactoring_goals)

        # Build improvement focus based on task configuration
        improvement_focus = self._build_improvement_focus(**kwargs)

        # Additional constraints
        constraints = []
        if kwargs.get("preserve_api", True):
            constraints.append("- Preserve all public function/class interfaces exactly")
        if kwargs.get("preserve_imports", False):
            constraints.append("- Keep the same imports (don't add new dependencies)")
        if kwargs.get("preserve_comments", False):
            constraints.append("- Preserve existing comments and documentation")
        if kwargs.get("target_complexity"):
            constraints.append(f"- Target complexity: {kwargs['target_complexity']}")

        return {"original_code": original_code, "refactoring_goals": refactoring_goals, "improvement_focus": improvement_focus, "additional_constraints": "\n".join(constraints) if constraints else "- None"}

    def _build_improvement_focus(self, **kwargs: Any) -> str:
        """Build specific improvement focus based on configuration."""
        focus_areas = []

        if self.check_complexity:
            focus_areas.append("- Reduce cyclomatic complexity by extracting functions and simplifying logic")

        if self.check_naming:
            focus_areas.append("- Use clear, descriptive names following language conventions")

        if self.check_structure:
            focus_areas.append("- Organize code into logical sections with proper separation of concerns")

        # Add custom focus areas from kwargs
        if "focus_performance" in kwargs and kwargs["focus_performance"]:
            focus_areas.append("- Optimize for performance (reduce loops, use efficient data structures)")

        if "focus_readability" in kwargs and kwargs["focus_readability"]:
            focus_areas.append("- Prioritize readability with clear logic flow and good formatting")

        if "focus_testing" in kwargs and kwargs["focus_testing"]:
            focus_areas.append("- Structure code to be easily testable (dependency injection, pure functions)")

        if "extract_functions" in kwargs and kwargs["extract_functions"]:
            focus_areas.append("- Extract complex logic into well-named helper functions")

        if "reduce_duplication" in kwargs and kwargs["reduce_duplication"]:
            focus_areas.append("- Eliminate code duplication through abstraction")

        return "\n".join(focus_areas) if focus_areas else "- General quality improvements"

    def _get_style_instructions(self) -> str:
        """Get refactoring style-specific instructions."""
        if self.refactoring_style == "clean_code":
            return """
CLEAN CODE PRINCIPLES:
- Single Responsibility: Each function/class should do one thing well
- DRY (Don't Repeat Yourself): Extract common code
- KISS (Keep It Simple): Prefer simple solutions
- Meaningful names: Variables and functions should clearly express intent
- Small functions: Break down complex logic into smaller pieces"""

        elif self.refactoring_style == "performance":
            return """
PERFORMANCE OPTIMIZATION:
- Minimize computational complexity
- Use efficient data structures
- Reduce unnecessary loops and iterations
- Cache computed values when appropriate
- Optimize hot paths in the code"""

        elif self.refactoring_style == "functional":
            return """
FUNCTIONAL PROGRAMMING STYLE:
- Prefer immutability where possible
- Use pure functions without side effects
- Replace loops with map/filter/reduce operations
- Avoid global state
- Use function composition"""

        else:  # modern
            return """
MODERN CODE STYLE:
- Use latest language features appropriately
- Apply modern design patterns
- Ensure code is async-ready if applicable
- Use type hints/annotations where supported
- Follow current best practices"""

    def configure_validator(self) -> Dict[str, Any]:
        """Configure the refactoring validator."""
        config = self._validator_config.copy()

        # Add original code if available
        if hasattr(self, "_original_code"):
            config["original_code"] = self._original_code

        return config


class PerformanceRefactoringTask(CodeRefactoringTask):
    """Specialized task for performance-focused refactoring."""

    def __init__(self, language: str = "python", **kwargs: Any):
        super().__init__(language=language, refactoring_style="performance", check_complexity=True, **kwargs)


class CleanCodeRefactoringTask(CodeRefactoringTask):
    """Specialized task for clean code refactoring."""

    def __init__(self, language: str = "python", **kwargs: Any):
        super().__init__(language=language, refactoring_style="clean_code", check_naming=True, check_structure=True, max_complexity=8, **kwargs)


class ModernizationRefactoringTask(CodeRefactoringTask):
    """Specialized task for modernizing legacy code."""

    def __init__(self, language: str = "python", **kwargs: Any):
        super().__init__(language=language, refactoring_style="modern", check_structure=True, **kwargs)
