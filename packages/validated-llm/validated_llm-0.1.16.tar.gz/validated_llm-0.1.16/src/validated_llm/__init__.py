"""
validated-llm: LLM output validation with retry loops

A robust framework for validating language model outputs with automatic retry mechanisms.
Designed for applications where you need reliable, structured responses from LLMs.
"""

# Plugin system
from . import plugins

# Core validation components
from .async_validation_loop import AsyncValidationLoop
from .async_validator import AsyncBaseValidator, AsyncCompositeValidator, AsyncFunctionValidator, AsyncValidatorAdapter
from .base_validator import BaseValidator, FunctionValidator, ValidationResult
from .cached_validator import CachedValidatorMixin, make_cached_validator

# Code import/export formats
from .code_formats import CodeExporter, CodeFormatter, CodeImporter

# Enhanced validation components
from .enhanced_validation import EnhancedValidationResult, ErrorCategory, ErrorSeverity
from .enhanced_validation import ValidationError as EnhancedValidationError

# LLM providers
from .llm_providers import LLMProvider, OllamaProvider, OpenAIProvider

# Import specific task classes
from .tasks.base_task import BaseTask
from .tasks.csv_generation import CSVGenerationTask
from .tasks.json_generation import PersonJSONTask, ProductCatalogTask
from .tasks.story_to_scenes import StoryToScenesTask

# Performance optimization components
from .validation_cache import ValidationCache, clear_global_cache, configure_global_cache, get_global_cache, get_global_cache_stats
from .validation_loop import ValidationLoop


# Define exceptions (will be moved to separate module later)
class ValidationError(Exception):
    """Raised when validation fails"""


class MaxRetriesExceeded(Exception):
    """Raised when maximum retry attempts are exceeded"""


class LLMError(Exception):
    """Raised when LLM API calls fail"""


__version__ = "0.1.15"
__author__ = "validated-llm contributors"
__email__ = "contact@example.com"

__all__ = [
    # Core classes
    "ValidationLoop",
    "AsyncValidationLoop",
    "BaseTask",
    "BaseValidator",
    "AsyncBaseValidator",
    "FunctionValidator",
    "AsyncFunctionValidator",
    "AsyncCompositeValidator",
    "AsyncValidatorAdapter",
    "ValidationResult",
    # LLM providers
    "LLMProvider",
    "OpenAIProvider",
    "OllamaProvider",
    # Performance optimization
    "ValidationCache",
    "get_global_cache",
    "configure_global_cache",
    "clear_global_cache",
    "get_global_cache_stats",
    "CachedValidatorMixin",
    "make_cached_validator",
    # Enhanced validation
    "EnhancedValidationError",
    "EnhancedValidationResult",
    "ErrorCategory",
    "ErrorSeverity",
    # Code formats
    "CodeFormatter",
    "CodeImporter",
    "CodeExporter",
    # Exceptions
    "ValidationError",
    "MaxRetriesExceeded",
    "LLMError",
    # Tasks
    "CSVGenerationTask",
    "PersonJSONTask",
    "ProductCatalogTask",
    "StoryToScenesTask",
    # Plugin system
    "plugins",
    # Metadata
    "__version__",
]
