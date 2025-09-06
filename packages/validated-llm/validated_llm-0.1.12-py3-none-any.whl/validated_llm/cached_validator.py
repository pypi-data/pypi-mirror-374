"""
Cached validator mixin for automatic performance optimization.

This module provides a mixin class that validators can inherit from to automatically
get intelligent caching of validation results with minimal code changes.
"""

import hashlib
import time
from typing import Any, Dict, Optional

from .base_validator import BaseValidator, ValidationResult
from .validation_cache import ValidationCache, get_global_cache


class CachedValidatorMixin:
    """Mixin class that adds intelligent caching to validators.

    This mixin automatically caches validation results to avoid redundant
    expensive operations. It's designed to be mixed with BaseValidator subclasses.

    Example:
        ```python
        class FastJSONSchemaValidator(CachedValidatorMixin, JSONSchemaValidator):
            def __init__(self, schema: Dict[str, Any], use_cache: bool = True):
                JSONSchemaValidator.__init__(self, schema)
                CachedValidatorMixin.__init__(self, use_cache=use_cache)

        validator = FastJSONSchemaValidator(schema)
        result = validator.validate(json_data)  # First call: validation + caching
        result = validator.validate(json_data)  # Second call: cached result
        ```
    """

    def __init__(self, use_cache: bool = True, cache_instance: Optional[ValidationCache] = None, cache_ttl: Optional[float] = None, include_context_in_key: bool = True):
        """Initialize the cached validator mixin.

        Args:
            use_cache: Whether to enable caching
            cache_instance: Custom cache instance (uses global cache if None)
            cache_ttl: Override TTL for this validator's entries
            include_context_in_key: Whether to include context in cache keys
        """
        self._use_cache = use_cache
        self._cache = cache_instance or get_global_cache()
        self._cache_ttl = cache_ttl
        self._include_context_in_key = include_context_in_key
        self._cache_stats = {"validator_hits": 0, "validator_misses": 0, "cache_saves": 0}

    def _get_validator_id(self) -> str:
        """Generate unique identifier for this validator instance.

        The ID includes the validator class and key configuration parameters
        to ensure cache isolation between different validator configurations.
        """
        # Get base class name (the actual validator, not the mixin)
        class_name = self.__class__.__name__

        # Include key configuration in ID
        config_parts = []

        # Add validator-specific configuration
        if hasattr(self, "schema"):
            # For schema validators, include schema hash
            schema_str = str(self.schema)
            schema_hash = hashlib.md5(schema_str.encode()).hexdigest()[:8]
            config_parts.append(f"schema:{schema_hash}")

        if hasattr(self, "pattern"):
            # For regex validators
            config_parts.append(f"pattern:{hash(self.pattern)}")

        if hasattr(self, "min_value") and hasattr(self, "max_value"):
            # For range validators
            config_parts.append(f"range:{self.min_value}-{self.max_value}")

        if hasattr(self, "url_regex"):
            # For URL validators
            config_parts.append(f"url_regex:{hash(str(self.url_regex))}")

        # Combine class name and configuration
        config_suffix = "_".join(config_parts) if config_parts else "default"
        return f"{class_name}_{config_suffix}"

    def _should_use_cache(self, context: Optional[Dict[str, Any]] = None) -> bool:
        """Determine if caching should be used for this validation."""
        if not self._use_cache:
            return False

        # Don't cache if context indicates this is a one-time validation
        if context and context.get("disable_cache", False):
            return False

        # Don't cache very small inputs (overhead not worth it)
        return True

    def _get_cache_context(self, context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Extract relevant context for cache key generation."""
        if not self._include_context_in_key or not context:
            return None

        # Only include serializable context values that affect validation
        cacheable_context: Dict[str, Any] = {}

        for key, value in context.items():
            # Skip non-serializable or cache-control values
            if key.startswith("_") or key in ["disable_cache", "cache_ttl"]:
                continue

            # Include basic types that affect validation behavior
            if isinstance(value, (str, int, float, bool, type(None))):
                cacheable_context[key] = value
            elif isinstance(value, (list, tuple)) and all(isinstance(x, (str, int, float, bool)) for x in value):
                cacheable_context[key] = value  # Keep as-is for cache key
            elif isinstance(value, dict):
                # Include simple dict values
                simple_dict = {k: v for k, v in value.items() if isinstance(v, (str, int, float, bool))}
                if simple_dict:
                    cacheable_context[key] = simple_dict

        return cacheable_context if cacheable_context else None

    def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Enhanced validate method with automatic caching.

        This method wraps the original validate method with caching logic.
        It checks the cache first, and only calls the actual validation
        if no cached result is available.
        """
        # Check if we should use caching
        if not self._should_use_cache(context):
            return self._validate_uncached(output, context)

        # Generate cache key
        validator_id = self._get_validator_id()
        cache_context = self._get_cache_context(context)

        # Try to get cached result
        cached_result = self._cache.get(validator_id, output, cache_context)
        if cached_result is not None:
            self._cache_stats["validator_hits"] += 1
            return cached_result

        # Cache miss - perform actual validation
        self._cache_stats["validator_misses"] += 1
        start_time = time.time()
        result = self._validate_uncached(output, context)
        validation_time = time.time() - start_time

        # Store result in cache
        self._cache.put(validator_id, output, result, cache_context)
        self._cache_stats["cache_saves"] += 1

        return result

    def _validate_uncached(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Perform actual validation without caching.

        This method must be overridden by subclasses to call the actual validator.
        """
        raise NotImplementedError("Subclasses must implement _validate_uncached to call the actual validator")

    def clear_cache(self) -> None:
        """Clear cache entries for this validator."""
        # This is a simplified clear - in practice, we'd need more sophisticated
        # cache management to clear only entries for this specific validator
        if hasattr(self._cache, "clear"):
            self._cache.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get caching statistics for this validator."""
        validator_total = self._cache_stats["validator_hits"] + self._cache_stats["validator_misses"]
        validator_hit_rate = self._cache_stats["validator_hits"] / validator_total if validator_total > 0 else 0.0

        return {
            "validator_id": self._get_validator_id(),
            "cache_enabled": self._use_cache,
            "validator_hit_rate": validator_hit_rate,
            "validator_hits": self._cache_stats["validator_hits"],
            "validator_misses": self._cache_stats["validator_misses"],
            "cache_saves": self._cache_stats["cache_saves"],
            "global_cache_stats": self._cache.get_stats(),
        }

    def configure_cache(self, use_cache: Optional[bool] = None, cache_ttl: Optional[float] = None, include_context_in_key: Optional[bool] = None) -> None:
        """Reconfigure caching settings for this validator."""
        if use_cache is not None:
            self._use_cache = use_cache
        if cache_ttl is not None:
            self._cache_ttl = cache_ttl
        if include_context_in_key is not None:
            self._include_context_in_key = include_context_in_key


class FastJSONSchemaValidator(CachedValidatorMixin):
    """Example cached JSON schema validator.

    This demonstrates how to create a cached version of an existing validator
    with minimal code changes.
    """

    def __init__(self, schema: Dict[str, Any], use_cache: bool = True, **kwargs: Any) -> None:
        """Initialize with caching enabled by default."""
        # Import here to avoid circular imports
        from .validators.json_schema import JSONSchemaValidator

        # Initialize the base validator
        self._base_validator = JSONSchemaValidator(schema, **kwargs)

        # Initialize caching
        CachedValidatorMixin.__init__(self, use_cache=use_cache)

        # Store schema for cache key generation
        self.schema = schema

    def _validate_uncached(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Delegate to the base validator."""
        return self._base_validator.validate(output, context)

    def get_validation_instructions(self) -> str:
        """Delegate to the base validator."""
        return self._base_validator.get_validation_instructions()


class FastRegexValidator(CachedValidatorMixin):
    """Example cached regex validator."""

    def __init__(self, pattern: str, use_cache: bool = True, **kwargs: Any) -> None:
        """Initialize with caching enabled by default."""
        # Import here to avoid circular imports
        from .validators.regex import RegexValidator

        # Initialize the base validator
        self._base_validator = RegexValidator(pattern, **kwargs)

        # Initialize caching
        CachedValidatorMixin.__init__(self, use_cache=use_cache)

        # Store pattern for cache key generation
        self.pattern = pattern

    def _validate_uncached(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Delegate to the base validator."""
        return self._base_validator.validate(output, context)

    def get_validation_instructions(self) -> str:
        """Delegate to the base validator."""
        return self._base_validator.get_validation_instructions()


def make_cached_validator(validator_class: type, use_cache: bool = True) -> type:
    """Factory function to create a cached version of any validator class.

    Args:
        validator_class: The validator class to add caching to
        use_cache: Whether caching should be enabled by default

    Returns:
        A new class that combines the original validator with caching

    Example:
        ```python
        CachedURLValidator = make_cached_validator(URLValidator)
        validator = CachedURLValidator()
        ```
    """

    class CachedValidator(CachedValidatorMixin, validator_class):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            # Extract cache-related kwargs
            cache_kwargs = {k: kwargs.pop(k) for k in list(kwargs.keys()) if k in ["use_cache", "cache_instance", "cache_ttl", "include_context_in_key"]}
            cache_kwargs.setdefault("use_cache", use_cache)

            # Initialize both parent classes
            super(CachedValidatorMixin, self).__init__(*args, **kwargs)
            CachedValidatorMixin.__init__(self, **cache_kwargs)

        def _validate_uncached(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
            """Call the original validator's validate method."""
            # Directly call the validator class's validate method
            result = super(CachedValidatorMixin, self).validate(output, context)
            assert isinstance(result, ValidationResult), f"Expected ValidationResult, got {type(result)}"
            return result

    # Set a meaningful name for the new class
    CachedValidator.__name__ = f"Cached{validator_class.__name__}"
    CachedValidator.__qualname__ = f"Cached{validator_class.__qualname__}"

    return CachedValidator
