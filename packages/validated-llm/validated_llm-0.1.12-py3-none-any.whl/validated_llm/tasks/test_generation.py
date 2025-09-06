"""
Test generation tasks for creating unit tests with automatic validation.
"""

from typing import Any, Dict, Type

from validated_llm.base_validator import BaseValidator
from validated_llm.tasks import BaseTask
from validated_llm.validators.test import UnitTestValidator


class TestGenerationTask(BaseTask):
    """Task for generating comprehensive unit tests.

    This task generates test code that automatically validates against
    testing best practices, ensuring proper test structure, coverage,
    and quality.

    Example:
        ```python
        task = TestGenerationTask(language="python")

        result = ValidationLoop(task=task).execute(
            function_to_test="factorial",
            function_signature="factorial(n: int) -> int",
            function_description="Calculate factorial of n",
            test_scenarios="normal cases, edge cases, error cases"
        )
        ```
    """

    def __init__(
        self,
        language: str = "python",
        test_framework: str = "auto",
        min_test_functions: int = 3,
        require_edge_cases: bool = True,
        require_error_tests: bool = True,
        include_setup_teardown: bool = False,
        test_style: str = "comprehensive",
    ):
        """Initialize the test generation task.

        Args:
            language: Programming language for tests
            test_framework: Testing framework to use ("auto", "unittest", "pytest", etc.)
            min_test_functions: Minimum number of test functions to generate
            require_edge_cases: Whether to require edge case tests
            require_error_tests: Whether to require error/exception tests
            include_setup_teardown: Whether to include setup/teardown methods
            test_style: Style of tests ("comprehensive", "minimal", "bdd")
        """
        self.language = language
        self.test_framework = test_framework
        self.min_test_functions = min_test_functions
        self.require_edge_cases = require_edge_cases
        self.require_error_tests = require_error_tests
        self.include_setup_teardown = include_setup_teardown
        self.test_style = test_style

        # Create validator with matching requirements
        self._validator = UnitTestValidator(
            language=language, min_test_functions=min_test_functions, require_edge_cases=require_edge_cases, require_error_tests=require_error_tests, require_setup_teardown=include_setup_teardown, check_documentation=True
        )

    @property
    def name(self) -> str:
        """Human-readable name for this task."""
        return f"{self.language.title()} Test Generation"

    @property
    def description(self) -> str:
        """Description of what this task does."""
        return f"Generate comprehensive unit tests in {self.language} with automatic validation"

    @property
    def prompt_template(self) -> str:
        """Get the prompt template for test generation."""
        framework_instruction = self._get_framework_instruction()

        base_template = f"""Generate comprehensive unit tests in {self.language} for the following specification:

{{test_specification}}

{framework_instruction}

REQUIREMENTS:
1. Generate at least {self.min_test_functions} test functions
2. Test multiple scenarios: normal cases, edge cases, error conditions
3. Include proper assertions/expectations
4. Follow {self.language} testing best practices
5. Use descriptive test names that explain what is being tested
6. Include test documentation/comments"""

        if self.require_edge_cases:
            base_template += "\n7. Include edge case tests (empty inputs, boundary values, null/None cases)"

        if self.require_error_tests:
            base_template += "\n8. Include error/exception tests for invalid inputs"

        if self.include_setup_teardown:
            base_template += "\n9. Include setup and teardown methods if needed"

        style_instruction = self._get_style_instruction()

        return (
            base_template
            + f"""

{style_instruction}

Generate only the test code, no additional explanation."""
        )

    @property
    def validator_class(self) -> Type[BaseValidator]:
        """Get the validator class for test validation."""
        return UnitTestValidator

    def prepare_prompt_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Prepare data for the prompt template."""
        specification = self._build_test_specification(**kwargs)

        return {"test_specification": specification}

    def _build_test_specification(self, **kwargs: Any) -> str:
        """Build test specification from kwargs."""
        specs = []

        # Function/class to test
        if "function_to_test" in kwargs:
            specs.append(f"Function to test: {kwargs['function_to_test']}")

            if "function_signature" in kwargs:
                specs.append(f"Function signature: {kwargs['function_signature']}")

            if "function_description" in kwargs:
                specs.append(f"Function description: {kwargs['function_description']}")

        elif "class_to_test" in kwargs:
            specs.append(f"Class to test: {kwargs['class_to_test']}")

            if "class_methods" in kwargs:
                specs.append(f"Methods to test: {kwargs['class_methods']}")

            if "class_description" in kwargs:
                specs.append(f"Class description: {kwargs['class_description']}")

        # Test scenarios
        if "test_scenarios" in kwargs:
            specs.append(f"Test scenarios: {kwargs['test_scenarios']}")

        # Expected behavior
        if "expected_behavior" in kwargs:
            specs.append(f"Expected behavior: {kwargs['expected_behavior']}")

        # Input/output examples
        if "examples" in kwargs:
            specs.append(f"Examples: {kwargs['examples']}")

        # Error conditions
        if "error_conditions" in kwargs:
            specs.append(f"Error conditions to test: {kwargs['error_conditions']}")

        # Dependencies or setup
        if "dependencies" in kwargs:
            specs.append(f"Dependencies/setup required: {kwargs['dependencies']}")

        # Custom requirements
        if "requirements" in kwargs:
            specs.append(f"Additional requirements: {kwargs['requirements']}")

        return "\n".join(specs) if specs else "Generate tests for the provided code"

    def _get_framework_instruction(self) -> str:
        """Get framework-specific instructions."""
        if self.test_framework == "auto":
            framework_map = {
                "python": "Use pytest or unittest",
                "javascript": "Use Jest or Mocha",
                "java": "Use JUnit",
                "go": "Use Go testing package",
                "rust": "Use Rust testing framework",
                "csharp": "Use NUnit or MSTest",
            }
            framework = framework_map.get(self.language, "Use appropriate testing framework")
        else:
            framework = f"Use {self.test_framework}"

        return f"TESTING FRAMEWORK: {framework}"

    def _get_style_instruction(self) -> str:
        """Get style-specific instructions."""
        if self.test_style == "comprehensive":
            return """
TEST STYLE: Comprehensive
- Write thorough tests covering all code paths
- Include detailed test descriptions and comments
- Test both happy path and error conditions
- Use meaningful test data and assertions"""

        elif self.test_style == "minimal":
            return """
TEST STYLE: Minimal
- Write essential tests covering main functionality
- Focus on critical paths and obvious edge cases
- Keep tests concise but complete"""

        elif self.test_style == "bdd":
            return """
TEST STYLE: Behavior-Driven Development (BDD)
- Write tests that describe behavior from user perspective
- Use Given/When/Then structure in test names or comments
- Focus on business requirements and user scenarios"""

        else:
            return """
TEST STYLE: Standard
- Follow language-specific testing conventions
- Balance thoroughness with maintainability"""

    def configure_validator(self) -> Dict[str, Any]:
        """Configure the test validator."""
        return {
            "language": self.language,
            "min_test_functions": self.min_test_functions,
            "require_edge_cases": self.require_edge_cases,
            "require_error_tests": self.require_error_tests,
            "require_setup_teardown": self.include_setup_teardown,
            "check_documentation": True,
        }


class UnitTestGenerationTask(TestGenerationTask):
    """Specialized task for generating unit tests."""

    def __init__(self, language: str = "python", **kwargs: Any):
        super().__init__(language=language, test_style="comprehensive", min_test_functions=3, require_edge_cases=True, require_error_tests=True, **kwargs)


class IntegrationTestGenerationTask(TestGenerationTask):
    """Specialized task for generating integration tests."""

    def __init__(self, language: str = "python", **kwargs: Any):
        super().__init__(language=language, test_style="comprehensive", min_test_functions=2, require_edge_cases=False, require_error_tests=True, include_setup_teardown=True, **kwargs)


class BDDTestGenerationTask(TestGenerationTask):
    """Specialized task for generating BDD-style tests."""

    def __init__(self, language: str = "python", **kwargs: Any):
        super().__init__(language=language, test_style="bdd", min_test_functions=3, require_edge_cases=True, require_error_tests=True, **kwargs)
