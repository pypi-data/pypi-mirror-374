"""
Configuration file validator for .validated-llm.yml files.
"""

from typing import Any, Dict, List, Optional, Set

import yaml

from ..base_validator import BaseValidator, ValidationResult


class ConfigValidator(BaseValidator):
    """
    Validates .validated-llm.yml configuration files.

    Ensures configuration files are properly formatted and contain valid settings.
    """

    # Valid top-level keys
    VALID_TOP_KEYS = {
        "llm_model",
        "llm_temperature",
        "llm_max_tokens",
        "max_retries",
        "timeout_seconds",
        "show_progress",
        "code_language",
        "code_style_formatter",
        "require_code_examples",
        "require_tests",
        "doc_min_sections",
        "doc_min_words_per_section",
        "doc_check_links",
        "doc_check_spelling",
        "output_format",
        "verbose",
        "validator_defaults",
        "task_defaults",
        "plugin_paths",
        "enabled_plugins",
    }

    # Valid code languages
    VALID_LANGUAGES = {"python", "javascript", "typescript", "go", "rust", "java"}

    # Valid formatters
    VALID_FORMATTERS = {"python": {"black", "autopep8", "yapf"}, "javascript": {"prettier", "standard"}, "typescript": {"prettier"}, "go": {"gofmt"}, "rust": {"rustfmt"}, "java": {"google-java-format"}}

    # Valid output formats
    VALID_OUTPUT_FORMATS = {"markdown", "json", "text", "html"}

    def __init__(self, strict_mode: bool = False):
        """
        Initialize config validator.

        Args:
            strict_mode: If True, unknown keys cause errors instead of warnings
        """
        self.strict_mode = strict_mode

    def validate(self, output: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate configuration file content.

        Args:
            output: YAML configuration content
            context: Optional context

        Returns:
            ValidationResult with validation details
        """
        if not output or not output.strip():
            return ValidationResult(is_valid=False, errors=["Configuration file is empty"], warnings=[], metadata={})

        errors = []
        warnings = []
        metadata = {}

        # Parse YAML
        try:
            config_data = yaml.safe_load(output)
        except yaml.YAMLError as e:
            return ValidationResult(is_valid=False, errors=[f"Invalid YAML syntax: {str(e)}"], warnings=[], metadata={})

        if not isinstance(config_data, dict):
            return ValidationResult(is_valid=False, errors=["Configuration must be a YAML dictionary/mapping"], warnings=[], metadata={})

        metadata["keys_found"] = list(config_data.keys())

        # Validate top-level keys
        unknown_keys = set(config_data.keys()) - self.VALID_TOP_KEYS
        if unknown_keys:
            message = f"Unknown configuration keys: {', '.join(sorted(unknown_keys))}"
            if self.strict_mode:
                errors.append(message)
            else:
                warnings.append(message)

        # Validate specific fields
        self._validate_llm_settings(config_data, errors, warnings)
        self._validate_validation_settings(config_data, errors, warnings)
        self._validate_code_settings(config_data, errors, warnings)
        self._validate_doc_settings(config_data, errors, warnings)
        self._validate_output_settings(config_data, errors, warnings)
        self._validate_defaults(config_data, errors, warnings, metadata)
        self._validate_plugin_settings(config_data, errors, warnings)

        is_valid = len(errors) == 0

        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings, metadata=metadata)

    def _validate_llm_settings(self, config: Dict[str, Any], errors: List[str], warnings: List[str]) -> None:
        """Validate LLM-related settings."""
        # Temperature validation
        if "llm_temperature" in config:
            temp = config["llm_temperature"]
            if not isinstance(temp, (int, float)):
                errors.append(f"llm_temperature must be a number, got {type(temp).__name__}")
            elif not 0 <= temp <= 2:
                warnings.append(f"llm_temperature {temp} is outside typical range [0, 2]")

        # Max tokens validation
        if "llm_max_tokens" in config:
            tokens = config["llm_max_tokens"]
            if tokens is not None and not isinstance(tokens, int):
                errors.append(f"llm_max_tokens must be an integer or null, got {type(tokens).__name__}")
            elif isinstance(tokens, int) and tokens <= 0:
                errors.append(f"llm_max_tokens must be positive, got {tokens}")

    def _validate_validation_settings(self, config: Dict[str, Any], errors: List[str], warnings: List[str]) -> None:
        """Validate validation-related settings."""
        # Max retries
        if "max_retries" in config:
            retries = config["max_retries"]
            if not isinstance(retries, int):
                errors.append(f"max_retries must be an integer, got {type(retries).__name__}")
            elif retries < 0:
                errors.append(f"max_retries must be non-negative, got {retries}")
            elif retries > 10:
                warnings.append(f"max_retries {retries} is unusually high")

        # Timeout
        if "timeout_seconds" in config:
            timeout = config["timeout_seconds"]
            if not isinstance(timeout, int):
                errors.append(f"timeout_seconds must be an integer, got {type(timeout).__name__}")
            elif timeout <= 0:
                errors.append(f"timeout_seconds must be positive, got {timeout}")

        # Boolean flags
        for bool_field in ["show_progress", "verbose"]:
            if bool_field in config and not isinstance(config[bool_field], bool):
                errors.append(f"{bool_field} must be a boolean, got {type(config[bool_field]).__name__}")

    def _validate_code_settings(self, config: Dict[str, Any], errors: List[str], warnings: List[str]) -> None:
        """Validate code generation settings."""
        # Language
        if "code_language" in config:
            lang = config["code_language"]
            if not isinstance(lang, str):
                errors.append(f"code_language must be a string, got {type(lang).__name__}")
            elif lang not in self.VALID_LANGUAGES:
                warnings.append(f"code_language '{lang}' is not a recognized language. " f"Valid options: {', '.join(sorted(self.VALID_LANGUAGES))}")

        # Formatter
        if "code_style_formatter" in config:
            formatter = config["code_style_formatter"]
            if not isinstance(formatter, str):
                errors.append(f"code_style_formatter must be a string, got {type(formatter).__name__}")
            else:
                # Check if formatter is valid for the language
                lang = config.get("code_language", "python")
                if lang in self.VALID_FORMATTERS and formatter not in self.VALID_FORMATTERS[lang]:
                    warnings.append(f"Formatter '{formatter}' may not be compatible with {lang}. " f"Common options: {', '.join(sorted(self.VALID_FORMATTERS.get(lang, [])))}")

        # Boolean flags
        for bool_field in ["require_code_examples", "require_tests"]:
            if bool_field in config and not isinstance(config[bool_field], bool):
                errors.append(f"{bool_field} must be a boolean, got {type(config[bool_field]).__name__}")

    def _validate_doc_settings(self, config: Dict[str, Any], errors: List[str], warnings: List[str]) -> None:
        """Validate documentation settings."""
        # Min sections
        if "doc_min_sections" in config:
            sections = config["doc_min_sections"]
            if not isinstance(sections, int):
                errors.append(f"doc_min_sections must be an integer, got {type(sections).__name__}")
            elif sections < 1:
                errors.append(f"doc_min_sections must be at least 1, got {sections}")

        # Min words per section
        if "doc_min_words_per_section" in config:
            words = config["doc_min_words_per_section"]
            if not isinstance(words, int):
                errors.append(f"doc_min_words_per_section must be an integer, got {type(words).__name__}")
            elif words < 0:
                errors.append(f"doc_min_words_per_section must be non-negative, got {words}")

        # Boolean flags
        for bool_field in ["doc_check_links", "doc_check_spelling"]:
            if bool_field in config and not isinstance(config[bool_field], bool):
                errors.append(f"{bool_field} must be a boolean, got {type(config[bool_field]).__name__}")

    def _validate_output_settings(self, config: Dict[str, Any], errors: List[str], warnings: List[str]) -> None:
        """Validate output settings."""
        if "output_format" in config:
            fmt = config["output_format"]
            if not isinstance(fmt, str):
                errors.append(f"output_format must be a string, got {type(fmt).__name__}")
            elif fmt not in self.VALID_OUTPUT_FORMATS:
                warnings.append(f"output_format '{fmt}' is not recognized. " f"Valid options: {', '.join(sorted(self.VALID_OUTPUT_FORMATS))}")

    def _validate_defaults(self, config: Dict[str, Any], errors: List[str], warnings: List[str], metadata: Dict[str, Any]) -> None:
        """Validate validator_defaults and task_defaults sections."""
        # Validator defaults
        if "validator_defaults" in config:
            val_defaults = config["validator_defaults"]
            if not isinstance(val_defaults, dict):
                errors.append("validator_defaults must be a dictionary")
            else:
                metadata["validator_defaults_count"] = len(val_defaults)
                for validator_name, settings in val_defaults.items():
                    if not isinstance(settings, dict):
                        errors.append(f"Settings for validator '{validator_name}' must be a dictionary")

        # Task defaults
        if "task_defaults" in config:
            task_defaults = config["task_defaults"]
            if not isinstance(task_defaults, dict):
                errors.append("task_defaults must be a dictionary")
            else:
                metadata["task_defaults_count"] = len(task_defaults)
                for task_name, settings in task_defaults.items():
                    if not isinstance(settings, dict):
                        errors.append(f"Settings for task '{task_name}' must be a dictionary")

    def _validate_plugin_settings(self, config: Dict[str, Any], errors: List[str], warnings: List[str]) -> None:
        """Validate plugin settings."""
        # Plugin paths
        if "plugin_paths" in config:
            paths = config["plugin_paths"]
            if not isinstance(paths, list):
                errors.append("plugin_paths must be a list")
            else:
                for i, path in enumerate(paths):
                    if not isinstance(path, str):
                        errors.append(f"plugin_paths[{i}] must be a string, got {type(path).__name__}")

        # Enabled plugins
        if "enabled_plugins" in config:
            plugins = config["enabled_plugins"]
            if not isinstance(plugins, list):
                errors.append("enabled_plugins must be a list")
            else:
                for i, plugin in enumerate(plugins):
                    if not isinstance(plugin, str):
                        errors.append(f"enabled_plugins[{i}] must be a string, got {type(plugin).__name__}")

    def get_description(self) -> str:
        """Get description of the config validator."""
        return f"Configuration validator for .validated-llm.yml files ({'strict' if self.strict_mode else 'lenient'} mode)"
