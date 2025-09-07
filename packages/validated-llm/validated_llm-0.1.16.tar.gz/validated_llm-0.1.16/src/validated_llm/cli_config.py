#!/usr/bin/env python3
"""
CLI utility for managing validated-llm configuration.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .config import create_sample_config
from .validators.config import ConfigValidator


def init_config(path: Optional[Path] = None) -> None:
    """Initialize a new .validated-llm.yml configuration file."""
    if path is None:
        path = Path.cwd() / ".validated-llm.yml"

    if path.exists():
        response = input(f"Configuration file already exists at {path}. Overwrite? [y/N] ")
        if response.lower() != "y":
            print("Aborted.")
            return

    # Create sample config
    config_content = create_sample_config()

    # Write to file
    with open(path, "w") as f:
        f.write(config_content)

    print(f"Configuration file created at {path}")
    print("\nYou can now customize the configuration to your needs.")
    print("Run 'validated-llm config validate' to check your configuration.")


def validate_config(path: Optional[Path] = None) -> None:
    """Validate a .validated-llm.yml configuration file."""
    if path is None:
        # Search for config in current directory tree
        current = Path.cwd()
        while current != current.parent:
            config_path = current / ".validated-llm.yml"
            if config_path.exists():
                path = config_path
                break
            current = current.parent

        if path is None:
            print("No .validated-llm.yml file found in current directory or parent directories.")
            print("Run 'validated-llm config init' to create one.")
            sys.exit(1)

    print(f"Validating configuration at {path}...")

    # Read config file
    try:
        with open(path, "r") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading config file: {e}")
        sys.exit(1)

    # Validate
    validator = ConfigValidator()
    result = validator.validate(content)

    if result.is_valid:
        print("✓ Configuration is valid!")
        if result.warnings:
            print("\nWarnings:")
            for warning in result.warnings:
                print(f"  - {warning}")
    else:
        print("✗ Configuration has errors:")
        for error in result.errors:
            print(f"  - {error}")
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Manage validated-llm configuration files", prog="validated-llm-config")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Init command
    init_parser = subparsers.add_parser("init", help="Create a new configuration file")
    init_parser.add_argument("--path", "-p", type=Path, help="Path for the configuration file (default: ./.validated-llm.yml)")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate a configuration file")
    validate_parser.add_argument("--path", "-p", type=Path, help="Path to the configuration file (searches upward if not specified)")

    args = parser.parse_args()

    if args.command == "init":
        init_config(args.path)
    elif args.command == "validate":
        validate_config(args.path)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
