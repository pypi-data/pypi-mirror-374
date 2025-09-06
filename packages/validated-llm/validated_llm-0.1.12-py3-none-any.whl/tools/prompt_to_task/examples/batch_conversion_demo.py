#!/usr/bin/env python3
"""
Batch Conversion Demo - Converting Multiple Prompts at Once

This example demonstrates how to use the batch conversion functionality
to process multiple prompt files efficiently.
"""

import tempfile
from pathlib import Path

# Example 1: Simple batch conversion
print("Example 1: Basic Batch Conversion")
print("-" * 50)
print(
    """
# Convert all .txt files in a directory
validated-llm-prompt2task batch prompts/

# Convert specific files
validated-llm-prompt2task batch prompt1.txt prompt2.txt prompt3.txt

# Convert all prompts recursively
validated-llm-prompt2task batch . --include "*.prompt" "*.txt"
"""
)

# Example 2: Custom output directory
print("\nExample 2: Custom Output Directory")
print("-" * 50)
print(
    """
# Put all generated tasks in a specific directory
validated-llm-prompt2task batch prompts/ --output-dir generated_tasks/

# Custom suffix for generated files
validated-llm-prompt2task batch prompts/ --output-suffix "_generated.py"
"""
)

# Example 3: Parallel processing
print("\nExample 3: Parallel Processing")
print("-" * 50)
print(
    """
# Process files in parallel (default)
validated-llm-prompt2task batch large_prompt_collection/

# Adjust number of workers
validated-llm-prompt2task batch prompts/ --max-workers 8

# Force sequential processing
validated-llm-prompt2task batch prompts/ --sequential
"""
)

# Example 4: Dry run and reporting
print("\nExample 4: Dry Run and Reporting")
print("-" * 50)
print(
    """
# See what would be converted without actually doing it
validated-llm-prompt2task batch prompts/ --dry-run

# Save detailed report
validated-llm-prompt2task batch prompts/ --report conversion_report.json

# Combine with custom progress reporting
validated-llm-prompt2task batch prompts/ --progress rich --report report.json
"""
)

# Example 5: Advanced filtering
print("\nExample 5: Advanced Filtering")
print("-" * 50)
print(
    """
# Custom include/exclude patterns
validated-llm-prompt2task batch . \\
    --include "*.txt" "*.prompt" "*.md" \\
    --exclude "*test*" "*example*" "README.md"

# Skip existing generated files (default)
validated-llm-prompt2task batch prompts/ --skip-existing

# Overwrite existing files
validated-llm-prompt2task batch prompts/ --overwrite
"""
)

# Example 6: Using templates and validators
print("\nExample 6: Templates and Common Validators")
print("-" * 50)
print(
    """
# Apply a template to all conversions
validated-llm-prompt2task batch prompts/ --template api_doc

# Apply common validators to all files
validated-llm-prompt2task batch data_prompts/ \\
    --validator JSONValidator \\
    --validator DateTimeValidator

# Combine template and validators
validated-llm-prompt2task batch api_prompts/ \\
    --template api_doc \\
    --validator JSONValidator \\
    --validator URLValidator
"""
)

# Example 7: Real-world scenario
print("\nExample 7: Real-World Migration Scenario")
print("-" * 50)
print(
    """
# Migrate an entire prompt library
validated-llm-prompt2task batch \\
    legacy_prompts/ \\
    new_prompts/generated/ \\
    admin_prompts/ \\
    --output-dir validated_tasks/ \\
    --template standard \\
    --validator RegexValidator \\
    --skip-existing \\
    --parallel \\
    --max-workers 6 \\
    --progress rich \\
    --report migration_report.json

# After completion, check the report
cat migration_report.json | jq '.summary'
"""
)

# Create a working example
print("\n" + "=" * 70)
print("WORKING EXAMPLE - Let's create and convert some sample prompts")
print("=" * 70)

with tempfile.TemporaryDirectory() as tmpdir:
    prompt_dir = Path(tmpdir) / "sample_prompts"
    prompt_dir.mkdir()

    # Create sample prompt files
    prompts = {
        "list_generator.txt": """Generate a list of {count} {item_type}.

Format as a bulleted list with brief descriptions.""",
        "json_creator.prompt": """Create a JSON object for a {entity_type} with the following fields:
- name
- description
- created_date
- status

Ensure all dates are in ISO format.""",
        "api_docs.md": """## API Documentation Generator

Generate documentation for the {endpoint_name} endpoint.

Include:
- Method: {method}
- Parameters
- Response format
- Example usage""",
        "data_analysis.txt": """Analyze the {dataset_name} dataset and provide:

1. Summary statistics
2. Key insights
3. Recommendations

Format the output as a structured report.""",
    }

    # Write prompt files
    for filename, content in prompts.items():
        (prompt_dir / filename).write_text(content)

    print(f"\nCreated sample prompts in: {prompt_dir}")
    print("\nFiles created:")
    for filename in prompts:
        print(f"  - {filename}")

    print("\nTo convert these prompts, you would run:")
    print(f"validated-llm-prompt2task batch {prompt_dir} --output-dir generated/")

    print("\nExpected output structure:")
    print(
        """
    generated/
    ├── list_generator_task.py
    ├── json_creator_task.py
    ├── api_docs_task.py
    └── data_analysis_task.py
    """
    )

print("\n" + "=" * 70)
print("BATCH CONVERSION BENEFITS")
print("=" * 70)
print(
    """
1. **Efficiency**: Process hundreds of prompts in seconds
2. **Consistency**: Apply same validators/templates to all files
3. **Flexibility**: Fine-grained control over what gets converted
4. **Tracking**: Detailed reports show what succeeded/failed
5. **Safety**: Dry-run mode lets you preview changes
6. **Performance**: Parallel processing for large collections
"""
)

if __name__ == "__main__":
    print("\nRun this script to see batch conversion examples!")
