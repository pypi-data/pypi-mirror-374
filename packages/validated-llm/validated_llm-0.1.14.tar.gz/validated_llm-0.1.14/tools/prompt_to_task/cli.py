"""
Main CLI entry point for prompt-to-task tool.

This combines the main conversion command with template management.
"""

from typing import Optional

import click

from .cli_batch import batch as batch_command
from .cli_click import main as convert_command
from .cli_template import template as template_group


@click.group()
def cli() -> None:
    """Convert prompts to validated-llm tasks with template support."""
    pass


# Add the main conversion command
cli.add_command(convert_command, name="convert")

# Add template management commands
cli.add_command(template_group, name="template")

# Add batch conversion command
cli.add_command(batch_command, name="batch")


# Add a default command that runs convert
@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file for generated task code")
@click.option("--interactive", "-i", is_flag=True, help="Run in interactive mode")
@click.pass_context
def default(ctx: click.Context, input_file: str, output: Optional[str], interactive: bool) -> None:
    """Default command - converts a prompt file to a task."""
    # Forward to the convert command
    ctx.invoke(convert_command, input_file=input_file, output=output, interactive=interactive)


if __name__ == "__main__":
    cli()
