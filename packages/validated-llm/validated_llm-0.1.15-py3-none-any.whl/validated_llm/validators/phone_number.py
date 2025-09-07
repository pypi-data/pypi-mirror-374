"""
Phone number validation for LLM outputs.
"""

import re
from typing import Any, Dict, List, Optional, Set

from validated_llm.base_validator import BaseValidator, ValidationResult


class PhoneNumberValidator(BaseValidator):
    """
    Validates phone numbers in LLM output.

    Features:
    - International format support (E.164)
    - Country-specific validation
    - Multiple phone number extraction
    - Format normalization
    - Common format detection
    """

    def __init__(
        self,
        name: str = "PhoneNumberValidator",
        description: str = "Validates phone numbers",
        extract_all: bool = False,
        min_numbers: int = 1,
        max_numbers: Optional[int] = None,
        allowed_countries: Optional[List[str]] = None,
        blocked_countries: Optional[List[str]] = None,
        require_country_code: bool = False,
        normalize_output: bool = True,
        allow_extensions: bool = True,
    ):
        """
        Initialize the phone number validator.

        Args:
            name: Validator name
            description: Validator description
            extract_all: Whether to extract all phone numbers from text
            min_numbers: Minimum number of valid phone numbers required
            max_numbers: Maximum number of phone numbers allowed
            allowed_countries: Whitelist of allowed country codes (e.g., ['US', 'GB'])
            blocked_countries: Blacklist of blocked country codes
            require_country_code: Whether country code is required
            normalize_output: Whether to normalize phone numbers to E.164 format
            allow_extensions: Whether to allow phone extensions
        """
        super().__init__(name, description)
        self.extract_all = extract_all
        self.min_numbers = min_numbers
        self.max_numbers = max_numbers
        self.allowed_countries = set(allowed_countries or [])
        self.blocked_countries = set(blocked_countries or [])
        self.require_country_code = require_country_code
        self.normalize_output = normalize_output
        self.allow_extensions = allow_extensions

        # Country codes mapping (partial list for common countries)
        self.country_codes = {"US": "1", "CA": "1", "GB": "44", "FR": "33", "DE": "49", "IT": "39", "ES": "34", "AU": "61", "JP": "81", "CN": "86", "IN": "91", "BR": "55", "MX": "52", "RU": "7", "ZA": "27"}

        # Phone number patterns
        self.patterns = [
            # E.164 format: +1234567890
            re.compile(r"\+\d{1,3}\d{4,14}(?:\s*(?:x|ext\.?|extension)\s*\d+)?"),
            # With separators: +1-234-567-8900, +1 (234) 567-8900
            re.compile(r"\+\d{1,3}[\s\-]?\(?\d{1,4}\)?[\s\-]?\d{1,4}[\s\-]?\d{1,4}[\s\-]?\d{0,4}(?:\s*(?:x|ext\.?|extension)\s*\d+)?"),
            # US format: (123) 456-7890, 123-456-7890
            re.compile(r"\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}(?:\s*(?:x|ext\.?|extension)\s*\d+)?"),
            # International without +: 00447911123456
            re.compile(r"00\d{1,3}\d{4,14}(?:\s*(?:x|ext\.?|extension)\s*\d+)?"),
        ]

    def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate phone numbers in the output.

        Args:
            output: The LLM output to validate
            context: Optional context with 'default_country' key

        Returns:
            ValidationResult with validation status and details
        """
        errors: list[str] = []
        warnings: list[str] = []
        metadata: dict[str, Any] = {"valid_numbers": [], "invalid_numbers": [], "normalized_numbers": [], "countries_found": set()}

        output = output.strip()
        default_country = context.get("default_country", "US") if context else "US"

        if not output:
            errors.append("Output is empty")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings, metadata=metadata)

        # Extract phone numbers
        if self.extract_all:
            found_numbers = []
            for pattern in self.patterns:
                found_numbers.extend(pattern.findall(output))
            # Remove duplicates while preserving order
            seen: Set[str] = set()
            unique_numbers = []
            for x in found_numbers:
                if x not in seen:
                    seen.add(x)
                    unique_numbers.append(x)
            found_numbers = unique_numbers
        else:
            # Treat entire output as single phone number
            found_numbers = [output.strip()]

        valid_numbers = []

        for number in found_numbers:
            number = number.strip()
            if not number:
                continue

            # Validate phone number format
            validation_result = self._validate_phone_format(number, default_country)

            if not validation_result["is_valid"]:
                metadata["invalid_numbers"].append(number)
                errors.append(validation_result["error"])
                continue

            normalized = validation_result["normalized"]
            country = validation_result["country"]

            # Check country whitelist
            if self.allowed_countries and country not in self.allowed_countries:
                metadata["invalid_numbers"].append(number)
                errors.append(f"Phone number country '{country}' not in allowed list: {', '.join(sorted(self.allowed_countries))}")
                continue

            # Check country blacklist
            if self.blocked_countries and country in self.blocked_countries:
                metadata["invalid_numbers"].append(number)
                errors.append(f"Phone number country '{country}' is blocked")
                continue

            # Check country code requirement
            if self.require_country_code and not validation_result["has_country_code"]:
                metadata["invalid_numbers"].append(number)
                errors.append(f"Phone number '{number}' missing required country code")
                continue

            # Check extension policy
            if not self.allow_extensions and validation_result.get("has_extension"):
                metadata["invalid_numbers"].append(number)
                errors.append(f"Phone number extensions not allowed: '{number}'")
                continue

            # Phone number is valid
            valid_numbers.append(number)
            metadata["valid_numbers"].append(number)
            metadata["normalized_numbers"].append(normalized)
            metadata["countries_found"].add(country)

        # Check phone number count requirements
        number_count = len(valid_numbers)

        if number_count < self.min_numbers:
            errors.append(f"Found {number_count} valid phone number(s), but at least {self.min_numbers} required")

        if self.max_numbers is not None and number_count > self.max_numbers:
            errors.append(f"Found {number_count} valid phone number(s), but maximum {self.max_numbers} allowed")

        # Convert sets to lists for JSON serialization
        metadata["countries_found"] = list(metadata["countries_found"])
        metadata["number_count"] = number_count

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings, metadata=metadata)

    def _validate_phone_format(self, number: str, default_country: str) -> Dict[str, Any]:
        """
        Validate phone number format and normalize.

        Args:
            number: Phone number to validate
            default_country: Default country code if not specified

        Returns:
            Dict with validation result and normalized number
        """
        result: Dict[str, Any] = {"is_valid": False, "error": "", "normalized": "", "country": default_country, "has_country_code": False, "has_extension": False}

        # Remove common formatting characters
        cleaned = re.sub(r"[\s\-\(\)]+", "", number)

        # Check for extension
        extension = ""
        ext_match = re.search(r"(?:x|ext\.?|extension)\s*(\d+)", number, re.IGNORECASE)
        if ext_match:
            result["has_extension"] = True
            extension = ext_match.group(1)
            # Remove extension for validation
            cleaned = re.sub(r"(?:x|ext\.?|extension)\s*\d+", "", cleaned, flags=re.IGNORECASE)

        # Check for country code
        if cleaned.startswith("+"):
            result["has_country_code"] = True
            # Extract country code (1-3 digits after +)
            for i in range(3, 0, -1):
                potential_code = cleaned[1 : i + 1]
                if potential_code.isdigit():
                    # Find country for this code
                    for country, code in self.country_codes.items():
                        if code == potential_code:
                            result["country"] = country
                            break
                    if result["country"] != default_country or potential_code in self.country_codes.values():
                        cleaned = cleaned[i + 1 :]
                        break
        elif cleaned.startswith("00"):
            result["has_country_code"] = True
            # International format without +
            cleaned = "+" + cleaned[2:]
            return self._validate_phone_format(number.replace("00", "+", 1), default_country)

        # Validate number length (excluding country code)
        if not cleaned.replace("+", "").isdigit():
            result["error"] = f"Invalid phone number format: '{number}' (contains non-numeric characters)"
            return result

        digits_only = re.sub(r"\D", "", cleaned)

        # Check length based on country
        if result["country"] == "US" or result["country"] == "CA":
            # North American Numbering Plan
            if not result["has_country_code"] and len(digits_only) == 10:
                result["is_valid"] = True
                result["normalized"] = f"+1{digits_only}"
            elif result["has_country_code"] and len(digits_only) == 11 and digits_only[0] == "1":
                result["is_valid"] = True
                result["normalized"] = f"+{digits_only}"
            else:
                result["error"] = f"Invalid phone number format: '{number}' (US/CA numbers must be 10 digits)"
        else:
            # General international validation (4-15 digits after country code)
            if len(digits_only) >= 4 and len(digits_only) <= 15:
                result["is_valid"] = True
                if result["has_country_code"]:
                    result["normalized"] = f"+{digits_only}"
                else:
                    # Add default country code
                    country = str(result["country"])
                    country_code = self.country_codes.get(country, "")
                    if country_code:
                        result["normalized"] = f"+{country_code}{digits_only}"
                    else:
                        result["normalized"] = f"+{digits_only}"
            else:
                result["error"] = f"Invalid phone number format: '{number}' (must be 4-15 digits)"

        # Add extension back if present and valid
        if result["is_valid"] and result["has_extension"]:
            result["normalized"] += f" x{extension}"

        return result

    def get_validation_instructions(self) -> str:
        """Get specific validation instructions for phone numbers."""
        instructions = f"""
PHONE NUMBER VALIDATION REQUIREMENTS:
- Output must contain valid phone number(s)
- Minimum phone numbers required: {self.min_numbers}"""

        if self.max_numbers:
            instructions += f"\n- Maximum phone numbers allowed: {self.max_numbers}"

        if self.allowed_countries:
            instructions += f"\n- Allowed countries: {', '.join(sorted(self.allowed_countries))}"

        if self.blocked_countries:
            instructions += f"\n- Blocked countries: {', '.join(sorted(self.blocked_countries))}"

        if self.require_country_code:
            instructions += "\n- Country code is REQUIRED (e.g., +1 for US/CA)"

        if not self.allow_extensions:
            instructions += "\n- Phone extensions are NOT allowed"

        if self.extract_all:
            instructions += "\n- All phone numbers in the output will be extracted and validated"
        else:
            instructions += "\n- The entire output will be treated as a single phone number"

        instructions += """

Examples of valid phone numbers:
- +1-234-567-8900 (US with country code)
- (234) 567-8900 (US without country code)
- +44 20 7123 4567 (UK)
- +33 1 42 86 82 00 (France)
- 123-456-7890 x123 (with extension)

Examples of invalid phone numbers:
- 123-456 (too short)
- 12345678901234567 (too long)
- abc-def-ghij (non-numeric)
- 123 456 789 (ambiguous without country context)
"""

        return instructions
