"""
Tests for batch conversion functionality.
"""

import json
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import Mock, patch

import pytest

from tools.prompt_to_task.batch_converter import BatchConverter
from tools.prompt_to_task.batch_types import BatchConfig, ConversionResult, ConversionStatus
from tools.prompt_to_task.progress_reporter import SimpleProgressReporter


class TestBatchConverter:
    """Test BatchConverter functionality."""

    @pytest.fixture
    def temp_dir(self) -> Generator[Path, None, None]:
        """Create a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def sample_prompts(self, temp_dir: Path) -> Path:
        """Create sample prompt files for testing."""
        prompts = {
            "simple.txt": "Generate a list of {count} items about {topic}",
            "json_prompt.txt": "Create a JSON object with name and age for {person}",
            "complex.prompt": """Generate a detailed report about {subject}.

            The report should include:
            - Executive summary
            - Key findings
            - Recommendations

            Format as markdown.""",
            "subdir/nested.txt": "Write a story about {character}",
        }

        # Create files
        for filename, content in prompts.items():
            file_path = temp_dir / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)

        return temp_dir

    def test_discover_files_single_file(self, sample_prompts: Path) -> None:
        """Test discovering a single file."""
        config = BatchConfig()
        converter = BatchConverter(config)

        files = converter.discover_files([sample_prompts / "simple.txt"])

        assert len(files) == 1
        assert files[0].name == "simple.txt"

    def test_discover_files_directory(self, sample_prompts: Path) -> None:
        """Test discovering files in a directory."""
        config = BatchConfig()
        converter = BatchConverter(config)

        files = converter.discover_files([sample_prompts])

        # Should find all .txt files including nested
        txt_files = [f for f in files if f.suffix == ".txt"]
        assert len(txt_files) == 3  # simple.txt, json_prompt.txt, nested.txt

        # Should find .prompt files
        prompt_files = [f for f in files if f.suffix == ".prompt"]
        assert len(prompt_files) == 1  # complex.prompt

    def test_discover_files_exclude_patterns(self, sample_prompts: Path) -> None:
        """Test file exclusion patterns."""
        # Create a file that should be excluded
        (sample_prompts / "simple_task.py").write_text("# Generated task")
        (sample_prompts / "README.md").write_text("# README")

        config = BatchConfig()
        converter = BatchConverter(config)

        files = converter.discover_files([sample_prompts])

        # Should not include excluded files
        assert not any(f.name == "simple_task.py" for f in files)
        assert not any(f.name == "README.md" for f in files)

    def test_get_output_path_default(self, sample_prompts: Path) -> None:
        """Test default output path generation."""
        config = BatchConfig()
        converter = BatchConverter(config)

        input_file = sample_prompts / "simple.txt"
        output_path = converter.get_output_path(input_file)

        assert output_path == sample_prompts / "simple_task.py"

    def test_get_output_path_custom_dir(self, temp_dir: Path) -> None:
        """Test custom output directory."""
        output_dir = temp_dir / "generated"
        config = BatchConfig(output_dir=output_dir)
        converter = BatchConverter(config)

        input_file = temp_dir / "prompts" / "simple.txt"
        output_path = converter.get_output_path(input_file)

        assert output_path == output_dir / "simple_task.py"
        assert output_path.parent == output_dir

    def test_should_skip_existing(self, sample_prompts: Path) -> None:
        """Test skip existing file logic."""
        config = BatchConfig(skip_existing=True)
        converter = BatchConverter(config)

        input_file = sample_prompts / "simple.txt"
        output_file = sample_prompts / "simple_task.py"

        # Should not skip non-existent file
        assert not converter.should_skip_file(input_file, output_file)

        # Create output file
        output_file.write_text("# existing")

        # Should skip existing file
        assert converter.should_skip_file(input_file, output_file)

        # Should not skip if skip_existing is False
        config.skip_existing = False
        converter = BatchConverter(config)
        assert not converter.should_skip_file(input_file, output_file)

    @patch("tools.prompt_to_task.batch_converter.TaskCodeGenerator")
    @patch("tools.prompt_to_task.batch_converter.ValidatorSuggester")
    @patch("tools.prompt_to_task.batch_converter.PromptAnalyzer")
    def test_convert_single_file_success(self, mock_analyzer: Mock, mock_suggester: Mock, mock_generator: Mock, sample_prompts: Path) -> None:
        """Test successful single file conversion."""
        # Setup mocks
        mock_analysis = Mock()
        mock_analysis.template_variables = ["count", "topic"]
        mock_analyzer.return_value.analyze.return_value = mock_analysis

        mock_suggestion = Mock()
        mock_suggestion.validator_type = "ListValidator"
        mock_suggester.return_value.suggest_validators.return_value = [mock_suggestion]

        mock_generator.return_value.generate_task_code.return_value = "# Generated task code"

        config = BatchConfig()
        converter = BatchConverter(config)

        input_file = sample_prompts / "simple.txt"
        result = converter.convert_single_file(input_file)

        assert result.status == ConversionStatus.SUCCESS
        assert result.task_name == "SimpleTask"
        assert result.validators_used == ["ListValidator"]
        assert result.error_message is None
        assert result.processing_time > 0

    def test_convert_single_file_skip_existing(self, sample_prompts: Path) -> None:
        """Test skipping existing files."""
        # Create existing output file
        output_file = sample_prompts / "simple_task.py"
        output_file.write_text("# existing")

        config = BatchConfig(skip_existing=True)
        converter = BatchConverter(config)

        input_file = sample_prompts / "simple.txt"
        result = converter.convert_single_file(input_file)

        assert result.status == ConversionStatus.SKIPPED

    @patch("tools.prompt_to_task.batch_converter.TaskCodeGenerator")
    def test_convert_single_file_failure(self, mock_generator: Mock, sample_prompts: Path) -> None:
        """Test handling conversion failure."""
        # Make generator raise exception
        mock_generator.return_value.generate_task_code.side_effect = ValueError("Generation failed")

        config = BatchConfig()
        converter = BatchConverter(config)

        input_file = sample_prompts / "simple.txt"
        result = converter.convert_single_file(input_file)

        assert result.status == ConversionStatus.FAILED
        assert result.error_message is not None
        assert "Generation failed" in result.error_message

    @patch("tools.prompt_to_task.batch_converter.TaskCodeGenerator")
    @patch("tools.prompt_to_task.batch_converter.ValidatorSuggester")
    @patch("tools.prompt_to_task.batch_converter.PromptAnalyzer")
    def test_convert_dry_run(self, mock_analyzer: Mock, mock_suggester: Mock, mock_generator: Mock, sample_prompts: Path) -> None:
        """Test dry run mode doesn't create files."""
        # Setup mocks
        mock_analysis = Mock()
        mock_analysis.template_variables = []
        mock_analyzer.return_value.analyze.return_value = mock_analysis

        mock_suggestion = Mock()
        mock_suggestion.validator_type = "RegexValidator"
        mock_suggester.return_value.suggest_validators.return_value = [mock_suggestion]

        mock_generator.return_value.generate_task_code.return_value = "# Generated code"

        config = BatchConfig(dry_run=True)
        converter = BatchConverter(config)

        input_file = sample_prompts / "simple.txt"
        result = converter.convert_single_file(input_file)

        # Should succeed but not create file
        assert result.status == ConversionStatus.SUCCESS
        assert not (sample_prompts / "simple_task.py").exists()

    def test_convert_batch_sequential(self, sample_prompts: Path) -> None:
        """Test sequential batch conversion."""
        config = BatchConfig(parallel=False, dry_run=True)
        converter = BatchConverter(config, progress_reporter=SimpleProgressReporter(verbose=False))

        results = converter.convert([sample_prompts])

        # Should process all files
        assert len(results) > 0
        assert all(r.status in [ConversionStatus.SUCCESS, ConversionStatus.FAILED] for r in results)

    def test_convert_batch_parallel(self, sample_prompts: Path) -> None:
        """Test parallel batch conversion."""
        config = BatchConfig(parallel=True, max_workers=2, dry_run=True)
        converter = BatchConverter(config, progress_reporter=SimpleProgressReporter(verbose=False))

        results = converter.convert([sample_prompts])

        # Should process all files
        assert len(results) > 0
        assert all(r.status in [ConversionStatus.SUCCESS, ConversionStatus.FAILED] for r in results)

    def test_generate_summary(self, sample_prompts: Path) -> None:
        """Test summary generation."""
        config = BatchConfig()
        converter = BatchConverter(config)

        # Add some mock results
        converter.results = [
            ConversionResult(input_file=Path("file1.txt"), status=ConversionStatus.SUCCESS, validators_used=["JSONValidator"], processing_time=1.5),
            ConversionResult(input_file=Path("file2.txt"), status=ConversionStatus.SUCCESS, validators_used=["ListValidator"], processing_time=0.8),
            ConversionResult(input_file=Path("file3.txt"), status=ConversionStatus.FAILED, error_message="Parse error", processing_time=0.2),
            ConversionResult(input_file=Path("file4.txt"), status=ConversionStatus.SKIPPED, processing_time=0.1),
        ]

        summary = converter.generate_summary()

        assert summary["total_files"] == 4
        assert summary["successful"] == 2
        assert summary["failed"] == 1
        assert summary["skipped"] == 1
        assert summary["total_time"] == 2.6
        assert summary["validators_used"]["JSONValidator"] == 1
        assert summary["validators_used"]["ListValidator"] == 1
        assert len(summary["errors"]) == 1
        assert summary["errors"][0]["file"] == "file3.txt"

    def test_save_report(self, temp_dir: Path) -> None:
        """Test saving conversion report."""
        config = BatchConfig(output_suffix="_generated.py")
        converter = BatchConverter(config)

        # Add a mock result
        converter.results = [
            ConversionResult(input_file=Path("test.txt"), output_file=Path("test_generated.py"), status=ConversionStatus.SUCCESS, task_name="TestTask", validators_used=["RegexValidator"], processing_time=1.23)
        ]

        report_path = temp_dir / "report.json"
        converter.save_report(report_path)

        assert report_path.exists()

        # Load and verify report
        report_data = json.loads(report_path.read_text())

        assert "summary" in report_data
        assert "config" in report_data
        assert "results" in report_data

        assert report_data["summary"]["total_files"] == 1
        assert report_data["summary"]["successful"] == 1

        assert report_data["config"]["output_suffix"] == "_generated.py"

        assert len(report_data["results"]) == 1
        assert report_data["results"][0]["task_name"] == "TestTask"


class TestBatchConfig:
    """Test BatchConfig dataclass."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = BatchConfig()

        assert config.output_dir is None
        assert config.output_suffix == "_task.py"
        assert config.skip_existing is True
        assert config.parallel is True
        assert config.max_workers == 4
        assert config.dry_run is False
        assert config.interactive is False
        assert config.template_name is None
        assert config.common_validators == []
        assert config.file_patterns == ["*.txt", "*.prompt", "*.md"]
        assert config.exclude_patterns == ["*_task.py", "README.md"]

    def test_custom_config(self) -> None:
        """Test custom configuration values."""
        output_dir = Path("/tmp/output")
        config = BatchConfig(
            output_dir=output_dir,
            output_suffix="_gen.py",
            skip_existing=False,
            parallel=False,
            max_workers=8,
            dry_run=True,
            template_name="api_doc",
            common_validators=["JSONValidator", "DateTimeValidator"],
            file_patterns=["*.prompt"],
            exclude_patterns=["test_*"],
        )

        assert config.output_dir == output_dir
        assert config.output_suffix == "_gen.py"
        assert config.skip_existing is False
        assert config.parallel is False
        assert config.max_workers == 8
        assert config.dry_run is True
        assert config.template_name == "api_doc"
        assert config.common_validators == ["JSONValidator", "DateTimeValidator"]
        assert config.file_patterns == ["*.prompt"]
        assert config.exclude_patterns == ["test_*"]
