"""
Email validation for LLM outputs.
"""

import re
from typing import Any, Dict, List, Optional, Set

from validated_llm.base_validator import BaseValidator, ValidationResult
from validated_llm.config import get_validator_config


class EmailValidator(BaseValidator):
    """
    Validates email addresses in LLM output.

    Features:
    - RFC-compliant email validation
    - Domain whitelist/blacklist support
    - Multiple email extraction
    - Case sensitivity options
    - Common typo detection
    """

    def __init__(
        self,
        name: str = "EmailValidator",
        description: str = "Validates email addresses",
        extract_all: bool = False,
        min_emails: int = 1,
        max_emails: Optional[int] = None,
        allowed_domains: Optional[List[str]] = None,
        blocked_domains: Optional[List[str]] = None,
        case_sensitive_local: bool = True,
        allow_smtputf8: Optional[bool] = None,
        check_deliverability: Optional[bool] = None,
        suggest_corrections: bool = True,
    ):
        """
        Initialize the email validator.

        Args:
            name: Validator name
            description: Validator description
            extract_all: Whether to extract all emails from text
            min_emails: Minimum number of valid emails required
            max_emails: Maximum number of emails allowed
            allowed_domains: Whitelist of allowed email domains
            blocked_domains: Blacklist of blocked email domains
            case_sensitive_local: Whether local part (before @) is case-sensitive
            allow_smtputf8: Whether to allow international characters
            check_deliverability: Whether to check if email is deliverable (DNS check)
            suggest_corrections: Whether to suggest corrections for common typos
        """
        super().__init__(name, description)

        # Load config defaults
        config = get_validator_config("EmailValidator")

        # Apply config defaults if not explicitly set
        if allow_smtputf8 is None:
            allow_smtputf8 = config.get("allow_smtputf8", True)
        if check_deliverability is None:
            check_deliverability = config.get("check_deliverability", False)

        self.extract_all = extract_all
        self.min_emails = min_emails
        self.max_emails = max_emails
        self.allowed_domains = set(d.lower() for d in (allowed_domains or []))
        self.blocked_domains = set(d.lower() for d in (blocked_domains or []))
        self.case_sensitive_local = case_sensitive_local
        self.allow_smtputf8 = allow_smtputf8
        self.check_deliverability = check_deliverability
        self.suggest_corrections = suggest_corrections

        # Email regex pattern (simplified but covers most cases)
        if self.allow_smtputf8:
            # Allow international characters
            self.email_pattern = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b", re.UNICODE)
        else:
            # ASCII only
            self.email_pattern = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b")

        # Common email domain typos
        self.common_typos = {
            "gmial.com": "gmail.com",
            "gmai.com": "gmail.com",
            "gmil.com": "gmail.com",
            "gamil.com": "gmail.com",
            "gmaill.com": "gmail.com",
            "yahooo.com": "yahoo.com",
            "yaho.com": "yahoo.com",
            "yahou.com": "yahoo.com",
            "outlok.com": "outlook.com",
            "outloo.com": "outlook.com",
            "hotmial.com": "hotmail.com",
            "hotmil.com": "hotmail.com",
            "hotmai.com": "hotmail.com",
        }

    def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate email addresses in the output.

        Args:
            output: The LLM output to validate
            context: Optional context (not used)

        Returns:
            ValidationResult with validation status and details
        """
        errors: list[str] = []
        warnings: list[str] = []
        metadata: dict[str, Any] = {"valid_emails": [], "invalid_emails": [], "suggested_corrections": {}, "domains_found": set()}

        output = output.strip()

        if not output:
            errors.append("Output is empty")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings, metadata=metadata)

        # Extract emails
        if self.extract_all:
            found_emails = self.email_pattern.findall(output)
        else:
            # Treat entire output as single email
            found_emails = [output.strip()]

        valid_emails = []

        for email in found_emails:
            email = email.strip()
            if not email:
                continue

            # Validate email format
            validation_result = self._validate_email_format(email)

            if not validation_result["is_valid"]:
                metadata["invalid_emails"].append(email)
                errors.append(validation_result["error"])

                # Suggest corrections if enabled
                if self.suggest_corrections and validation_result.get("suggestion"):
                    metadata["suggested_corrections"][email] = validation_result["suggestion"]
                    warnings.append(f"Did you mean: {validation_result['suggestion']}?")
                continue

            # Extract domain
            local_part, domain = email.rsplit("@", 1)
            domain_lower = domain.lower()
            metadata["domains_found"].add(domain_lower)

            # Check domain whitelist
            if self.allowed_domains and domain_lower not in self.allowed_domains:
                metadata["invalid_emails"].append(email)
                errors.append(f"Email domain '{domain}' not in allowed list: {', '.join(sorted(self.allowed_domains))}")
                continue

            # Check domain blacklist
            if self.blocked_domains and domain_lower in self.blocked_domains:
                metadata["invalid_emails"].append(email)
                errors.append(f"Email domain '{domain}' is blocked")
                continue

            # Check for common typos
            if self.suggest_corrections and domain_lower in self.common_typos:
                corrected = f"{local_part}@{self.common_typos[domain_lower]}"
                metadata["suggested_corrections"][email] = corrected
                warnings.append(f"Possible typo in '{email}'. Did you mean '{corrected}'?")

            # Check deliverability if requested
            if self.check_deliverability and not self._check_email_deliverable(email):
                warnings.append(f"Email domain '{domain}' may not be deliverable (DNS check failed)")

            # Email is valid
            valid_emails.append(email)
            metadata["valid_emails"].append(email)

        # Check email count requirements
        email_count = len(valid_emails)

        if email_count < self.min_emails:
            errors.append(f"Found {email_count} valid email(s), but at least {self.min_emails} required")

        if self.max_emails is not None and email_count > self.max_emails:
            errors.append(f"Found {email_count} valid email(s), but maximum {self.max_emails} allowed")

        # Convert domains set to list for JSON serialization
        metadata["domains_found"] = list(metadata["domains_found"])
        metadata["email_count"] = email_count

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings, metadata=metadata)

    def _validate_email_format(self, email: str) -> Dict[str, Any]:
        """
        Validate email format according to RFC standards.

        Args:
            email: Email address to validate

        Returns:
            Dict with validation result and possible suggestion
        """
        result = {"is_valid": False, "error": "", "suggestion": None}

        # Basic format check
        if "@" not in email:
            result["error"] = f"Invalid email format: '{email}' (missing @ symbol)"
            return result

        parts = email.split("@")
        if len(parts) != 2:
            result["error"] = f"Invalid email format: '{email}' (multiple @ symbols)"
            return result

        local_part, domain = parts

        # Validate local part
        if not local_part:
            result["error"] = f"Invalid email format: '{email}' (empty local part)"
            return result

        if len(local_part) > 64:
            result["error"] = f"Invalid email format: '{email}' (local part too long, max 64 characters)"
            return result

        # Check for invalid characters in local part
        if not re.match(r"^[a-zA-Z0-9._%+-]+$", local_part):
            result["error"] = f"Invalid email format: '{email}' (invalid characters in local part)"
            return result

        # Check for consecutive dots
        if ".." in local_part:
            result["error"] = f"Invalid email format: '{email}' (consecutive dots not allowed)"
            return result

        # Check if starts or ends with dot
        if local_part.startswith(".") or local_part.endswith("."):
            result["error"] = f"Invalid email format: '{email}' (local part cannot start or end with dot)"
            return result

        # Validate domain
        if not domain:
            result["error"] = f"Invalid email format: '{email}' (empty domain)"
            return result

        if len(domain) > 255:
            result["error"] = f"Invalid email format: '{email}' (domain too long, max 255 characters)"
            return result

        # Check domain format
        domain_parts = domain.split(".")
        if len(domain_parts) < 2:
            result["error"] = f"Invalid email format: '{email}' (domain must have at least one dot)"

            # Suggest adding .com if no TLD
            if self.suggest_corrections and domain_parts[0] in ["gmail", "yahoo", "outlook", "hotmail"]:
                result["suggestion"] = f"{local_part}@{domain_parts[0]}.com"
            return result

        # Check each domain part
        for part in domain_parts:
            if not part:
                result["error"] = f"Invalid email format: '{email}' (empty domain part)"
                return result

            if not re.match(r"^[a-zA-Z0-9-]+$", part):
                result["error"] = f"Invalid email format: '{email}' (invalid characters in domain)"
                return result

            if part.startswith("-") or part.endswith("-"):
                result["error"] = f"Invalid email format: '{email}' (domain parts cannot start or end with hyphen)"
                return result

        # Check TLD
        tld = domain_parts[-1]
        if not tld.isalpha() or len(tld) < 2:
            result["error"] = f"Invalid email format: '{email}' (invalid top-level domain)"
            return result

        result["is_valid"] = True
        return result

    def _check_email_deliverable(self, email: str) -> bool:
        """
        Check if email domain has valid MX records.

        Args:
            email: Email address to check

        Returns:
            True if domain has MX records, False otherwise
        """
        try:
            import dns.resolver

            domain = email.split("@")[1]
            mx_records = dns.resolver.resolve(domain, "MX")
            return len(mx_records) > 0
        except Exception:
            # DNS resolution failed or dnspython not installed
            return False

    def get_validation_instructions(self) -> str:
        """Get specific validation instructions for email."""
        instructions = f"""
EMAIL VALIDATION REQUIREMENTS:
- Output must contain valid email address(es)
- Minimum emails required: {self.min_emails}"""

        if self.max_emails:
            instructions += f"\n- Maximum emails allowed: {self.max_emails}"

        if self.allowed_domains:
            instructions += f"\n- Allowed email domains: {', '.join(sorted(self.allowed_domains))}"

        if self.blocked_domains:
            instructions += f"\n- Blocked email domains: {', '.join(sorted(self.blocked_domains))}"

        if not self.case_sensitive_local:
            instructions += "\n- Email local parts are case-insensitive"

        if self.extract_all:
            instructions += "\n- All email addresses in the output will be extracted and validated"
        else:
            instructions += "\n- The entire output will be treated as a single email address"

        instructions += """

Examples of valid email addresses:
- john.doe@example.com
- jane_smith123@company.org
- support+tag@service.io
- user.name@subdomain.example.com

Examples of invalid email addresses:
- invalid.email (missing @ and domain)
- @example.com (missing local part)
- user@.com (missing domain name)
- user..name@example.com (consecutive dots)
- user@domain (missing top-level domain)
"""

        return instructions
