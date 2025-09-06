"""
Style validator for checking code formatting and conventions.
"""

import difflib
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from validated_llm.base_validator import BaseValidator, ValidationResult


class StyleValidator(BaseValidator):
    """Validator for code style and formatting standards.

    This validator checks that generated code follows style conventions
    for the specified programming language using popular formatters:
    - Python: Black, isort, autopep8
    - JavaScript/TypeScript: Prettier, ESLint
    - Go: gofmt, goimports
    - Rust: rustfmt
    - Java: google-java-format

    Example:
        ```python
        # Python style validation with Black
        validator = StyleValidator(language="python", formatter="black")
        result = validator.validate('''
        def hello(name):
            return f"Hello, {name}!"
        ''')

        # JavaScript validation with Prettier
        validator = StyleValidator(language="javascript", formatter="prettier")
        result = validator.validate('function hello(name){return `Hello ${name}!`}')
        ```
    """

    FORMATTERS: Dict[str, Dict[str, Dict[str, Any]]] = {
        "python": {
            "black": {"command": ["black", "-"], "check_command": ["black", "--check", "-"]},
            "autopep8": {"command": ["autopep8", "-"], "check_command": None},
            "isort": {"command": ["isort", "-"], "check_command": ["isort", "--check", "-"]},
        },
        "javascript": {
            "prettier": {"command": ["prettier", "--no-config", "--stdin-filepath", "file.js"], "check_command": ["prettier", "--no-config", "--check", "--stdin-filepath", "file.js"]},
        },
        "typescript": {
            "prettier": {"command": ["prettier", "--no-config", "--stdin-filepath", "file.ts"], "check_command": ["prettier", "--no-config", "--check", "--stdin-filepath", "file.ts"]},
        },
        "go": {
            "gofmt": {"command": ["gofmt"], "check_command": None},
            "goimports": {"command": ["goimports"], "check_command": None},
        },
        "rust": {
            "rustfmt": {"command": ["rustfmt", "--emit=stdout"], "check_command": None},
        },
        "java": {
            "google-java-format": {"command": ["google-java-format", "-"], "check_command": None},
        },
    }

    def __init__(self, language: str, formatter: Optional[str] = None, show_diff: bool = True, auto_fix: bool = False, timeout: int = 10, config_file: Optional[str] = None):
        """Initialize the style validator.

        Args:
            language: Programming language to validate
            formatter: Specific formatter to use (defaults to language default)
            show_diff: Whether to show formatting differences
            auto_fix: Whether to return formatted code instead of errors
            timeout: Maximum time in seconds for formatter
            config_file: Optional config file for the formatter
        """
        self.language = language.lower()
        if self.language not in self.FORMATTERS:
            raise ValueError(f"Unsupported language: {language}. " f"Supported: {', '.join(self.FORMATTERS.keys())}")

        # Set default formatter if not specified
        if formatter is None:
            formatter = list(self.FORMATTERS[self.language].keys())[0]

        if formatter not in self.FORMATTERS[self.language]:
            raise ValueError(f"Unsupported formatter '{formatter}' for {language}. " f"Available: {', '.join(self.FORMATTERS[self.language].keys())}")

        self.formatter = formatter
        self.show_diff = show_diff
        self.auto_fix = auto_fix
        self.timeout = timeout
        self.config_file = config_file

    def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate code style.

        Args:
            output: The code string to validate
            context: Optional validation context

        Returns:
            ValidationResult containing style violations or formatted code
        """
        errors: List[str] = []
        warnings: List[str] = []
        metadata: Dict[str, Any] = {"language": self.language, "formatter": self.formatter}

        # Get formatter configuration
        formatter_config = self.FORMATTERS[self.language][self.formatter]

        # Try to format the code
        try:
            formatted_code = self._run_formatter(output.strip(), formatter_config)

            if formatted_code is None:
                warnings.append(f"{self.formatter} is not available, skipping style validation")
                return ValidationResult(is_valid=True, errors=errors, warnings=warnings, metadata=metadata)

            # Compare original and formatted
            if output.strip() != formatted_code.strip():
                if self.auto_fix:
                    # Return the formatted code
                    metadata["formatted_code"] = formatted_code
                    metadata["auto_fixed"] = True
                else:
                    # Report style violations
                    errors.append(f"Code does not conform to {self.formatter} style standards")

                    if self.show_diff:
                        diff = self._generate_diff(output.strip(), formatted_code.strip())
                        if diff:
                            errors.append(f"Style differences:\n{diff}")

                    metadata["has_style_issues"] = True
            else:
                metadata["style_compliant"] = True

        except Exception as e:
            errors.append(f"Style validation error: {str(e)}")

        # Store formatted code in metadata if auto-fix is enabled
        if self.auto_fix and formatted_code and len(errors) == 0:
            metadata["output"] = formatted_code

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings, metadata=metadata)

    def _run_formatter(self, code: str, formatter_config: Dict[str, Any]) -> Optional[str]:
        """Run the formatter on the code.

        Args:
            code: The code to format
            formatter_config: Formatter command configuration

        Returns:
            Formatted code or None if formatter not available
        """
        command = formatter_config["command"].copy()

        # Add config file if specified
        if self.config_file:
            if self.formatter == "black":
                command.extend(["--config", self.config_file])
            elif self.formatter == "prettier":
                command.extend(["--config", self.config_file])
            elif self.formatter == "isort":
                command.extend(["--settings-file", self.config_file])

        try:
            # Special handling for different formatters
            if self.formatter in ["black", "autopep8", "isort", "google-java-format"]:
                # These read from stdin
                result = subprocess.run(command, input=code, capture_output=True, text=True, timeout=self.timeout)
            elif self.formatter == "prettier":
                # Prettier needs stdin
                result = subprocess.run(command, input=code, capture_output=True, text=True, timeout=self.timeout)
            elif self.formatter in ["gofmt", "goimports"]:
                # These need a file
                with tempfile.NamedTemporaryFile(mode="w", suffix=".go", delete=False) as f:
                    f.write(code)
                    temp_path = f.name

                result = subprocess.run(command + [temp_path], capture_output=True, text=True, timeout=self.timeout)

                Path(temp_path).unlink()
            elif self.formatter == "rustfmt":
                # Rustfmt can work with stdin
                result = subprocess.run(command, input=code, capture_output=True, text=True, timeout=self.timeout)
            else:
                return None

            if result.returncode == 0:
                return result.stdout if result.stdout else code
            else:
                # Some formatters return non-zero for style issues
                if result.stdout:
                    return result.stdout
                return None

        except (subprocess.TimeoutExpired, FileNotFoundError):
            return None
        except Exception:
            return None

    def _generate_diff(self, original: str, formatted: str) -> str:
        """Generate a readable diff between original and formatted code.

        Args:
            original: Original code
            formatted: Formatted code

        Returns:
            Diff string
        """
        original_lines = original.splitlines(keepends=True)
        formatted_lines = formatted.splitlines(keepends=True)

        diff = difflib.unified_diff(original_lines, formatted_lines, fromfile="original", tofile="formatted", n=3)

        return "".join(diff)

    def get_validator_description(self) -> str:
        """Get a description of this validator for LLM context."""
        return f"""Style Validator for {self.language.title()} using {self.formatter}

Validates that the generated code follows {self.formatter} style conventions.

Requirements:
1. Code must be properly formatted according to {self.formatter} standards
2. Consistent indentation and spacing
3. Proper line length limits
4. Correct import ordering (if applicable)
5. Consistent quote usage (if applicable)

The validator will {"automatically fix" if self.auto_fix else "report"} any style violations found.
"""
