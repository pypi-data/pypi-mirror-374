"""
Async range validation for LLM outputs.
"""

import asyncio
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Tuple, Union

from ..async_validator import AsyncBaseValidator
from ..base_validator import ValidationResult


class AsyncRangeValidator(AsyncBaseValidator):
    """
    Async validator for numeric and date/time values against specified ranges.

    Features:
    - Numeric range validation (int, float, Decimal)
    - Date/time range validation
    - Multiple value extraction and validation
    - Inclusive/exclusive bounds
    - Custom parsing patterns
    - Unit conversion support
    - Async execution to avoid blocking
    """

    def __init__(
        self,
        min_value: Optional[Union[int, float, Decimal, datetime, date, str]] = None,
        max_value: Optional[Union[int, float, Decimal, datetime, date, str]] = None,
        value_type: str = "number",  # "number", "integer", "decimal", "datetime", "date"
        inclusive_min: bool = True,
        inclusive_max: bool = True,
        extract_all: bool = False,
        parsing_patterns: Optional[List[str]] = None,
        date_formats: Optional[List[str]] = None,
        allow_units: bool = True,
        unit_conversions: Optional[Dict[str, float]] = None,
        decimal_places: Optional[int] = None,
        required_count: Optional[int] = None,
    ):
        """
        Initialize the async range validator.

        Args:
            min_value: Minimum allowed value (None for no minimum)
            max_value: Maximum allowed value (None for no maximum)
            value_type: Type of value to validate
            inclusive_min: Whether min_value is inclusive (>=) or exclusive (>)
            inclusive_max: Whether max_value is inclusive (<=) or exclusive (<)
            extract_all: Whether to extract all values from text or treat as single value
            parsing_patterns: Custom regex patterns for extracting values
            date_formats: List of date formats to try (for datetime/date types)
            allow_units: Whether to parse units (e.g., "5kg", "10 miles")
            unit_conversions: Dict of unit conversions to base unit
            decimal_places: Required decimal places (for decimal type)
            required_count: Exact number of values required (for extract_all mode)
        """
        super().__init__(name="AsyncRangeValidator", description=f"Validates {value_type} values within specified ranges asynchronously")

        self.value_type = value_type
        self.inclusive_min = inclusive_min
        self.inclusive_max = inclusive_max
        self.extract_all = extract_all
        self.parsing_patterns = parsing_patterns or self._get_default_patterns()
        self.date_formats = date_formats or self._get_default_date_formats()
        self.allow_units = allow_units
        self.unit_conversions = unit_conversions or self._get_default_units()
        self.decimal_places = decimal_places
        self.required_count = required_count

        # Convert and validate min/max values
        self.min_value: Any = self._convert_value(min_value) if min_value is not None else None
        self.max_value: Any = self._convert_value(max_value) if max_value is not None else None

        # Validate range
        if self.min_value is not None and self.max_value is not None:
            try:
                if self.min_value > self.max_value:
                    raise ValueError(f"min_value ({self.min_value}) cannot be greater than max_value ({self.max_value})")
            except TypeError:
                # Can't compare different types
                pass

    async def validate_async(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate values in output against specified ranges asynchronously.

        Args:
            output: The LLM output containing values to validate
            context: Optional context (unused for range validation)

        Returns:
            ValidationResult with validation status and details
        """
        # Run validation in thread pool for CPU-intensive operations
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._validate_sync, output, context)

    def _validate_sync(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Synchronous validation logic (to be run in thread pool)."""
        errors: List[str] = []
        warnings: List[str] = []
        metadata: Dict[str, Any] = {"values_found": [], "valid_values": [], "invalid_values": [], "out_of_range_values": [], "units_found": [], "async_validation": True}

        output = output.strip()
        if not output:
            errors.append("Output is empty")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings, metadata=metadata)

        values: List[Tuple[str, Optional[str], Any]] = []

        if self.extract_all:
            # Extract all values from text
            if self.value_type in ["datetime", "date"]:
                # For dates, try to parse the entire segments
                for fmt in self.date_formats:
                    # Create a pattern from the format
                    pattern = fmt.replace("%Y", r"\\d{4}").replace("%y", r"\\d{2}")
                    pattern = pattern.replace("%m", r"\\d{1,2}").replace("%d", r"\\d{1,2}")
                    pattern = pattern.replace("%H", r"\\d{1,2}").replace("%M", r"\\d{1,2}")
                    pattern = pattern.replace("%S", r"\\d{1,2}").replace("%f", r"\\d+")
                    pattern = pattern.replace("%B", r"\\w+").replace("%b", r"\\w+")
                    pattern = re.sub(r"[^\\w\\d\\\\]", lambda m: "\\\\" + str(m.group(0)), pattern)

                    matches = re.findall(pattern, output)
                    for match in matches:
                        try:
                            parsed = self._convert_value(match)
                            values.append((match, None, parsed))
                        except ValueError:
                            continue
            else:
                # Extract numeric values
                extracted = self._extract_values(output)
                for value_str, unit in extracted:
                    try:
                        converted = self._convert_with_unit(value_str, unit)
                        values.append((value_str, unit, converted))
                        if unit:
                            metadata["units_found"].append(unit)
                    except (ValueError, InvalidOperation):
                        metadata["invalid_values"].append(value_str)
        else:
            # Treat entire output as single value
            try:
                if self.value_type in ["datetime", "date"]:
                    converted = self._convert_value(output)
                    values = [(output, None, converted)]
                else:
                    # Check for unit at the end
                    match = re.match(r"^(.+?)\\s*([a-zA-Z]+)?$", output)
                    if match and self.allow_units:
                        value_str, unit = match.groups()
                        if unit and unit.lower() in self.unit_conversions:
                            converted = self._convert_with_unit(value_str, unit.lower())
                            values = [(value_str, unit, converted)]
                            metadata["units_found"].append(unit)
                        else:
                            converted = self._convert_value(output)
                            values = [(output, None, converted)]
                    else:
                        converted = self._convert_value(output)
                        values = [(output, None, converted)]
            except (ValueError, InvalidOperation) as e:
                errors.append(f"Invalid {self.value_type} format: {output}")
                metadata["invalid_values"].append(output)
                return ValidationResult(is_valid=False, errors=errors, warnings=warnings, metadata=metadata)

        # Validate each value against range
        for original, unit, value in values:
            metadata["values_found"].append({"original": original, "unit": unit, "converted": str(value)})

            in_range = True

            # Check minimum
            if self.min_value is not None:
                try:
                    if self.inclusive_min:
                        if value < self.min_value:
                            in_range = False
                    else:
                        if value <= self.min_value:
                            in_range = False
                except TypeError:
                    # Can't compare different types
                    errors.append(f"Cannot compare {self.value_type} value with range bounds")
                    continue

            # Check maximum
            if self.max_value is not None:
                try:
                    if self.inclusive_max:
                        if value > self.max_value:
                            in_range = False
                    else:
                        if value >= self.max_value:
                            in_range = False
                except TypeError:
                    # Can't compare different types
                    errors.append(f"Cannot compare {self.value_type} value with range bounds")
                    continue

            if in_range:
                metadata["valid_values"].append(str(value))
            else:
                metadata["out_of_range_values"].append(str(value))
                min_str = f"{'≥' if self.inclusive_min else '>'} {self.min_value}" if self.min_value is not None else ""
                max_str = f"{'≤' if self.inclusive_max else '<'} {self.max_value}" if self.max_value is not None else ""
                range_str = f"{min_str} and {max_str}" if min_str and max_str else min_str or max_str
                errors.append(f"Value {value} is out of range (must be {range_str})")

        # Check required count
        if self.extract_all and self.required_count is not None:
            if len(metadata["valid_values"]) != self.required_count:
                errors.append(f"Expected exactly {self.required_count} valid values, but found {len(metadata['valid_values'])}")

        # Check decimal places for decimal type
        if self.value_type == "decimal" and self.decimal_places is not None:
            for original, _, value in values:
                if isinstance(value, Decimal):
                    # Check decimal places
                    value_str = str(value)
                    if "." in value_str:
                        decimal_part = value_str.split(".")[1]
                        if len(decimal_part) != self.decimal_places:
                            warnings.append(f"Value {value} should have exactly {self.decimal_places} decimal places")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings, metadata=metadata)

    def _get_default_patterns(self) -> List[str]:
        """Get default parsing patterns based on value type."""
        if self.value_type in ["number", "decimal"]:
            return [
                r"-?\\d+\\.?\\d*",  # Basic number
                r"-?\\d{1,3}(?:,\\d{3})*(?:\\.\\d+)?",  # Number with commas
                r"-?\\d+(?:\\.\\d+)?(?:[eE][+-]?\\d+)?",  # Scientific notation
            ]
        elif self.value_type == "integer":
            return [
                r"-?\\d+",  # Basic integer
                r"-?\\d{1,3}(?:,\\d{3})*",  # Integer with commas
            ]
        else:
            return []

    def _get_default_date_formats(self) -> List[str]:
        """Get default date formats."""
        if self.value_type == "datetime":
            return [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M",
                "%Y/%m/%d %H:%M:%S",
                "%Y/%m/%d %H:%M",
                "%d/%m/%Y %H:%M:%S",
                "%d/%m/%Y %H:%M",
                "%d-%m-%Y %H:%M:%S",
                "%d-%m-%Y %H:%M",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S.%fZ",
            ]
        elif self.value_type == "date":
            return [
                "%Y-%m-%d",
                "%Y/%m/%d",
                "%d/%m/%Y",
                "%d-%m-%Y",
                "%m/%d/%Y",
                "%m-%d-%Y",
                "%B %d, %Y",
                "%b %d, %Y",
                "%d %B %Y",
                "%d %b %Y",
            ]
        else:
            return []

    def _get_default_units(self) -> Dict[str, float]:
        """Get default unit conversions."""
        return {
            # Length (to meters)
            "mm": 0.001,
            "cm": 0.01,
            "m": 1.0,
            "meter": 1.0,
            "meters": 1.0,
            "km": 1000.0,
            "kilometer": 1000.0,
            "kilometers": 1000.0,
            "inch": 0.0254,
            "inches": 0.0254,
            "ft": 0.3048,
            "feet": 0.3048,
            "yard": 0.9144,
            "yards": 0.9144,
            "mile": 1609.34,
            "miles": 1609.34,
            # Weight (to kg)
            "mg": 0.000001,
            "g": 0.001,
            "gram": 0.001,
            "grams": 0.001,
            "kg": 1.0,
            "kilogram": 1.0,
            "kilograms": 1.0,
            "lb": 0.453592,
            "lbs": 0.453592,
            "pound": 0.453592,
            "pounds": 0.453592,
            "oz": 0.0283495,
            "ounce": 0.0283495,
            "ounces": 0.0283495,
            "ton": 1000.0,
            "tons": 1000.0,
            # Time (to seconds)
            "ms": 0.001,
            "millisecond": 0.001,
            "milliseconds": 0.001,
            "s": 1.0,
            "sec": 1.0,
            "second": 1.0,
            "seconds": 1.0,
            "min": 60.0,
            "minute": 60.0,
            "minutes": 60.0,
            "h": 3600.0,
            "hr": 3600.0,
            "hour": 3600.0,
            "hours": 3600.0,
            "day": 86400.0,
            "days": 86400.0,
        }

    def _convert_value(self, value: Any) -> Any:
        """Convert value to appropriate type."""
        if isinstance(value, str):
            if self.value_type in ["number", "integer", "decimal"]:
                # Remove commas and parse
                value = value.replace(",", "")
                if self.value_type == "integer":
                    return int(float(value))
                elif self.value_type == "decimal":
                    return Decimal(value)
                else:
                    return float(value)
            elif self.value_type == "datetime":
                for fmt in self.date_formats:
                    try:
                        return datetime.strptime(value, fmt)
                    except ValueError:
                        continue
                raise ValueError(f"Could not parse datetime: {value}")
            elif self.value_type == "date":
                for fmt in self.date_formats:
                    try:
                        return datetime.strptime(value, fmt).date()
                    except ValueError:
                        continue
                raise ValueError(f"Could not parse date: {value}")

        return value

    def _extract_values(self, output: str) -> List[Tuple[str, Optional[str]]]:
        """Extract values and optional units from output."""
        values_with_units = []

        if self.allow_units and self.value_type in ["number", "integer", "decimal"]:
            # Look for numbers with units
            unit_pattern = r"(-?\\d+(?:[.,]\\d+)?)\\s*([a-zA-Z]+)"
            matches = re.findall(unit_pattern, output)
            for number, unit in matches:
                values_with_units.append((number.replace(",", ""), unit.lower()))

        # Extract plain numbers
        for pattern in self.parsing_patterns:
            matches = re.findall(pattern, output)
            for match in matches:
                # Check if this number wasn't already captured with a unit
                clean_match = match.replace(",", "")
                if not any(clean_match in v[0] for v in values_with_units):
                    values_with_units.append((match, None))

        return values_with_units

    def _convert_with_unit(self, value_str: str, unit: Optional[str]) -> Any:
        """Convert value with optional unit to base unit."""
        # Parse the numeric value
        value = self._convert_value(value_str)

        if unit and self.allow_units and self.value_type in ["number", "integer", "decimal"]:
            if unit in self.unit_conversions:
                conversion = self.unit_conversions[unit]
                if isinstance(value, Decimal):
                    value = value * Decimal(str(conversion))
                else:
                    value = value * conversion

        return value

    def get_validation_instructions(self) -> str:
        """Get specific validation instructions for ranges."""
        instructions = f"""
ASYNC RANGE VALIDATION REQUIREMENTS:
- Output must contain {self.value_type} value(s)"""

        # Range requirements
        if self.min_value is not None and self.max_value is not None:
            min_op = "≥" if self.inclusive_min else ">"
            max_op = "≤" if self.inclusive_max else "<"
            instructions += f"\\n- Value must be {min_op} {self.min_value} and {max_op} {self.max_value}"
        elif self.min_value is not None:
            min_op = "≥" if self.inclusive_min else ">"
            instructions += f"\\n- Value must be {min_op} {self.min_value}"
        elif self.max_value is not None:
            max_op = "≤" if self.inclusive_max else "<"
            instructions += f"\\n- Value must be {max_op} {self.max_value}"

        if self.extract_all:
            instructions += "\\n- All numeric values in the output will be validated"
            if self.required_count:
                instructions += f"\\n- Exactly {self.required_count} valid values required"
        else:
            instructions += "\\n- The entire output will be treated as a single value"

        if self.allow_units and self.value_type in ["number", "integer", "decimal"]:
            instructions += "\\n- Values may include units (e.g., '5kg', '10 miles')"

        instructions += "\\n\\nThis validator runs asynchronously for better performance."

        return instructions
