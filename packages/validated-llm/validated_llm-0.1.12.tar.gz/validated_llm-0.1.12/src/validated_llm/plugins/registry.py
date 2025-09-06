"""
Plugin registry for managing validator plugins.
"""

import importlib
import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union

from ..base_validator import BaseValidator
from .exceptions import PluginError, PluginRegistrationError, PluginValidationError


@dataclass
class ValidationPlugin:
    """
    Metadata for a validation plugin.
    """

    name: str
    version: str
    description: str
    author: str
    validator_class: Type[BaseValidator]
    dependencies: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    plugin_module: Optional[str] = None

    def __post_init__(self) -> None:
        if self.dependencies is None:
            self.dependencies = []
        if self.tags is None:
            self.tags = []


class PluginRegistry:
    """
    Central registry for managing validator plugins.

    The registry maintains a catalog of available plugins, handles
    registration, and provides lookup functionality.
    """

    def __init__(self) -> None:
        self._plugins: Dict[str, ValidationPlugin] = {}
        self._loaded_modules: Dict[str, Any] = {}

    def register_plugin(self, plugin: ValidationPlugin) -> None:
        """
        Register a plugin with the registry.

        Args:
            plugin: The plugin metadata to register

        Raises:
            PluginRegistrationError: If plugin cannot be registered
        """
        # Validate plugin
        self._validate_plugin(plugin)

        # Check for naming conflicts
        if plugin.name in self._plugins:
            existing = self._plugins[plugin.name]
            raise PluginRegistrationError(f"Plugin '{plugin.name}' already registered by {existing.author}")

        # Register the plugin
        self._plugins[plugin.name] = plugin

    def register_validator_class(
        self, validator_class: Type[BaseValidator], name: str, version: str = "1.0.0", description: str = "", author: str = "Unknown", dependencies: Optional[List[str]] = None, tags: Optional[List[str]] = None
    ) -> ValidationPlugin:
        """
        Register a validator class directly as a plugin.

        Args:
            validator_class: The validator class to register
            name: Plugin name
            version: Plugin version
            description: Plugin description
            author: Plugin author
            dependencies: List of required dependencies
            tags: List of tags for categorization

        Returns:
            The created ValidationPlugin
        """
        plugin = ValidationPlugin(name=name, version=version, description=description, author=author, validator_class=validator_class, dependencies=dependencies, tags=tags)

        self.register_plugin(plugin)
        return plugin

    def unregister_plugin(self, name: str) -> bool:
        """
        Unregister a plugin by name.

        Args:
            name: Name of the plugin to unregister

        Returns:
            True if plugin was unregistered, False if not found
        """
        if name in self._plugins:
            del self._plugins[name]
            return True
        return False

    def get_plugin(self, name: str) -> Optional[ValidationPlugin]:
        """
        Get a plugin by name.

        Args:
            name: Name of the plugin

        Returns:
            The plugin if found, None otherwise
        """
        return self._plugins.get(name)

    def list_plugins(self, tag: Optional[str] = None) -> List[ValidationPlugin]:
        """
        List all registered plugins, optionally filtered by tag.

        Args:
            tag: Optional tag to filter by

        Returns:
            List of plugins
        """
        plugins = list(self._plugins.values())

        if tag:
            plugins = [p for p in plugins if tag in (p.tags or [])]

        return plugins

    def create_validator(self, name: str, **kwargs: Any) -> BaseValidator:
        """
        Create a validator instance from a registered plugin.

        Args:
            name: Name of the plugin
            **kwargs: Arguments to pass to the validator constructor

        Returns:
            Validator instance

        Raises:
            PluginError: If plugin not found or cannot be instantiated
        """
        plugin = self.get_plugin(name)
        if not plugin:
            raise PluginError(f"Plugin '{name}' not found")

        try:
            return plugin.validator_class(**kwargs)
        except Exception as e:
            raise PluginError(f"Failed to create validator '{name}': {e}")

    def _validate_plugin(self, plugin: ValidationPlugin) -> None:
        """
        Validate that a plugin meets requirements.

        Args:
            plugin: Plugin to validate

        Raises:
            PluginValidationError: If plugin is invalid
        """
        # Check required fields
        if not plugin.name:
            raise PluginValidationError("Plugin name is required")

        if not plugin.version:
            raise PluginValidationError("Plugin version is required")

        if not plugin.validator_class:
            raise PluginValidationError("Plugin must have a validator class")

        # Validate validator class
        if not inspect.isclass(plugin.validator_class):
            raise PluginValidationError("validator_class must be a class")

        if not issubclass(plugin.validator_class, BaseValidator):
            raise PluginValidationError("validator_class must inherit from BaseValidator")

        # Check that the validator can be instantiated
        try:
            # Try to get the signature to validate it's callable
            sig = inspect.signature(plugin.validator_class.__init__)
            # Check if it has only self and optional parameters
            params = list(sig.parameters.values())[1:]  # Skip 'self'
            for param in params:
                if param.default is param.empty and param.kind not in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                    # Has required parameters - that's fine, we'll let users handle it
                    break
        except Exception as e:
            raise PluginValidationError(f"Invalid validator class: {e}")

    def get_plugin_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a plugin.

        Args:
            name: Name of the plugin

        Returns:
            Plugin information dictionary or None if not found
        """
        plugin = self.get_plugin(name)
        if not plugin:
            return None

        return {
            "name": plugin.name,
            "version": plugin.version,
            "description": plugin.description,
            "author": plugin.author,
            "dependencies": plugin.dependencies,
            "tags": plugin.tags,
            "validator_class": plugin.validator_class.__name__,
            "module": plugin.plugin_module,
        }

    def clear(self) -> None:
        """Clear all registered plugins."""
        self._plugins.clear()
        self._loaded_modules.clear()


# Global plugin registry instance
_registry = PluginRegistry()


def get_registry() -> PluginRegistry:
    """Get the global plugin registry instance."""
    return _registry
