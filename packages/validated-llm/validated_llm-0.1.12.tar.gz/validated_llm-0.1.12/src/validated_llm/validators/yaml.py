"""
YAML validator for validating YAML syntax and structure.
"""

from typing import Any, Dict, List, Optional, Union

import yaml
from yaml import YAMLError, safe_load

from validated_llm.base_validator import BaseValidator, ValidationResult


class YAMLValidator(BaseValidator):
    """Validator for YAML syntax and optional structure validation.

    This validator checks for:
    - Valid YAML syntax
    - Proper indentation
    - Required keys
    - Type constraints
    - Custom structure validation

    Example:
        ```python
        # Basic YAML validation
        validator = YAMLValidator()
        result = validator.validate('''
        name: John Doe
        age: 30
        skills:
          - Python
          - Java
        ''')

        # With structure requirements
        validator = YAMLValidator(
            required_keys=["name", "age", "skills"],
            type_constraints={
                "name": str,
                "age": int,
                "skills": list
            }
        )
        ```
    """

    def __init__(self, required_keys: Optional[List[str]] = None, type_constraints: Optional[Dict[str, type]] = None, allow_duplicate_keys: bool = False, strict_mode: bool = True, max_depth: Optional[int] = None):
        """Initialize the YAML validator.

        Args:
            required_keys: List of keys that must be present at the root level
            type_constraints: Dictionary mapping keys to expected types
            allow_duplicate_keys: If False, reject YAML with duplicate keys
            strict_mode: If True, treat warnings as errors
            max_depth: Maximum nesting depth allowed (None for unlimited)
        """
        self.required_keys = required_keys or []
        self.type_constraints = type_constraints or {}
        self.allow_duplicate_keys = allow_duplicate_keys
        self.strict_mode = strict_mode
        self.max_depth = max_depth

    def validate(self, output: str, context: Optional[dict[str, Any]] = None) -> ValidationResult:
        """Validate YAML output.

        Args:
            output: The YAML string to validate
            context: Optional validation context

        Returns:
            ValidationResult containing any errors or warnings
        """
        llm_output = output
        errors: List[str] = []
        warnings: List[str] = []
        metadata: Dict[str, Any] = {}

        # Try to parse YAML
        try:
            # Use safe_load to avoid security issues
            data = safe_load(llm_output.strip())

            # Check if YAML is not just a scalar value when we expect structure
            if self.required_keys and not isinstance(data, dict):
                errors.append(f"Expected YAML object/mapping but got {type(data).__name__}")
                return ValidationResult(is_valid=False, errors=errors, warnings=warnings, metadata=metadata)

            # Store parsed data in metadata
            metadata["parsed_data"] = data

            # Check for duplicate keys (requires custom loader)
            if not self.allow_duplicate_keys:
                dup_errors = self._check_duplicate_keys(llm_output.strip())
                errors.extend(dup_errors)

            # Validate structure if data is a dict
            if isinstance(data, dict):
                # Check required keys
                missing_keys = [key for key in self.required_keys if key not in data]
                if missing_keys:
                    error_msg = f"Missing required keys: {', '.join(missing_keys)}"
                    if self.strict_mode:
                        errors.append(error_msg)
                    else:
                        warnings.append(error_msg)

                # Check type constraints
                for key, expected_type in self.type_constraints.items():
                    if key in data:
                        actual_type = type(data[key])
                        if not isinstance(data[key], expected_type):
                            error_msg = f"Key '{key}' has wrong type: expected " f"{expected_type.__name__}, got {actual_type.__name__}"
                            if self.strict_mode:
                                errors.append(error_msg)
                            else:
                                warnings.append(error_msg)

            # Check nesting depth
            if self.max_depth is not None:
                depth = self._get_max_depth(data)
                if depth > self.max_depth:
                    warnings.append(f"YAML nesting depth ({depth}) exceeds maximum ({self.max_depth})")
                metadata["max_depth"] = depth

            # Add structure info to metadata
            metadata["root_type"] = type(data).__name__
            if isinstance(data, dict):
                metadata["keys"] = list(data.keys())
            elif isinstance(data, list):
                metadata["length"] = len(data)

        except YAMLError as e:
            # Parse the error to provide more helpful feedback
            error_msg = str(e)
            if hasattr(e, "problem_mark") and hasattr(e, "problem"):
                mark = e.problem_mark
                problem = getattr(e, "problem", "unknown error")
                error_msg = f"YAML syntax error at line {mark.line + 1}, " f"column {mark.column + 1}: {problem}"
            errors.append(error_msg)

        except Exception as e:
            errors.append(f"Unexpected error parsing YAML: {str(e)}")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings, metadata=metadata)

    def _check_duplicate_keys(self, yaml_content: str) -> List[str]:
        """Check for duplicate keys in YAML.

        Args:
            yaml_content: The YAML content to check

        Returns:
            List of error messages for duplicate keys
        """
        errors = []

        class DuplicateKeyChecker:
            """Custom YAML loader that detects duplicate keys."""

            def __init__(self) -> None:
                self.keys_seen: Dict[str, bool] = {}
                self.duplicates: List[str] = []

            def check_key(self, node: Any, key: str) -> None:
                if key in self.keys_seen:
                    self.duplicates.append(f"Duplicate key '{key}' found at line {node.start_mark.line + 1}")
                self.keys_seen[key] = True

        # This is a simplified check - full implementation would use custom YAML loader
        # For now, we'll do a basic line-by-line check for obvious duplicates
        lines = yaml_content.split("\n")
        keys_at_level: Dict[int, set[str]] = {}

        for i, line in enumerate(lines):
            # Skip empty lines and comments
            if not line.strip() or line.strip().startswith("#"):
                continue

            # Simple check for key: value pattern
            if ":" in line and not line.strip().startswith("-"):
                indent = len(line) - len(line.lstrip())
                key = line.split(":")[0].strip()

                if indent not in keys_at_level:
                    keys_at_level[indent] = set()

                if key in keys_at_level[indent]:
                    errors.append(f"Duplicate key '{key}' found around line {i + 1}")
                else:
                    keys_at_level[indent].add(key)

        return errors

    def _get_max_depth(self, data: Any, current_depth: int = 0) -> int:
        """Get the maximum nesting depth of a data structure.

        Args:
            data: The data to check
            current_depth: Current recursion depth

        Returns:
            Maximum depth found
        """
        if isinstance(data, dict):
            if not data:
                return current_depth
            return max(self._get_max_depth(v, current_depth + 1) for v in data.values())
        elif isinstance(data, list):
            if not data:
                return current_depth
            return max(self._get_max_depth(item, current_depth + 1) for item in data)
        else:
            return current_depth

    def get_validator_description(self) -> str:
        """Get a description of this validator for LLM context."""
        desc = """YAML Validator

Validates that the output is valid YAML with:
1. Proper YAML syntax
2. Correct indentation (spaces, not tabs)
3. Valid data types (strings, numbers, lists, objects)
4. No syntax errors
"""

        if self.required_keys:
            desc += f"\nRequired keys at root level: {', '.join(self.required_keys)}\n"

        if self.type_constraints:
            desc += "\nType constraints:\n"
            for key, type_ in self.type_constraints.items():
                desc += f"  - {key}: {type_.__name__}\n"

        if not self.allow_duplicate_keys:
            desc += "\nDuplicate keys are not allowed.\n"

        if self.max_depth is not None:
            desc += f"\nMaximum nesting depth: {self.max_depth}\n"

        return desc
