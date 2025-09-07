"""
Plugin manager for coordinating plugin discovery, loading, and management.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from ..base_validator import BaseValidator
from .discovery import PluginDiscovery
from .exceptions import PluginError
from .registry import PluginRegistry, ValidationPlugin, get_registry


class PluginManager:
    """
    Main interface for managing validator plugins.

    The PluginManager coordinates plugin discovery, loading, and provides
    a unified interface for working with plugins.
    """

    def __init__(self, registry: Optional[PluginRegistry] = None) -> None:
        self.registry = registry or get_registry()
        self.discovery = PluginDiscovery()
        self._initialized = False

    def initialize(self) -> None:
        """
        Initialize the plugin system by setting up default search paths
        and discovering plugins.
        """
        if self._initialized:
            return

        # Add default search paths
        self._setup_default_search_paths()

        # Discover and load plugins
        self.discover_plugins()

        self._initialized = True

    def _setup_default_search_paths(self) -> None:
        """Setup default search paths for plugins."""
        # User plugins directory
        user_home = Path.home()
        user_plugins = user_home / ".validated-llm" / "plugins"
        if user_plugins.exists():
            self.discovery.add_search_path(user_plugins)

        # Project-local plugins directory
        local_plugins = Path.cwd() / "validated_llm_plugins"
        if local_plugins.exists():
            self.discovery.add_search_path(local_plugins)

        # Environment variable override
        plugin_path = os.environ.get("VALIDATED_LLM_PLUGIN_PATH")
        if plugin_path:
            for path_str in plugin_path.split(os.pathsep):
                path = Path(path_str)
                if path.exists():
                    self.discovery.add_search_path(path)

        # Add namespace packages
        self.discovery.add_namespace_package("validated_llm_plugins")

    def discover_plugins(self) -> List[ValidationPlugin]:
        """
        Discover and register all available plugins.

        Returns:
            List of discovered plugins
        """
        plugins = []

        for plugin in self.discovery.discover_all():
            try:
                self.registry.register_plugin(plugin)
                plugins.append(plugin)
            except Exception as e:
                print(f"Warning: Failed to register plugin {plugin.name}: {e}")

        return plugins

    def register_plugin(
        self, validator_class: Type[BaseValidator], name: str, version: str = "1.0.0", description: str = "", author: str = "Unknown", dependencies: Optional[List[str]] = None, tags: Optional[List[str]] = None
    ) -> ValidationPlugin:
        """
        Register a validator class as a plugin.

        Args:
            validator_class: The validator class to register
            name: Plugin name
            version: Plugin version
            description: Plugin description
            author: Plugin author
            dependencies: List of required dependencies
            tags: List of tags for categorization

        Returns:
            The registered ValidationPlugin
        """
        return self.registry.register_validator_class(validator_class=validator_class, name=name, version=version, description=description, author=author, dependencies=dependencies, tags=tags)

    def get_plugin(self, name: str) -> Optional[ValidationPlugin]:
        """
        Get a plugin by name.

        Args:
            name: Name of the plugin

        Returns:
            The plugin if found, None otherwise
        """
        return self.registry.get_plugin(name)

    def list_plugins(self, tag: Optional[str] = None) -> List[ValidationPlugin]:
        """
        List all registered plugins.

        Args:
            tag: Optional tag to filter by

        Returns:
            List of plugins
        """
        return self.registry.list_plugins(tag=tag)

    def create_validator(self, name: str, **kwargs: Any) -> BaseValidator:
        """
        Create a validator instance from a plugin.

        Args:
            name: Name of the plugin
            **kwargs: Arguments to pass to the validator constructor

        Returns:
            Validator instance

        Raises:
            PluginError: If plugin not found or cannot be instantiated
        """
        if not self._initialized:
            self.initialize()

        return self.registry.create_validator(name, **kwargs)

    def get_plugin_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a plugin.

        Args:
            name: Name of the plugin

        Returns:
            Plugin information dictionary or None if not found
        """
        return self.registry.get_plugin_info(name)

    def add_search_path(self, path: Path) -> None:
        """
        Add a directory to search for plugins.

        Args:
            path: Directory path to search
        """
        self.discovery.add_search_path(path)

    def reload_plugins(self) -> List[ValidationPlugin]:
        """
        Reload all plugins from search paths.

        Returns:
            List of discovered plugins
        """
        # Clear existing plugins
        self.registry.clear()

        # Rediscover
        return self.discover_plugins()


# Global plugin manager instance
_manager = PluginManager()


def get_manager() -> PluginManager:
    """Get the global plugin manager instance."""
    return _manager
