"""
Batch conversion functionality for prompt-to-task tool.

This module handles converting multiple prompt files at once with
progress tracking and summary reporting.
"""

import asyncio
import concurrent.futures
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from .analyzer import PromptAnalyzer
from .batch_types import BatchConfig, ConversionResult, ConversionStatus
from .code_generator import TaskCodeGenerator
from .progress_reporter import ProgressReporter, create_progress_reporter
from .template_library import TemplateLibrary
from .validator_suggester import ValidatorSuggester


class BatchConverter:
    """Handles batch conversion of multiple prompt files."""

    def __init__(self, config: BatchConfig, progress_reporter: Optional[ProgressReporter] = None):
        """Initialize batch converter with configuration."""
        self.config = config
        self.analyzer = PromptAnalyzer()
        self.suggester = ValidatorSuggester()
        self.generator = TaskCodeGenerator()
        self.template_library = TemplateLibrary()
        self.results: List[ConversionResult] = []
        self.progress_reporter = progress_reporter or create_progress_reporter("auto")

    def discover_files(self, paths: List[Path]) -> List[Path]:
        """Discover all prompt files to convert from given paths."""
        prompt_files: Set[Path] = set()

        for path in paths:
            if path.is_file():
                # Single file specified
                prompt_files.add(path)
            elif path.is_dir():
                # Directory - search for matching files
                for pattern in self.config.file_patterns:
                    prompt_files.update(path.glob(f"**/{pattern}"))

        # Filter out excluded patterns
        filtered_files = []
        for file in prompt_files:
            if not any(file.match(pattern) for pattern in self.config.exclude_patterns):
                filtered_files.append(file)

        return sorted(filtered_files)

    def get_output_path(self, input_file: Path) -> Path:
        """Determine output path for a given input file."""
        if self.config.output_dir:
            # Use specified output directory
            output_dir = self.config.output_dir
            output_dir.mkdir(parents=True, exist_ok=True)
            base_name = input_file.stem + self.config.output_suffix
            return output_dir / base_name
        else:
            # Output next to input file
            return input_file.parent / (input_file.stem + self.config.output_suffix)

    def should_skip_file(self, input_file: Path, output_file: Path) -> bool:
        """Check if file should be skipped based on configuration."""
        if self.config.skip_existing and output_file.exists():
            return True
        return False

    def convert_single_file(self, input_file: Path) -> ConversionResult:
        """Convert a single prompt file to a task."""
        import time

        start_time = time.time()

        result = ConversionResult(input_file=input_file)

        try:
            # Determine output path
            output_file = self.get_output_path(input_file)
            result.output_file = output_file

            # Check if should skip
            if self.should_skip_file(input_file, output_file):
                result.status = ConversionStatus.SKIPPED
                return result

            result.status = ConversionStatus.IN_PROGRESS

            # Read prompt content
            prompt_content = input_file.read_text(encoding="utf-8")

            # Check for template
            template = None
            if self.config.template_name:
                template = self.template_library.get_template(self.config.template_name)

            # Analyze prompt
            analysis = self.analyzer.analyze(prompt_content)

            # Get validator suggestions
            suggestions = self.suggester.suggest_validators(analysis)

            # Apply common validators if specified
            if self.config.common_validators:
                # Add common validators to suggestions
                for validator_name in self.config.common_validators:
                    if not any(s.validator_type == validator_name for s in suggestions):
                        # Add to suggestions (simplified - in real implementation would need proper validator class)
                        pass

            # Select best validator
            selected_validator = suggestions[0] if suggestions else None

            # Generate task name from filename
            task_name = input_file.stem.replace("-", "_").replace(" ", "_")
            task_name = "".join(word.capitalize() for word in task_name.split("_")) + "Task"
            result.task_name = task_name

            # Generate code
            code = self.generator.generate_task_code(
                analysis=analysis, suggestions=suggestions, task_name=task_name, task_description=f"Task generated from {input_file.name}", prompt_template=prompt_content, source_file=str(input_file)
            )

            # Write output if not dry run
            if not self.config.dry_run:
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text(code, encoding="utf-8")

            result.status = ConversionStatus.SUCCESS
            if suggestions:
                result.validators_used = [s.validator_type for s in suggestions]

        except Exception as e:
            result.status = ConversionStatus.FAILED
            result.error_message = str(e)

        finally:
            result.processing_time = time.time() - start_time

        return result

    def convert_parallel(self, files: List[Path]) -> List[ConversionResult]:
        """Convert multiple files in parallel."""
        results = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            future_to_file = {executor.submit(self.convert_single_file, file): file for file in files}

            for future in concurrent.futures.as_completed(future_to_file):
                result = future.result()
                results.append(result)
                self.progress_reporter.update(result)

        return results

    def convert_sequential(self, files: List[Path]) -> List[ConversionResult]:
        """Convert multiple files sequentially."""
        results = []
        for file in files:
            result = self.convert_single_file(file)
            results.append(result)
            self.progress_reporter.update(result)
        return results

    def convert(self, paths: List[Path]) -> List[ConversionResult]:
        """Main entry point for batch conversion."""
        # Discover files
        files = self.discover_files(paths)

        if not files:
            return []

        # Start progress reporting
        self.progress_reporter.start(len(files), "Converting prompt files")

        # Convert files
        if self.config.parallel and len(files) > 1:
            self.results = self.convert_parallel(files)
        else:
            self.results = self.convert_sequential(files)

        # Finish progress reporting
        self.progress_reporter.finish()

        # Sort results by input file for consistent output
        self.results.sort(key=lambda r: r.input_file)

        return self.results

    def generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics for the batch conversion."""
        summary: Dict[str, Any] = {
            "total_files": len(self.results),
            "successful": sum(1 for r in self.results if r.status == ConversionStatus.SUCCESS),
            "failed": sum(1 for r in self.results if r.status == ConversionStatus.FAILED),
            "skipped": sum(1 for r in self.results if r.status == ConversionStatus.SKIPPED),
            "total_time": sum(r.processing_time for r in self.results),
            "validators_used": {},
            "errors": [],
        }

        # Count validator usage
        for result in self.results:
            for validator in result.validators_used:
                summary["validators_used"][validator] = summary["validators_used"].get(validator, 0) + 1

        # Collect errors
        for result in self.results:
            if result.status == ConversionStatus.FAILED and result.error_message:
                summary["errors"].append({"file": str(result.input_file), "error": result.error_message})

        return summary

    def save_report(self, report_path: Path) -> None:
        """Save detailed conversion report to JSON file."""
        report = {
            "summary": self.generate_summary(),
            "config": {
                "output_dir": str(self.config.output_dir) if self.config.output_dir else None,
                "output_suffix": self.config.output_suffix,
                "skip_existing": self.config.skip_existing,
                "parallel": self.config.parallel,
                "max_workers": self.config.max_workers,
                "dry_run": self.config.dry_run,
                "template_name": self.config.template_name,
                "common_validators": self.config.common_validators,
                "file_patterns": self.config.file_patterns,
                "exclude_patterns": self.config.exclude_patterns,
            },
            "results": [
                {
                    "input_file": str(r.input_file),
                    "output_file": str(r.output_file) if r.output_file else None,
                    "status": r.status.value,
                    "error_message": r.error_message,
                    "task_name": r.task_name,
                    "validators_used": r.validators_used,
                    "processing_time": r.processing_time,
                }
                for r in self.results
            ],
        }

        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
