#!/usr/bin/env python3
"""
Template to Task Demo

This script demonstrates how to use the template library to quickly create
validated tasks from templates, showing the complete workflow from template
selection to task generation.
"""

import json

# Add the parent directory to the path
import sys
from pathlib import Path
from typing import Any, Dict

sys.path.append(str(Path(__file__).parent.parent.parent))

from tools.prompt_to_task.code_generator import TaskCodeGenerator
from tools.prompt_to_task.template_library import TemplateLibrary


def generate_task_from_template(template_name: str, template_vars: Dict[str, Any], output_file: str) -> None:
    """Generate a complete task file from a template."""
    library = TemplateLibrary()
    template = library.get_template(template_name)

    if not template:
        print(f"Error: Template '{template_name}' not found!")
        return

    print(f"\n=== Using Template: {template.name} ===")
    print(f"Description: {template.description}")
    print(f"Category: {template.category}")

    # Fill in the prompt template
    filled_prompt = template.prompt_template
    for key, value in template_vars.items():
        filled_prompt = filled_prompt.replace(f"{{{key}}}", str(value))

    print(f"\nFilled Prompt:")
    print(filled_prompt)

    # Generate the task code
    generator = TaskCodeGenerator()

    # Prepare task metadata
    task_name = template_name.replace("_", " ").title().replace(" ", "") + "Task"

    # Map validator types to actual validator classes
    validator_mapping = {
        "json": "JSONValidator",
        "csv": "CSVValidator",
        "email": "EmailValidator",
        "markdown": "MarkdownValidator",
        "sql": "SQLValidator",
        "story_scenes": "StoryToScenesValidator",
    }

    validator_class = validator_mapping.get(template.validator_type, "BaseValidator")

    # Generate the code
    code = f'''"""
Generated task from template: {template.name}
{template.description}
"""

from typing import Dict, Any, Optional
from validated_llm.tasks import BaseTask
from validated_llm.validators import {validator_class}


class {task_name}(BaseTask):
    """
    {template.description}

    Template Variables:
    {chr(10).join(f"    - {key}: {value}" for key, value in template_vars.items())}
    """

    def __init__(self):
        super().__init__()
        self.template_vars = {json.dumps(template_vars, indent=8)}

    @property
    def prompt_template(self) -> str:
        """The prompt template for this task."""
        return """{filled_prompt}"""

    @property
    def validator_class(self):
        """The validator class for this task."""
        return {validator_class}

    def prepare_prompt_data(self, **kwargs) -> Dict[str, Any]:
        """Prepare data for the prompt template."""
        # Use template variables as defaults, allow overrides
        data = self.template_vars.copy()
        data.update(kwargs)
        return data

    def configure_validator(self) -> Dict[str, Any]:
        """Configure the validator with template-specific settings."""
        return {json.dumps(template.validator_config, indent=8)}


# Example usage
if __name__ == "__main__":
    from validated_llm import ValidationLoop

    # Create task instance
    task = {task_name}()

    # Create validation loop
    loop = ValidationLoop(
        task=task,
        model="gpt-4",  # or your preferred model
        max_retries=3
    )

    # Execute with any additional parameters
    result = loop.execute(
        # Override any template variables here if needed
        # For example: api_name="My Custom API"
    )

    print("Generated content:")
    print(result)
'''

    # Write the generated code
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(code)

    print(f"\nTask generated successfully!")
    print(f"Output file: {output_path}")

    # Update usage count
    library.update_usage_count(template_name)


def main() -> None:
    """Demonstrate template to task conversion with various examples."""
    print("=== Template to Task Generation Demo ===\n")

    # Example 1: Generate an API documentation task
    print("1. Generating API Documentation Task")
    generate_task_from_template(
        template_name="rest_api_endpoint",
        template_vars={"http_method": "POST", "endpoint_path": "/api/v1/users", "endpoint_description": "creates a new user account with email verification"},
        output_file="generated_tasks/api_doc_task.py",
    )

    # Example 2: Generate a data analysis report task
    print("\n2. Generating Data Analysis Report Task")
    generate_task_from_template(
        template_name="statistical_analysis_report",
        template_vars={
            "dataset_description": "customer churn data from telecom company",
            "analysis_objectives": "predicting churn probability and identifying key factors",
            "statistical_tests": "logistic regression, chi-square tests, and survival analysis",
        },
        output_file="generated_tasks/churn_analysis_task.py",
    )

    # Example 3: Generate a blog post task
    print("\n3. Generating Blog Post Task")
    generate_task_from_template(
        template_name="blog_post_seo",
        template_vars={"word_count": 2000, "topic": "machine learning for beginners", "target_keyword": "machine learning tutorial", "num_sections": 6, "target_audience": "aspiring data scientists and developers"},
        output_file="generated_tasks/blog_post_task.py",
    )

    # Example 4: Generate a user story task
    print("\n4. Generating User Story Task")
    generate_task_from_template(
        template_name="user_story_agile",
        template_vars={"feature_name": "Password Reset", "product_name": "Customer Portal", "user_type": "registered user", "user_goal": "reset their forgotten password securely"},
        output_file="generated_tasks/user_story_task.py",
    )

    # Example 5: Generate a database schema task
    print("\n5. Generating Database Schema Task")
    generate_task_from_template(
        template_name="database_schema_design",
        template_vars={"application_name": "Blog Platform", "data_types": "users, posts, comments, tags, categories", "database_type": "MySQL"},
        output_file="generated_tasks/db_schema_task.py",
    )

    # Show how to discover templates programmatically
    print("\n\n=== Template Discovery ===")
    library = TemplateLibrary()

    # Find templates for content generation
    print("\nContent generation templates:")
    content_templates = library.list_templates(category="content")
    for template in content_templates:
        print(f"  - {template.name}: {template.description}")

    # Find templates by similarity
    print("\nTemplates similar to 'write technical documentation':")
    similar = library.find_similar_templates("write technical documentation", top_k=5)
    for template, score in similar:
        print(f"  - {template.name} (score: {score:.2f})")


if __name__ == "__main__":
    main()
