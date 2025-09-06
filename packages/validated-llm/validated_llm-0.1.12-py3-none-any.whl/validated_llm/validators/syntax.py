"""
Syntax validator for validating code syntax in multiple programming languages.
"""

import ast
import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from validated_llm.base_validator import BaseValidator, ValidationResult


class SyntaxValidator(BaseValidator):
    """Validator for code syntax in various programming languages.

    This validator checks that generated code has valid syntax for the
    specified programming language. It supports:
    - Python (using ast module)
    - JavaScript/TypeScript (using node if available)
    - Go (using go compiler if available)
    - Rust (using rustc if available)
    - Java (using javac if available)

    Example:
        ```python
        # Python syntax validation
        validator = SyntaxValidator(language="python")
        result = validator.validate('''
        def hello_world():
            print("Hello, World!")
        ''')

        # JavaScript validation
        validator = SyntaxValidator(language="javascript")
        result = validator.validate('function hello() { console.log("Hello"); }')
        ```
    """

    SUPPORTED_LANGUAGES: Dict[str, Dict[str, Any]] = {
        "python": {"extensions": [".py"], "validator": "_validate_python"},
        "javascript": {"extensions": [".js"], "validator": "_validate_javascript"},
        "typescript": {"extensions": [".ts"], "validator": "_validate_typescript"},
        "go": {"extensions": [".go"], "validator": "_validate_go"},
        "rust": {"extensions": [".rs"], "validator": "_validate_rust"},
        "java": {"extensions": [".java"], "validator": "_validate_java"},
    }

    def __init__(self, language: str, strict_mode: bool = True, allow_warnings: bool = True, timeout: int = 10, check_best_practices: bool = True):
        """Initialize the syntax validator.

        Args:
            language: Programming language to validate (python, javascript, etc.)
            strict_mode: If True, treat warnings as errors
            allow_warnings: If False, fail on any warnings
            timeout: Maximum time in seconds for external validators
        """
        self.language = language.lower()
        if self.language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {language}. " f"Supported: {', '.join(self.SUPPORTED_LANGUAGES.keys())}")

        self.strict_mode = strict_mode
        self.allow_warnings = allow_warnings
        self.timeout = timeout
        self.check_best_practices = check_best_practices

    def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate code syntax.

        Args:
            output: The code string to validate
            context: Optional validation context

        Returns:
            ValidationResult containing any syntax errors
        """
        errors: List[str] = []
        warnings: List[str] = []
        metadata: Dict[str, Any] = {"language": self.language}

        # Get the appropriate validator method
        validator_method = getattr(self, self.SUPPORTED_LANGUAGES[self.language]["validator"])

        # Run language-specific validation
        try:
            result = validator_method(output.strip(), errors, warnings, metadata)
            if not result and not errors:
                # If validator returned False but no errors, add generic error
                errors.append(f"Invalid {self.language} syntax")
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")

        # Handle strict mode
        if self.strict_mode and warnings:
            errors.extend(warnings)
            warnings = []

        # Handle allow_warnings
        if not self.allow_warnings and warnings:
            errors.extend(warnings)
            warnings = []

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings, metadata=metadata)

    def _validate_python(self, code: str, errors: List[str], warnings: List[str], metadata: Dict[str, Any]) -> bool:
        """Validate Python syntax using ast module."""
        try:
            tree = ast.parse(code)
            metadata["ast_nodes"] = len(list(ast.walk(tree)))

            # Check for common issues
            if self.check_best_practices:
                self._check_python_best_practices(tree, warnings)

            # Try to compile to catch more errors
            compile(code, "<string>", "exec")

            return True
        except SyntaxError as e:
            error_msg = f"Python syntax error at line {e.lineno}: {e.msg}"
            if e.text:
                error_msg += f"\n  {e.text.strip()}"
                if e.offset:
                    error_msg += f"\n  {' ' * (e.offset - 1)}^"
            errors.append(error_msg)
            return False
        except Exception as e:
            errors.append(f"Python validation error: {str(e)}")
            return False

    def _check_python_best_practices(self, tree: ast.AST, warnings: List[str]) -> None:
        """Check for Python best practices and add warnings."""
        # Check for missing docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    warnings.append(f"Missing docstring for {node.__class__.__name__} '{node.name}'")

        # Check for broad except clauses
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    warnings.append("Bare except clause found (catches all exceptions)")

    def _validate_javascript(self, code: str, errors: List[str], warnings: List[str], metadata: Dict[str, Any]) -> bool:
        """Validate JavaScript syntax using Node.js if available."""
        return self._validate_with_node(code, errors, warnings, metadata, "javascript")

    def _validate_typescript(self, code: str, errors: List[str], warnings: List[str], metadata: Dict[str, Any]) -> bool:
        """Validate TypeScript syntax using tsc if available."""
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".ts", delete=False) as f:
                f.write(code)
                temp_path = f.name

            result = subprocess.run(["tsc", "--noEmit", "--skipLibCheck", temp_path], capture_output=True, text=True, timeout=self.timeout)

            Path(temp_path).unlink()

            if result.returncode != 0:
                for line in result.stdout.split("\n") + result.stderr.split("\n"):
                    if line.strip():
                        errors.append(line.strip())
                return False

            return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            warnings.append("TypeScript compiler (tsc) not available, skipping validation")
            return True
        except Exception as e:
            errors.append(f"TypeScript validation error: {str(e)}")
            return False

    def _validate_with_node(self, code: str, errors: List[str], warnings: List[str], metadata: Dict[str, Any], language: str) -> bool:
        """Validate JavaScript/TypeScript using Node.js."""
        try:
            # Try to parse with Node.js
            result = subprocess.run(["node", "-c"], input=code, capture_output=True, text=True, timeout=self.timeout)

            if result.returncode != 0:
                error_output = result.stderr.strip()
                if error_output:
                    errors.append(f"{language} syntax error: {error_output}")
                return False

            return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            warnings.append(f"Node.js not available, skipping {language} validation")
            return True
        except Exception as e:
            errors.append(f"{language} validation error: {str(e)}")
            return False

    def _validate_go(self, code: str, errors: List[str], warnings: List[str], metadata: Dict[str, Any]) -> bool:
        """Validate Go syntax using go compiler if available."""
        try:
            # Go requires a package declaration
            if "package " not in code:
                code = "package main\n\n" + code

            with tempfile.NamedTemporaryFile(mode="w", suffix=".go", delete=False) as f:
                f.write(code)
                temp_path = f.name

            # Use gofmt instead of go fmt for syntax checking
            result = subprocess.run(["gofmt", "-e", temp_path], capture_output=True, text=True, timeout=self.timeout)

            Path(temp_path).unlink()

            if result.returncode != 0:
                error_output = result.stderr.strip()
                if error_output:
                    errors.append(f"Go syntax error: {error_output}")
                return False

            return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            warnings.append("Go compiler not available, skipping validation")
            return True
        except Exception as e:
            errors.append(f"Go validation error: {str(e)}")
            return False

    def _validate_rust(self, code: str, errors: List[str], warnings: List[str], metadata: Dict[str, Any]) -> bool:
        """Validate Rust syntax using rustc if available."""
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".rs", delete=False) as f:
                f.write(code)
                temp_path = f.name

            # Create a temp directory for rust output
            with tempfile.TemporaryDirectory() as output_dir:
                output_path = Path(output_dir) / "output.mir"
                result = subprocess.run(["rustc", "--crate-type", "lib", "--emit=mir", "-o", str(output_path), temp_path], capture_output=True, text=True, timeout=self.timeout)

            Path(temp_path).unlink()

            if result.returncode != 0:
                error_output = result.stderr.strip()
                if error_output:
                    # Parse Rust error output
                    for line in error_output.split("\n"):
                        if "error" in line or "ERROR" in line:
                            errors.append(line.strip())
                return False

            return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            warnings.append("Rust compiler (rustc) not available, skipping validation")
            return True
        except Exception as e:
            errors.append(f"Rust validation error: {str(e)}")
            return False

    def _validate_java(self, code: str, errors: List[str], warnings: List[str], metadata: Dict[str, Any]) -> bool:
        """Validate Java syntax using javac if available."""
        try:
            # Extract class name from code
            class_match = re.search(r"(?:public\s+)?class\s+(\w+)", code)
            if not class_match:
                errors.append("No class definition found in Java code")
                return False

            class_name = class_match.group(1)

            # Java requires filename to match class name
            temp_dir = tempfile.mkdtemp()
            temp_path = Path(temp_dir) / f"{class_name}.java"

            with open(temp_path, "w") as f:
                f.write(code)

            result = subprocess.run(["javac", "-Xlint:none", str(temp_path)], capture_output=True, text=True, timeout=self.timeout)

            # Clean up
            temp_path.unlink()
            class_file = temp_path.with_suffix(".class")
            if class_file.exists():
                class_file.unlink()
            Path(temp_dir).rmdir()

            if result.returncode != 0:
                error_output = result.stderr.strip()
                if error_output:
                    errors.append(f"Java syntax error: {error_output}")
                return False

            return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            warnings.append("Java compiler (javac) not available, skipping validation")
            return True
        except Exception as e:
            errors.append(f"Java validation error: {str(e)}")
            return False

    def get_validator_description(self) -> str:
        """Get a description of this validator for LLM context."""
        return f"""Syntax Validator for {self.language.title()}

Validates that the generated code has correct syntax for {self.language}.

Requirements:
1. Code must be syntactically valid {self.language}
2. All brackets, parentheses, and quotes must be properly matched
3. Keywords and constructs must be used correctly
4. Indentation must be correct (for Python)
5. Statements must be properly terminated

The validator will report specific line numbers and error messages for any syntax errors found.
"""
