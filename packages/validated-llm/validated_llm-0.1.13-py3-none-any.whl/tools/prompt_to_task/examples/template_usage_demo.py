#!/usr/bin/env python3
"""
Demo script showing how to use the template library programmatically.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.prompt_to_task.analyzer import PromptAnalyzer
from tools.prompt_to_task.code_generator import TaskCodeGenerator
from tools.prompt_to_task.template_library import PromptTemplate, TemplateLibrary
from tools.prompt_to_task.validator_suggester import ValidatorSuggester


def demo_template_library() -> None:
    """Demonstrate template library functionality."""
    print("🚀 Template Library Demo")
    print("=" * 50)

    # Initialize library
    library = TemplateLibrary()

    # 1. List available templates
    print("\n📚 Available Templates:")
    print("-" * 30)
    templates = library.list_templates()
    for template in templates[:5]:  # Show first 5
        print(f"  • {template.name} ({template.category})")
        print(f"    {template.description}")

    # 2. Find templates by category
    print("\n📁 JSON Templates:")
    print("-" * 30)
    json_templates = library.list_templates(category="json")
    for template in json_templates:
        print(f"  • {template.name}: {template.description}")

    # 3. Search by tags
    print("\n🏷️  Templates with 'email' tag:")
    print("-" * 30)
    email_templates = library.list_templates(tags=["email"])
    for template in email_templates:
        print(f"  • {template.name}: {template.description}")

    # 4. Find similar templates
    test_prompt = """
    Generate a user profile for John Smith who is 25 years old.
    Include their email, occupation, and hobbies in JSON format.
    """

    print(f"\n🔍 Finding templates similar to prompt:")
    print(f"'{test_prompt.strip()}'")
    print("-" * 30)

    matches = library.find_similar_templates(test_prompt, top_k=3)
    for template, score in matches:
        print(f"  • {template.name}: {score:.1%} match")
        print(f"    {template.description}")

    # 5. Use a template with analyzer
    print("\n🔧 Using template with analyzer:")
    print("-" * 30)

    # Get the best matching template
    if matches:
        best_template, best_score = matches[0]
        print(f"Using template: {best_template.name}")

        # Analyze with template library
        analyzer = PromptAnalyzer(template_library=library)
        analysis = analyzer.analyze(test_prompt)

        print(f"\nAnalysis results:")
        print(f"  • Format: {analysis.output_format}")
        print(f"  • Confidence: {analysis.confidence:.1%}")
        print(f"  • Variables: {analysis.template_variables}")

        if analysis.json_schema:
            print(f"  • JSON Schema properties: {list(analysis.json_schema.get('properties', {}).keys())}")

        if analysis.matched_templates:
            print(f"  • Best match: {analysis.matched_templates[0][0].name} ({analysis.matched_templates[0][1]:.1%})")

    # 6. Create a custom template
    print("\n✨ Creating custom template:")
    print("-" * 30)

    custom_template = PromptTemplate(
        name="custom_api_response",
        category="json",
        description="API response with status and data",
        prompt_template="Generate an API response for {endpoint} with {status_code} status. Include {data_type} in the response body.",
        validator_type="json",
        validator_config={
            "required_fields": ["status", "message", "data"],
            "schema": {"type": "object", "properties": {"status": {"type": "integer"}, "message": {"type": "string"}, "data": {"type": "object"}}, "required": ["status", "message", "data"]},
        },
        json_schema={
            "type": "object",
            "properties": {"status": {"type": "integer", "minimum": 100, "maximum": 599}, "message": {"type": "string"}, "data": {"type": "object"}, "timestamp": {"type": "string", "format": "date-time"}},
            "required": ["status", "message", "data"],
        },
        example_output='{"status": 200, "message": "Success", "data": {"id": 123, "name": "Example"}, "timestamp": "2024-01-01T12:00:00Z"}',
        tags=["api", "response", "json", "rest"],
    )

    # Add to library
    library.add_template(custom_template)
    print(f"Added template: {custom_template.name}")

    # 7. Generate code using template
    print("\n🚀 Generating code from template:")
    print("-" * 30)

    # Use template to analyze
    template_prompt = best_template.prompt_template.format(name="Alice Johnson", age="30", occupation="Data Scientist")

    analysis = analyzer.analyze(template_prompt)
    suggester = ValidatorSuggester()
    suggestions = suggester.suggest_validators(analysis)

    if suggestions:
        generator = TaskCodeGenerator()
        code = generator.generate_task_code(
            analysis=analysis, suggestions=suggestions[:1], task_name="User Profile Generation", task_description="Generate user profiles using template", prompt_template=template_prompt, source_file="template_demo.txt"
        )

        print("Generated task code preview:")
        print("-" * 30)
        # Show first 20 lines
        lines = code.split("\n")[:20]
        for line in lines:
            print(line)
        print("... (truncated)")


if __name__ == "__main__":
    demo_template_library()
