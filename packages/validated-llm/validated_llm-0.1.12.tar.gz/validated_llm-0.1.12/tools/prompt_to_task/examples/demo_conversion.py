"""
Demo script for the prompt-to-task conversion tool.

This script demonstrates how to use the tool programmatically
with various prompt patterns (JSON, CSV, lists, etc).
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.prompt_to_task.analyzer import PromptAnalyzer
from tools.prompt_to_task.code_generator import TaskCodeGenerator
from tools.prompt_to_task.validator_suggester import ValidatorSuggester


def test_json_prompt() -> None:
    """Test JSON prompt conversion."""
    print("🧪 Testing JSON Prompt Conversion")
    print("=" * 40)

    prompt = """
Generate a JSON object for a product with the following details:

Product Name: {product_name}
Price: {price}
Category: {category}
Description: {description}

Output format:
{
    "id": "unique_id",
    "name": "product name",
    "price": 29.99,
    "category": "electronics",
    "description": "product description",
    "in_stock": true
}

Requirements:
- Price must be a positive number
- Category must be one of: electronics, clothing, books, home
- Description minimum 10 characters
"""

    # Analyze prompt
    analyzer = PromptAnalyzer()
    analysis = analyzer.analyze(prompt)

    print(f"📊 Detected format: {analysis.output_format} (confidence: {analysis.confidence:.1%})")
    print(f"🔗 Template variables: {analysis.template_variables}")
    print(f"📋 JSON schema found: {bool(analysis.json_schema)}")

    # Get suggestions
    suggester = ValidatorSuggester()
    suggestions = suggester.suggest_validators(analysis)

    print(f"💡 Validator suggestions: {len(suggestions)}")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion.validator_type} ({suggestion.confidence:.1%})")

    # Generate code
    generator = TaskCodeGenerator()
    code = generator.generate_task_code(
        analysis=analysis, suggestions=suggestions[:1], task_name="Product JSON Generation", task_description="Generate JSON objects for product data", prompt_template=prompt, source_file="demo_json_prompt.txt"
    )

    print(f"\n📝 Generated {len(code.split(chr(10)))} lines of code")
    print("✅ JSON prompt test completed")


def test_csv_prompt() -> None:
    """Test CSV prompt conversion."""
    print("\n🧪 Testing CSV Prompt Conversion")
    print("=" * 40)

    prompt = """
Create a CSV report for employee data with these columns:
Name, Department, Salary, Start_Date, Manager

Input data:
Department: {department}
Manager: {manager_name}

Requirements:
- Include header row
- Salary range: 30000-150000
- Date format: YYYY-MM-DD
- At least 5 employees
- Department must match input
"""

    analyzer = PromptAnalyzer()
    analysis = analyzer.analyze(prompt)

    print(f"📊 Detected format: {analysis.output_format} (confidence: {analysis.confidence:.1%})")
    print(f"📋 CSV columns: {analysis.csv_columns}")

    suggester = ValidatorSuggester()
    suggestions = suggester.suggest_validators(analysis)

    print(f"💡 Best suggestion: {suggestions[0].validator_type}")
    print("✅ CSV prompt test completed")


def test_list_prompt() -> None:
    """Test list prompt conversion."""
    print("\n🧪 Testing List Prompt Conversion")
    print("=" * 40)

    prompt = """
Generate a to-do list for {project_type} project:

Project: {project_name}
Timeline: {timeline}

Create 8-12 action items in this format:
1. First action item
2. Second action item
3. Third action item

Requirements:
- Each item should be specific and actionable
- Include estimated time where relevant
- Prioritize by importance
"""

    analyzer = PromptAnalyzer()
    analysis = analyzer.analyze(prompt)

    print(f"📊 Detected format: {analysis.output_format} (confidence: {analysis.confidence:.1%})")
    print(f"📝 List pattern: {analysis.list_pattern}")

    suggester = ValidatorSuggester()
    suggestions = suggester.suggest_validators(analysis)

    print(f"💡 Best suggestion: {suggestions[0].validator_type}")
    print("✅ List prompt test completed")


def test_edge_cases() -> None:
    """Test edge cases and unusual prompts."""
    print("\n🧪 Testing Edge Cases")
    print("=" * 40)

    # Minimal prompt
    minimal_prompt = "Generate something for {input}"

    analyzer = PromptAnalyzer()
    analysis = analyzer.analyze(minimal_prompt)

    print(f"📊 Minimal prompt format: {analysis.output_format} (confidence: {analysis.confidence:.1%})")

    # Complex prompt with mixed format indicators
    complex_prompt = """
Generate a report that includes:
1. JSON summary with key metrics
2. CSV data table
3. Bulleted list of recommendations

Input: {data_source}
Format: {output_format}
"""

    analysis = analyzer.analyze(complex_prompt)
    print(f"📊 Complex prompt format: {analysis.output_format} (confidence: {analysis.confidence:.1%})")

    print("✅ Edge cases test completed")


def main() -> None:
    """Run all demos."""
    print("🚀 Starting Prompt-to-Task Conversion Demo")
    print("=" * 50)

    # Test different prompt types
    test_json_prompt()
    test_csv_prompt()
    test_list_prompt()
    test_edge_cases()

    print("\n📊 Demo Summary")
    print("=" * 30)
    print("✅ All demos completed successfully")
    print("🔧 Tool is ready for use")

    # Optionally, comment out or remove the file writing block if not needed.


if __name__ == "__main__":
    main()
