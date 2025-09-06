#!/usr/bin/env python3
"""
Template Library Showcase

This script demonstrates the comprehensive template library for the prompt-to-task tool,
showing examples of how to use templates for various content generation tasks.
"""

import json

# Add the parent directory to the path
import sys
from pathlib import Path
from typing import Any, Dict

sys.path.append(str(Path(__file__).parent.parent.parent))

from tools.prompt_to_task.template_library import PromptTemplate, TemplateLibrary


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"{title:^60}")
    print(f"{'=' * 60}\n")


def showcase_template(template: PromptTemplate, template_vars: Dict[str, Any]) -> None:
    """Showcase a single template with example usage."""
    print(f"\n## Template: {template.name}")
    print(f"Category: {template.category}")
    print(f"Description: {template.description}")
    print(f"Tags: {', '.join(template.tags)}")
    print(f"\nPrompt Template:")
    print(f"  {template.prompt_template}")

    # Show filled prompt
    filled_prompt = template.prompt_template
    for key, value in template_vars.items():
        filled_prompt = filled_prompt.replace(f"{{{key}}}", str(value))

    print(f"\nFilled Prompt Example:")
    print(f"  {filled_prompt}")

    print(f"\nValidator Type: {template.validator_type}")
    print(f"Validator Config: {json.dumps(template.validator_config, indent=2)}")

    if template.example_output:
        print(f"\nExample Output:")
        print(f"  {template.example_output[:200]}{'...' if len(template.example_output) > 200 else ''}")


def main() -> None:
    """Run the template library showcase."""
    # Initialize template library
    library = TemplateLibrary()

    print_section("Template Library Showcase")
    print(f"Total templates available: {len(library._templates)}")
    print(f"Categories: {', '.join(library.get_categories())}")

    # Showcase templates by category
    showcases = {
        "API Documentation": [
            ("openapi_specification", {"api_name": "E-commerce", "api_purpose": "manages products, orders, and customers", "resource_types": "products, orders, customers, payments"}),
            ("graphql_schema_docs", {"domain": "social media platform", "entity_types": "User, Post, Comment, Like", "operations": "user management, content creation, social interactions"}),
            ("api_integration_guide", {"api_name": "Payment Gateway", "use_case": "process credit card payments securely", "programming_languages": "Python, JavaScript, and Java"}),
        ],
        "Data Analysis & Reporting": [
            (
                "statistical_analysis_report",
                {
                    "dataset_description": "customer purchase behavior data from Q4 2023",
                    "analysis_objectives": "identifying seasonal trends and customer segments",
                    "statistical_tests": "ANOVA, regression analysis, and cluster analysis",
                },
            ),
            (
                "business_intelligence_dashboard",
                {"business_area": "Sales Performance", "key_metrics": "revenue, conversion rate, customer acquisition cost, lifetime value", "target_audience": "C-suite executives and sales managers"},
            ),
            ("market_research_report", {"industry": "renewable energy", "research_objectives": "market penetration strategies and competitive positioning", "geographic_region": "North America and Europe"}),
        ],
        "Content Generation": [
            (
                "blog_post_seo",
                {"word_count": 1500, "topic": "artificial intelligence in healthcare", "target_keyword": "AI healthcare applications", "num_sections": 5, "target_audience": "healthcare professionals and tech enthusiasts"},
            ),
            (
                "marketing_campaign_copy",
                {
                    "campaign_type": "product launch",
                    "product_service": "AI-powered fitness app",
                    "channels": "email, social media, web landing page",
                    "audience_segments": "fitness enthusiasts, busy professionals",
                    "campaign_goal": "drive app downloads and premium subscriptions",
                },
            ),
            (
                "social_media_content_calendar",
                {"duration": "one month", "brand_name": "TechStart Innovation", "platforms": "LinkedIn, Twitter, Instagram", "content_themes": "thought leadership, product updates, team culture", "posts_per_week": 12},
            ),
        ],
        "Code Documentation": [
            ("code_api_reference", {"language": "Python", "module_name": "DataProcessor", "module_purpose": "handles ETL operations for big data pipelines"}),
            ("code_architecture_doc", {"system_name": "Microservices E-commerce Platform", "system_purpose": "provides scalable online shopping experience with distributed services"}),
            ("code_tutorial", {"tutorial_topic": "building RESTful APIs with FastAPI", "programming_language": "Python", "skill_level": "intermediate developers", "num_exercises": 5}),
        ],
        "Technical Specifications": [
            ("technical_requirements_doc", {"project_name": "Customer Portal Redesign", "project_goal": "improve user experience and add self-service capabilities"}),
            ("database_schema_design", {"application_name": "Inventory Management System", "data_types": "products, warehouses, stock levels, orders, suppliers", "database_type": "PostgreSQL"}),
            ("system_integration_spec", {"system_a": "CRM System", "system_b": "Email Marketing Platform", "integration_goal": "synchronize customer data and automate marketing campaigns"}),
        ],
        "User Stories & Requirements": [
            ("user_story_agile", {"feature_name": "Two-Factor Authentication", "product_name": "Banking Mobile App", "user_type": "account holder", "user_goal": "secure their account with additional authentication"}),
            ("use_case_specification", {"system_feature": "Shopping Cart Checkout", "system_name": "E-commerce Platform"}),
            ("product_roadmap", {"timeframe": "12-month", "product_name": "AI Writing Assistant", "num_releases": 4, "target_market": "content creators and marketing teams"}),
        ],
    }

    # Demonstrate each category
    for category_name, templates in showcases.items():
        print_section(category_name)

        for template_name, template_vars in templates:  # type: ignore
            template = library.get_template(template_name)
            if template:
                showcase_template(template, template_vars)
            else:
                print(f"Warning: Template '{template_name}' not found!")

    # Demonstrate template discovery features
    print_section("Template Discovery Features")

    # Find similar templates
    test_prompt = "I need to create API documentation for a REST service"
    print(f"\nFinding templates similar to: '{test_prompt}'")
    similar = library.find_similar_templates(test_prompt, top_k=3)
    for template, score in similar:
        print(f"  - {template.name} (similarity: {score:.2f})")

    # List templates by tags
    print(f"\nTemplates with 'api' tag:")
    api_templates = library.list_templates(tags=["api"])
    for template in api_templates[:5]:  # Show first 5
        print(f"  - {template.name}: {template.description}")

    # Show popular templates (simulated)
    print(f"\nCategories available:")
    for category in library.get_categories():
        category_templates = library.list_templates(category=category)
        print(f"  - {category}: {len(category_templates)} templates")


if __name__ == "__main__":
    main()
