# validated-llm

- [![PyPI version](https://badge.fury.io/py/validated-llm.svg)](https://badge.fury.io/py/validated-llm)
- [![Python Support](https://img.shields.io/pypi/pyversions/validated-llm.svg)](https://pypi.org/project/validated-llm/)
- [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
- LLM output validation with retry loops - ensure your language model responses meet requirements.

## Overview

`validated-llm` provides a robust framework for validating language model outputs with automatic retry mechanisms. It's designed for applications where you need reliable, structured responses from LLMs.

### Why validated-llm?

Unlike other solutions, validated-llm offers:
- **Clean separation of concerns** - Validators independent from LLM interaction
- **Framework agnostic** - Works with any LLM (OpenAI, Anthropic, Ollama)
- **Flexible validation** - Not tied to specific schema formats
- **Comprehensive debugging** - Detailed execution logs and attempt tracking
- **Simple API** - Just `execute()` with template, validator, and data

## Key Features

- Automatic Retry Logic: Handles failed validations with configurable retry attempts
- 16 Built-in Validators: JSON Schema, XML, YAML, Email, Phone, URL, Markdown, DateTime, Range, Regex, SQL, Syntax, Style, Test, Composite, and Documentation validators
- Enhanced JSON Detection: Detects nested objects, arrays of objects, and complex JSON structures with intelligent validator selection
- Code Generation & Validation: Multi-language code generation (Python, JavaScript, TypeScript, Go, Rust, Java) with syntax validation
- Template Library: 29 pre-built templates across 6 categories for common prompt patterns
- Prompt Migration Tools: Convert existing prompts to validated tasks with batch processing
- Task-Based Architecture: Organize validation logic into reusable task classes
- Langchain Integration: Full converter for migrating Langchain prompts to validated-llm
- Config File Support: Project-level configuration with `.validated-llm.yml`
- Comprehensive CLI Tools: Interactive template browsing, batch conversion, and analysis

## Quick Start

### Installation

`pip install validated-llm`

### Basic Usage

```python
from validated_llm import ValidationLoop
from validated_llm.validators import JSONSchemaValidator

# Define your validation schema
schema = {
    "type": "object",
    "properties": {
        "scenes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "characters": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["title", "description", "characters"]
            }
        }
    },
    "required": ["scenes"]
}

# Create validation loop with built-in LLM provider
validator = ValidationLoop(
    vendor="openai",  # or "ollama", "anthropic"
    model="gpt-4o",
    api_key="your-openai-api-key",
    max_retries=3,
    temperature=0.7
)

# Execute with validation
result = validator.execute(
    prompt_template="Convert this story into 3-5 scenes: {story}. Return as JSON with scenes array.",
    validator=JSONSchemaValidator(schema),
    input_data={"story": "Once upon a time..."}
)

print(result['output'])  # Validated JSON response
```

### Built-in Tasks

The package includes comprehensive pre-built validation tasks:

#### JSON Generation with Schema Detection

```python
from validated_llm.tasks import JSONGenerationTask
# Automatic schema detection from examples
task = JSONGenerationTask(
    schema={
        "type": "object",
        "properties": {
            "scenes": {
                "type": "array",
                "items": {"type": "object"}
            }
        },
        "required": ["scenes"]
    }
)
```

#### Code Generation with Multi-Language Support

```python
from validated_llm.tasks import FunctionGenerationTask
task = FunctionGenerationTask(
    language="python",
    function_name="binary_search",
    requirements="Implement binary search algorithm with proper error handling"
)
```

#### CSV Generation

```python
from validated_llm.tasks import CSVGenerationTask
task = CSVGenerationTask(
    required_columns=["name", "age", "role"],
    min_rows=3
)
```

#### Documentation Generation

```python
from validated_llm.tasks import APIDocumentationTask
task = APIDocumentationTask(
    api_type="REST",
    include_examples=True,
    validate_completeness=True
)
```

## Architecture

### Core Components

- ValidationLoop: Main orchestrator that handles the retry logic
- BaseTask: Abstract base class for creating validation tasks
- BaseValidator: Pluggable validation system for different response types

### Creating Custom Tasks

```python
class CustomTask(BaseTask):
    def get_prompt(self, input_data: str) -> str:
        # Return the prompt for the LLM
        return f"Process this data: {input_data}"
    def validate_response(self, response: str) -> bool:
        # Return True if response is valid
        return len(response) > 10
    def parse_response(self, response: str) -> dict:
        # Optional: transform the response
        return {"processed": response}
```

## CLI Tools

### Prompt to Task Converter

Convert existing prompts into validated task classes with enhanced JSON schema detection:

```bash
pip install validated-llm # Install the package
validated-llm-prompt2task prompt.txt # Convert a prompt file to a task
validated-llm-prompt2task batch prompts_directory/ # Batch convert multiple prompts with parallel processing
validated-llm-prompt2task prompt.txt --interactive # Interactive mode with validator selection
validated-llm-prompt2task prompt.txt --template api_doc # Use templates for consistent patterns
validated-llm-prompt2task prompt.txt --analyze-only # Analyze prompt without generating code
```

The tool will:

- Enhanced JSON Detection: Automatically detect nested objects, arrays of objects, and complex JSON structures
- Smart Validator Selection: Choose between JSONValidator and JSONSchemaValidator based on complexity
- Template Integration: Apply 29 pre-built templates for common use cases
- Batch Processing: Convert entire directories with parallel processing and progress tracking
- Format Detection: Detect JSON, CSV, text, lists, code, and documentation formats
- Generate Complete Tasks: Create task classes with appropriate validators and documentation

### Template Library

Browse and use pre-built templates:

```bash
validated-llm-templates list # Browse available templates
validated-llm-templates list --category "api" # Search templates by category
validated-llm-templates show product_catalog_json # Show template details
validated-llm-templates use business_email # Use a template interactively
```

### Configuration Management

Manage project-level settings:

```bash
validated-llm-config init # Initialize project configuration
validated-llm-config validate # Validate configuration file
validated-llm-config show # Show current configuration
```

### Plugin Management

Manage validator plugins for custom validation logic:

```bash
validated-llm-plugin list # List available plugins
validated-llm-plugin info credit_card_validator # Show detailed plugin information
validated-llm-plugin test credit_card_validator --args '{"strict_mode": true}' # Test a plugin
validated-llm-plugin discover ./custom_plugins/ # Discover plugins from a directory
validated-llm-plugin paths # Show plugin search paths
validated-llm-plugin validate-plugin my_validator # Validate plugin meets requirements
```

## Configuration

### LLM Provider Setup

```python
# OpenAI (default)
validator = ValidationLoop(
    model="gpt-4",
    api_key="your-api-key"
)
# Custom endpoint (e.g., local LLM)
validator = ValidationLoop(
    model="llama2",
    base_url="http://localhost:11434/v1/",
    api_key="not-needed"
)
```

### Retry Configuration

```python
validator = ValidationLoop(
    model="gpt-4",
    max_retries=5,           # Maximum retry attempts
    temperature=0.7,         # LLM temperature
    timeout=30,              # Request timeout in seconds
    backoff_factor=1.5       # Exponential backoff multiplier
)
```

## Advanced Usage

### Custom Validators

```python
from validated_llm import BaseValidator
class SchemaValidator(BaseValidator):
    def init(self, schema: dict):
        self.schema = schema
    def validate(self, response: str) -> tuple[bool, str]:
        try:
            data = json.loads(response)
            # Validate against schema
            return True, "Valid JSON"
        except Exception as e:
            return False, f"Invalid: {e}"
```

### Error Handling

```python
from validated_llm.exceptions import ValidationError, MaxRetriesExceeded
try:
    result = validator.run_task(task, input_data)
except MaxRetriesExceeded:
    print("Failed after maximum retries")
except ValidationError as e:
    print(f"Validation failed: {e}")
```

## Testing

- Run the test suite: `poetry run pytest`
- With coverage: `poetry run pytest --cov=src tests/`

## Contributing

- Fork the repository
- Create a feature branch: `git checkout -b feature-name`
- Make changes and add tests
- Run tests: `poetry run pytest`
- Format code: `poetry run black . && poetry run isort .`
- Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Documentation

Comprehensive guides and documentation:

- [Cookbook](docs/COOKBOOK.md) - Practical examples and common patterns
- [Best Practices](docs/BEST_PRACTICES.md) - Production-ready patterns and optimization
- [Plugin Development](docs/PLUGIN_DEVELOPMENT.md) - Complete guide to creating custom validators
- [Plugin System](docs/PLUGIN_SYSTEM.md) - Architecture and usage of the plugin system

## Examples

See the `examples/` directory for more detailed usage examples:

- `basic_validation.py` - Simple validation example
- `custom_task.py` - Creating custom validation tasks
- `multiple_providers.py` - Using different LLM providers
- `story_to_scenes.py` - Real-world story processing example
- `validation_patterns.py` - Common validation patterns and use cases
