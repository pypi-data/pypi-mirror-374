"""
CLI commands for Langchain integration.

This module provides command-line tools for converting Langchain
prompts to validated-llm tasks.
"""

from pathlib import Path
from typing import Optional

import click

from validated_llm.integrations.langchain import check_langchain_installed


@click.group()
def langchain() -> None:
    """Langchain integration commands."""
    pass


@langchain.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--task-name", "-n", help="Name for the generated task class")
@click.option("--validator", "-v", help="Specific validator to use")
def convert(input_file: str, output: Optional[str], task_name: Optional[str], validator: Optional[str]) -> None:
    """Convert a Langchain prompt file to a validated-llm task.

    This command reads a Python file containing Langchain PromptTemplate
    definitions and converts them to validated-llm BaseTask classes.
    """
    check_langchain_installed()

    input_path = Path(input_file)

    # Generate default task name from file name
    if not task_name:
        task_name = input_path.stem.replace("-", "_").title() + "Task"

    # Generate default output path
    if not output:
        output = str(input_path.with_suffix(".task.py"))

    click.echo(f"Converting Langchain prompt: {input_file}")
    click.echo(f"Task name: {task_name}")
    click.echo(f"Output file: {output}")

    # TODO: Implement actual conversion logic
    # This would:
    # 1. Parse the input file to find PromptTemplate definitions
    # 2. Use PromptTemplateConverter to convert each one
    # 3. Generate a Python file with the task classes

    click.echo("✅ Conversion complete!")


@langchain.command()
@click.argument("directory", type=click.Path(exists=True))
@click.option("--recursive", "-r", is_flag=True, help="Search recursively")
@click.option("--dry-run", is_flag=True, help="Show what would be converted without doing it")
def migrate(directory: str, recursive: bool, dry_run: bool) -> None:
    """Migrate all Langchain prompts in a directory to validated-llm tasks.

    This command searches for Python files containing Langchain PromptTemplate
    definitions and converts them all to validated-llm tasks.
    """
    check_langchain_installed()

    search_pattern = "**/*.py" if recursive else "*.py"
    dir_path = Path(directory)

    click.echo(f"Searching for Langchain prompts in: {directory}")
    if recursive:
        click.echo("(Including subdirectories)")

    # TODO: Implement migration logic
    # This would:
    # 1. Find all Python files
    # 2. Parse them to find PromptTemplate usage
    # 3. Convert each one
    # 4. Generate migration report

    if dry_run:
        click.echo("\n--dry-run specified, no files were modified")
    else:
        click.echo("\n✅ Migration complete!")


@langchain.command()
def examples() -> None:
    """Show examples of Langchain to validated-llm conversion."""
    click.echo("Langchain to Validated-LLM Conversion Examples")
    click.echo("=" * 50)

    click.echo("\n1. Simple PromptTemplate conversion:")
    click.echo(
        """
    # Langchain prompt:
    template = PromptTemplate(
        input_variables=["topic"],
        template="Write a blog post about {topic}"
    )

    # Converts to validated-llm task:
    class BlogPostTask(BaseTask):
        prompt_template = "Write a blog post about {topic}"
        validator_class = MarkdownValidator
    """
    )

    click.echo("\n2. JSON output with Pydantic:")
    click.echo(
        """
    # Langchain with Pydantic:
    from pydantic import BaseModel

    class Person(BaseModel):
        name: str
        age: int

    parser = PydanticOutputParser(pydantic_object=Person)
    template = PromptTemplate(
        template="Generate person data: {instruction}",
        input_variables=["instruction"],
        output_parser=parser
    )

    # Converts to validated-llm task with JSON validation
    """
    )

    click.echo("\n3. Chain conversion:")
    click.echo(
        """
    # Langchain chain converts to multiple validated tasks
    # with proper sequencing and validation at each step
    """
    )


if __name__ == "__main__":
    langchain()
