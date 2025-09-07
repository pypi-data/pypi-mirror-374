#!/usr/bin/env python3
"""
Enhanced CLI for Template Library with Rich Interface

Interactive command-line interface for browsing, searching, and using
templates from the template library with a rich, colorful UI.
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
from code_generator import CodeGenerator
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.table import Table
from rich.tree import Tree
from template_library import PromptTemplate, TemplateLibrary

console = Console()


@click.group()
def cli() -> None:
    """Template Library CLI - Enhanced interface for browsing and using prompt templates."""
    pass


@cli.command()
@click.option("--category", "-c", help="Filter by category")
@click.option("--tag", "-t", multiple=True, help="Filter by tags")
@click.option("--search", "-s", help="Search in names and descriptions")
@click.option("--format", "-f", type=click.Choice(["table", "grid", "list"]), default="table", help="Output format")
def list(category: Optional[str], tag: List[str], search: Optional[str], format: str) -> None:
    """List available templates with filtering options."""
    library = TemplateLibrary()
    templates = library.list_templates(category=category, tags=list(tag) if tag else None)

    # Apply search filter if provided
    if search:
        search_lower = search.lower()
        templates = [t for t in templates if search_lower in t.name.lower() or search_lower in t.description.lower()]

    if not templates:
        console.print("[yellow]No templates found matching your criteria.[/yellow]")
        return

    if format == "table":
        # Create table
        table = Table(title=f"Available Templates ({len(templates)} found)", box=box.ROUNDED)
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Category", style="green")
        table.add_column("Description", style="white")
        table.add_column("Tags", style="yellow")
        table.add_column("Uses", style="magenta", justify="right")

        for template in templates:
            table.add_row(
                template.name,
                template.category,
                template.description[:50] + "..." if len(template.description) > 50 else template.description,
                ", ".join(template.tags[:3]) + ("..." if len(template.tags) > 3 else ""),
                str(template.usage_count),
            )

        console.print(table)

    elif format == "grid":
        # Grid layout
        for i in range(0, len(templates), 2):
            row = []
            for j in range(2):
                if i + j < len(templates):
                    t = templates[i + j]
                    panel_content = f"[green]{t.category}[/green]\n{t.description[:60]}...\n[yellow]Tags:[/yellow] {', '.join(t.tags[:3])}"
                    row.append(Panel(panel_content, title=f"[cyan]{t.name}[/cyan]", width=40))
            if row:
                console.print(*row)

    else:  # list format
        for template in templates:
            console.print(f"\n[cyan]• {template.name}[/cyan] [{template.category}]")
            console.print(f"  {template.description}")
            console.print(f"  [yellow]Tags:[/yellow] {', '.join(template.tags)}")


@cli.command()
@click.argument("name")
def show(name: str) -> None:
    """Show detailed information about a template."""
    library = TemplateLibrary()
    template = library.get_template(name)

    if not template:
        console.print(f"[red]Template '{name}' not found![/red]")
        # Suggest similar templates
        similar = library.find_similar_templates(name, top_k=3)
        if similar:
            console.print("\n[yellow]Did you mean one of these?[/yellow]")
            for t, _ in similar:
                console.print(f"  • {t.name}")
        return

    # Header
    console.print(Panel.fit(f"[bold cyan]{template.name}[/bold cyan]\n[dim]{template.description}[/dim]", title="Template Details", box=box.DOUBLE))

    # Basic info
    info_table = Table(show_header=False, box=None)
    info_table.add_column("Property", style="bold")
    info_table.add_column("Value")

    info_table.add_row("Category", f"[green]{template.category}[/green]")
    info_table.add_row("Tags", f"[yellow]{', '.join(template.tags)}[/yellow]")
    info_table.add_row("Validator Type", f"[blue]{template.validator_type}[/blue]")
    info_table.add_row("Usage Count", f"[magenta]{template.usage_count}[/magenta]")
    info_table.add_row("Created", template.created_at)

    console.print(info_table)

    # Show prompt template with variables highlighted
    console.print("\n[bold]Prompt Template:[/bold]")
    prompt_display = template.prompt_template
    variables = re.findall(r"\{(\w+)\}", template.prompt_template)
    for var in set(variables):
        prompt_display = prompt_display.replace(f"{{{var}}}", f"[bold red]{{{var}}}[/bold red]")
    console.print(Panel(prompt_display, title="Template", border_style="blue"))

    # Show variables in a tree
    if variables:
        var_tree = Tree("[bold]Template Variables[/bold]")
        for var in sorted(set(variables)):
            var_tree.add(f"[red]{var}[/red]")
        console.print(var_tree)

    # Show validator configuration
    console.print("\n[bold]Validator Configuration:[/bold]")
    config_json = json.dumps(template.validator_config, indent=2)
    syntax = Syntax(config_json, "json", theme="monokai", line_numbers=False)
    console.print(Panel(syntax, title="Configuration", border_style="green"))

    # Show JSON schema if available
    if template.json_schema:
        console.print("\n[bold]JSON Schema:[/bold]")
        schema_json = json.dumps(template.json_schema, indent=2)
        syntax = Syntax(schema_json, "json", theme="monokai", line_numbers=False)
        console.print(Panel(syntax, title="Schema", border_style="yellow"))

    # Show example output if available
    if template.example_output:
        console.print("\n[bold]Example Output:[/bold]")
        # Determine syntax highlighting based on validator type
        syntax_lang = {"json": "json", "sql": "sql", "markdown": "markdown", "csv": "csv", "email": "text"}.get(template.validator_type, "text")

        syntax = Syntax(template.example_output[:800] + ("..." if len(template.example_output) > 800 else ""), syntax_lang, theme="monokai", line_numbers=False)
        console.print(Panel(syntax, title="Example", border_style="green"))


@cli.command()
@click.argument("template_name")
@click.option("--output", "-o", help="Output file path", required=True)
@click.option("--interactive", "-i", is_flag=True, help="Interactive mode to fill variables")
@click.option("--preview", "-p", is_flag=True, help="Preview generated code before saving")
def use(template_name: str, output: str, interactive: bool, preview: bool) -> None:
    """Use a template to generate a task with interactive variable filling."""
    library = TemplateLibrary()
    template = library.get_template(template_name)

    if not template:
        console.print(f"[red]Template '{template_name}' not found![/red]")
        return

    console.print(Panel.fit(f"[bold cyan]Using Template: {template.name}[/bold cyan]\n{template.description}", title="Template Usage", box=box.DOUBLE))

    # Extract variables from template
    variables = list(set(re.findall(r"\{(\w+)\}", template.prompt_template)))

    template_vars = {}

    if interactive and variables:
        console.print("\n[bold]Please provide values for template variables:[/bold]")

        # Show helper text for common variables
        var_hints = {
            "api_name": "Name of your API (e.g., UserManagement)",
            "api_purpose": "What the API does (e.g., manages user accounts)",
            "resource_types": "Comma-separated list (e.g., users, roles, permissions)",
            "dataset_description": "Brief description of your data",
            "analysis_objectives": "What you want to analyze",
            "topic": "Main topic or subject",
            "product_name": "Name of your product",
            "feature_name": "Name of the feature",
            "company_name": "Your company name",
            "system_name": "Name of your system",
            "word_count": "Number of words (e.g., 1000)",
            "num_sections": "Number of sections (e.g., 5)",
            "target_keyword": "SEO keyword to target",
            "target_audience": "Who will read/use this",
        }

        for var in variables:
            hint = var_hints.get(var, f"Value for {var}")
            value = Prompt.ask(f"  [cyan]{var}[/cyan]", default="", console=console)
            if not value:
                value = Prompt.ask(f"    [dim]{hint}[/dim]", console=console)
            template_vars[var] = value
    else:
        # Provide smart default values based on variable names
        console.print("\n[yellow]Using default values. Edit the generated file to customize.[/yellow]")
        default_values = {
            "api_name": "MyAPI",
            "api_purpose": "manages resources",
            "resource_types": "items, users, settings",
            "dataset_description": "sample dataset",
            "analysis_objectives": "identify patterns and trends",
            "topic": "Technology Trends",
            "product_name": "MyProduct",
            "feature_name": "Core Feature",
            "company_name": "Acme Corp",
            "system_name": "MySystem",
            "word_count": "1500",
            "num_sections": "5",
            "target_keyword": "best practices",
            "target_audience": "developers",
            "http_method": "GET",
            "endpoint_path": "/api/v1/resource",
            "endpoint_description": "retrieves resource data",
            "programming_language": "Python",
            "skill_level": "intermediate",
            "num_exercises": "3",
            "duration": "30 days",
            "platforms": "Twitter, LinkedIn",
            "posts_per_week": "7",
        }

        for var in variables:
            template_vars[var] = default_values.get(var, f"example_{var}")

    # Fill in the prompt
    filled_prompt = template.prompt_template
    for key, value in template_vars.items():
        filled_prompt = filled_prompt.replace(f"{{{key}}}", str(value))

    # Show filled prompt
    console.print("\n[bold]Filled Prompt:[/bold]")
    console.print(Panel(filled_prompt, border_style="blue"))

    # Confirm generation
    if not interactive:
        proceed = Confirm.ask("\n[bold]Generate task with these values?[/bold]", default=True)
        if not proceed:
            console.print("[yellow]Generation cancelled.[/yellow]")
            return

    # Generate with progress indicator
    with console.status("[bold green]Generating task code...[/bold green]"):
        # Generate the task
        task_name = template_name.replace("_", " ").title().replace(" ", "") + "Task"

        # Map validator types
        validator_mapping = {
            "json": "JSONValidator",
            "csv": "CSVValidator",
            "email": "EmailValidator",
            "markdown": "MarkdownValidator",
            "sql": "SQLValidator",
            "story_scenes": "StoryToScenesValidator",
        }

        validator_class = validator_mapping.get(template.validator_type, "BaseValidator")

        # Generate code
        code = generate_task_code(template, template_vars, task_name, validator_class, filled_prompt)

    # Preview if requested
    if preview:
        console.print("\n[bold]Generated Code Preview:[/bold]")
        syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title=f"{task_name}.py", border_style="green"))

        if not Confirm.ask("\n[bold]Save this code?[/bold]", default=True):
            console.print("[yellow]Save cancelled.[/yellow]")
            return

    # Write file
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(code)

    console.print(f"\n[green]✓ Task generated successfully![/green]")
    console.print(f"[bold]Output file:[/bold] {output_path.absolute()}")

    # Show next steps
    console.print("\n[bold]Next steps:[/bold]")
    console.print("1. Review and customize the generated task")
    console.print("2. Test with: [cyan]python {output_path.name}[/cyan]")
    console.print("3. Integrate into your project")

    # Update usage count
    library.update_usage_count(template_name)


@cli.command()
@click.argument("query")
@click.option("--top", "-n", default=5, help="Number of results to show")
def search(query: str, top: int) -> None:
    """Search for templates similar to a query with visual results."""
    library = TemplateLibrary()

    with console.status(f"[bold green]Searching for templates similar to '{query}'...[/bold green]"):
        results = library.find_similar_templates(query, top_k=top)

    if not results:
        console.print("[yellow]No similar templates found.[/yellow]")
        return

    console.print(Panel.fit(f"[bold]Templates similar to: '{query}'[/bold]", title="Search Results", box=box.DOUBLE))

    for i, (template, score) in enumerate(results, 1):
        # Color code similarity scores
        score_color = "green" if score > 0.7 else "yellow" if score > 0.4 else "red"

        console.print(f"\n[bold]{i}.[/bold] [cyan]{template.name}[/cyan] [dim]({score_color}similarity: {score:.0%}[/{score_color})[/dim]")
        console.print(f"   [green]Category:[/green] {template.category}")
        console.print(f"   [white]Description:[/white] {template.description}")
        console.print(f"   [yellow]Tags:[/yellow] {', '.join(template.tags[:5])}")

        # Show a snippet of the template
        snippet = template.prompt_template[:100] + "..." if len(template.prompt_template) > 100 else template.prompt_template
        console.print(f"   [dim]Template:[/dim] {snippet}")


@cli.command()
def categories() -> None:
    """List all available categories with visual hierarchy."""
    library = TemplateLibrary()
    cats = library.get_categories()

    tree = Tree("[bold]Template Categories[/bold]")

    total_templates = 0
    for cat in cats:
        templates = library.list_templates(category=cat)
        count = len(templates)
        total_templates += count

        # Add category with count and color coding
        color = "green" if count > 5 else "yellow" if count > 2 else "red"
        cat_branch = tree.add(f"[{color}]{cat}[/{color}] ({count} templates)")

        # Show first 3 templates in each category
        for template in templates[:3]:
            cat_branch.add(f"[dim]{template.name}[/dim]")
        if count > 3:
            cat_branch.add(f"[dim]... and {count - 3} more[/dim]")

    console.print(tree)
    console.print(f"\n[bold]Total:[/bold] {total_templates} templates across {len(cats)} categories")


@cli.command()
def tags() -> None:
    """List all available tags in a tag cloud style."""
    library = TemplateLibrary()
    all_tags = library.get_all_tags()

    console.print(Panel.fit("[bold]Available Tags[/bold]", box=box.DOUBLE))

    # Count templates per tag for sizing
    tag_counts = {}
    for tag in all_tags:
        count = len(library.list_templates(tags=[tag]))
        tag_counts[tag] = count

    # Group tags by first letter with visual formatting
    grouped: Dict[str, List[str]] = {}
    for tag in all_tags:
        first_letter = tag[0].upper()
        if first_letter not in grouped:
            grouped[first_letter] = []
        grouped[first_letter].append(tag)

    for letter in sorted(grouped.keys()):
        tags_in_letter = []
        for tag in sorted(grouped[letter]):
            count = tag_counts[tag]
            # Size and color based on usage
            if count > 5:
                style = "bold green"
            elif count > 2:
                style = "yellow"
            else:
                style = "dim"
            tags_in_letter.append(f"[{style}]{tag}[/{style}]")

        console.print(f"\n[bold cyan]{letter}:[/bold cyan] {', '.join(tags_in_letter)}")


@cli.command()
@click.option("--limit", "-n", default=10, help="Number of templates to show")
def popular(limit: int) -> None:
    """Show most popular templates with usage statistics."""
    library = TemplateLibrary()
    templates = library.get_popular_templates(top_k=limit)

    if not templates:
        console.print("[yellow]No usage data available yet.[/yellow]")
        console.print("[dim]Templates will appear here as you use them.[/dim]")
        return

    console.print(Panel.fit(f"[bold]Top {min(limit, len(templates))} Most Used Templates[/bold]", title="Popular Templates", box=box.DOUBLE))

    # Create a bar chart-like visualization
    max_uses = max(t.usage_count for t in templates) if templates else 1

    for i, template in enumerate(templates[:limit], 1):
        # Calculate bar width
        bar_width = int((template.usage_count / max_uses) * 30)
        bar = "█" * bar_width + "░" * (30 - bar_width)

        console.print(f"\n[bold]{i:2d}.[/bold] [cyan]{template.name}[/cyan]")
        console.print(f"    [{template.category}] {template.description[:50]}...")
        console.print(f"    [green]{bar}[/green] {template.usage_count} uses")


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--output", "-o", help="Output directory for generated task")
def wizard(input_file: str, output: Optional[str]) -> None:
    """Interactive wizard to convert a prompt file to a task."""
    console.print(Panel.fit("[bold]Template Wizard[/bold]\nInteractive prompt-to-task conversion", box=box.DOUBLE))

    # Read the prompt file
    with open(input_file, "r") as f:
        prompt_content = f.read()

    console.print(f"\n[bold]Input prompt:[/bold] {input_file}")
    console.print(Panel(prompt_content[:200] + "..." if len(prompt_content) > 200 else prompt_content))

    # Find matching templates
    library = TemplateLibrary()
    with console.status("[bold green]Analyzing prompt and finding matches...[/bold green]"):
        matches = library.find_similar_templates(prompt_content, top_k=5)

    if matches:
        console.print("\n[bold]Suggested templates:[/bold]")
        choices = []
        for i, (template, score) in enumerate(matches, 1):
            score_color = "green" if score > 0.5 else "yellow"
            console.print(f"{i}. [cyan]{template.name}[/cyan] [{score_color}]{score:.0%} match[/{score_color}]")
            console.print(f"   {template.description}")
            choices.append(template)

        # Let user choose
        choice = Prompt.ask("\nSelect a template (number) or press Enter to skip", default="", console=console)

        if choice.isdigit() and 1 <= int(choice) <= len(choices):
            selected_template = choices[int(choice) - 1]

            # Generate output path
            if not output:
                output = Path(input_file).stem + "_task.py"
            else:
                output = str(Path(output) / (Path(input_file).stem + "_task.py"))

            # Use the template
            console.print(f"\n[green]Using template: {selected_template.name}[/green]")
            ctx = click.Context(use)
            ctx.invoke(use, template_name=selected_template.name, output=str(output), interactive=True, preview=True)
            return

    console.print("\n[yellow]No suitable templates found. Consider creating a custom task.[/yellow]")


def generate_task_code(template: PromptTemplate, template_vars: Dict[str, Any], task_name: str, validator_class: str, filled_prompt: str) -> str:
    """Generate task code from template."""
    # Escape quotes in the filled prompt
    escaped_prompt = filled_prompt.replace('"""', '\\"""')

    return f'''"""
Generated task from template: {template.name}
{template.description}

Generated using the Template Library CLI.
Template Category: {template.category}
"""

from typing import Dict, Any, Optional
from validated_llm.tasks import BaseTask
from validated_llm.validators import {validator_class}


class {task_name}(BaseTask):
    """
    {template.description}

    This task was generated from the '{template.name}' template.

    Template Variables Used:
    {chr(10).join(f"    - {key}: {value}" for key, value in template_vars.items())}
    """

    def __init__(self):
        super().__init__()
        self.template_vars = {json.dumps(template_vars, indent=8)}
        self.template_name = "{template.name}"
        self.template_category = "{template.category}"

    @property
    def prompt_template(self) -> str:
        """The prompt template for this task."""
        return """{escaped_prompt}"""

    @property
    def validator_class(self):
        """The validator class for this task."""
        return {validator_class}

    def prepare_prompt_data(self, **kwargs) -> Dict[str, Any]:
        """
        Prepare data for the prompt template.

        Default values are taken from the template variables used during generation.
        You can override any of these by passing keyword arguments.
        """
        # Use template variables as defaults, allow overrides
        data = self.template_vars.copy()
        data.update(kwargs)
        return data

    def configure_validator(self) -> Dict[str, Any]:
        """Configure the validator with template-specific settings."""
        config = {json.dumps(template.validator_config, indent=8)}

        # You can add runtime configuration here
        # For example, to make certain validations stricter or more lenient

        return config


# Example usage
if __name__ == "__main__":
    from validated_llm import ValidationLoop

    # Create task instance
    task = {task_name}()

    print(f"Running {task_name}...")
    print(f"Template: {{task.template_name}} ({{task.template_category}})")
    print("-" * 50)

    # Create validation loop
    loop = ValidationLoop(
        task=task,
        model="gpt-4",  # or your preferred model
        max_retries=3
    )

    try:
        # Execute with any additional parameters
        result = loop.execute(
            # Override any template variables here if needed
            # For example: api_name="My Custom API"
        )

        print("\\nGenerated content:")
        print("-" * 50)
        print(result)

    except Exception as e:
        print(f"\\nError: {{e}}")
        print("\\nTip: Check that your model is running and accessible.")
'''


if __name__ == "__main__":
    cli()
