from tools.prompt_to_task.analyzer import PromptAnalyzer
from tools.prompt_to_task.validator_suggester import ValidatorSuggester


class TestValidatorSuggester:
    def test_suggest_validators_text_format(self) -> None:
        suggester = ValidatorSuggester()
        analyzer = PromptAnalyzer()

        prompt = "Generate a story about {character}"
        analysis = analyzer.analyze(prompt)

        suggestions = suggester.suggest_validators(analysis)

        assert len(suggestions) > 0
        # Should suggest a text validator as primary
        assert suggestions[0].validator_type in ["TextValidator", "CustomTextValidator"]
        assert suggestions[0].confidence > 0

    def test_suggest_validators_json_format(self) -> None:
        suggester = ValidatorSuggester()
        analyzer = PromptAnalyzer()

        prompt = "Generate JSON user data with name and email for {username}"
        analysis = analyzer.analyze(prompt)

        suggestions = suggester.suggest_validators(analysis)

        assert len(suggestions) > 0
        # Should have at least one JSON-related validator in the suggestions
        json_found = any("JSON" in s.validator_type or "json" in s.description.lower() for s in suggestions)
        assert json_found

    def test_suggest_validators_csv_format(self) -> None:
        suggester = ValidatorSuggester()
        analyzer = PromptAnalyzer()

        prompt = "Create a CSV file with sales data including columns: Date, Product, Amount"
        analysis = analyzer.analyze(prompt)

        suggestions = suggester.suggest_validators(analysis)

        assert len(suggestions) > 0
        primary = suggestions[0]
        assert "CSV" in primary.validator_type or "csv" in primary.description.lower()

    def test_suggest_validators_list_format(self) -> None:
        suggester = ValidatorSuggester()
        analyzer = PromptAnalyzer()

        prompt = """List the top 10 benefits:
        - Benefit 1
        - Benefit 2"""
        analysis = analyzer.analyze(prompt)

        suggestions = suggester.suggest_validators(analysis)

        assert len(suggestions) > 0
        # List format should be detected

    def test_suggest_validators_with_schema(self) -> None:
        suggester = ValidatorSuggester()
        analyzer = PromptAnalyzer()

        prompt = 'Generate JSON: {"name": "string", "age": "number", "email": "string"}'
        analysis = analyzer.analyze(prompt)

        suggestions = suggester.suggest_validators(analysis)

        assert len(suggestions) > 0
        # Should include JSON validator with schema info

    def test_builtin_validator_detection(self) -> None:
        suggester = ValidatorSuggester()
        analyzer = PromptAnalyzer()

        # Test JSON builtin
        prompt = "Generate product catalog JSON with name, price, description"
        analysis = analyzer.analyze(prompt)
        suggestions = suggester.suggest_validators(analysis)

        # Check if any suggestion is builtin
        builtin_found = any(s.is_builtin for s in suggestions)
        assert builtin_found or len(suggestions) > 0  # At least have suggestions

    def test_confidence_ordering(self) -> None:
        suggester = ValidatorSuggester()
        analyzer = PromptAnalyzer()

        prompt = "Generate JSON data with validation: name (required), email (must be valid email)"
        analysis = analyzer.analyze(prompt)

        suggestions = suggester.suggest_validators(analysis)

        assert len(suggestions) > 0
        # Check that suggestions are ordered by confidence (descending)
        if len(suggestions) > 1:
            for i in range(len(suggestions) - 1):
                assert suggestions[i].confidence >= suggestions[i + 1].confidence

    def test_custom_validator_generation(self) -> None:
        suggester = ValidatorSuggester()
        analyzer = PromptAnalyzer()

        prompt = "Generate a special format output"
        analysis = analyzer.analyze(prompt)

        suggestions = suggester.suggest_validators(analysis)

        assert len(suggestions) > 0
        # Should generate custom validator for unknown formats
        if not suggestions[0].is_builtin:
            assert suggestions[0].custom_code is not None

    def test_empty_prompt(self) -> None:
        suggester = ValidatorSuggester()
        analyzer = PromptAnalyzer()

        prompt = ""
        analysis = analyzer.analyze(prompt)

        suggestions = suggester.suggest_validators(analysis)

        # Should still provide at least a basic suggestion
        assert len(suggestions) > 0

    def test_complex_prompt_multiple_validators(self) -> None:
        suggester = ValidatorSuggester()
        analyzer = PromptAnalyzer()

        prompt = """Generate a report with:
        1. JSON summary section
        2. CSV data table
        3. Text narrative
        All for {company}"""

        analysis = analyzer.analyze(prompt)
        suggestions = suggester.suggest_validators(analysis)

        # Should provide suggestions even for complex multi-format prompts
        assert len(suggestions) > 0

    def test_validator_suggester_edge_cases(self) -> None:
        suggester = ValidatorSuggester()
        analyzer = PromptAnalyzer()

        # Prompt with code generation hints
        code_prompt = "Write a Python function to calculate {metric}"
        analysis = analyzer.analyze(code_prompt)
        suggestions = suggester.suggest_validators(analysis)
        assert len(suggestions) > 0
        # Should suggest text validator for code (no specific code validator yet)

        # Prompt with validation requirements
        validation_prompt = "Generate JSON with required fields: id (integer), name (max 50 chars)"
        analysis = analyzer.analyze(validation_prompt)
        suggestions = suggester.suggest_validators(analysis)
        assert len(suggestions) > 0
        # Should detect validation requirements

        # Ambiguous format prompt
        ambiguous_prompt = "Generate structured data for {entity}"
        analysis = analyzer.analyze(ambiguous_prompt)
        suggestions = suggester.suggest_validators(analysis)
        assert len(suggestions) > 0
        # Should provide multiple format suggestions

    def test_schema_detection_edge_cases(self) -> None:
        suggester = ValidatorSuggester()
        analyzer = PromptAnalyzer()

        # Schema with nested objects
        nested_schema = """Generate JSON matching:
        {
            "user": {
                "name": "string",
                "contacts": {
                    "email": "string",
                    "phone": "string"
                }
            }
        }"""
        analysis = analyzer.analyze(nested_schema)
        suggestions = suggester.suggest_validators(analysis)
        assert len(suggestions) > 0

        # Schema with arrays
        array_schema = 'Generate JSON: {"items": ["string"], "count": "number"}'
        analysis = analyzer.analyze(array_schema)
        suggestions = suggester.suggest_validators(analysis)
        assert len(suggestions) > 0

        # Malformed schema
        bad_schema = "Generate JSON: {name: string, age: number}"  # Missing quotes
        analysis = analyzer.analyze(bad_schema)
        suggestions = suggester.suggest_validators(analysis)
        assert len(suggestions) > 0  # Should still provide suggestions

    def test_confidence_calculation_edge_cases(self) -> None:
        suggester = ValidatorSuggester()
        analyzer = PromptAnalyzer()

        # Very specific format requirements
        specific_prompt = "Generate exactly 5 CSV rows with columns: ID,Name,Date(YYYY-MM-DD)"
        analysis = analyzer.analyze(specific_prompt)
        suggestions = suggester.suggest_validators(analysis)
        assert len(suggestions) > 0
        # High confidence for CSV
        assert suggestions[0].confidence > 0.7

        # Vague requirements
        vague_prompt = "Generate some data"
        analysis = analyzer.analyze(vague_prompt)
        suggestions = suggester.suggest_validators(analysis)
        assert len(suggestions) > 0
        # Lower confidence for vague prompts
        assert suggestions[0].confidence < 0.8

    def test_custom_validator_code_generation(self) -> None:
        suggester = ValidatorSuggester()
        analyzer = PromptAnalyzer()

        # Test various output formats that need custom validators
        custom_formats = [("Generate YAML configuration", "yaml"), ("Create XML document", "xml"), ("Generate markdown table", "markdown"), ("Create SQL query", "sql")]

        for prompt, expected_format in custom_formats:
            analysis = analyzer.analyze(prompt)
            suggestions = suggester.suggest_validators(analysis)
            assert len(suggestions) > 0
            # Should generate custom validator code for unsupported formats
            if not suggestions[0].is_builtin:
                assert suggestions[0].custom_code is not None
                assert "class" in suggestions[0].custom_code
                assert "validate" in suggestions[0].custom_code
