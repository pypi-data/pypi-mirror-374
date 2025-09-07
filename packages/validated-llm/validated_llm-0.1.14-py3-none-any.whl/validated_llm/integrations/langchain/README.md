# Langchain Integration for Validated-LLM

## Overview

This integration allows users to convert their existing Langchain prompts and chains to validated-llm tasks, gaining automatic validation and retry capabilities.

## Key Components

### 1. PromptTemplate Converter

Converts Langchain's `PromptTemplate` objects to validated-llm `BaseTask` subclasses.

**Langchain PromptTemplate:**

```python
from langchain.prompts import PromptTemplate

template = PromptTemplate(
    input_variables=["product"],
    template="Generate a product description for {product}"
)
```

**Converted to validated-llm Task:**

```python
from validated_llm.tasks import BaseTask
from validated_llm.validators import MarkdownValidator

class ProductDescriptionTask(BaseTask):
    prompt_template = "Generate a product description for {product}"
    validator_class = MarkdownValidator  # Auto-suggested based on analysis
```

### 2. Output Parser Mapping

Maps Langchain output parsers to appropriate validated-llm validators:

| Langchain Parser       | Validated-LLM Validator   |
| ---------------------- | ------------------------- |
| PydanticOutputParser   | JSONValidator with schema |
| StructuredOutputParser | JSONValidator             |
| ListOutputParser       | Custom ListValidator      |
| DatetimeOutputParser   | DateTimeValidator         |
| OutputFixingParser     | Built into ValidationLoop |

### 3. Chain Support

Convert multi-step Langchain chains to validated task sequences:

- Sequential chains → Task pipelines
- Router chains → Conditional task execution
- Memory/History → Context preservation between tasks

## Usage Example

```python
from validated_llm.integrations.langchain import convert_prompt_template

# Convert a Langchain prompt
langchain_prompt = PromptTemplate(
    input_variables=["topic"],
    template="Write a blog post about {topic}"
)

# Auto-convert to validated task
task = convert_prompt_template(
    langchain_prompt,
    task_name="BlogPostTask",
    validator_hints=["markdown", "min_length:500"]
)

# Use the task with validation
result = task.execute(topic="Python best practices")
```

## Implementation Plan

1. **Phase 1**: Basic PromptTemplate conversion
2. **Phase 2**: Output parser mapping
3. **Phase 3**: Chain support
4. **Phase 4**: Memory/context handling
5. **Phase 5**: Migration CLI tool
