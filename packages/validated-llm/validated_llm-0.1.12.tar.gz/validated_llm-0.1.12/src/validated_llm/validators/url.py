"""
URL validation for LLM outputs.
"""

import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from validated_llm.base_validator import BaseValidator, ValidationResult


class URLValidator(BaseValidator):
    """
    Validates that the output contains valid URLs.

    Can validate:
    - Single URL outputs
    - Multiple URLs in text
    - Specific URL schemes (http, https, ftp, etc.)
    - URL reachability (optional)
    """

    def __init__(
        self,
        name: str = "URLValidator",
        description: str = "Validates URLs in the output",
        require_scheme: bool = True,
        allowed_schemes: Optional[List[str]] = None,
        check_reachability: bool = False,
        extract_all: bool = False,
        min_urls: int = 1,
        max_urls: Optional[int] = None,
    ):
        """
        Initialize the URL validator.

        Args:
            name: Validator name
            description: Validator description
            require_scheme: Whether URLs must have a scheme (http://, https://, etc.)
            allowed_schemes: List of allowed URL schemes. If None, common schemes are allowed
            check_reachability: Whether to check if URLs are reachable (makes HTTP requests)
            extract_all: Whether to extract and validate all URLs in the text
            min_urls: Minimum number of valid URLs required
            max_urls: Maximum number of URLs allowed (None for unlimited)
        """
        super().__init__(name, description)
        self.require_scheme = require_scheme
        self.allowed_schemes = allowed_schemes or ["http", "https", "ftp", "ftps"]
        self.check_reachability = check_reachability
        self.extract_all = extract_all
        self.min_urls = min_urls
        self.max_urls = max_urls

        # URL regex pattern - handles most common URL formats
        self.url_pattern = re.compile(
            r"(?:(?:https?|ftp|ftps):\/\/)?" r"(?:www\.)?" r"(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}" r"(?::[0-9]+)?" r'(?:\/[^"\s]*)?',  # Optional scheme  # Optional www  # Domain  # Optional port  # Optional path
            re.IGNORECASE,
        )

    def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate URLs in the output.

        Args:
            output: The LLM output to validate
            context: Optional context (not used for URL validation)

        Returns:
            ValidationResult with validation status and details
        """
        errors: list[str] = []
        warnings: list[str] = []
        metadata: dict[str, Any] = {"valid_urls": [], "invalid_urls": []}

        # Clean the output
        output = output.strip()

        if not output:
            errors.append("Output is empty")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings, metadata=metadata)

        # Extract URLs based on mode
        if self.extract_all:
            # Find all URLs in the text
            found_urls = self.url_pattern.findall(output)
        else:
            # Treat the entire output as a single URL
            found_urls = [output]

        # Validate each URL
        valid_urls = []
        for url in found_urls:
            url = url.strip()
            if not url:
                continue

            # Add scheme if missing and not required
            if not self.require_scheme and not url.startswith(("http://", "https://", "ftp://", "ftps://")):
                # Try with https://
                test_url = f"https://{url}"
            else:
                test_url = url

            # Parse and validate URL
            try:
                parsed = urlparse(test_url)

                # Check if URL has required components
                if self.require_scheme and not parsed.scheme:
                    metadata["invalid_urls"].append(url)
                    errors.append(f"URL missing scheme: {url}")
                    continue

                # Check allowed schemes
                if parsed.scheme and parsed.scheme.lower() not in self.allowed_schemes:
                    metadata["invalid_urls"].append(url)
                    errors.append(f"URL scheme '{parsed.scheme}' not allowed. Allowed schemes: {', '.join(self.allowed_schemes)}")
                    continue

                # Check if URL has a valid domain
                if not parsed.netloc:
                    metadata["invalid_urls"].append(url)
                    errors.append(f"URL missing domain: {url}")
                    continue

                # Basic domain validation
                domain_parts = parsed.netloc.split(".")
                if len(domain_parts) < 2:
                    metadata["invalid_urls"].append(url)
                    errors.append(f"Invalid domain format: {parsed.netloc}")
                    continue

                # URL is valid
                valid_urls.append(test_url)
                metadata["valid_urls"].append(test_url)

                # Check reachability if requested
                if self.check_reachability:
                    if not self._check_url_reachable(test_url):
                        warnings.append(f"URL is not reachable: {test_url}")

            except Exception as e:
                metadata["invalid_urls"].append(url)
                errors.append(f"Invalid URL format '{url}': {str(e)}")

        # Check URL count requirements
        url_count = len(valid_urls)

        if url_count < self.min_urls:
            errors.append(f"Found {url_count} valid URL(s), but at least {self.min_urls} required")

        if self.max_urls is not None and url_count > self.max_urls:
            errors.append(f"Found {url_count} valid URL(s), but maximum {self.max_urls} allowed")

        # Add metadata
        metadata["url_count"] = url_count
        metadata["schemes_found"] = list(set(urlparse(url).scheme for url in valid_urls if urlparse(url).scheme))

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings, metadata=metadata)

    def _check_url_reachable(self, url: str) -> bool:
        """
        Check if a URL is reachable by making a HEAD request.

        Args:
            url: The URL to check

        Returns:
            True if reachable, False otherwise
        """
        try:
            import requests  # type: ignore

            response = requests.head(url, timeout=5, allow_redirects=True)
            return bool(response.status_code < 400)
        except Exception:
            return False

    def get_validation_instructions(self) -> str:
        """Get specific validation instructions for URLs."""
        instructions = f"""
URL VALIDATION REQUIREMENTS:
- Output must contain valid URL(s)
- Minimum URLs required: {self.min_urls}"""

        if self.max_urls:
            instructions += f"\n- Maximum URLs allowed: {self.max_urls}"

        if self.require_scheme:
            instructions += f"\n- URLs must include scheme (e.g., http://, https://)"

        if self.allowed_schemes:
            instructions += f"\n- Allowed URL schemes: {', '.join(self.allowed_schemes)}"

        if self.extract_all:
            instructions += "\n- All URLs in the output will be extracted and validated"
        else:
            instructions += "\n- The entire output will be treated as a single URL"

        if self.check_reachability:
            instructions += "\n- URLs will be checked for reachability"

        instructions += """

Examples of valid URLs:
- https://www.example.com
- http://subdomain.example.org:8080/path/to/resource
- ftp://files.example.net/downloads/file.zip

Examples of invalid URLs:
- example.com (missing scheme if required)
- http:// (missing domain)
- not-a-url (invalid format)
"""

        return instructions
