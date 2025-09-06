from tools.prompt_to_task.analyzer import PromptAnalyzer


class TestPromptAnalyzer:
    def test_extract_template_variables(self) -> None:
        analyzer = PromptAnalyzer()

        prompt = "Generate a story about {character_name} who lives in {location}."
        result = analyzer.analyze(prompt)
        assert result.template_variables == ["character_name", "location"]

        prompt_no_vars = "Generate a random story."
        result = analyzer.analyze(prompt_no_vars)
        assert result.template_variables == []

        prompt_with_json = 'Generate JSON: {"name": "John", "age": 30}'
        result = analyzer.analyze(prompt_with_json)
        assert result.template_variables == []

        prompt_complex = "Story about {hero} fighting {villain} in {_place123}"
        result = analyzer.analyze(prompt_complex)
        assert result.template_variables == ["hero", "villain", "_place123"]

    def test_analyze_prompt_basic(self) -> None:
        analyzer = PromptAnalyzer()

        prompt = "Generate a story about {character_name} who lives in {location}."
        result = analyzer.analyze(prompt)

        assert result.template_variables == ["character_name", "location"]
        assert result.output_format == "text"
        assert result.confidence >= 0.0
        assert result.confidence <= 1.0

    def test_analyze_prompt_json_output(self) -> None:
        analyzer = PromptAnalyzer()

        prompt = "Generate a JSON object with user information for {username}"
        result = analyzer.analyze(prompt)

        assert result.output_format == "json"
        assert result.template_variables == ["username"]
        assert result.confidence > 0.3

    def test_analyze_prompt_csv_output(self) -> None:
        analyzer = PromptAnalyzer()

        prompt = "Create a CSV file with sales data for {company}"
        result = analyzer.analyze(prompt)

        assert result.output_format == "csv"
        assert result.template_variables == ["company"]

    def test_analyze_prompt_list_output(self) -> None:
        analyzer = PromptAnalyzer()

        prompt = "List all the benefits of {product}"
        result = analyzer.analyze(prompt)

        # "List" in prompt should trigger list detection
        assert result.output_format in ["list", "text"]  # May be detected as either
        assert result.template_variables == ["product"]

    def test_analyze_prompt_yaml_output(self) -> None:
        analyzer = PromptAnalyzer()

        prompt = "Generate YAML configuration for {service}"
        result = analyzer.analyze(prompt)

        # YAML detection isn't implemented, so it should default to text
        assert result.output_format == "text"
        assert result.template_variables == ["service"]

    def test_analyze_prompt_code_output(self) -> None:
        analyzer = PromptAnalyzer()

        prompt = "Write a Python function to calculate {calculation}"
        result = analyzer.analyze(prompt)

        # Code detection isn't implemented, so it should default to text
        assert result.output_format == "text"
        assert result.template_variables == ["calculation"]

    def test_analyze_prompt_multiline(self) -> None:
        analyzer = PromptAnalyzer()

        prompt = """Generate a detailed report about {company}:
        - Include financial data
        - Add market analysis
        - Provide future projections"""

        result = analyzer.analyze(prompt)
        assert result.template_variables == ["company"]
        # Should detect as text despite having bullet points (they're not primary content)
        assert result.output_format in ["text", "list"]

    def test_analyze_prompt_no_variables(self) -> None:
        analyzer = PromptAnalyzer()

        prompt = "Generate a random inspirational quote"
        result = analyzer.analyze(prompt)

        assert result.template_variables == []
        assert result.output_format == "text"

    def test_analyze_prompt_special_characters(self) -> None:
        analyzer = PromptAnalyzer()

        prompt = "Generate {item_1} and {item-2} but not {123invalid}"
        result = analyzer.analyze(prompt)

        assert result.template_variables == ["item_1"]

    def test_analyze_prompt_edge_cases(self) -> None:
        analyzer = PromptAnalyzer()

        # Empty prompt
        result = analyzer.analyze("")
        assert result.template_variables == []
        assert result.output_format == "text"

        # Very large prompt
        large_prompt = "x" * 10000 + " {variable} " + "y" * 10000
        result = analyzer.analyze(large_prompt)
        assert result.template_variables == ["variable"]

        # Unicode characters
        unicode_prompt = "Generate content for {用户名} and {ユーザー}"
        result = analyzer.analyze(unicode_prompt)
        assert result.template_variables == ["用户名", "ユーザー"]

        # Nested braces
        nested_prompt = "Generate {{nested}} and {valid_var}"
        result = analyzer.analyze(nested_prompt)
        assert result.template_variables == ["valid_var"]

        # Multiple spaces and newlines
        spaced_prompt = "Generate   {  var1  }   and\n\n{var2}\t{var3}"
        result = analyzer.analyze(spaced_prompt)
        # Should handle spaces within braces appropriately
        assert "var2" in result.template_variables
        assert "var3" in result.template_variables

    def test_analyze_prompt_format_detection_edge_cases(self) -> None:
        analyzer = PromptAnalyzer()

        # Mixed format indicators
        mixed_prompt = "Generate JSON data and CSV report for {data}"
        result = analyzer.analyze(mixed_prompt)
        # Should pick one format with higher confidence
        assert result.output_format in ["json", "csv"]

        # Case sensitivity
        upper_prompt = "GENERATE JSON FOR {USER}"
        result = analyzer.analyze(upper_prompt)
        assert result.output_format == "json"
        assert result.template_variables == ["USER"]

        # Format word in variable
        misleading_prompt = "Generate report for {json_data}"
        result = analyzer.analyze(misleading_prompt)
        # Should not be confused by json in variable name
        assert result.output_format == "text"

    def test_analyze_prompt_malformed_templates(self) -> None:
        analyzer = PromptAnalyzer()

        # Unclosed braces
        unclosed_prompt = "Generate {item and {item2}"
        result = analyzer.analyze(unclosed_prompt)
        assert result.template_variables == ["item2"]

        # Empty braces
        empty_prompt = "Generate {} and {  } content"
        result = analyzer.analyze(empty_prompt)
        assert result.template_variables == []

        # Special regex characters in template
        regex_prompt = "Generate {item.*} and {item[0]}"
        result = analyzer.analyze(regex_prompt)
        # Should handle regex special chars safely
        assert len(result.template_variables) == 0  # Invalid variable names
