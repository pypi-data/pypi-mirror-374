"""
Template management commands for the prompt-to-task tool.

This module provides CLI commands for managing the template library.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import click

from .template_library import PromptTemplate, TemplateLibrary


@click.group()
def template() -> None:
    """Manage prompt templates."""
    pass


@template.command()
@click.option("--category", "-c", help="Filter by category")
@click.option("--tag", "-t", multiple=True, help="Filter by tags")
@click.option("--popular", "-p", is_flag=True, help="Show most popular templates")
def list(category: Optional[str], tag: Tuple[str, ...], popular: bool) -> None:
    """List available templates."""
    library = TemplateLibrary()

    if popular:
        templates = library.get_popular_templates(10)
        click.echo("🌟 POPULAR TEMPLATES")
    else:
        templates = library.list_templates(category=category, tags=list(tag) if tag else None)
        click.echo("📚 AVAILABLE TEMPLATES")

    click.echo("=" * 60)

    if not templates:
        click.echo("No templates found matching criteria.")
        return

    # Group by category
    by_category: Dict[str, List[PromptTemplate]] = {}
    for template in templates:
        by_category.setdefault(template.category, []).append(template)

    for cat, cat_templates in sorted(by_category.items()):
        click.echo(f"\n📁 {cat.upper()}")
        click.echo("-" * 40)

        for template in cat_templates:
            click.echo(f"\n  📝 {template.name}")
            click.echo(f"     {template.description}")
            if template.tags:
                click.echo(f"     🏷️  {', '.join(template.tags)}")
            if popular:
                click.echo(f"     📊 Used {template.usage_count} times")


@template.command()
@click.argument("name")
def show(name: str) -> None:
    """Show details of a specific template."""
    library = TemplateLibrary()
    template = library.get_template(name)

    if not template:
        click.echo(f"❌ Template '{name}' not found", err=True)
        return

    click.echo(f"📝 TEMPLATE: {template.name}")
    click.echo("=" * 60)
    click.echo(f"📁 Category: {template.category}")
    click.echo(f"📖 Description: {template.description}")
    click.echo(f"🏷️  Tags: {', '.join(template.tags)}")
    click.echo(f"⚙️  Validator: {template.validator_type}")
    click.echo(f"📊 Usage count: {template.usage_count}")
    click.echo(f"📅 Created: {template.created_at}")

    click.echo(f"\n📄 PROMPT TEMPLATE:")
    click.echo("-" * 40)
    click.echo(template.prompt_template)

    if template.example_output:
        click.echo(f"\n📋 EXAMPLE OUTPUT:")
        click.echo("-" * 40)
        click.echo(template.example_output)

    if template.json_schema:
        click.echo(f"\n🔗 JSON SCHEMA:")
        click.echo("-" * 40)
        click.echo(json.dumps(template.json_schema, indent=2))

    if template.validator_config:
        click.echo(f"\n⚙️  VALIDATOR CONFIG:")
        click.echo("-" * 40)
        click.echo(json.dumps(template.validator_config, indent=2))


@template.command()
@click.argument("name")
@click.argument("output_path", type=click.Path())
def export(name: str, output_path: str) -> None:
    """Export a template to a file."""
    library = TemplateLibrary()

    try:
        library.export_template(name, Path(output_path))
        click.echo(f"✅ Template '{name}' exported to: {output_path}")
    except Exception as e:
        click.echo(f"❌ Error exporting template: {e}", err=True)


@template.command()
@click.argument("input_path", type=click.Path(exists=True))
def import_(input_path: str) -> None:
    """Import a template from a file."""
    library = TemplateLibrary()

    try:
        template = library.import_template(Path(input_path))
        click.echo(f"✅ Template '{template.name}' imported successfully")
    except Exception as e:
        click.echo(f"❌ Error importing template: {e}", err=True)


@template.command()
@click.argument("prompt_file", type=click.Path(exists=True))
@click.option("--top", "-n", default=5, help="Number of matches to show")
def match(prompt_file: str, top: int) -> None:
    """Find templates matching a prompt file."""
    library = TemplateLibrary()

    # Read prompt
    with open(prompt_file, "r") as f:
        prompt_text = f.read()

    # Find matches
    matches = library.find_similar_templates(prompt_text, top_k=top)

    if not matches:
        click.echo("No matching templates found.")
        return

    click.echo(f"🔍 TOP {len(matches)} MATCHING TEMPLATES")
    click.echo("=" * 60)

    for i, (template, score) in enumerate(matches, 1):
        click.echo(f"\n{i}. {template.name} (similarity: {score:.1%})")
        click.echo(f"   📁 Category: {template.category}")
        click.echo(f"   📖 {template.description}")
        if template.tags:
            click.echo(f"   🏷️  {', '.join(template.tags)}")


@template.command()
def categories() -> None:
    """List all template categories."""
    library = TemplateLibrary()
    categories = library.get_categories()

    click.echo("📁 TEMPLATE CATEGORIES")
    click.echo("=" * 30)

    for category in categories:
        count = len(library.list_templates(category=category))
        click.echo(f"  • {category} ({count} templates)")


@template.command()
def tags() -> None:
    """List all template tags."""
    library = TemplateLibrary()
    all_tags = library.get_all_tags()

    click.echo("🏷️  TEMPLATE TAGS")
    click.echo("=" * 30)

    # Group tags by first letter
    by_letter: Dict[str, List[str]] = {}
    for tag in all_tags:
        first = tag[0].upper()
        by_letter.setdefault(first, []).append(tag)

    for letter, letter_tags in sorted(by_letter.items()):
        click.echo(f"\n{letter}: {', '.join(letter_tags)}")


if __name__ == "__main__":
    template()
