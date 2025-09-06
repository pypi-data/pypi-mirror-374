"""
Batch conversion CLI commands for prompt-to-task tool.

This module provides the batch conversion command that processes
multiple prompt files at once.
"""

from pathlib import Path
from typing import List, Optional

import click

from .batch_converter import BatchConverter
from .batch_types import BatchConfig
from .progress_reporter import create_progress_reporter


@click.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True), required=True)
@click.option("--output-dir", "-o", type=click.Path(file_okay=False), help="Directory to write all generated task files")
@click.option("--output-suffix", default="_task.py", help="Suffix for generated files (default: _task.py)")
@click.option("--skip-existing/--overwrite", default=True, help="Skip files that already have generated tasks")
@click.option("--parallel/--sequential", default=True, help="Process files in parallel (default: parallel)")
@click.option("--max-workers", type=int, default=4, help="Maximum number of parallel workers")
@click.option("--dry-run", is_flag=True, help="Show what would be done without actually doing it")
@click.option("--template", "-t", help="Template name to use for all conversions")
@click.option("--validator", "-v", multiple=True, help="Common validators to apply to all files (can be specified multiple times)")
@click.option("--include", "-i", multiple=True, default=["*.txt", "*.prompt", "*.md"], help="File patterns to include (default: *.txt, *.prompt, *.md)")
@click.option("--exclude", "-e", multiple=True, default=["*_task.py", "README.md"], help="File patterns to exclude (default: *_task.py, README.md)")
@click.option("--progress", type=click.Choice(["auto", "rich", "tqdm", "simple", "none"]), default="auto", help="Progress reporter type")
@click.option("--report", type=click.Path(dir_okay=False), help="Save detailed conversion report to JSON file")
def batch(
    paths: tuple,
    output_dir: Optional[str],
    output_suffix: str,
    skip_existing: bool,
    parallel: bool,
    max_workers: int,
    dry_run: bool,
    template: Optional[str],
    validator: tuple,
    include: tuple,
    exclude: tuple,
    progress: str,
    report: Optional[str],
) -> None:
    """
    Convert multiple prompt files to validated-llm tasks.

    PATHS can be files or directories. When directories are specified,
    they are searched recursively for matching files.

    Examples:

        # Convert all .txt files in current directory
        validated-llm-prompt2task batch .

        # Convert specific files
        validated-llm-prompt2task batch prompt1.txt prompt2.txt

        # Convert all prompts in a directory tree
        validated-llm-prompt2task batch prompts/

        # Convert with custom output directory
        validated-llm-prompt2task batch prompts/ -o generated_tasks/

        # Dry run to see what would be converted
        validated-llm-prompt2task batch . --dry-run

        # Use a specific template for all conversions
        validated-llm-prompt2task batch prompts/ --template api_doc

        # Apply common validators to all files
        validated-llm-prompt2task batch . -v JSONValidator -v DateTimeValidator
    """
    # Convert paths to Path objects
    path_list = [Path(p) for p in paths]

    # Create batch configuration
    config = BatchConfig(
        output_dir=Path(output_dir) if output_dir else None,
        output_suffix=output_suffix,
        skip_existing=skip_existing,
        parallel=parallel,
        max_workers=max_workers,
        dry_run=dry_run,
        template_name=template,
        common_validators=list(validator),
        file_patterns=list(include),
        exclude_patterns=list(exclude),
    )

    # Create progress reporter
    progress_reporter = create_progress_reporter(progress)

    # Create and run batch converter
    converter = BatchConverter(config, progress_reporter)
    results = converter.convert(path_list)

    if not results:
        click.echo("No files found to convert.")
        return

    # Show summary
    summary = converter.generate_summary()

    if dry_run:
        click.echo("\n🔍 DRY RUN - No files were actually created")

    click.echo(f"\n📊 Conversion Summary:")
    click.echo(f"   Total files: {summary['total_files']}")
    click.echo(f"   ✅ Successful: {summary['successful']}")
    click.echo(f"   ❌ Failed: {summary['failed']}")
    click.echo(f"   ⏭️  Skipped: {summary['skipped']}")
    click.echo(f"   ⏱️  Total time: {summary['total_time']:.2f}s")

    validators_used = summary.get("validators_used", {})
    if validators_used:
        click.echo("\n📝 Validators used:")
        for validator_name, count in validators_used.items():
            click.echo(f"   - {validator_name}: {count} files")

    errors = summary.get("errors", [])
    if errors:
        click.echo("\n❌ Errors:")
        for error_info in errors:
            click.echo(f"   {error_info['file']}: {error_info['error']}")

    # Save report if requested
    if report:
        report_path = Path(report)
        converter.save_report(report_path)
        click.echo(f"\n📄 Detailed report saved to: {report_path}")


if __name__ == "__main__":
    batch()
