"""
Plugin discovery mechanisms for finding and loading validator plugins.
"""

import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple

from .exceptions import PluginLoadError
from .registry import ValidationPlugin


class PluginDiscovery:
    """
    Discovers and loads validator plugins from various sources.
    """

    def __init__(self) -> None:
        self._search_paths: List[Path] = []
        self._namespace_packages: List[str] = []

    def add_search_path(self, path: Path) -> None:
        """
        Add a directory to search for plugins.

        Args:
            path: Directory path to search
        """
        if path.exists() and path.is_dir():
            self._search_paths.append(path)

    def add_namespace_package(self, namespace: str) -> None:
        """
        Add a namespace package to search for plugins.

        Args:
            namespace: Namespace package name (e.g., 'validated_llm_plugins')
        """
        self._namespace_packages.append(namespace)

    def discover_from_directory(self, directory: Path) -> Generator[ValidationPlugin, None, None]:
        """
        Discover plugins from a directory.

        Args:
            directory: Directory to search

        Yields:
            ValidationPlugin instances
        """
        if not directory.exists() or not directory.is_dir():
            return

        # Look for Python files
        for py_file in directory.glob("*.py"):
            if py_file.name.startswith("__"):
                continue

            try:
                plugin = self._load_plugin_from_file(py_file)
                if plugin:
                    yield plugin
            except Exception as e:
                # Log warning but continue
                print(f"Warning: Failed to load plugin from {py_file}: {e}")

        # Look for package directories
        for pkg_dir in directory.iterdir():
            if pkg_dir.is_dir() and (pkg_dir / "__init__.py").exists():
                try:
                    plugin = self._load_plugin_from_package(pkg_dir)
                    if plugin:
                        yield plugin
                except Exception as e:
                    print(f"Warning: Failed to load plugin from {pkg_dir}: {e}")

    def discover_from_namespace(self, namespace: str) -> Generator[ValidationPlugin, None, None]:
        """
        Discover plugins from a namespace package.

        Args:
            namespace: Namespace package to search

        Yields:
            ValidationPlugin instances
        """
        try:
            # Try to import the namespace package
            namespace_pkg = importlib.import_module(namespace)

            # If it has __path__, it's a namespace package
            if hasattr(namespace_pkg, "__path__"):
                for finder, name, ispkg in iter_namespace(namespace_pkg):
                    if ispkg:
                        try:
                            plugin = self._load_plugin_from_module(f"{namespace}.{name}")
                            if plugin:
                                yield plugin
                        except Exception as e:
                            print(f"Warning: Failed to load plugin {name}: {e}")
        except ImportError:
            # Namespace package doesn't exist, skip
            pass

    def discover_all(self) -> List[ValidationPlugin]:
        """
        Discover all plugins from configured sources.

        Returns:
            List of discovered plugins
        """
        plugins: List[ValidationPlugin] = []

        # Search directories
        for path in self._search_paths:
            plugins.extend(self.discover_from_directory(path))

        # Search namespace packages
        for namespace in self._namespace_packages:
            plugins.extend(self.discover_from_namespace(namespace))

        return plugins

    def _load_plugin_from_file(self, file_path: Path) -> Optional[ValidationPlugin]:
        """
        Load a plugin from a Python file.

        Args:
            file_path: Path to the Python file

        Returns:
            ValidationPlugin if found, None otherwise
        """
        module_name = file_path.stem
        spec = importlib.util.spec_from_file_location(module_name, file_path)

        if spec is None or spec.loader is None:
            return None

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        return self._extract_plugin_from_module(module, str(file_path))

    def _load_plugin_from_package(self, package_path: Path) -> Optional[ValidationPlugin]:
        """
        Load a plugin from a package directory.

        Args:
            package_path: Path to the package directory

        Returns:
            ValidationPlugin if found, None otherwise
        """
        module_name = package_path.name
        spec = importlib.util.spec_from_file_location(module_name, package_path / "__init__.py")

        if spec is None or spec.loader is None:
            return None

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        return self._extract_plugin_from_module(module, str(package_path))

    def _load_plugin_from_module(self, module_name: str) -> Optional[ValidationPlugin]:
        """
        Load a plugin from a module name.

        Args:
            module_name: Full module name

        Returns:
            ValidationPlugin if found, None otherwise
        """
        try:
            module = importlib.import_module(module_name)
            return self._extract_plugin_from_module(module, module_name)
        except ImportError as e:
            raise PluginLoadError(f"Cannot import module {module_name}: {e}")

    def _extract_plugin_from_module(self, module: Any, source: str) -> Optional[ValidationPlugin]:
        """
        Extract plugin metadata from a loaded module.

        Args:
            module: The loaded module
            source: Source identifier for the module

        Returns:
            ValidationPlugin if valid plugin found, None otherwise
        """
        # Look for plugin metadata
        plugin_info = getattr(module, "PLUGIN_INFO", None)
        if not plugin_info:
            return None

        # Validate plugin info
        required_fields = ["name", "version", "description", "author", "validator_class"]
        for field in required_fields:
            if field not in plugin_info:
                raise PluginLoadError(f"Plugin in {source} missing required field: {field}")

        # Create plugin
        return ValidationPlugin(
            name=plugin_info["name"],
            version=plugin_info["version"],
            description=plugin_info["description"],
            author=plugin_info["author"],
            validator_class=plugin_info["validator_class"],
            dependencies=plugin_info.get("dependencies", []),
            tags=plugin_info.get("tags", []),
            plugin_module=source,
        )


def iter_namespace(ns_pkg: Any) -> Generator[Tuple[Any, str, bool], None, None]:
    """
    Iterate over modules in a namespace package.

    Args:
        ns_pkg: Namespace package

    Yields:
        Tuples of (finder, name, ispkg)
    """
    # Use pkgutil if available
    try:
        import pkgutil

        yield from pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")
    except ImportError:
        # Fallback for environments without pkgutil
        return
