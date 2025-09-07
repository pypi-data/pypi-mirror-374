#!/usr/bin/env python3
"""
CLI commands for plugin management.
"""

import builtins
import json
import sys
from pathlib import Path
from typing import List, Optional

import click

from .exceptions import PluginError
from .manager import get_manager


@click.group(name="plugin")
def plugin_cli() -> None:
    """Manage validator plugins."""
    pass


@plugin_cli.command()
@click.option("--tag", help="Filter plugins by tag")
@click.option("--format", "output_format", type=click.Choice(["table", "json", "simple"]), default="table", help="Output format")
def list(tag: Optional[str], output_format: str) -> None:
    """List all available plugins."""
    manager = get_manager()
    manager.initialize()

    plugins = manager.list_plugins(tag=tag)

    if not plugins:
        if tag:
            click.echo(f"No plugins found with tag '{tag}'")
        else:
            click.echo("No plugins found")
        return

    if output_format == "json":
        plugin_data = []
        for plugin in plugins:
            plugin_data.append({"name": plugin.name, "version": plugin.version, "description": plugin.description, "author": plugin.author, "tags": plugin.tags, "dependencies": plugin.dependencies})
        click.echo(json.dumps(plugin_data, indent=2))

    elif output_format == "simple":
        for plugin in plugins:
            click.echo(f"{plugin.name} v{plugin.version} - {plugin.description}")

    else:  # table format
        click.echo("Available Plugins:")
        click.echo("=" * 80)
        for plugin in plugins:
            click.echo(f"Name:        {plugin.name}")
            click.echo(f"Version:     {plugin.version}")
            click.echo(f"Description: {plugin.description}")
            click.echo(f"Author:      {plugin.author}")
            if plugin.tags:
                click.echo(f"Tags:        {', '.join(plugin.tags)}")
            if plugin.dependencies:
                click.echo(f"Dependencies: {', '.join(plugin.dependencies)}")
            click.echo("-" * 40)


@plugin_cli.command()
@click.argument("name")
def info(name: str) -> None:
    """Show detailed information about a plugin."""
    manager = get_manager()
    manager.initialize()

    plugin_info = manager.get_plugin_info(name)

    if not plugin_info:
        click.echo(f"Plugin '{name}' not found", err=True)
        sys.exit(1)

    click.echo(f"Plugin Information: {name}")
    click.echo("=" * 50)

    for key, value in plugin_info.items():
        if isinstance(value, builtins.list):
            if value:
                click.echo(f"{key.title()}: {', '.join(value)}")
            else:
                click.echo(f"{key.title()}: None")
        else:
            click.echo(f"{key.title()}: {value}")


@plugin_cli.command()
@click.argument("name")
@click.option("--args", help="JSON string of arguments to pass to validator")
def test(name: str, args: Optional[str]) -> None:
    """Test a plugin by creating a validator instance."""
    manager = get_manager()
    manager.initialize()

    try:
        # Parse arguments if provided
        kwargs = {}
        if args:
            try:
                kwargs = json.loads(args)
            except json.JSONDecodeError as e:
                click.echo(f"Invalid JSON in args: {e}", err=True)
                sys.exit(1)

        # Create validator instance
        validator = manager.create_validator(name, **kwargs)

        click.echo(f"✓ Successfully created validator '{name}'")
        click.echo(f"Class: {validator.__class__.__name__}")
        click.echo(f"Description: {validator.description}")

        # Test with empty string
        try:
            result = validator.validate("")
            click.echo(f"✓ Validator callable (empty string test)")
            click.echo(f"  Result: {'PASS' if result.is_valid else 'FAIL'}")
        except Exception as e:
            click.echo(f"⚠ Validator test failed: {e}")

    except PluginError as e:
        click.echo(f"Plugin error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@plugin_cli.command()
def reload() -> None:
    """Reload all plugins from search paths."""
    manager = get_manager()

    click.echo("Reloading plugins...")
    plugins = manager.reload_plugins()

    click.echo(f"✓ Reloaded {len(plugins)} plugin(s)")
    for plugin in plugins:
        click.echo(f"  - {plugin.name} v{plugin.version}")


@plugin_cli.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
def discover(path: Path) -> None:
    """Discover plugins from a specific directory."""
    manager = get_manager()

    click.echo(f"Discovering plugins in {path}...")

    # Add path and discover
    manager.add_search_path(path)
    plugins = []

    for plugin in manager.discovery.discover_from_directory(path):
        try:
            manager.registry.register_plugin(plugin)
            plugins.append(plugin)
            click.echo(f"✓ Found: {plugin.name} v{plugin.version}")
        except Exception as e:
            click.echo(f"✗ Failed to load plugin: {e}")

    click.echo(f"\\nDiscovered {len(plugins)} plugin(s)")


@plugin_cli.command()
def paths() -> None:
    """Show plugin search paths."""
    manager = get_manager()
    manager.initialize()

    click.echo("Plugin Search Paths:")
    click.echo("=" * 30)

    for path in manager.discovery._search_paths:
        exists = "✓" if path.exists() else "✗"
        click.echo(f"{exists} {path}")

    click.echo("\\nNamespace Packages:")
    click.echo("=" * 20)

    for namespace in manager.discovery._namespace_packages:
        click.echo(f"  {namespace}")


@plugin_cli.command()
@click.argument("name")
def validate_plugin(name: str) -> None:
    """Validate that a plugin meets requirements."""
    manager = get_manager()
    manager.initialize()

    plugin = manager.get_plugin(name)
    if not plugin:
        click.echo(f"Plugin '{name}' not found", err=True)
        sys.exit(1)

    try:
        # Re-validate the plugin
        manager.registry._validate_plugin(plugin)
        click.echo(f"✓ Plugin '{name}' is valid")

        # Test instantiation
        validator = manager.create_validator(name)
        click.echo(f"✓ Plugin can be instantiated")

        # Test validation method
        result = validator.validate("test")
        click.echo(f"✓ Validation method works")

    except Exception as e:
        click.echo(f"✗ Plugin validation failed: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    plugin_cli()
