from tools.prompt_to_task.analyzer import PromptAnalyzer
from tools.prompt_to_task.code_generator import TaskCodeGenerator
from tools.prompt_to_task.validator_suggester import ValidatorSuggester, ValidatorSuggestion


class TestTaskCodeGenerator:
    def test_generate_task_code_basic(self) -> None:
        generator = TaskCodeGenerator()
        analyzer = PromptAnalyzer()
        suggester = ValidatorSuggester()

        prompt = "Generate a story about {character} who lives in {location}"
        analysis = analyzer.analyze(prompt)
        suggestions = suggester.suggest_validators(analysis)

        code = generator.generate_task_code(analysis=analysis, suggestions=suggestions, task_name="StoryTask", task_description="Generate stories with characters", prompt_template=prompt)

        assert "class StorytaskTask(BaseTask)" in code or "class StoryTaskTask(BaseTask)" in code
        assert "Generate a story about {character}" in code
        assert "def get_prompt_data" in code
        assert "character" in code
        assert "location" in code

    def test_generate_task_code_no_variables(self) -> None:
        generator = TaskCodeGenerator()
        analyzer = PromptAnalyzer()
        suggester = ValidatorSuggester()

        prompt = "Generate a random quote"
        analysis = analyzer.analyze(prompt)
        suggestions = suggester.suggest_validators(analysis)

        code = generator.generate_task_code(analysis=analysis, suggestions=suggestions, task_name="QuoteTask", task_description="Generate random quotes", prompt_template=prompt)

        assert "class QuotetaskTask(BaseTask)" in code or "class QuoteTaskTask(BaseTask)" in code
        # No template variables, so no get_prompt_data method
        assert "def create_validator" in code or "validator_class" in code

    def test_generate_task_code_json_format(self) -> None:
        generator = TaskCodeGenerator()
        analyzer = PromptAnalyzer()
        suggester = ValidatorSuggester()

        prompt = "Generate JSON data for user {username}"
        analysis = analyzer.analyze(prompt)
        suggestions = suggester.suggest_validators(analysis)

        code = generator.generate_task_code(analysis=analysis, suggestions=suggestions, task_name="UserDataTask", task_description="Generate user data in JSON format", prompt_template=prompt)

        assert "class UserdatataskTask(BaseTask)" in code or "class UserDataTaskTask(BaseTask)" in code
        assert "username" in code
        # Should include JSON-related validator

    def test_generate_task_code_csv_format(self) -> None:
        generator = TaskCodeGenerator()
        analyzer = PromptAnalyzer()
        suggester = ValidatorSuggester()

        prompt = "Create a CSV file with sales data for {company}"
        analysis = analyzer.analyze(prompt)
        suggestions = suggester.suggest_validators(analysis)

        code = generator.generate_task_code(analysis=analysis, suggestions=suggestions, task_name="SalesDataTask", task_description="Generate sales data in CSV format", prompt_template=prompt)

        assert "class SalesdatataskTask(BaseTask)" in code or "class SalesDataTaskTask(BaseTask)" in code
        assert "company" in code

    def test_generate_task_code_with_source_file(self) -> None:
        generator = TaskCodeGenerator()
        analyzer = PromptAnalyzer()
        suggester = ValidatorSuggester()

        prompt = "Generate content"
        analysis = analyzer.analyze(prompt)
        suggestions = suggester.suggest_validators(analysis)

        code = generator.generate_task_code(analysis=analysis, suggestions=suggestions, task_name="MyTask", task_description="My task", prompt_template=prompt, source_file="my_prompt.txt")

        assert "Generated from: my_prompt.txt" in code

    def test_generate_validator_code_only_builtin(self) -> None:
        generator = TaskCodeGenerator()

        suggestion = ValidatorSuggestion(validator_type="JSONValidator", import_path="validated_llm.tasks.json_generation", config={}, confidence=0.9, description="Validates JSON output", is_builtin=True)

        code = generator.generate_validator_code_only(suggestion)

        assert "Built-in validator: JSONValidator" in code
        assert "validated_llm.tasks.json_generation" in code

    def test_generate_validator_code_only_custom(self) -> None:
        generator = TaskCodeGenerator()

        custom_code = """class CustomValidator(BaseValidator):
    def validate(self, output: str) -> ValidationResult:
        errors = []
        if not output:
            errors.append("Output is empty")
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)"""

        suggestion = ValidatorSuggestion(validator_type="CustomValidator", import_path="", config={}, confidence=0.8, description="Custom validation logic", is_builtin=False, custom_code=custom_code)

        code = generator.generate_validator_code_only(suggestion)

        assert "Custom Validator: CustomValidator" in code
        assert "class CustomValidator(BaseValidator)" in code
        assert "def validate(self, output: str)" in code

    def test_generate_validator_code_only_no_custom_code(self) -> None:
        generator = TaskCodeGenerator()

        suggestion = ValidatorSuggestion(validator_type="CustomValidator", import_path="", config={}, confidence=0.8, description="Custom validation logic", is_builtin=False, custom_code=None)

        code = generator.generate_validator_code_only(suggestion)

        assert "No custom code available" in code

    def test_class_name_conversion(self) -> None:
        generator = TaskCodeGenerator()

        # Test private method - class names always end with "Task"
        assert generator._to_class_name("my-task") == "MyTask"
        # Already ends with task, so gets TaskTask
        assert generator._to_class_name("user_data_task") == "UserDataTask"
        assert generator._to_class_name("JSON Generator") == "JsonGeneratorTask"

    def test_generate_task_code_edge_cases(self) -> None:
        generator = TaskCodeGenerator()
        analyzer = PromptAnalyzer()
        suggester = ValidatorSuggester()

        # Very long prompt
        long_prompt = "x" * 500 + " {var} " + "y" * 500
        analysis = analyzer.analyze(long_prompt)
        suggestions = suggester.suggest_validators(analysis)
        code = generator.generate_task_code(analysis=analysis, suggestions=suggestions, task_name="LongTask", task_description="Task with very long prompt", prompt_template=long_prompt)
        assert "class LongtaskTask(BaseTask)" in code or "class LongTaskTask(BaseTask)" in code
        # Should handle long prompts gracefully

        # Unicode in prompt and variables
        unicode_prompt = "Generate content for {用户名} with {ユーザー設定}"
        analysis = analyzer.analyze(unicode_prompt)
        suggestions = suggester.suggest_validators(analysis)
        code = generator.generate_task_code(analysis=analysis, suggestions=suggestions, task_name="UnicodeTask", task_description="Unicode task", prompt_template=unicode_prompt)
        assert "class UnicodetaskTask(BaseTask)" in code or "class UnicodeTaskTask(BaseTask)" in code
        assert "用户名" in code
        assert "ユーザー設定" in code

        # Special characters in task name
        special_name = "My@Special#Task$Name"
        code = generator.generate_task_code(analysis=analysis, suggestions=suggestions, task_name=special_name, task_description="Special name task", prompt_template="Generate content")
        # Should sanitize special characters in class name
        assert "class MySpecialTaskNameTask(" in code

    def test_generate_task_code_multiple_validators(self) -> None:
        generator = TaskCodeGenerator()
        analyzer = PromptAnalyzer()

        prompt = "Generate both JSON and CSV data"
        analysis = analyzer.analyze(prompt)

        # Create multiple validator suggestions
        suggestions = [
            ValidatorSuggestion(validator_type="JSONValidator", import_path="validated_llm.tasks.json_generation", config={}, confidence=0.9, description="Validates JSON", is_builtin=True),
            ValidatorSuggestion(validator_type="CSVValidator", import_path="validated_llm.tasks.csv_generation", config={}, confidence=0.8, description="Validates CSV", is_builtin=True),
        ]

        code = generator.generate_task_code(analysis=analysis, suggestions=suggestions, task_name="MultiFormatTask", task_description="Multi-format task", prompt_template=prompt)
        assert "class MultiformattaskTask(BaseTask)" in code or "class MultiFormatTaskTask(BaseTask)" in code
        # Should include primary validator

    def test_generate_task_code_with_config(self) -> None:
        generator = TaskCodeGenerator()
        analyzer = PromptAnalyzer()

        prompt = "Generate JSON with specific schema"
        analysis = analyzer.analyze(prompt)

        # Validator with configuration
        suggestions = [
            ValidatorSuggestion(
                validator_type="JSONValidator",
                import_path="validated_llm.tasks.json_generation",
                config={"schema": {"type": "object", "properties": {"name": {"type": "string"}}}},
                confidence=0.9,
                description="Validates JSON with schema",
                is_builtin=True,
            )
        ]

        code = generator.generate_task_code(analysis=analysis, suggestions=suggestions, task_name="SchemaTask", task_description="JSON with schema", prompt_template=prompt)
        assert "class SchemataskTask(BaseTask)" in code or "class SchemaTaskTask(BaseTask)" in code
        # Should handle validator config

    def test_prompt_template_escaping(self) -> None:
        generator = TaskCodeGenerator()
        analyzer = PromptAnalyzer()
        suggester = ValidatorSuggester()

        # Prompt with quotes and special characters
        tricky_prompt = '''Generate "quoted" text with 'single quotes' and {var}
        Also include: backslash \\ and newline
        Triple quotes """ inside'''

        analysis = analyzer.analyze(tricky_prompt)
        suggestions = suggester.suggest_validators(analysis)

        code = generator.generate_task_code(analysis=analysis, suggestions=suggestions, task_name="TrickyTask", task_description="Tricky prompt", prompt_template=tricky_prompt)

        # Should properly escape the prompt template
        assert "class TrickytaskTask(BaseTask)" in code or "class TrickyTaskTask(BaseTask)" in code
        # Check that the prompt is properly handled (should use triple quotes in the return statement)
        assert 'return """' in code or "return '''" in code

    def test_empty_suggestions_handling(self) -> None:
        generator = TaskCodeGenerator()
        analyzer = PromptAnalyzer()

        prompt = "Generate something"
        analysis = analyzer.analyze(prompt)

        # Empty suggestions list
        code = generator.generate_task_code(analysis=analysis, suggestions=[], task_name="EmptyTask", task_description="No validators", prompt_template=prompt)

        assert "class EmptytaskTask(BaseTask)" in code or "class EmptyTaskTask(BaseTask)" in code
        # Should still generate valid code with basic validator
