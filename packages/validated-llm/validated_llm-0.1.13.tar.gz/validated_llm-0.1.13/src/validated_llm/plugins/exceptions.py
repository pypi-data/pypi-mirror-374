"""
Plugin system exceptions.
"""


class PluginError(Exception):
    """Base exception for all plugin-related errors."""

    pass


class PluginLoadError(PluginError):
    """Raised when a plugin cannot be loaded."""

    pass


class PluginValidationError(PluginError):
    """Raised when a plugin fails validation requirements."""

    pass


class PluginRegistrationError(PluginError):
    """Raised when a plugin cannot be registered."""

    pass


class PluginDependencyError(PluginError):
    """Raised when plugin dependencies cannot be satisfied."""

    pass
