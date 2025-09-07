"""
Test validator for validating test code quality and completeness.
"""

import ast
import re
from typing import Any, Dict, List, Optional, Set, Union

from validated_llm.base_validator import BaseValidator, ValidationResult


class UnitTestValidator(BaseValidator):
    """Validator for test code quality and completeness.

    This validator checks that generated test code follows best practices:
    - Has proper test function naming (test_*, *_test)
    - Contains assertions
    - Tests different scenarios (positive, negative, edge cases)
    - Has appropriate test structure
    - Covers error conditions
    - Uses proper test frameworks

    Example:
        ```python
        # Basic test validation
        validator = TestValidator(language="python")
        result = validator.validate('''
        def test_addition():
            assert add(2, 3) == 5
            assert add(0, 0) == 0
            assert add(-1, 1) == 0
        ''')

        # With coverage requirements
        validator = TestValidator(
            language="python",
            min_test_functions=3,
            require_edge_cases=True,
            require_error_tests=True
        )
        ```
    """

    SUPPORTED_LANGUAGES = {
        "python": {
            "test_patterns": [r"^test_\w+", r"\w+_test$"],
            "assertion_patterns": [
                r"assert\s+",
                r"self\.assert\w+\(",
                r"unittest\.TestCase",
                r"pytest\.",
                r"self\.assertEqual\(",
                r"self\.assertTrue\(",
                r"self\.assertFalse\(",
                r"self\.assertRaises\(",
            ],
            "frameworks": ["unittest", "pytest", "nose2"],
            "imports": ["unittest", "pytest", "nose2", "mock", "unittest.mock"],
        },
        "javascript": {
            "test_patterns": [r"test\s*\(", r"it\s*\(", r"describe\s*\("],
            "assertion_patterns": [
                r"expect\(",
                r"assert\.",
                r"should\.",
                r"toBe\(",
                r"toEqual\(",
                r"toThrow\(",
            ],
            "frameworks": ["jest", "mocha", "jasmine", "chai"],
            "imports": ["jest", "mocha", "chai", "sinon"],
        },
        "java": {
            "test_patterns": [r"@Test", r"^test\w+", r"\w+Test$"],
            "assertion_patterns": [
                r"assertEquals\(",
                r"assertTrue\(",
                r"assertFalse\(",
                r"assertNotNull\(",
                r"assertThrows\(",
                r"Assert\.",
            ],
            "frameworks": ["junit", "testng"],
            "imports": ["org.junit", "org.testng"],
        },
        "go": {
            "test_patterns": [r"^Test\w+", r"func\s+Test\w+"],
            "assertion_patterns": [
                r"t\.Error",  # Matches t.Error, t.Errorf, etc.
                r"t\.Fatal",  # Matches t.Fatal, t.Fatalf, etc.
                r"t\.Fail",  # Matches t.Fail, t.FailNow, etc.
                r"assert\.",
                r"require\.",
            ],
            "frameworks": ["testing", "testify"],
            "imports": ["testing", "github.com/stretchr/testify"],
        },
    }

    def __init__(
        self,
        language: str = "python",
        min_test_functions: int = 1,
        min_assertions_per_test: int = 1,
        require_edge_cases: bool = False,
        require_error_tests: bool = False,
        require_setup_teardown: bool = False,
        check_naming: bool = True,
        check_documentation: bool = False,
    ):
        """Initialize the test validator.

        Args:
            language: Programming language of the tests
            min_test_functions: Minimum number of test functions required
            min_assertions_per_test: Minimum assertions per test function
            require_edge_cases: Whether to require edge case testing
            require_error_tests: Whether to require error/exception testing
            require_setup_teardown: Whether to require setup/teardown methods
            check_naming: Whether to validate test naming conventions
            check_documentation: Whether to require test documentation
        """
        self.language = language.lower()
        if self.language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {language}. " f"Supported: {', '.join(self.SUPPORTED_LANGUAGES.keys())}")

        self.min_test_functions = min_test_functions
        self.min_assertions_per_test = min_assertions_per_test
        self.require_edge_cases = require_edge_cases
        self.require_error_tests = require_error_tests
        self.require_setup_teardown = require_setup_teardown
        self.check_naming = check_naming
        self.check_documentation = check_documentation

        self.config = self.SUPPORTED_LANGUAGES[self.language]

    def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate test code quality and completeness.

        Args:
            output: The test code to validate
            context: Optional validation context

        Returns:
            ValidationResult containing test quality assessment
        """
        errors: List[str] = []
        warnings: List[str] = []
        metadata: Dict[str, Any] = {"language": self.language}

        if self.language == "python":
            self._validate_python_tests(output, errors, warnings, metadata)
        elif self.language == "javascript":
            self._validate_javascript_tests(output, errors, warnings, metadata)
        elif self.language == "java":
            self._validate_java_tests(output, errors, warnings, metadata)
        elif self.language == "go":
            self._validate_go_tests(output, errors, warnings, metadata)

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings, metadata=metadata)

    def _validate_python_tests(self, code: str, errors: List[str], warnings: List[str], metadata: Dict[str, Any]) -> None:
        """Validate Python test code using AST analysis."""
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            errors.append(f"Invalid Python syntax: {e}")
            return

        test_functions = []
        classes = []
        imports = []

        # Analyze AST
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if self._is_test_function(node.name):
                    test_functions.append(node)
            elif isinstance(node, ast.ClassDef):
                classes.append(node)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(node)

        metadata["test_functions"] = len(test_functions)
        metadata["test_classes"] = len(classes)
        metadata["imports"] = len(imports)

        # Check minimum test functions
        if len(test_functions) < self.min_test_functions:
            errors.append(f"Insufficient test functions: found {len(test_functions)}, " f"required {self.min_test_functions}")

        # Validate each test function
        for func in test_functions:
            self._validate_test_function(func, code, errors, warnings, metadata)

        # Check for test framework imports
        has_test_framework = self._check_test_framework_imports(imports, errors, warnings)
        metadata["has_test_framework"] = has_test_framework

        # Check for setup/teardown if required
        if self.require_setup_teardown:
            self._check_setup_teardown(tree, errors, warnings)

        # Check for edge cases and error tests
        if self.require_edge_cases:
            self._check_edge_cases(test_functions, code, warnings)

        if self.require_error_tests:
            self._check_error_tests(test_functions, code, errors, warnings)

    def _validate_javascript_tests(self, code: str, errors: List[str], warnings: List[str], metadata: Dict[str, Any]) -> None:
        """Validate JavaScript/TypeScript test code."""
        # Count test blocks and assertions
        test_blocks = self._count_patterns(code, self.config["test_patterns"])
        assertions = self._count_patterns(code, self.config["assertion_patterns"])

        metadata["test_blocks"] = test_blocks
        metadata["assertions"] = assertions

        if test_blocks < self.min_test_functions:
            errors.append(f"Insufficient test blocks: found {test_blocks}, " f"required {self.min_test_functions}")

        if assertions == 0:
            errors.append("No assertions found in test code")
        elif assertions < test_blocks * self.min_assertions_per_test:
            warnings.append(f"Low assertion count: {assertions} assertions for {test_blocks} tests")

        # Check for test framework usage
        framework_found = any(fw in code for fw in self.config["frameworks"])
        metadata["has_test_framework"] = framework_found

        if not framework_found:
            warnings.append("No recognized test framework detected")

    def _validate_java_tests(self, code: str, errors: List[str], warnings: List[str], metadata: Dict[str, Any]) -> None:
        """Validate Java test code."""
        test_methods = self._count_patterns(code, self.config["test_patterns"])
        assertions = self._count_patterns(code, self.config["assertion_patterns"])

        metadata["test_methods"] = test_methods
        metadata["assertions"] = assertions

        if test_methods < self.min_test_functions:
            errors.append(f"Insufficient test methods: found {test_methods}, " f"required {self.min_test_functions}")

        if assertions == 0:
            errors.append("No assertions found in test code")

        # Check for JUnit annotations
        if "@Test" not in code:
            warnings.append("No @Test annotations found")

        # Check for test framework imports
        framework_found = any(import_name in code for import_name in self.config["imports"])
        metadata["has_test_framework"] = framework_found

        if not framework_found:
            warnings.append("No JUnit/TestNG imports detected")

    def _validate_go_tests(self, code: str, errors: List[str], warnings: List[str], metadata: Dict[str, Any]) -> None:
        """Validate Go test code."""
        test_functions = self._count_patterns(code, self.config["test_patterns"])
        assertions = self._count_patterns(code, self.config["assertion_patterns"])

        metadata["test_functions"] = test_functions
        metadata["assertions"] = assertions

        if test_functions < self.min_test_functions:
            errors.append(f"Insufficient test functions: found {test_functions}, " f"required {self.min_test_functions}")

        if assertions == 0:
            errors.append("No test assertions found")

        # Check for testing package import
        if 'import "testing"' not in code and "testing" not in code:
            errors.append("Missing 'testing' package import")

        # Check for proper test function signature
        if test_functions > 0 and "*testing.T" not in code:
            warnings.append("Test functions should accept *testing.T parameter")

    def _is_test_function(self, func_name: str) -> bool:
        """Check if function name follows test naming conventions."""
        if not self.check_naming:
            return True

        for pattern in self.config["test_patterns"]:
            if re.match(pattern, func_name):
                return True
        return False

    def _validate_test_function(self, func: ast.FunctionDef, code: str, errors: List[str], warnings: List[str], metadata: Dict[str, Any]) -> None:
        """Validate individual test function."""
        # Count assertions in this function
        func_source = ast.get_source_segment(code, func)
        if func_source:
            assertions = self._count_patterns(func_source, self.config["assertion_patterns"])

            if assertions < self.min_assertions_per_test:
                warnings.append(f"Test function '{func.name}' has {assertions} assertions, " f"expected at least {self.min_assertions_per_test}")

        # Check for docstring if required
        if self.check_documentation:
            docstring = ast.get_docstring(func)
            if not docstring:
                warnings.append(f"Test function '{func.name}' lacks documentation")

    def _check_test_framework_imports(self, imports: List[Union[ast.Import, ast.ImportFrom]], errors: List[str], warnings: List[str]) -> bool:
        """Check for proper test framework imports."""
        framework_imports = []

        for node in imports:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in self.config["imports"]:
                        framework_imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module in self.config["imports"]:
                    framework_imports.append(node.module)

        if not framework_imports:
            warnings.append("No test framework imports detected")
            return False

        return True

    def _check_setup_teardown(self, tree: ast.AST, errors: List[str], warnings: List[str]) -> None:
        """Check for setup and teardown methods."""
        setup_methods = []
        teardown_methods = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                name = node.name.lower()
                if any(setup in name for setup in ["setup", "before"]):
                    setup_methods.append(node.name)
                elif any(teardown in name for teardown in ["teardown", "after", "cleanup"]):
                    teardown_methods.append(node.name)

        if not setup_methods:
            warnings.append("No setup methods found")
        if not teardown_methods:
            warnings.append("No teardown methods found")

    def _check_edge_cases(self, test_functions: List[ast.FunctionDef], code: str, warnings: List[str]) -> None:
        """Check for edge case testing patterns."""
        edge_case_indicators = ["empty", "null", "none", "zero", "negative", "boundary", "edge", "limit", "max", "min", "overflow", "underflow"]

        edge_case_found = False
        for func in test_functions:
            func_name = func.name.lower()
            if any(indicator in func_name for indicator in edge_case_indicators):
                edge_case_found = True
                break

        if not edge_case_found:
            # Check function content
            code_lower = code.lower()
            if any(indicator in code_lower for indicator in edge_case_indicators):
                edge_case_found = True

        if not edge_case_found:
            warnings.append("No edge case tests detected")

    def _check_error_tests(self, test_functions: List[ast.FunctionDef], code: str, errors: List[str], warnings: List[str]) -> None:
        """Check for error/exception testing."""
        error_test_patterns = [
            r"assertRaises\(",
            r"pytest\.raises\(",
            r"with\s+pytest\.raises",
            r"except\s+\w+Error",
            r"try:",
            r"raises\s*=\s*\w+Error",
        ]

        error_tests = self._count_patterns(code, error_test_patterns)

        if error_tests == 0:
            if self.require_error_tests:
                errors.append("No error/exception tests found")
            else:
                warnings.append("Consider adding tests for error conditions")

    def _count_patterns(self, text: str, patterns: List[str]) -> int:
        """Count occurrences of regex patterns in text."""
        count = 0
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            count += len(matches)
        return count

    def get_validator_description(self) -> str:
        """Get a description of this validator for LLM context."""
        return f"""Test Validator for {self.language.title()}

Validates that generated test code follows best practices:

1. **Test Structure**:
   - Minimum {self.min_test_functions} test function(s)
   - At least {self.min_assertions_per_test} assertion(s) per test
   - Proper test naming conventions (test_*, *_test)

2. **Test Framework**:
   - Uses recognized testing framework ({', '.join(self.config['frameworks'])})
   - Includes appropriate imports

3. **Test Quality**:
   - Contains actual assertions/expectations
   - Tests different scenarios
   {'- Includes edge case testing' if self.require_edge_cases else ''}
   {'- Includes error/exception testing' if self.require_error_tests else ''}
   {'- Has setup/teardown methods' if self.require_setup_teardown else ''}

4. **Code Quality**:
   {'- Test functions have documentation' if self.check_documentation else ''}
   - Follows language-specific conventions

The validator ensures comprehensive test coverage and maintainable test code.
"""
