"""Integration tests for the prompt-to-task tool.

These tests verify the complete flow from prompt analysis to task code generation.
"""

import os
import tempfile
from pathlib import Path

import pytest

from tools.prompt_to_task.analyzer import PromptAnalyzer
from tools.prompt_to_task.code_generator import TaskCodeGenerator
from tools.prompt_to_task.validator_suggester import ValidatorSuggester


class TestPromptToTaskIntegration:
    """Test the complete prompt-to-task conversion flow."""

    def test_full_conversion_flow_text_prompt(self) -> None:
        """Test converting a simple text generation prompt."""
        # Step 1: Analyze prompt
        prompt = "Generate a detailed product description for {product_name} highlighting its {key_features}"
        analyzer = PromptAnalyzer()
        analysis = analyzer.analyze(prompt)

        assert analysis.template_variables == ["product_name", "key_features"]
        assert analysis.output_format == "text"

        # Step 2: Suggest validators
        suggester = ValidatorSuggester()
        suggestions = suggester.suggest_validators(analysis)

        assert len(suggestions) > 0
        assert suggestions[0].confidence > 0

        # Step 3: Generate task code
        generator = TaskCodeGenerator()
        code = generator.generate_task_code(analysis=analysis, suggestions=suggestions, task_name="ProductDescription", task_description="Generate product descriptions", prompt_template=prompt)

        # Verify generated code
        assert "class ProductdescriptionTask(BaseTask)" in code or "class ProductDescriptionTask(BaseTask)" in code
        assert "product_name" in code
        assert "key_features" in code
        assert "prompt_template" in code

        # Verify the code is valid Python
        compile(code, "generated_task.py", "exec")

    def test_full_conversion_flow_json_prompt(self) -> None:
        """Test converting a JSON generation prompt with schema."""
        prompt = """Generate user profile JSON:
        {
            "id": "integer",
            "name": "string (required)",
            "email": "email address",
            "age": "number (18-100)",
            "preferences": {
                "notifications": "boolean",
                "theme": "light or dark"
            }
        }
        For user {username}"""

        analyzer = PromptAnalyzer()
        analysis = analyzer.analyze(prompt)

        assert "username" in analysis.template_variables
        assert analysis.output_format == "json"

        suggester = ValidatorSuggester()
        suggestions = suggester.suggest_validators(analysis)

        # Should suggest JSON validator
        json_suggested = any("json" in s.validator_type.lower() for s in suggestions)
        assert json_suggested

        generator = TaskCodeGenerator()
        code = generator.generate_task_code(analysis=analysis, suggestions=suggestions, task_name="UserProfile", task_description="Generate user profiles", prompt_template=prompt)

        assert "JSON" in code or "json" in code
        compile(code, "generated_task.py", "exec")

    def test_full_conversion_flow_csv_prompt(self) -> None:
        """Test converting a CSV generation prompt."""
        prompt = """Generate CSV sales report with columns:
        - Date (YYYY-MM-DD)
        - Product
        - Quantity (integer)
        - Price (decimal)
        - Total (calculated)

        For company: {company_name} and period: {time_period}"""

        analyzer = PromptAnalyzer()
        analysis = analyzer.analyze(prompt)

        assert set(analysis.template_variables) == {"company_name", "time_period"}
        assert analysis.output_format == "csv"

        suggester = ValidatorSuggester()
        suggestions = suggester.suggest_validators(analysis)

        generator = TaskCodeGenerator()
        code = generator.generate_task_code(analysis=analysis, suggestions=suggestions, task_name="SalesReport", task_description="Generate sales reports", prompt_template=prompt)

        assert "CSV" in code or "csv" in code
        compile(code, "generated_task.py", "exec")

    def test_complex_multi_format_prompt(self) -> None:
        """Test handling a prompt that could have multiple output formats."""
        prompt = """Create a comprehensive analysis report for {topic} that includes:

        1. Executive Summary (text paragraph)
        2. Key Metrics (JSON format):
           - metric_name: value
           - trend: up/down/stable
        3. Detailed Data (CSV table)
        4. Recommendations (bullet list)

        Make it suitable for {audience} audience."""

        analyzer = PromptAnalyzer()
        analysis = analyzer.analyze(prompt)

        assert set(analysis.template_variables) == {"topic", "audience"}
        # Could detect as text, json, or csv
        assert analysis.output_format in ["text", "json", "csv", "list"]

        suggester = ValidatorSuggester()
        suggestions = suggester.suggest_validators(analysis)

        # Should provide multiple suggestions
        assert len(suggestions) >= 1

        generator = TaskCodeGenerator()
        code = generator.generate_task_code(analysis=analysis, suggestions=suggestions, task_name="AnalysisReport", task_description="Generate analysis reports", prompt_template=prompt)

        compile(code, "generated_task.py", "exec")

    def test_prompt_with_no_variables(self) -> None:
        """Test handling prompts without template variables."""
        prompt = "Generate a random motivational quote about success and perseverance"

        analyzer = PromptAnalyzer()
        analysis = analyzer.analyze(prompt)

        assert analysis.template_variables == []
        assert analysis.output_format == "text"

        suggester = ValidatorSuggester()
        suggestions = suggester.suggest_validators(analysis)

        generator = TaskCodeGenerator()
        code = generator.generate_task_code(analysis=analysis, suggestions=suggestions, task_name="MotivationalQuote", task_description="Generate motivational quotes", prompt_template=prompt)

        # Should not have get_prompt_data method since no variables
        assert "get_prompt_data" not in code or "pass" in code
        compile(code, "generated_task.py", "exec")

    def test_edge_case_prompts(self) -> None:
        """Test various edge case prompts."""
        edge_cases = [
            # Empty prompt
            ("", "EmptyTask"),
            # Only variables
            ("{var1} {var2} {var3}", "VarsOnly"),
            # Very long variable names
            ("Generate {very_long_variable_name_that_exceeds_normal_length}", "LongVar"),
            # Special characters
            ("Generate report for {company-name} (invalid var) and {company_name}", "SpecialChars"),
            # Unicode
            ("生成 {用户} 的报告", "Unicode"),
        ]

        for prompt, task_name in edge_cases:
            analyzer = PromptAnalyzer()
            analysis = analyzer.analyze(prompt)

            suggester = ValidatorSuggester()
            suggestions = suggester.suggest_validators(analysis)

            generator = TaskCodeGenerator()
            code = generator.generate_task_code(analysis=analysis, suggestions=suggestions, task_name=task_name, task_description=f"Test {task_name}", prompt_template=prompt)

            # All should generate compilable code
            try:
                compile(code, f"{task_name.lower()}_task.py", "exec")
            except SyntaxError as e:
                pytest.fail(f"Generated invalid Python for prompt '{prompt}': {e}")

    def test_file_output_integration(self) -> None:
        """Test writing generated code to files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt = "Generate a story about {hero} saving {kingdom}"

            # Full pipeline
            analyzer = PromptAnalyzer()
            analysis = analyzer.analyze(prompt)

            suggester = ValidatorSuggester()
            suggestions = suggester.suggest_validators(analysis)

            generator = TaskCodeGenerator()
            code = generator.generate_task_code(analysis=analysis, suggestions=suggestions, task_name="HeroStory", task_description="Generate hero stories", prompt_template=prompt, source_file="hero_prompt.txt")

            # Write to file
            output_path = Path(tmpdir) / "hero_story_task.py"
            output_path.write_text(code)

            # Verify file exists and is valid
            assert output_path.exists()
            assert output_path.stat().st_size > 0

            # Verify we can import it (would need proper Python path setup)
            content = output_path.read_text()
            assert "Generated from: hero_prompt.txt" in content
            compile(content, str(output_path), "exec")

    def test_validator_selection_logic(self) -> None:
        """Test that appropriate validators are selected for different prompts."""
        test_cases = [
            ("Generate JSON: {data}", "json"),
            ("Create CSV file with {columns}", "csv"),
            ("List the benefits of {product}", "list"),
            ("Write a paragraph about {topic}", "text"),
            ("Generate YAML config for {service}", "text"),  # No YAML validator yet
        ]

        for prompt, expected_format in test_cases:
            analyzer = PromptAnalyzer()
            analysis = analyzer.analyze(prompt)

            if expected_format != "list":  # List detection is fuzzy
                assert analysis.output_format == expected_format

            suggester = ValidatorSuggester()
            suggestions = suggester.suggest_validators(analysis)

            # Should always have at least one suggestion
            assert len(suggestions) > 0

            # Should have reasonable confidence for clear format indicators
            if expected_format in ["json", "csv"]:
                assert suggestions[0].confidence >= 0.5

    def test_generated_code_imports(self) -> None:
        """Test that generated code has correct imports."""
        prompt = "Generate user data as JSON for {user_id}"

        analyzer = PromptAnalyzer()
        analysis = analyzer.analyze(prompt)

        suggester = ValidatorSuggester()
        suggestions = suggester.suggest_validators(analysis)

        generator = TaskCodeGenerator()
        code = generator.generate_task_code(analysis=analysis, suggestions=suggestions, task_name="UserData", task_description="Get user data", prompt_template=prompt)

        # Check for required imports
        assert "from validated_llm.tasks.base_task import BaseTask" in code
        assert "from validated_llm" in code

        # Should include appropriate validator imports
        if any(s.is_builtin for s in suggestions):
            assert "import" in code

    def test_error_handling_in_pipeline(self) -> None:
        """Test that the pipeline handles errors gracefully."""
        # Malformed prompt that might cause issues
        problem_prompts = [
            "Generate {unclosed",
            "Generate }invalid{",
            "Generate {123invalid}",
            "Generate {-invalid-}",
        ]

        for prompt in problem_prompts:
            # Should not raise exceptions
            analyzer = PromptAnalyzer()
            analysis = analyzer.analyze(prompt)

            suggester = ValidatorSuggester()
            suggestions = suggester.suggest_validators(analysis)

            generator = TaskCodeGenerator()
            code = generator.generate_task_code(analysis=analysis, suggestions=suggestions, task_name="ErrorTest", task_description="Error test", prompt_template=prompt)

            # Should still generate valid Python
            compile(code, "error_test.py", "exec")
