"""
Date and time validation for LLM outputs.
"""

import re
from datetime import date, datetime, time
from typing import Any, Dict, List, Optional, Tuple, Union

from validated_llm.base_validator import BaseValidator, ValidationResult


class DateTimeValidator(BaseValidator):
    """
    Validates date, time, and datetime values in various formats.

    Supports:
    - Multiple date/time formats
    - Custom format strings
    - Date/time range validation
    - Timezone awareness
    - Relative date validation (e.g., "tomorrow", "next week")
    """

    # Common date formats
    DEFAULT_DATE_FORMATS = [
        "%Y-%m-%d",  # 2024-01-15
        "%Y/%m/%d",  # 2024/01/15
        "%m/%d/%Y",  # 01/15/2024
        "%m-%d-%Y",  # 01-15-2024
        "%d/%m/%Y",  # 15/01/2024
        "%d-%m-%Y",  # 15-01-2024
        "%d.%m.%Y",  # 15.01.2024
        "%B %d, %Y",  # January 15, 2024
        "%b %d, %Y",  # Jan 15, 2024
        "%d %B %Y",  # 15 January 2024
        "%d %b %Y",  # 15 Jan 2024
    ]

    # Common time formats
    DEFAULT_TIME_FORMATS = [
        "%H:%M:%S",  # 14:30:45
        "%H:%M",  # 14:30
        "%I:%M %p",  # 2:30 PM
        "%I:%M:%S %p",  # 2:30:45 PM
    ]

    # Common datetime formats
    DEFAULT_DATETIME_FORMATS = [
        "%Y-%m-%d %H:%M:%S",  # 2024-01-15 14:30:45
        "%Y-%m-%d %H:%M",  # 2024-01-15 14:30
        "%Y-%m-%dT%H:%M:%S",  # 2024-01-15T14:30:45
        "%Y-%m-%dT%H:%M:%SZ",  # 2024-01-15T14:30:45Z
        "%Y-%m-%dT%H:%M:%S.%f",  # 2024-01-15T14:30:45.123456
        "%Y-%m-%dT%H:%M:%S.%fZ",  # 2024-01-15T14:30:45.123456Z
        "%Y-%m-%d %I:%M %p",  # 2024-01-15 2:30 PM
        "%m/%d/%Y %H:%M:%S",  # 01/15/2024 14:30:45
        "%d/%m/%Y %H:%M:%S",  # 15/01/2024 14:30:45
    ]

    def __init__(
        self,
        name: str = "DateTimeValidator",
        description: str = "Validates date/time values",
        formats: Optional[List[str]] = None,
        mode: str = "datetime",  # "date", "time", or "datetime"
        min_value: Optional[Union[str, datetime, date, time]] = None,
        max_value: Optional[Union[str, datetime, date, time]] = None,
        extract_all: bool = False,
        allow_relative: bool = False,
        timezone_required: bool = False,
    ):
        """
        Initialize the date/time validator.

        Args:
            name: Validator name
            description: Validator description
            formats: List of format strings to try. If None, uses defaults based on mode
            mode: What to validate - "date", "time", or "datetime"
            min_value: Minimum allowed date/time value
            max_value: Maximum allowed date/time value
            extract_all: Whether to extract all dates/times from text
            allow_relative: Whether to allow relative dates like "tomorrow"
            timezone_required: Whether timezone info is required (for datetime mode)
        """
        super().__init__(name, description)
        self.mode = mode.lower()
        self.extract_all = extract_all
        self.allow_relative = allow_relative
        self.timezone_required = timezone_required

        # Set formats based on mode
        if formats:
            self.formats = formats
        else:
            if self.mode == "date":
                self.formats = self.DEFAULT_DATE_FORMATS
            elif self.mode == "time":
                self.formats = self.DEFAULT_TIME_FORMATS
            else:  # datetime
                self.formats = self.DEFAULT_DATETIME_FORMATS

        # Parse min/max values
        self.min_value = self._parse_boundary(min_value) if min_value else None
        self.max_value = self._parse_boundary(max_value) if max_value else None

        # Relative date patterns
        self.relative_patterns = {
            r"\btoday\b": 0,
            r"\btomorrow\b": 1,
            r"\byesterday\b": -1,
            r"\bnext\s+week\b": 7,
            r"\blast\s+week\b": -7,
            r"\bnext\s+month\b": 30,  # Approximate
            r"\blast\s+month\b": -30,  # Approximate
        }

    def _parse_boundary(self, value: Union[str, datetime, date, time]) -> Union[datetime, date, time]:
        """Parse boundary value to appropriate type."""
        if isinstance(value, (datetime, date, time)):
            return value

        # Try parsing as string
        for fmt in self.formats:
            try:
                if self.mode == "date":
                    return datetime.strptime(value, fmt).date()
                elif self.mode == "time":
                    return datetime.strptime(value, fmt).time()
                else:
                    return datetime.strptime(value, fmt)
            except ValueError:
                continue

        raise ValueError(f"Could not parse boundary value: {value}")

    def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate date/time values in the output.

        Args:
            output: The LLM output to validate
            context: Optional context (not used)

        Returns:
            ValidationResult with validation status and details
        """
        errors: list[str] = []
        warnings: list[str] = []
        metadata: dict[str, Any] = {"valid_values": [], "invalid_values": [], "formats_used": []}

        output = output.strip()

        if not output:
            errors.append("Output is empty")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings, metadata=metadata)

        # Extract values based on mode
        if self.extract_all:
            values = self._extract_all_values(output)
        else:
            values = [output]

        # Validate each value
        valid_count = 0
        for value_str in values:
            value_str = value_str.strip()
            if not value_str:
                continue

            # Try relative dates if allowed
            if self.allow_relative and self._is_relative_date(value_str):
                rel_value = self._parse_relative_date(value_str)
                if rel_value:
                    valid_count += 1
                    metadata["valid_values"].append(value_str)
                    continue

            parsed_value: Optional[Union[date, time, datetime]] = None
            used_format = None

            for fmt in self.formats:
                try:
                    if self.mode == "date":
                        parsed = datetime.strptime(value_str, fmt)
                        parsed_value = parsed.date()
                    elif self.mode == "time":
                        parsed_value = datetime.strptime(value_str, fmt).time()
                    else:
                        parsed_value = datetime.strptime(value_str, fmt)

                    used_format = fmt
                    break
                except ValueError:
                    continue

            if parsed_value is None:
                metadata["invalid_values"].append(value_str)
                errors.append(f"Could not parse {self.mode} value: '{value_str}'")
                continue

            # Check timezone requirement for datetime
            if self.mode == "datetime" and self.timezone_required:
                if not any(tz in value_str for tz in ["Z", "+", "-"]):
                    errors.append(f"Timezone information required but not found in: '{value_str}'")
                    continue

            # Check range
            if self.min_value is not None and type(parsed_value) == type(self.min_value):
                if isinstance(parsed_value, (date, datetime)) and isinstance(self.min_value, (date, datetime)):
                    if parsed_value < self.min_value:
                        errors.append(f"Value '{value_str}' is before minimum allowed value: {self.min_value}")
                        continue
                elif isinstance(parsed_value, time) and isinstance(self.min_value, time):
                    if parsed_value < self.min_value:
                        errors.append(f"Value '{value_str}' is before minimum allowed value: {self.min_value}")
                        continue

            if self.max_value is not None and type(parsed_value) == type(self.max_value):
                if isinstance(parsed_value, (date, datetime)) and isinstance(self.max_value, (date, datetime)):
                    if parsed_value > self.max_value:
                        errors.append(f"Value '{value_str}' is after maximum allowed value: {self.max_value}")
                        continue
                elif isinstance(parsed_value, time) and isinstance(self.max_value, time):
                    if parsed_value > self.max_value:
                        errors.append(f"Value '{value_str}' is after maximum allowed value: {self.max_value}")
                        continue

            # Valid value
            valid_count += 1
            metadata["valid_values"].append(value_str)
            if used_format and used_format not in metadata["formats_used"]:
                metadata["formats_used"].append(used_format)

        # Check if we found any valid values
        if valid_count == 0:
            errors.append(f"No valid {self.mode} values found in output")

        metadata["valid_count"] = valid_count

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings, metadata=metadata)

    def _extract_all_values(self, text: str) -> List[str]:
        """Extract potential date/time values from text."""
        # Use regex patterns based on mode
        patterns = []

        if self.mode == "date":
            patterns = [
                r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b",  # YYYY-MM-DD or YYYY/MM/DD
                r"\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b",  # MM-DD-YYYY or MM/DD/YYYY
                r"\b\d{1,2}\.\d{1,2}\.\d{4}\b",  # DD.MM.YYYY
                r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b",
                r"\b\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}\b",
            ]
        elif self.mode == "time":
            patterns = [
                r"\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?\b",  # HH:MM[:SS] [AM/PM]
            ]
        else:  # datetime
            patterns = [
                r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}[T\s]\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?Z?\b",
                r"\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\s+\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?\b",
            ]

        # Add relative patterns if allowed
        if self.allow_relative:
            patterns.extend(self.relative_patterns.keys())

        # Find all matches
        found_values = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            found_values.extend(matches)

        return found_values

    def _is_relative_date(self, value: str) -> bool:
        """Check if value is a relative date."""
        value_lower = value.lower()
        return any(re.search(pattern, value_lower) for pattern in self.relative_patterns)

    def _parse_relative_date(self, value: str) -> Optional[Union[datetime, date]]:
        """Parse relative date to actual date."""
        from datetime import timedelta

        value_lower = value.lower()
        today = datetime.now().date() if self.mode == "date" else datetime.now()

        for pattern, days_offset in self.relative_patterns.items():
            if re.search(pattern, value_lower):
                result = today + timedelta(days=days_offset)
                if self.mode == "date" and isinstance(result, datetime):
                    return result.date()
                return result

        return None

    def get_validation_instructions(self) -> str:
        """Get specific validation instructions for date/time."""
        instructions = f"""
DATE/TIME VALIDATION REQUIREMENTS:
- Output must contain valid {self.mode} value(s)
- Mode: {self.mode.upper()}"""

        if self.formats:
            instructions += f"\n- Accepted formats:"
            for fmt in self.formats[:5]:  # Show first 5 formats
                example = self._format_example(fmt)
                instructions += f"\n  - {fmt} (e.g., {example})"
            if len(self.formats) > 5:
                instructions += f"\n  - ... and {len(self.formats) - 5} more formats"

        if self.min_value:
            instructions += f"\n- Minimum value: {self.min_value}"

        if self.max_value:
            instructions += f"\n- Maximum value: {self.max_value}"

        if self.allow_relative:
            instructions += "\n- Relative dates allowed (e.g., 'tomorrow', 'next week')"

        if self.timezone_required:
            instructions += "\n- Timezone information required (e.g., 'Z' for UTC or '+00:00')"

        instructions += f"""

Examples of valid {self.mode} values:"""

        # Add examples based on mode
        if self.mode == "date":
            instructions += """
- 2024-01-15
- 01/15/2024
- January 15, 2024
- 15 Jan 2024"""
        elif self.mode == "time":
            instructions += """
- 14:30:45
- 2:30 PM
- 14:30
- 02:30:45 PM"""
        else:  # datetime
            instructions += """
- 2024-01-15 14:30:45
- 2024-01-15T14:30:45Z
- 01/15/2024 2:30 PM
- 2024-01-15T14:30:45.123456Z"""

        return instructions

    def _format_example(self, fmt: str) -> str:
        """Generate an example for a given format string."""
        example_dt = datetime(2024, 1, 15, 14, 30, 45, 123456)
        try:
            return example_dt.strftime(fmt)
        except:
            return "2024-01-15"  # Fallback
