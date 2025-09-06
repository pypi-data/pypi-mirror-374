"""
Main entry point for tools package.

This allows running tools with: python -m tools
"""

from .prompt_to_task.cli_click import main

if __name__ == "__main__":
    main()
