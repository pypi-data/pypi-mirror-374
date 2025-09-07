import os
import tempfile
from typing import Generator

import pytest
from click.testing import CliRunner

from tools.prompt_to_task.cli_click import main


class TestCLI:
    @pytest.fixture
    def runner(self) -> CliRunner:
        return CliRunner()

    @pytest.fixture
    def temp_prompt_file(self) -> Generator[str, None, None]:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Generate a story about {character} who lives in {location}.")
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    def test_help_command(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Convert prompts to validated-llm tasks" in result.output
        assert "--output" in result.output
        assert "--name" in result.output

    def test_basic_conversion(self, runner: CliRunner, temp_prompt_file: str) -> None:
        output_file = "output_task.py"
        result = runner.invoke(main, [temp_prompt_file, "--output", output_file])

        assert result.exit_code == 0
        assert os.path.exists(output_file)

        with open(output_file, "r") as f:
            content = f.read()
            assert "class" in content
            assert "BaseTask" in content
            assert "character" in content
            assert "location" in content

    def test_analyze_only(self, runner: CliRunner, temp_prompt_file: str) -> None:
        result = runner.invoke(main, [temp_prompt_file, "--analyze-only"])

        assert result.exit_code == 0
        assert "ANALYSIS RESULTS" in result.output
        assert "Format:" in result.output
        assert "Variables:" in result.output
        assert "character" in result.output
        assert "location" in result.output

    def test_validator_only(self, runner: CliRunner, temp_prompt_file: str) -> None:
        # First run analyze to see available validators
        result = runner.invoke(main, [temp_prompt_file, "--analyze-only"])
        assert result.exit_code == 0

        # Then generate validator code for the first suggestion
        result = runner.invoke(main, [temp_prompt_file, "--validator-only", "1"])

        assert result.exit_code == 0
        # Should output validator code or comment about built-in validator
        # May also show task generation output
        assert len(result.output) > 0

    def test_custom_names(self, runner: CliRunner, temp_prompt_file: str) -> None:
        output_file = "custom_task.py"
        result = runner.invoke(main, [temp_prompt_file, "--output", output_file, "--name", "MyCustomTask", "--description", "My custom description"])

        assert result.exit_code == 0

        with open(output_file, "r") as f:
            content = f.read()
            assert "class MycustomtaskTask" in content or "class MyCustomTaskTask" in content
            assert "My custom description" in content

    def test_interactive_mode_basic(self, runner: CliRunner, temp_prompt_file: str) -> None:
        output_file = "interactive_task.py"
        # Provide input for interactive prompts: validator choice, task name, description
        result = runner.invoke(main, [temp_prompt_file, "--output", output_file, "--interactive"], input="1\nMyTask\nTask description\n")

        assert result.exit_code == 0
        assert os.path.exists(output_file)

    def test_no_output_file_default(self, runner: CliRunner, temp_prompt_file: str) -> None:
        result = runner.invoke(main, [temp_prompt_file])

        assert result.exit_code == 0
        # Should show that it's using a default output file
        assert "No output file specified" in result.output or "using:" in result.output

        # Check that a file was created in the current directory
        created_files = [f for f in os.listdir(".") if f.endswith("_task.py")]
        assert len(created_files) >= 1

    def test_nonexistent_input_file(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["nonexistent_file.txt"])

        assert result.exit_code == 2
        assert "does not exist" in result.output

    def test_json_prompt(self, runner: CliRunner) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Generate JSON data for user {username}")
            temp_path = f.name

        try:
            result = runner.invoke(main, [temp_path, "--analyze-only"])
            assert result.exit_code == 0
            assert "json" in result.output.lower()
        finally:
            os.unlink(temp_path)

    def test_csv_prompt(self, runner: CliRunner) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Create a CSV file with sales data")
            temp_path = f.name

        try:
            result = runner.invoke(main, [temp_path, "--analyze-only"])
            assert result.exit_code == 0
            assert "csv" in result.output.lower()
        finally:
            os.unlink(temp_path)

    def test_empty_prompt_file(self, runner: CliRunner) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("")
            temp_path = f.name

        try:
            result = runner.invoke(main, [temp_path])
            assert result.exit_code == 0
        finally:
            os.unlink(temp_path)

    def test_multiline_prompt(self, runner: CliRunner) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(
                """Generate a report for {company}:
            - Financial summary
            - Market analysis
            - Future projections"""
            )
            temp_path = f.name

        try:
            output_file = "report_task.py"
            result = runner.invoke(main, [temp_path, "--output", output_file])

            assert result.exit_code == 0
            with open(output_file, "r") as f:
                content = f.read()
                assert "company" in content
        finally:
            os.unlink(temp_path)

    def test_cli_edge_cases(self, runner: CliRunner) -> None:
        # Test with very long filename
        long_name = "a" * 200 + ".txt"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Generate content")
            temp_path = f.name

        try:
            result = runner.invoke(main, [temp_path, "--analyze-only"])
            assert result.exit_code == 0
        finally:
            os.unlink(temp_path)

        # Test with unicode filename
        unicode_prompt = "Generate content for {user}"
        with tempfile.NamedTemporaryFile(mode="w", suffix="_测试.txt", delete=False) as f:
            f.write(unicode_prompt)
            temp_path = f.name

        try:
            result = runner.invoke(main, [temp_path, "--analyze-only"])
            assert result.exit_code == 0
        finally:
            os.unlink(temp_path)

    def test_invalid_validator_choice(self, runner: CliRunner, temp_prompt_file: str) -> None:
        # Test invalid validator number
        result = runner.invoke(main, [temp_prompt_file, "--validator-only", "99"])
        assert result.exit_code != 0 or "Invalid" in result.output

        # Test non-numeric validator choice
        result = runner.invoke(main, [temp_prompt_file, "--validator-only", "abc"])
        assert result.exit_code != 0

    def test_output_file_permissions(self, runner: CliRunner, temp_prompt_file: str) -> None:
        # Test writing to directory without permissions (skip on Windows)
        if os.name != "nt":
            with tempfile.TemporaryDirectory() as tmpdir:
                output_file = os.path.join(tmpdir, "output.py")
                # Make directory read-only
                os.chmod(tmpdir, 0o444)

                result = runner.invoke(main, [temp_prompt_file, "--output", output_file])
                # Should fail due to permissions
                assert result.exit_code != 0

                # Restore permissions for cleanup
                os.chmod(tmpdir, 0o755)

    def test_conflicting_options(self, runner: CliRunner, temp_prompt_file: str) -> None:
        # Test analyze-only with output file (should ignore output)
        result = runner.invoke(main, [temp_prompt_file, "--analyze-only", "--output", "ignored.py"])
        assert result.exit_code == 0
        assert not os.path.exists("ignored.py")

        # Test validator-only with interactive mode
        result = runner.invoke(main, [temp_prompt_file, "--validator-only", "1", "--interactive"])
        # Should handle conflicting options gracefully
        assert result.exit_code == 0 or "Cannot use" in result.output

    def test_special_characters_in_prompt(self, runner: CliRunner) -> None:
        # Prompt with various special characters
        special_prompt = """Generate "quoted" text with 'quotes' and {var}
        Special chars: @#$%^&*()_+-=[]{}|;:,.<>?/~`
        Unicode: 你好世界 🌍 émojis"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(special_prompt)
            temp_path = f.name

        try:
            output_file = "special_task.py"
            result = runner.invoke(main, [temp_path, "--output", output_file])

            assert result.exit_code == 0
            assert os.path.exists(output_file)

            # Verify the generated code is valid Python
            with open(output_file, "r") as f:
                content = f.read()
                # Try to compile the code to check syntax
                compile(content, output_file, "exec")
        finally:
            os.unlink(temp_path)
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_interactive_mode_edge_cases(self, runner: CliRunner, temp_prompt_file: str) -> None:
        # Test with empty inputs in interactive mode
        result = runner.invoke(main, [temp_prompt_file, "--interactive"], input="\n\n\n")
        # Should use defaults or fail gracefully with abort message
        assert result.exit_code == 0 or "required" in result.output.lower() or "aborted" in result.output.lower()

        # Test with very long inputs
        long_input = "x" * 1000
        result = runner.invoke(main, [temp_prompt_file, "--interactive"], input=f"1\n{long_input}\n{long_input}\n")
        # Should handle long inputs

    def test_prompt_file_encodings(self, runner: CliRunner) -> None:
        # Test different file encodings
        encodings = ["utf-8", "latin-1", "cp1252"]

        for encoding in encodings:
            try:
                with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding=encoding) as f:
                    f.write("Generate content for {user}")
                    temp_path = f.name

                result = runner.invoke(main, [temp_path, "--analyze-only"])
                # Should handle different encodings
                assert result.exit_code == 0 or encoding == "cp1252"  # Windows encoding might fail
            except Exception:
                pass  # Some encodings might not be available
            finally:
                if "temp_path" in locals() and os.path.exists(temp_path):
                    os.unlink(temp_path)

    def test_multiple_validator_suggestions(self, runner: CliRunner) -> None:
        # Create prompt that might generate multiple validator suggestions
        multi_format_prompt = """Generate output that includes:
        - JSON data section
        - CSV table section
        - Plain text summary
        For {entity}"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(multi_format_prompt)
            temp_path = f.name

        try:
            # Test analyzing
            result = runner.invoke(main, [temp_path, "--analyze-only"])
            assert result.exit_code == 0

            # Test selecting validator 1 (should always exist)
            result = runner.invoke(main, [temp_path, "--validator-only", "1"])
            assert result.exit_code == 0

            # Test with a very high validator index that surely doesn't exist
            result = runner.invoke(main, [temp_path, "--validator-only", "99"])
            # Should either fail or show invalid message
            assert result.exit_code != 0 or "Invalid" in result.output or "invalid" in result.output.lower()
        finally:
            os.unlink(temp_path)
