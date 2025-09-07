"""
Configuration management for validated-llm framework.

Supports loading configuration from .validated-llm.yml files for project-specific defaults.
"""

import dataclasses
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

import yaml

from .error_formatting import ErrorCategory, create_enhanced_error


@dataclass
class ValidatedLLMConfig:
    """Configuration for validated-llm framework."""

    # LLM settings
    llm_vendor: str = "ollama"  # Default vendor
    llm_model: str = "gemma3:27b"
    llm_temperature: float = 0.7
    llm_max_tokens: Optional[int] = None

    # Validation settings
    max_retries: int = 3
    timeout_seconds: int = 60
    show_progress: bool = True

    # Default validator settings
    validator_defaults: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Task-specific settings
    task_defaults: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Code generation defaults
    code_language: str = "python"
    code_style_formatter: str = "black"
    require_code_examples: bool = True
    require_tests: bool = True

    # Documentation defaults
    doc_min_sections: int = 3
    doc_min_words_per_section: int = 50
    doc_check_links: bool = True
    doc_check_spelling: bool = False

    # Output settings
    output_format: str = "markdown"
    verbose: bool = False

    # Plugin settings
    plugin_paths: List[str] = field(default_factory=list)
    enabled_plugins: List[str] = field(default_factory=list)

    def merge(self, other: "ValidatedLLMConfig") -> None:
        """Merge another config into this one, with other taking precedence."""
        for field_name in self.__dataclass_fields__:
            other_value = getattr(other, field_name)
            current_value = getattr(self, field_name)

            # Get the default value for this field
            field_info = self.__dataclass_fields__[field_name]
            if hasattr(field_info, "default") and field_info.default is not dataclasses.MISSING:
                default_value = field_info.default
            elif hasattr(field_info, "default_factory") and field_info.default_factory is not dataclasses.MISSING:
                # For fields with default_factory
                default_value = field_info.default_factory()
            else:
                default_value = None

            # Only merge if other value differs from default
            if other_value != default_value:
                if field_name in ("validator_defaults", "task_defaults"):
                    # Deep merge dictionaries
                    for key, value in other_value.items():
                        if key in current_value:
                            current_value[key].update(value)
                        else:
                            current_value[key] = value
                elif field_name in ("plugin_paths", "enabled_plugins"):
                    # Extend lists only with non-duplicate values
                    for item in other_value:
                        if item not in current_value:
                            current_value.append(item)
                else:
                    # Simple override
                    setattr(self, field_name, other_value)


class ConfigLoader:
    """Loads and manages validated-llm configuration."""

    CONFIG_FILENAME = ".validated-llm.yml"
    GLOBAL_CONFIG_DIR = Path.home() / ".config" / "validated-llm"

    def __init__(self) -> None:
        self._config_cache: Dict[str, ValidatedLLMConfig] = {}
        self._current_config: Optional[ValidatedLLMConfig] = None

    def _get_env_cache_key(self) -> str:
        """Get cache key based on environment variables."""
        env_keys = [
            "VALIDATED_LLM_VENDOR",
            "VALIDATED_LLM_MODEL",
            "VALIDATED_LLM_TEMPERATURE",
            "VALIDATED_LLM_MAX_TOKENS",
            "VALIDATED_LLM_MAX_RETRIES",
            "VALIDATED_LLM_TIMEOUT",
            "VALIDATED_LLM_SHOW_PROGRESS",
            "VALIDATED_LLM_CODE_LANGUAGE",
            "VALIDATED_LLM_VERBOSE",
        ]
        env_values = [os.environ.get(key, "") for key in env_keys]
        return ":".join(env_values)

    def load_config(self, start_path: Optional[Union[str, Path]] = None) -> ValidatedLLMConfig:
        """
        Load configuration from multiple sources in order of precedence:
        1. Environment variables (VALIDATED_LLM_*)
        2. Local project config (.validated-llm.yml in current or parent dirs)
        3. User global config (~/.config/validated-llm/config.yml)
        4. Default configuration

        Args:
            start_path: Starting directory to search for config (defaults to cwd)

        Returns:
            Merged configuration object
        """
        # Create cache key based on start_path and environment variables
        cache_key = f"{start_path or 'cwd'}:{self._get_env_cache_key()}"

        # Check if we have this exact configuration cached
        if cache_key in self._config_cache:
            config = self._config_cache[cache_key]
            self._current_config = config
            return config

        # Start with defaults
        config = ValidatedLLMConfig()

        # Load global config if exists
        global_config = self._load_global_config()
        if global_config:
            config.merge(global_config)

        # Load project config (searches up directory tree)
        project_config = self._load_project_config(start_path)
        if project_config:
            config.merge(project_config)

        # Apply environment variable overrides
        env_config = self._load_env_config()
        if env_config:
            config.merge(env_config)

        # Cache the merged result
        self._config_cache[cache_key] = config
        self._current_config = config
        return config

    def _load_global_config(self) -> Optional[ValidatedLLMConfig]:
        """Load global user configuration."""
        global_config_path = self.GLOBAL_CONFIG_DIR / "config.yml"

        if global_config_path.exists():
            try:
                return self._load_config_file(global_config_path)
            except Exception as e:
                # Log warning but don't fail
                print(f"Warning: Failed to load global config: {e}")

        return None

    def _load_project_config(self, start_path: Optional[Union[str, Path]] = None) -> Optional[ValidatedLLMConfig]:
        """Load project-specific configuration by searching up directory tree."""
        if start_path is None:
            start_path = Path.cwd()
        else:
            start_path = Path(start_path)

        # Search up directory tree
        current_path = start_path.resolve()

        while current_path != current_path.parent:
            config_path = current_path / self.CONFIG_FILENAME

            if config_path.exists():
                # Load config file
                try:
                    config = self._load_config_file(config_path)
                    return config
                except Exception as e:
                    raise ValueError(f"Invalid config at {config_path}: {e}")

            current_path = current_path.parent

        return None

    def _load_config_file(self, path: Path) -> ValidatedLLMConfig:
        """Load configuration from a YAML file."""
        with open(path, "r") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValueError(f"Config file must contain a YAML dictionary, got {type(data)}")

        # Validate and convert to config object
        return self._parse_config_dict(data)

    def _parse_config_dict(self, data: Dict[str, Any]) -> ValidatedLLMConfig:
        """Parse a configuration dictionary into ValidatedLLMConfig."""
        config = ValidatedLLMConfig()

        # Direct field mappings
        direct_fields: Dict[str, Union[Type[Any], Tuple[Type[Any], ...]]] = {
            "llm_vendor": str,
            "llm_model": str,
            "llm_temperature": float,
            "llm_max_tokens": (int, type(None)),
            "max_retries": int,
            "timeout_seconds": int,
            "show_progress": bool,
            "code_language": str,
            "code_style_formatter": str,
            "require_code_examples": bool,
            "require_tests": bool,
            "doc_min_sections": int,
            "doc_min_words_per_section": int,
            "doc_check_links": bool,
            "doc_check_spelling": bool,
            "output_format": str,
            "verbose": bool,
        }

        for field_name, expected_type in direct_fields.items():
            if field_name in data:
                value = data[field_name]
                # Handle Union types
                if isinstance(expected_type, tuple):
                    if not isinstance(value, expected_type):
                        raise ValueError(f"Config field '{field_name}' must be one of {expected_type}, got {type(value)}")
                else:
                    if not isinstance(value, expected_type):
                        raise ValueError(f"Config field '{field_name}' must be {expected_type}, got {type(value)}")
                setattr(config, field_name, value)

        # Special handling for dictionaries
        if "validator_defaults" in data:
            if not isinstance(data["validator_defaults"], dict):
                raise ValueError("validator_defaults must be a dictionary")
            config.validator_defaults = data["validator_defaults"]

        if "task_defaults" in data:
            if not isinstance(data["task_defaults"], dict):
                raise ValueError("task_defaults must be a dictionary")
            config.task_defaults = data["task_defaults"]

        # Special handling for lists
        if "plugin_paths" in data:
            if not isinstance(data["plugin_paths"], list):
                raise ValueError("plugin_paths must be a list")
            config.plugin_paths = data["plugin_paths"]

        if "enabled_plugins" in data:
            if not isinstance(data["enabled_plugins"], list):
                raise ValueError("enabled_plugins must be a list")
            config.enabled_plugins = data["enabled_plugins"]

        return config

    def _load_env_config(self) -> Optional[ValidatedLLMConfig]:
        """Load configuration from environment variables."""
        env_config = ValidatedLLMConfig()
        found_any = False

        # Check for environment variable overrides
        env_mappings: Dict[str, tuple[str, Callable[[str], Any]]] = {
            "VALIDATED_LLM_VENDOR": ("llm_vendor", str),
            "VALIDATED_LLM_MODEL": ("llm_model", str),
            "VALIDATED_LLM_TEMPERATURE": ("llm_temperature", float),
            "VALIDATED_LLM_MAX_TOKENS": ("llm_max_tokens", int),
            "VALIDATED_LLM_MAX_RETRIES": ("max_retries", int),
            "VALIDATED_LLM_TIMEOUT": ("timeout_seconds", int),
            "VALIDATED_LLM_SHOW_PROGRESS": ("show_progress", lambda x: x.lower() in ("true", "1", "yes")),
            "VALIDATED_LLM_CODE_LANGUAGE": ("code_language", str),
            "VALIDATED_LLM_VERBOSE": ("verbose", lambda x: x.lower() in ("true", "1", "yes")),
        }

        for env_key, (field_name, converter) in env_mappings.items():
            if env_key in os.environ:
                try:
                    value = converter(os.environ[env_key])
                    setattr(env_config, field_name, value)
                    found_any = True
                except Exception as e:
                    raise ValueError(f"Invalid value for {env_key}: {e}")

        return env_config if found_any else None

    def get_current_config(self) -> ValidatedLLMConfig:
        """Get the current configuration, loading if necessary."""
        if self._current_config is None:
            self._current_config = self.load_config()
        return self._current_config

    def get_validator_config(self, validator_name: str) -> Dict[str, Any]:
        """Get configuration for a specific validator."""
        config = self.get_current_config()
        return config.validator_defaults.get(validator_name, {})

    def get_task_config(self, task_name: str) -> Dict[str, Any]:
        """Get configuration for a specific task."""
        config = self.get_current_config()
        return config.task_defaults.get(task_name, {})


# Global config loader instance
_config_loader = ConfigLoader()


def load_config(start_path: Optional[Union[str, Path]] = None) -> ValidatedLLMConfig:
    """Load validated-llm configuration."""
    return _config_loader.load_config(start_path)


def get_config() -> ValidatedLLMConfig:
    """Get current configuration."""
    return _config_loader.get_current_config()


def get_validator_config(validator_name: str) -> Dict[str, Any]:
    """Get configuration for a specific validator."""
    return _config_loader.get_validator_config(validator_name)


def get_task_config(task_name: str) -> Dict[str, Any]:
    """Get configuration for a specific task."""
    return _config_loader.get_task_config(task_name)


def create_sample_config() -> str:
    """Create a sample configuration file content."""
    return """# Validated-LLM Configuration File
# Place this file as .validated-llm.yml in your project root

# LLM Settings
llm_vendor: ollama  # Vendor: 'ollama', 'openai', 'anthropic', etc.
llm_model: gemma3:27b
llm_temperature: 0.7
# llm_max_tokens: 2000  # Optional token limit

# Validation Settings
max_retries: 3
timeout_seconds: 60
show_progress: true

# Code Generation Defaults
code_language: python
code_style_formatter: black
require_code_examples: true
require_tests: true

# Documentation Defaults
doc_min_sections: 3
doc_min_words_per_section: 50
doc_check_links: true
doc_check_spelling: false

# Output Settings
output_format: markdown
verbose: false

# Validator-specific defaults
validator_defaults:
  EmailValidator:
    allow_smtputf8: true
    check_deliverability: false

  JSONSchemaValidator:
    strict_mode: true
    validate_schema: true

  CodeValidator:
    language: python
    strict_mode: true

  DocumentationValidator:
    min_sections: 5
    require_code_examples: true

# Task-specific defaults
task_defaults:
  CodeGenerationTask:
    language: python
    include_type_hints: true
    include_docstrings: true

  DocumentationTask:
    doc_type: readme
    include_examples: true
    include_installation: true

# Plugin Settings (future feature)
# plugin_paths:
#   - ./my_validators
#   - ~/.validated-llm/plugins
#
# enabled_plugins:
#   - custom_validator
#   - domain_specific_tasks
"""
