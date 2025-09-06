"""
CSV generation LLM validation task.

This task converts data descriptions into structured CSV output.
"""

import csv
import io
from typing import Any, Dict, List, Optional, Type

from ..base_validator import BaseValidator, ValidationResult
from .base_task import BaseTask


class CSVGenerationTask(BaseTask):
    """Task for generating CSV reports from data descriptions."""

    @property
    def name(self) -> str:
        return "CSV Report Generation"

    @property
    def description(self) -> str:
        return "Generate CSV reports from data descriptions"

    @property
    def prompt_template(self) -> str:
        return """
Generate a CSV report from the following data: {data_description}

OUTPUT REQUIREMENTS:
- First row must be column headers
- Use comma as delimiter
- Do not wrap in markdown code blocks
- Include at least 3 data rows
- Ensure proper CSV formatting (quote fields containing commas)

Required columns based on data type:
- If sales data: Date, Product, Sales_Rep, Amount, Region
- If employee data: Name, Department, Hire_Date, Salary, Manager
- If inventory data: SKU, Product_Name, Category, Stock_Level, Location
- If generic data: create appropriate column headers based on content

Your response:"""

    @property
    def validator_class(self) -> Type[BaseValidator]:
        return CSVValidator


class CSVValidator(BaseValidator):
    """Validates LLM output as properly formatted CSV."""

    def __init__(self, required_columns: Optional[List[str]] = None, min_rows: int = 1, max_rows: Optional[int] = None, delimiter: str = ","):
        """
        Initialize the CSV validator.

        Args:
            required_columns: List of column names that must be present
            min_rows: Minimum number of data rows (excluding header)
            max_rows: Maximum number of data rows (optional)
            delimiter: CSV delimiter character
        """
        super().__init__(name="csv_validator", description=f"Validates CSV output with {min_rows}+ rows")
        self.required_columns = required_columns or []
        self.min_rows = min_rows
        self.max_rows = max_rows
        self.delimiter = delimiter

    def validate(self, content: str, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate content as proper CSV format."""
        errors = []
        warnings: List[str] = []

        try:
            # Parse CSV content
            csv_file = io.StringIO(content.strip())
            reader = csv.reader(csv_file, delimiter=self.delimiter)

            rows = list(reader)
            if not rows:
                errors.append("CSV is empty")
                return ValidationResult(False, errors, warnings)

            # Check header row
            header = rows[0]
            data_rows = rows[1:]

            # Validate required columns
            for col in self.required_columns:
                if col not in header:
                    errors.append(f"Required column '{col}' not found in header")

            # Check row count
            if len(data_rows) < self.min_rows:
                errors.append(f"Too few data rows: {len(data_rows)}, minimum required: {self.min_rows}")

            if self.max_rows and len(data_rows) > self.max_rows:
                errors.append(f"Too many data rows: {len(data_rows)}, maximum allowed: {self.max_rows}")

            # Check for consistent column count
            expected_cols = len(header)
            for i, row in enumerate(data_rows, 1):
                if len(row) != expected_cols:
                    errors.append(f"Row {i} has {len(row)} columns, expected {expected_cols}")

            # Check for empty cells (warning only)
            for i, row in enumerate(data_rows, 1):
                for j, cell in enumerate(row):
                    if not cell.strip():
                        warnings.append(f"Empty cell at row {i}, column {j+1}")

        except csv.Error as e:
            errors.append(f"CSV parsing error: {str(e)}")
        except Exception as e:
            errors.append(f"Unexpected error parsing CSV: {str(e)}")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)
