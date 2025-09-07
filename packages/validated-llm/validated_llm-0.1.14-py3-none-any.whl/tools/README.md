# Tools

Development tools for the validated-llm project.

## Prompt-to-Task Converter

Converts text prompts into validated-llm task classes with appropriate validators.

### Usage

```bash
python -m tools.prompt_to_task.cli convert my_prompt.txt # Convert single prompt
python -m tools.prompt_to_task.cli convert my_prompt.txt --output path/to/my_task.py # Specify custom output location
python -m tools.prompt_to_task.cli convert my_prompt.txt --interactive # Interactive mode
python -m tools.prompt_to_task.cli convert my_prompt.txt --analyze-only # Analyze only
```

### Batch Conversion (NEW!)

Convert multiple prompt files at once with parallel processing and progress tracking:

```bash
python -m tools.prompt_to_task.cli batch prompts/ # Convert all prompts in a directory
python -m tools.prompt_to_task.cli batch prompts/ --output-dir generated_tasks/ # Convert with custom output directory
python -m tools.prompt_to_task.cli batch prompts/ --dry-run # Dry run to see what would be converted
python -m tools.prompt_to_task.cli batch prompts/ --report conversion_report.json # Generate detailed report
python -m tools.prompt_to_task.cli batch data_prompts/ -v JSONValidator -v DateTimeValidator # Apply common validators to all files
python -m tools.prompt_to_task.cli batch api_prompts/ --template api_doc # Use specific template for all conversions
```

### Features

- Single File Conversion: Convert individual prompts with interactive refinement
- Batch Processing: Convert entire directories of prompts efficiently
- Format Detection: Automatically detects JSON, CSV, lists, markdown, etc.
- Enhanced JSON Detection (NEW!):
  - Detects nested objects and arrays in JSON examples
  - Supports arrays of objects
  - Infers JSON schema from textual descriptions
  - Intelligently selects JSONValidator vs JSONSchemaValidator based on complexity
- Smart Validators: Suggests appropriate validators based on content
- Parallel Processing: Process multiple files concurrently for speed
- Progress Tracking: Beautiful progress bars with rich/tqdm
- Detailed Reports: JSON reports with conversion statistics
- Template Support: Apply consistent templates across conversions
- Flexible Filtering: Include/exclude patterns for file selection

### Batch Conversion Examples

```bash
python -m tools.prompt_to_task.cli batch . --include "*.txt" "*.prompt" # Convert all .txt and .prompt files recursively
python -m tools.prompt_to_task.cli batch prompts/ --exclude "*test*" "*example*" # Exclude test files and examples
python -m tools.prompt_to_task.cli batch large_collection/ --max-workers 8 # Parallel processing with 8 workers
python -m tools.prompt_to_task.cli batch prompts/ --sequential # Sequential processing for debugging
python -m tools.prompt_to_task.cli batch prompts/ --overwrite # Overwrite existing files
```

### Example Workflow

```bash
python -m tools.prompt_to_task.cli batch legacy_prompts/ --output-dir src/validated_llm/tasks/generated/ --report report.json # 1. Convert a directory of prompts
cat migration_report.json | jq '.summary' # 2. Check the report
from validated_llm.tasks.generated.email_task import EmailTask # 3. Use the generated tasks
from validated_llm.tasks.generated.report_task import ReportTask
```

### Progress Reporting

The batch converter supports multiple progress reporting backends:

- auto (default): Uses rich if available, falls back to tqdm or simple
- rich: Beautiful progress bars with summary tables
- tqdm: Classic progress bars
- simple: Plain text output
- none: No progress output

```bash
python -m tools.prompt_to_task.cli batch prompts/ --progress rich # Use rich progress bars
python -m tools.prompt_to_task.cli batch prompts/ --progress simple # Simple text output
```
