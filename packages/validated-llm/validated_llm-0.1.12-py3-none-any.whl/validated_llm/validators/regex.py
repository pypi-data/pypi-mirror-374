"""
Regular expression validation for LLM outputs.
"""

import re
from typing import Any, Dict, List, Optional, Pattern, Union

from validated_llm.base_validator import BaseValidator, ValidationResult


class RegexValidator(BaseValidator):
    """
    Validates LLM output against custom regular expression patterns.

    Features:
    - Single or multiple regex pattern validation
    - Full match or partial match modes
    - Pattern grouping and extraction
    - Negative pattern matching (must NOT match)
    - Custom error messages per pattern
    - Case sensitivity control
    """

    def __init__(
        self,
        name: str = "RegexValidator",
        description: str = "Validates against regex patterns",
        patterns: Optional[Union[str, List[str], Dict[str, str]]] = None,
        negative_patterns: Optional[Union[str, List[str], Dict[str, str]]] = None,
        mode: str = "match",  # "match" (full), "search" (partial), "findall"
        case_sensitive: bool = True,
        multiline: bool = True,
        dotall: bool = False,
        extract_groups: bool = False,
        min_matches: Optional[int] = None,
        max_matches: Optional[int] = None,
        strip_output: bool = True,
    ):
        """
        Initialize the regex validator.

        Args:
            name: Validator name
            description: Validator description
            patterns: Regex pattern(s) to match. Can be:
                     - Single pattern string
                     - List of pattern strings (all must match in "match" mode)
                     - Dict of {pattern_name: pattern} for named patterns
            negative_patterns: Pattern(s) that must NOT match
            mode: Validation mode:
                  - "match": Full string must match (anchored at start/end)
                  - "search": Pattern must be found somewhere in string
                  - "findall": Find all occurrences (use with min/max_matches)
            case_sensitive: Whether patterns are case sensitive
            multiline: Whether ^ and $ match line boundaries
            dotall: Whether . matches newlines
            extract_groups: Whether to extract and return capturing groups
            min_matches: Minimum number of matches required (for "findall" mode)
            max_matches: Maximum number of matches allowed (for "findall" mode)
            strip_output: Whether to strip whitespace before validation
        """
        super().__init__(name, description)

        # Normalize patterns to dict format
        self.patterns = self._normalize_patterns(patterns)
        self.negative_patterns = self._normalize_patterns(negative_patterns)

        self.mode = mode
        self.case_sensitive = case_sensitive
        self.multiline = multiline
        self.dotall = dotall
        self.extract_groups = extract_groups
        self.min_matches = min_matches
        self.max_matches = max_matches
        self.strip_output = strip_output

        # Compile patterns
        self._compiled_patterns = {}
        self._compiled_negative_patterns = {}

        flags = 0
        if not case_sensitive:
            flags |= re.IGNORECASE
        if multiline:
            flags |= re.MULTILINE
        if dotall:
            flags |= re.DOTALL

        for name, pattern in self.patterns.items():
            try:
                self._compiled_patterns[name] = re.compile(pattern, flags)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern '{name}': {pattern} - {e}")

        for name, pattern in self.negative_patterns.items():
            try:
                self._compiled_negative_patterns[name] = re.compile(pattern, flags)
            except re.error as e:
                raise ValueError(f"Invalid negative regex pattern '{name}': {pattern} - {e}")

    def _normalize_patterns(self, patterns: Optional[Union[str, List[str], Dict[str, str]]]) -> Dict[str, str]:
        """Normalize patterns to dict format."""
        if patterns is None:
            return {}
        elif isinstance(patterns, str):
            return {"pattern": patterns}
        elif isinstance(patterns, list):
            return {f"pattern_{i}": p for i, p in enumerate(patterns)}
        elif isinstance(patterns, dict):
            return patterns
        else:
            raise ValueError(f"Invalid pattern type: {type(patterns)}")

    def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate output against regex patterns.

        Args:
            output: The LLM output to validate
            context: Optional context (unused for regex validation)

        Returns:
            ValidationResult with validation status and details
        """
        errors: List[str] = []
        warnings: List[str] = []
        metadata: Dict[str, Any] = {"matches": {}, "groups": {}, "match_counts": {}, "failed_patterns": [], "matched_negative_patterns": []}

        if self.strip_output:
            output = output.strip()

        if not output:
            errors.append("Output is empty")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings, metadata=metadata)

        # Validate positive patterns
        for name, pattern in self._compiled_patterns.items():
            if self.mode == "match":
                # Full match mode
                match = pattern.fullmatch(output)
                if match:
                    metadata["matches"][name] = match.group(0)
                    if self.extract_groups and match.groups():
                        metadata["groups"][name] = match.groups()
                else:
                    errors.append(f"Output does not match required pattern '{name}': {self.patterns[name]}")
                    metadata["failed_patterns"].append(name)

            elif self.mode == "search":
                # Search mode - pattern must exist somewhere
                match = pattern.search(output)
                if match:
                    metadata["matches"][name] = match.group(0)
                    if self.extract_groups and match.groups():
                        metadata["groups"][name] = match.groups()
                else:
                    errors.append(f"Required pattern '{name}' not found: {self.patterns[name]}")
                    metadata["failed_patterns"].append(name)

            elif self.mode == "findall":
                # Find all occurrences
                matches = pattern.findall(output)
                metadata["matches"][name] = matches
                metadata["match_counts"][name] = len(matches)

                # Check min/max matches
                if self.min_matches is not None and len(matches) < self.min_matches:
                    errors.append(f"Pattern '{name}' found {len(matches)} times, but minimum {self.min_matches} required")
                    metadata["failed_patterns"].append(name)

                if self.max_matches is not None and len(matches) > self.max_matches:
                    errors.append(f"Pattern '{name}' found {len(matches)} times, but maximum {self.max_matches} allowed")
                    metadata["failed_patterns"].append(name)

        # Validate negative patterns (must NOT match)
        for name, pattern in self._compiled_negative_patterns.items():
            if pattern.search(output):
                errors.append(f"Output contains forbidden pattern '{name}': {self.negative_patterns[name]}")
                metadata["matched_negative_patterns"].append(name)

        # Additional validation for findall mode when no specific patterns provided
        if self.mode == "findall" and not self.patterns:
            warnings.append("No patterns specified for 'findall' mode")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings, metadata=metadata)

    def get_validation_instructions(self) -> str:
        """Get specific validation instructions for regex patterns."""
        instructions = f"""
REGEX VALIDATION REQUIREMENTS:
- Output must match the specified regular expression pattern(s)
- Validation mode: {self.mode}"""

        if self.patterns:
            instructions += "\n\nRequired patterns:"
            for name, pattern in self.patterns.items():
                instructions += f"\n- {name}: {pattern}"

        if self.negative_patterns:
            instructions += "\n\nForbidden patterns (must NOT match):"
            for name, pattern in self.negative_patterns.items():
                instructions += f"\n- {name}: {pattern}"

        if not self.case_sensitive:
            instructions += "\n- Patterns are case-insensitive"

        if self.mode == "match":
            instructions += "\n- The ENTIRE output must match the pattern (not just a portion)"
        elif self.mode == "search":
            instructions += "\n- The pattern must be found somewhere in the output"
        elif self.mode == "findall":
            instructions += "\n- All occurrences of the pattern will be found and counted"
            if self.min_matches:
                instructions += f"\n- Minimum matches required: {self.min_matches}"
            if self.max_matches:
                instructions += f"\n- Maximum matches allowed: {self.max_matches}"

        # Add examples based on patterns
        if self.patterns:
            instructions += "\n\nExamples:"

            # Try to provide meaningful examples
            for name, pattern in list(self.patterns.items())[:3]:  # Show up to 3 examples
                if pattern == r"^\d+$":
                    instructions += f"\n- Valid for '{name}': 12345"
                    instructions += f"\n- Invalid for '{name}': 12.34 or abc123"
                elif pattern == r"^[A-Z][a-z]+$":
                    instructions += f"\n- Valid for '{name}': Hello"
                    instructions += f"\n- Invalid for '{name}': hello or HELLO"
                elif pattern == r"^\w+@\w+\.\w+$":
                    instructions += f"\n- Valid for '{name}': user@example.com"
                    instructions += f"\n- Invalid for '{name}': invalid.email"
                elif "http" in pattern.lower():
                    instructions += f"\n- Pattern '{name}' appears to match URLs"
                elif r"\d{4}" in pattern:
                    instructions += f"\n- Pattern '{name}' appears to match 4-digit numbers"
                else:
                    # Generic example
                    instructions += f"\n- Pattern '{name}': {pattern}"

        return instructions
