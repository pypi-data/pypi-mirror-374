"""
Command-line interface for the prompt-to-task conversion tool using Click.

Usage:
    validated-llm-prompt2task input.txt --output generated_task.py
    validated-llm-prompt2task input.txt --interactive
"""

import os
from pathlib import Path
from typing import Any, Tuple

import click

from .analyzer import PromptAnalyzer
from .code_generator import TaskCodeGenerator
from .template_library import PromptTemplate, TemplateLibrary
from .validator_suggester import ValidatorSuggester


def read_prompt_file(file_path: str) -> str:
    """Read prompt from file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        click.echo(f"❌ Error: File '{file_path}' not found", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"❌ Error reading file: {e}", err=True)
        raise click.Abort()


def write_output_file(file_path: str, content: str) -> None:
    """Write generated code to file."""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        click.echo(f"✅ Generated task code written to: {file_path}")
    except Exception as e:
        click.echo(f"❌ Error writing file: {e}", err=True)
        raise click.Abort()


def interactive_mode(analysis: Any, suggestions: list[Any], prompt_template: str) -> Tuple[Any, str, str]:
    """Run in interactive mode to refine suggestions."""
    click.echo("\n🔍 PROMPT ANALYSIS RESULTS")
    click.echo("=" * 50)
    click.echo(f"📝 Template variables: {', '.join(analysis.template_variables) if analysis.template_variables else 'None'}")
    click.echo(f"📊 Detected format: {analysis.output_format} (confidence: {analysis.confidence:.1%})")

    if analysis.json_schema:
        click.echo(f"🔗 JSON schema detected: {len(analysis.json_schema.get('properties', {}))} properties")

    if analysis.csv_columns:
        click.echo(f"📋 CSV columns: {', '.join(analysis.csv_columns)}")

    if analysis.validation_hints:
        click.echo(f"⚠️  Validation hints found: {len(analysis.validation_hints)}")
        for hint in analysis.validation_hints[:3]:
            click.echo(f"   • {hint[:80]}...")

    # Show matched templates if any
    if analysis.matched_templates:
        click.echo(f"\n📚 MATCHED TEMPLATES")
        click.echo("=" * 50)
        for template, score in analysis.matched_templates[:3]:
            click.echo(f"• {template.name} ({score:.1%} match)")
            click.echo(f"  {template.description}")
            click.echo()

    click.echo(f"\n🤖 VALIDATOR SUGGESTIONS")
    click.echo("=" * 50)

    for i, suggestion in enumerate(suggestions, 1):
        click.echo(f"{i}. {suggestion.validator_type} (confidence: {suggestion.confidence:.1%})")
        click.echo(f"   📖 {suggestion.description}")
        click.echo(f"   🔧 Type: {'Built-in' if suggestion.is_builtin else 'Custom'}")
        if suggestion.config:
            click.echo(f"   ⚙️  Config: {suggestion.config}")
        click.echo()

    # Let user choose validator
    while True:
        choice = click.prompt(f"Select validator (1-{len(suggestions)}) or 'q' to quit", type=str).strip()
        if choice.lower() == "q":
            raise click.Abort()

        try:
            validator_index = int(choice) - 1
            if 0 <= validator_index < len(suggestions):
                selected_suggestion = suggestions[validator_index]
                break
            else:
                click.echo(f"Please enter a number between 1 and {len(suggestions)}")
        except ValueError:
            click.echo("Please enter a valid number or 'q'")

    # Get task details
    task_name = click.prompt("\nEnter task name (e.g., 'Email Generation')", default="Generated Task")
    task_description = click.prompt("Enter task description", default="Automatically generated task from prompt analysis")

    return selected_suggestion, task_name, task_description


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file for generated task code")
@click.option("--name", help="Name for the generated task")
@click.option("--description", help="Description for the generated task")
@click.option("--interactive", "-i", is_flag=True, help="Run in interactive mode to refine suggestions")
@click.option("--analyze-only", is_flag=True, help="Only analyze the prompt, don't generate code")
@click.option("--validator-only", help="Generate only validator code for specific suggestion (by index)")
@click.option("--use-template", help="Use a specific template by name")
@click.option("--show-templates", is_flag=True, help="Show matching templates and exit")
def main(
    input_file: str,
    output: str,
    name: str,
    description: str,
    interactive: bool,
    analyze_only: bool,
    validator_only: str,
    use_template: str,
    show_templates: bool,
) -> None:
    """Convert prompts to validated-llm tasks.

    Examples:

        validated-llm-prompt2task my_prompt.txt

        validated-llm-prompt2task my_prompt.txt --output my_task.py

        validated-llm-prompt2task my_prompt.txt --interactive

        validated-llm-prompt2task my_prompt.txt --analyze-only
    """
    # Generate default output filename if not specified
    if not output and not interactive and not analyze_only:
        # Convert input filename to output filename: foo-bar.txt -> foo_bar_task.py
        input_path = Path(input_file)
        input_stem = input_path.stem  # removes extension
        # Replace hyphens with underscores for Python naming convention
        python_safe_name = input_stem.replace("-", "_")

        # In testing environment, use a cleaner name
        if os.getenv("TESTING") == "true":
            # For temp files, use a simpler name
            if input_stem.startswith("tmp"):
                output = "generated_task.py"
            else:
                output = f"{python_safe_name}_task.py"
        else:
            # Default to current directory
            output = f"{python_safe_name}_task.py"
        click.echo(f"📝 No output file specified, using: {output}")

    # Read input prompt
    prompt_template = read_prompt_file(input_file)

    click.echo(f"📖 Analyzing prompt from: {input_file}")
    click.echo(f"📏 Prompt length: {len(prompt_template)} characters")

    # Initialize components
    template_library = TemplateLibrary()
    analyzer = PromptAnalyzer(template_library=template_library)
    suggester = ValidatorSuggester()
    generator = TaskCodeGenerator()

    # Handle show-templates mode
    if show_templates:
        matches = template_library.find_similar_templates(prompt_template, top_k=5)
        if matches:
            click.echo("\n📚 MATCHING TEMPLATES")
            click.echo("=" * 50)
            for i, (template, score) in enumerate(matches, 1):
                click.echo(f"\n{i}. {template.name} (similarity: {score:.1%})")
                click.echo(f"   📁 Category: {template.category}")
                click.echo(f"   📖 {template.description}")
                if template.tags:
                    click.echo(f"   🏷️  {', '.join(template.tags)}")
        else:
            click.echo("No matching templates found.")
        return

    # Handle use-template mode
    if use_template:
        selected_template = template_library.get_template(use_template)
        if not selected_template:
            click.echo(f"❌ Template '{use_template}' not found", err=True)
            raise click.Abort()

        # Update usage count
        template_library.update_usage_count(use_template)

        # Use template's prompt as base
        prompt_template = selected_template.prompt_template
        click.echo(f"📚 Using template: {selected_template.name}")

    # Analyze prompt
    analysis = analyzer.analyze(prompt_template)
    suggestions = suggester.suggest_validators(analysis)

    if not suggestions:
        click.echo("⚠️  No validator suggestions could be generated", err=True)
        raise click.Abort()

    # Handle analyze-only mode
    if analyze_only:
        click.echo("\n🔍 ANALYSIS RESULTS")
        click.echo("=" * 30)
        click.echo(f"Format: {analysis.output_format} ({analysis.confidence:.1%})")
        click.echo(f"Variables: {analysis.template_variables}")
        click.echo(f"Suggestions: {len(suggestions)}")
        return

    # Handle validator-only mode
    if validator_only:
        try:
            index = int(validator_only) - 1
            if 0 <= index < len(suggestions):
                validator_code = generator.generate_validator_code_only(suggestions[index])
                if output:
                    write_output_file(output, validator_code)
                else:
                    click.echo(validator_code)
                return
            else:
                click.echo(f"❌ Invalid validator index: {validator_only}", err=True)
                raise click.Abort()
        except ValueError:
            click.echo(f"❌ Invalid validator index: {validator_only}", err=True)
            raise click.Abort()

    # Handle interactive mode
    if interactive:
        selected_suggestion, task_name, task_description = interactive_mode(analysis, suggestions, prompt_template)
        selected_suggestions = [selected_suggestion]
    else:
        # Use best suggestion and provided or default values
        selected_suggestions = suggestions[:1]  # Use top suggestion
        task_name = name or "Generated Task"
        task_description = description or "Automatically generated task from prompt analysis"

    # Generate code
    click.echo(f"\n🔧 Generating task code...")
    generated_code = generator.generate_task_code(analysis=analysis, suggestions=selected_suggestions, task_name=task_name, task_description=task_description, prompt_template=prompt_template, source_file=str(input_file))

    # Output results
    if output:
        write_output_file(output, generated_code)

        # Show summary
        click.echo(f"\n📊 GENERATION SUMMARY")
        click.echo("=" * 30)
        click.echo(f"📝 Task: {task_name}")
        click.echo(f"🔍 Format: {analysis.output_format}")
        click.echo(f"⚙️  Validator: {selected_suggestions[0].validator_type}")
        click.echo(f"📁 Output: {output}")

        if analysis.template_variables:
            click.echo(f"🔗 Variables: {', '.join(analysis.template_variables)}")

        click.echo(f"\n💡 Next steps:")
        click.echo(f"1. Review and customize the generated code")
        click.echo(f"2. Test with: python {output}")
        output_path = Path(output)
        click.echo(f"3. Import and use: from {output_path.stem} import {generator._to_class_name(task_name)}")

        click.echo(f"\n📁 For validated-llm projects:")
        click.echo(f"   Move to: src/validated_llm/tasks/prompt_to_task_generated/{output_path.name}")
        click.echo(f"   Then import: from validated_llm.tasks.prompt_to_task_generated.{output_path.stem} import {generator._to_class_name(task_name)}")

    else:
        click.echo(generated_code)


if __name__ == "__main__":
    main()
