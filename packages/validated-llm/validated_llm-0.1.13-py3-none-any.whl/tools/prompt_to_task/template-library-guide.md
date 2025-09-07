# Template Library Guide

## Overview

The Template Library is a comprehensive collection of reusable prompt templates for the `validated-llm` prompt-to-task tool. It provides pre-configured templates for common content generation tasks, making it easy to create validated LLM tasks without starting from scratch.

## Template Categories

### 1. API Documentation (`api_docs`)

- openapi_specification: Generate OpenAPI/Swagger specifications
- graphql_schema_docs: Document GraphQL schemas with types and resolvers
- api_integration_guide: Create comprehensive API integration guides
- rest_api_endpoint: Document REST API endpoints

### 2. Data Analysis & Reporting (`analysis_report`)

- statistical_analysis_report: Generate detailed statistical analysis reports
- business_intelligence_dashboard: Design BI dashboard specifications
- market_research_report: Create comprehensive market research reports
- data_analysis_report: Analyze datasets and provide insights

### 3. Content Generation (`content`)

- blog_post_seo: Generate SEO-optimized blog posts
- marketing_campaign_copy: Create multi-channel marketing campaign copy
- social_media_content_calendar: Generate social media content calendars
- email_newsletter: Design email newsletters with sections and CTAs

### 4. Code Documentation (`code_docs`)

- code_api_reference: Generate API reference documentation from code
- code_architecture_doc: Create software architecture documentation
- code_tutorial: Write step-by-step coding tutorials

### 5. Technical Specifications (`tech_specs`)

- technical_requirements_doc: Generate technical requirements documentation
- database_schema_design: Design database schemas with relationships
- system_integration_spec: Document system integration specifications

### 6. User Stories & Requirements (`requirements`)

- user_story_agile: Generate user stories with acceptance criteria
- use_case_specification: Write detailed use case specifications
- product_roadmap: Create product roadmaps with milestones

### 7. Other Categories

- json: JSON data generation templates
- csv: CSV data generation templates
- email: Email composition templates
- sql: SQL query generation templates
- story: Creative writing and story generation templates

## Using the Template Library

### Command Line Interface

#### 1. List Available Templates

```bash
# List all templates
python -m tools.prompt_to_task.cli_template list
# Filter by category
python -m tools.prompt_to_task.cli_template list --category api_docs
# Filter by tags
python -m tools.prompt_to_task.cli_template list --tag documentation --tag api
# Search templates
python -m tools.prompt_to_task.cli_template list --search "api documentation"
```

#### 2. View Template Details

```bash
# Show detailed information about a template
python -m tools.prompt_to_task.cli_template show openapi_specification
```

#### 3. Use a Template

```bash
# Generate a task from a template (interactive mode)
python -m tools.prompt_to_task.cli_template use openapi_specification -o tasks/my_api_task.py -i
# Generate with preview
python -m tools.prompt_to_task.cli_template use blog_post_seo -o tasks/blog_task.py -p
```

#### 4. Search for Templates

```bash
# Find templates similar to your needs
python -m tools.prompt_to_task.cli_template search "I need to document a REST API"
```

#### 5. Browse Categories and Tags

```bash
# List all categories
python -m tools.prompt_to_task.cli_template categories
# List all tags
python -m tools.prompt_to_task.cli_template tags
# Show popular templates
python -m tools.prompt_to_task.cli_template popular
```

### Rich CLI Interface

For an enhanced experience with colorful output and interactive features:

```bash
# Use the rich CLI
python -m tools.prompt_to_task.cli_template_rich list
# Interactive wizard for converting prompts
python -m tools.prompt_to_task.cli_template_rich wizard my_prompt.txt
```

### Programmatic Usage

```python
from tools.prompt_to_task.template_library import TemplateLibrary
# Initialize library
library = TemplateLibrary()
# Get a specific template
template = library.get_template("openapi_specification")
# Find similar templates
matches = library.find_similar_templates("create API documentation", top_k=5)
# List templates by category
api_templates = library.list_templates(category="api_docs")
# List templates by tags
doc_templates = library.list_templates(tags=["documentation", "api"])
```

## Template Structure

Each template contains:

- name: Unique identifier for the template
- category: Category for organization
- description: What the template does
- prompt_template: The actual prompt with variable placeholders
- validator_type: Type of validator to use (json, markdown, csv, etc.)
- validator_config: Configuration for the validator
- json_schema: Optional JSON schema for JSON validators
- example_output: Example of expected output
- tags: Tags for searching and filtering

## Creating Custom Templates

You can add your own templates programmatically:

```python
from tools.prompt_to_task.template_library import TemplateLibrary, PromptTemplate
library = TemplateLibrary()
# Create a new template
custom_template = PromptTemplate(
    name="my_custom_template",
    category="custom",
    description="My custom template for specific needs",
    prompt_template="Generate {content_type} for {purpose} including {requirements}",
    validator_type="markdown",
    validator_config={
        "required_sections": ["introduction", "main_content", "conclusion"],
        "min_length": 500
    },
    tags=["custom", "specific", "markdown"]
)
# Add to library
library.add_template(custom_template)
```

## Template Variables

Templates use placeholders in the format `{variable_name}`. Common variables include:

- `{api_name}`, `{api_purpose}`: For API-related templates
- `{dataset_description}`, `{analysis_objectives}`: For data analysis
- `{topic}`, `{target_keyword}`, `{word_count}`: For content generation
- `{product_name}`, `{feature_name}`: For product documentation
- `{system_name}`, `{system_purpose}`: For technical documentation

## Best Practices

- Choose the Right Template: Use the search feature to find templates that match your needs
- Customize Variables: Always provide meaningful values for template variables
- Review Generated Code: Always review and customize the generated task code
- Validate Output: Test the generated task with sample data before production use
- Extend Templates: Feel free to modify generated tasks to add custom logic

## Examples

### Example 1: Generate API Documentation Task

`python -m tools.prompt_to_task.cli_template use rest_api_endpoint -o tasks/user_api_doc.py -i`

### Example 2: Create a Blog Post Generator

`python -m tools.prompt_to_task.cli_template use blog_post_seo -o tasks/tech_blog_generator.py --preview`

### Example 3: Build a Data Analysis Task

`python -m tools.prompt_to_task.cli_template use statistical_analysis_report -o tasks/sales_analysis.py -i`

## Template Library Architecture

The template library is designed to be:

- Extensible: Easy to add new templates
- Searchable: Find templates by name, category, tags, or similarity
- Reusable: Templates can be exported/imported
- Trackable: Usage statistics help identify popular templates
- Discoverable: Rich CLI interface for browsing and exploring

## Troubleshooting

### Template Not Found

- Check the template name spelling
- Use the search feature to find similar templates
- List all templates to see available options

### Variable Errors

- Ensure all template variables are provided
- Check for typos in variable names
- Use interactive mode for guided variable input

### Validator Issues

- Verify the validator type matches your content
- Check validator configuration for your specific needs
- Review the example output for expected format

## Contributing Templates

To contribute new templates:

- Create a well-documented template with clear variables
- Include comprehensive validator configuration
- Provide a realistic example output
- Add appropriate tags for discoverability
- Test the template with real use cases

## Future Enhancements

- Template versioning
- Template inheritance and composition
- Online template marketplace
- AI-powered template suggestions
- Template performance metrics
