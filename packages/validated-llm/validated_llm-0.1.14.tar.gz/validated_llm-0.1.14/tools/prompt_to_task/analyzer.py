"""
Prompt analyzer that detects output patterns and structure.

This module analyzes prompt text to identify:
- Template variables ({variable})
- Expected output formats (JSON, CSV, lists, etc.)
- Validation requirements
- Structure patterns
"""

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

from .template_library import PromptTemplate, TemplateLibrary


@dataclass
class AnalysisResult:
    """Result of prompt analysis."""

    # Template variables found in prompt
    template_variables: List[str]

    # Detected output format
    output_format: str  # 'json', 'csv', 'list', 'text', 'unknown'

    # For JSON: detected schema structure
    json_schema: Optional[Dict[str, Any]] = None

    # For CSV: detected column names
    csv_columns: Optional[List[str]] = None

    # For lists: detected list item pattern
    list_pattern: Optional[str] = None

    # Validation hints found in prompt
    validation_hints: Optional[List[str]] = None

    # Confidence score (0.0 to 1.0)
    confidence: float = 0.0

    # Raw patterns found
    patterns: Optional[Dict[str, Any]] = None

    # Matched templates from library
    matched_templates: Optional[List[Tuple[PromptTemplate, float]]] = None

    def __post_init__(self) -> None:
        if self.validation_hints is None:
            self.validation_hints = []
        if self.patterns is None:
            self.patterns = {}
        if self.matched_templates is None:
            self.matched_templates = []


class PromptAnalyzer:
    """
    Analyzes prompts to detect output patterns and structure.

    This analyzer uses pattern matching and heuristics to identify:
    - What kind of output the prompt expects
    - What validation would be appropriate
    - What template variables are used
    """

    def __init__(self, template_library: Optional[TemplateLibrary] = None) -> None:
        """Initialize the prompt analyzer.

        Args:
            template_library: Optional template library to use for matching
        """
        self.template_library = template_library or TemplateLibrary()
        self.json_indicators = [
            r'\{[^{}]*"[^"]*"[^{}]*\}',  # JSON object pattern
            r"\[[^[\]]*\{[^}]*\}[^[\]]*\]",  # JSON array pattern
            "json",
            "JSON",
            '"key":',
            '"name":',
            '"id":',
            "return.*json",
            "output.*json",
            "format.*json",
            "structure.*json",
        ]

        self.csv_indicators = [r"csv", r"CSV", r"comma.separated", r"comma-separated", r"columns?:", r"headers?:", r"Name,.*,.*", r"[A-Za-z]+,[A-Za-z]+,[A-Za-z]+", "spreadsheet", "table format"]

        self.list_indicators = [r"^\d+\.", r"^\*", r"^-", "list of", "items:", "bullet points", "enumerate", "one per line"]  # Numbered/bulleted lists

        self.validation_keywords = [
            "required",
            "must",
            "should",
            "validate",
            "ensure",
            "check",
            "verify",
            "format",
            "minimum",
            "maximum",
            "between",
            "length",
            "type",
            "integer",
            "string",
            "number",
            "email",
            "url",
            "phone",
            "date",
        ]

    def analyze(self, prompt_text: str) -> AnalysisResult:
        """
        Analyze a prompt to detect patterns and structure.

        Args:
            prompt_text: The prompt text to analyze

        Returns:
            AnalysisResult with detected patterns and suggestions
        """
        # Extract template variables
        template_vars = self._extract_template_variables(prompt_text)

        # Detect output format
        output_format, format_confidence = self._detect_output_format(prompt_text)

        # Extract format-specific details
        json_schema = None
        csv_columns = None
        list_pattern = None

        if output_format == "json":
            json_schema = self._extract_json_schema(prompt_text)
        elif output_format == "csv":
            csv_columns = self._extract_csv_columns(prompt_text)
        elif output_format == "list":
            list_pattern = self._extract_list_pattern(prompt_text)

        # Extract validation hints
        validation_hints = self._extract_validation_hints(prompt_text)

        # Find similar templates
        matched_templates = self.template_library.find_similar_templates(prompt_text, top_k=3)

        # Enhance JSON schema detection with template library
        if output_format == "json" and matched_templates:
            json_schema = self._enhance_json_schema_with_templates(json_schema, matched_templates)

        # Calculate overall confidence
        confidence = self._calculate_confidence(prompt_text, output_format, format_confidence, json_schema, csv_columns, list_pattern)

        return AnalysisResult(
            template_variables=template_vars,
            output_format=output_format,
            json_schema=json_schema,
            csv_columns=csv_columns,
            list_pattern=list_pattern,
            validation_hints=validation_hints,
            confidence=confidence,
            patterns={"format_confidence": format_confidence, "has_examples": self._has_examples(prompt_text), "has_constraints": len(validation_hints) > 0},
            matched_templates=matched_templates,
        )

    def _extract_template_variables(self, prompt_text: str) -> List[str]:
        """Extract template variables like {variable} from prompt."""
        # First, replace double braces {{}} with placeholders to ignore them
        # This handles escaped braces that shouldn't be treated as variables
        text = prompt_text.replace("{{", "<<DOUBLE_OPEN>>").replace("}}", "<<DOUBLE_CLOSE>>")

        # More strict pattern to avoid matching JSON content
        # Allow alphanumeric, underscore, and Unicode word characters
        # But must start with a letter or underscore (not a number)
        # Don't allow special regex characters like *, [], .
        pattern = r"\{([a-zA-Z_\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff][a-zA-Z0-9_\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]*)\}"
        matches = re.findall(pattern, text)

        # Clean up variable names and remove duplicates
        variables = []
        for match in matches:
            var_name = match.strip()
            if var_name and var_name not in variables:
                # Skip if it looks like JSON property (contains quotes or colons)
                if '"' not in var_name and ":" not in var_name and "," not in var_name:
                    variables.append(var_name)

        return variables

    def _detect_output_format(self, prompt_text: str) -> tuple[str, float]:
        """
        Detect the expected output format.

        Returns:
            Tuple of (format_name, confidence_score)
        """
        # Remove template variables from text to avoid false positives
        # Replace {variable_name} with placeholder to not trigger format detection
        text_without_vars = re.sub(r"\{[^}]+\}", "VAR", prompt_text)
        text_lower = text_without_vars.lower()

        # Count indicators for each format
        json_score = self._count_indicators(text_lower, self.json_indicators)
        csv_score = self._count_indicators(text_lower, self.csv_indicators)
        list_score = self._count_indicators(text_lower, self.list_indicators)

        # Determine format based on highest score
        max_score = max(json_score, csv_score, list_score)

        if max_score == 0:
            return "text", 0.3  # Default to text with low confidence

        if json_score == max_score:
            return "json", min(0.9, 0.3 + json_score * 0.1)
        elif csv_score == max_score:
            return "csv", min(0.9, 0.3 + csv_score * 0.1)
        elif list_score == max_score:
            return "list", min(0.9, 0.3 + list_score * 0.1)
        else:
            return "text", 0.3

    def _count_indicators(self, text: str, indicators: List[str]) -> int:
        """Count how many indicators are found in text."""
        count = 0
        for indicator in indicators:
            if re.search(indicator, text, re.IGNORECASE):
                count += 1
        return count

    def _extract_json_schema(self, prompt_text: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON schema from prompt examples or descriptions.

        Enhanced to detect nested objects and arrays.
        """
        # Look for JSON-like structures in the prompt
        # Enhanced patterns to find nested structures
        json_patterns = [
            r"\{[^{}]*\{[^{}]*\}[^{}]*\}",  # Nested objects
            r"\[[^\[\]]*\{[^{}]*\}[^\[\]]*\]",  # Array of objects
            r'\{[^{}]*"[^"]*":[^{}]*\}',  # Simple JSON objects
            r"\{[^{}]*\}",  # Any curly braces content
        ]

        schema: dict[str, Any] = {"type": "object", "properties": {}}
        found_properties: dict[str, Any] = {}  # Changed to dict to store type info

        # Try to find and parse complete JSON examples
        # Look for code blocks first
        code_block_pattern = r"```(?:json)?\s*\n?([\s\S]*?)\n?```"
        code_blocks = re.findall(code_block_pattern, prompt_text)

        for block in code_blocks:
            try:
                parsed = json.loads(block.strip())
                if isinstance(parsed, dict):
                    self._extract_schema_from_json(parsed, found_properties)
                elif isinstance(parsed, list) and parsed:
                    # Handle array of objects
                    schema["type"] = "array"
                    schema["items"] = {"type": "object", "properties": {}}
                    if isinstance(parsed[0], dict):
                        self._extract_schema_from_json(parsed[0], schema["items"]["properties"])
                    return schema
            except:
                pass

        # If no code blocks, try other patterns
        # First try to find complete JSON blocks
        json_block_pattern = r"\{[^{}]*(?:\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}[^{}]*)*\}"
        large_matches = re.findall(json_block_pattern, prompt_text, re.DOTALL)

        for match in large_matches:
            try:
                parsed = json.loads(match.strip())
                if isinstance(parsed, dict):
                    self._extract_schema_from_json(parsed, found_properties)
            except:
                # If full parsing fails, try smaller patterns
                for pattern in json_patterns:
                    inner_matches = re.findall(pattern, match, re.DOTALL)
                    for inner_match in inner_matches:
                        try:
                            # Clean up the match to make it valid JSON
                            cleaned = inner_match.strip()
                            if not cleaned.startswith("{") and "{" in cleaned:
                                cleaned = cleaned[cleaned.index("{") :]
                            if not cleaned.endswith("}") and "}" in cleaned:
                                cleaned = cleaned[: cleaned.rindex("}") + 1]

                            parsed = json.loads(cleaned)
                            if isinstance(parsed, dict):
                                self._extract_schema_from_json(parsed, found_properties)
                        except:
                            # If parsing fails, look for quoted strings that might be keys
                            key_pattern = r'"([^"]+)":\s*(?:"[^"]*"|[0-9.]+|true|false|null|\{[^}]*\}|\[[^\]]*\])'
                            key_matches = re.findall(key_pattern, inner_match)
                            for key in key_matches:
                                if key not in found_properties:
                                    found_properties[key] = {"type": "string"}

        # Look for key descriptions in text
        # First, find root-level properties only (not indented)
        root_prop_pattern = r"^-\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]+)\)[^:]*:\s*(.*)$"
        lines = prompt_text.split("\n")
        # Detect the base indentation level
        base_indent = 0
        for line in lines:
            if line.strip():  # First non-empty line
                base_indent = len(line) - len(line.lstrip())
                break

        for i, line in enumerate(lines):
            if line.strip():
                # Calculate relative indentation
                current_indent = len(line) - len(line.lstrip())
                relative_indent = current_indent - base_indent

                if relative_indent == 0:  # Root level item
                    match = re.match(root_prop_pattern, line.strip())
                    if match:
                        key = match.group(1)
                        type_hint = match.group(2).lower()

                        # Skip words that aren't property names
                        if key.lower() in ["create", "generate", "following", "fields", "containing"]:
                            continue

                        if key not in found_properties:  # Don't overwrite existing entries
                            if "array of object" in type_hint:
                                found_properties[key] = {"type": "array", "items": {"type": "object", "properties": {}}}
                            elif "array" in type_hint or "list" in type_hint:
                                found_properties[key] = {"type": "array", "items": {"type": "string"}}
                            elif "object" in type_hint:
                                found_properties[key] = {"type": "object", "properties": {}}
                            elif "number" in type_hint or "int" in type_hint:
                                found_properties[key] = {"type": "number"}
                            elif "bool" in type_hint:
                                found_properties[key] = {"type": "boolean"}
                            elif "string" in type_hint:
                                found_properties[key] = {"type": "string"}
                            else:
                                found_properties[key] = {"type": "string"}

        # Process nested properties by looking at indentation
        # Second pass: find nested properties under objects
        current_object = None

        for i, line in enumerate(lines):
            if line.strip():
                current_indent = len(line) - len(line.lstrip())
                relative_indent = current_indent - base_indent

                # Check if this is an object declaration
                if relative_indent == 0:
                    object_match = re.match(r"^-\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(object\)", line.strip())
                    if object_match:
                        current_object = object_match.group(1)

                # Check if this is a nested property
                elif relative_indent > 0 and current_object and current_object in found_properties:
                    nested_match = re.match(r"^-\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]+)\)", line.strip())
                    if nested_match:
                        prop_name = nested_match.group(1)
                        prop_type = nested_match.group(2).lower()

                        if "properties" not in found_properties[current_object]:
                            found_properties[current_object]["properties"] = {}

                        if "array of object" in prop_type:
                            found_properties[current_object]["properties"][prop_name] = {"type": "array", "items": {"type": "object", "properties": {}}}
                        elif "array" in prop_type:
                            found_properties[current_object]["properties"][prop_name] = {"type": "array", "items": {"type": "string"}}
                        elif "object" in prop_type:
                            found_properties[current_object]["properties"][prop_name] = {"type": "object", "properties": {}}
                        elif "number" in prop_type or "int" in prop_type:
                            found_properties[current_object]["properties"][prop_name] = {"type": "number"}
                        elif "bool" in prop_type:
                            found_properties[current_object]["properties"][prop_name] = {"type": "boolean"}
                        elif "string" in prop_type:
                            found_properties[current_object]["properties"][prop_name] = {"type": "string"}
                        else:
                            found_properties[current_object]["properties"][prop_name] = {"type": "string"}

        # Build schema from found properties
        if found_properties:
            schema["properties"] = found_properties
            schema["required"] = list(found_properties.keys())
            return schema

        # If we detect JSON format but no properties, return minimal schema
        return None

    def _extract_schema_from_json(self, json_obj: Union[Dict, List], schema_properties: Dict[str, Any]) -> None:
        """
        Recursively extract schema from a JSON object.

        Args:
            json_obj: The JSON object to analyze
            schema_properties: Dictionary to populate with schema properties
        """
        if isinstance(json_obj, dict):
            for key, value in json_obj.items():
                if isinstance(value, dict):
                    schema_properties[key] = {"type": "object", "properties": {}}
                    self._extract_schema_from_json(value, schema_properties[key]["properties"])
                elif isinstance(value, list):
                    schema_properties[key] = {"type": "array", "items": {}}
                    if value:  # If list is not empty
                        if isinstance(value[0], dict):
                            schema_properties[key]["items"] = {"type": "object", "properties": {}}
                            self._extract_schema_from_json(value[0], schema_properties[key]["items"]["properties"])
                        elif isinstance(value[0], str):
                            schema_properties[key]["items"] = {"type": "string"}
                        elif isinstance(value[0], (int, float)):
                            schema_properties[key]["items"] = {"type": "number"}
                        elif isinstance(value[0], bool):
                            schema_properties[key]["items"] = {"type": "boolean"}
                    else:
                        schema_properties[key]["items"] = {"type": "string"}  # Default
                elif isinstance(value, str):
                    schema_properties[key] = {"type": "string"}
                elif isinstance(value, bool):
                    schema_properties[key] = {"type": "boolean"}
                elif isinstance(value, (int, float)):
                    schema_properties[key] = {"type": "number"}
                elif value is None:
                    schema_properties[key] = {"type": "null"}

    def _extract_csv_columns(self, prompt_text: str) -> Optional[List[str]]:
        """Extract CSV column names from prompt."""
        columns = []

        # Look for explicit column definitions
        column_patterns = [
            r"columns?:\s*([^\n]+)",
            r"headers?:\s*([^\n]+)",
            r"([A-Za-z][A-Za-z0-9_]*),\s*([A-Za-z][A-Za-z0-9_]*),\s*([A-Za-z][A-Za-z0-9_]*)",
        ]

        for pattern in column_patterns:
            matches = re.findall(pattern, prompt_text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    columns.extend([col.strip() for col in match if col.strip()])
                else:
                    # Split by comma and clean
                    cols = [col.strip() for col in match.split(",")]
                    columns.extend([col for col in cols if col])

        return columns if columns else None

    def _extract_list_pattern(self, prompt_text: str) -> Optional[str]:
        """Extract list item pattern from prompt."""
        # Look for list examples
        list_patterns = [
            r"^\d+\.\s*(.+)$",  # 1. item
            r"^\*\s*(.+)$",  # * item
            r"^-\s*(.+)$",  # - item
        ]

        lines = prompt_text.split("\n")
        patterns_found = []

        for line in lines:
            line = line.strip()
            for pattern in list_patterns:
                match = re.match(pattern, line)
                if match:
                    patterns_found.append(match.group(1))

        if patterns_found:
            # Return the most common pattern or first one
            return patterns_found[0]

        return None

    def _extract_validation_hints(self, prompt_text: str) -> List[str]:
        """Extract validation requirements from prompt text."""
        hints = []
        text_lower = prompt_text.lower()

        # Look for validation keywords and their context
        for keyword in self.validation_keywords:
            if keyword in text_lower:
                # Find sentences containing the keyword
                sentences = re.split(r"[.!?]+", prompt_text)
                for sentence in sentences:
                    if keyword.lower() in sentence.lower():
                        hints.append(sentence.strip())

        return hints

    def _has_examples(self, prompt_text: str) -> bool:
        """Check if prompt contains examples of expected output."""
        example_indicators = ["example:", "for example", "like:", "such as", "```", "sample:", "output:", "format:"]

        text_lower = prompt_text.lower()
        return any(indicator in text_lower for indicator in example_indicators)

    def _calculate_confidence(self, prompt_text: str, output_format: str, format_confidence: float, json_schema: Optional[Dict], csv_columns: Optional[List], list_pattern: Optional[str]) -> float:
        """Calculate overall confidence in the analysis."""
        base_confidence = format_confidence

        # Boost confidence based on additional details found
        if output_format == "json" and json_schema:
            base_confidence += 0.2
        elif output_format == "csv" and csv_columns:
            base_confidence += 0.2
        elif output_format == "list" and list_pattern:
            base_confidence += 0.2

        # Boost confidence if examples are present
        if self._has_examples(prompt_text):
            base_confidence += 0.1

        # Ensure confidence stays within bounds
        return min(1.0, max(0.0, base_confidence))

    def _enhance_json_schema_with_templates(self, detected_schema: Optional[Dict[str, Any]], matched_templates: List[Tuple[PromptTemplate, float]]) -> Optional[Dict[str, Any]]:
        """Enhance detected JSON schema using matched templates."""
        if not matched_templates:
            return detected_schema

        # Find the best matching JSON template
        best_json_template = None
        best_score = 0.0

        for template, score in matched_templates:
            if template.json_schema and template.category == "json" and score > best_score:
                best_json_template = template
                best_score = score

        if best_json_template and best_score > 0.5:  # Use template if similarity is high enough
            template_schema = best_json_template.json_schema
            if template_schema is None:
                return detected_schema

            if detected_schema:
                # Merge detected schema with template schema
                merged_schema = template_schema.copy()
                if "properties" in detected_schema:
                    merged_schema.setdefault("properties", {}).update(detected_schema["properties"])
                if "required" in detected_schema:
                    merged_schema["required"] = list(set(merged_schema.get("required", []) + detected_schema["required"]))
                return merged_schema
            else:
                # Use template schema directly
                return template_schema

        return detected_schema
