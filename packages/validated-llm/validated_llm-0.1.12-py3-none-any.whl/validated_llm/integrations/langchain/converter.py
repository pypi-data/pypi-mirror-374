"""
Langchain to validated-llm converter.

This module provides functionality to convert Langchain prompts and chains
to validated-llm tasks.
"""

import re
from typing import Any, Dict, List, Optional, Type, cast

from validated_llm.base_validator import BaseValidator
from validated_llm.integrations.langchain import check_langchain_installed
from validated_llm.tasks import BaseTask


class PromptTemplateConverter:
    """Convert Langchain PromptTemplate to validated-llm BaseTask."""

    def __init__(self) -> None:
        """Initialize converter."""
        check_langchain_installed()

    def analyze_prompt(self, template: str) -> Dict[str, Any]:
        """Analyze a prompt template to infer its purpose and suggest validators.

        Args:
            template: The prompt template string

        Returns:
            Dictionary with analysis results including suggested validators
        """
        analysis: Dict[str, Any] = {"template": template, "variables": self._extract_variables(template), "output_type": self._infer_output_type(template), "suggested_validators": []}

        # Analyze template content for validator suggestions
        template_lower = template.lower()

        if any(word in template_lower for word in ["json", "object", "structure"]):
            analysis["suggested_validators"].append("JSONValidator")
            analysis["output_type"] = "json"
        elif any(word in template_lower for word in ["list", "items", "bullet"]):
            analysis["suggested_validators"].append("ListValidator")
            analysis["output_type"] = "list"
        elif any(word in template_lower for word in ["markdown", "blog", "article"]):
            analysis["suggested_validators"].append("MarkdownValidator")
            analysis["output_type"] = "markdown"
        elif any(word in template_lower for word in ["email", "message"]):
            analysis["suggested_validators"].append("EmailValidator")
            analysis["output_type"] = "email"
        elif any(word in template_lower for word in ["code", "function", "class"]):
            analysis["suggested_validators"].append("SyntaxValidator")
            analysis["output_type"] = "code"
        else:
            analysis["suggested_validators"].append("RegexValidator")
            analysis["output_type"] = "text"

        return analysis

    def _extract_variables(self, template: str) -> List[str]:
        """Extract variable names from template string.

        Args:
            template: Template string with {variable} placeholders

        Returns:
            List of variable names
        """
        # Find all {variable} patterns
        pattern = r"\{(\w+)\}"
        return list(set(re.findall(pattern, template)))

    def _infer_output_type(self, template: str) -> str:
        """Infer the expected output type from template content.

        Args:
            template: The prompt template string

        Returns:
            Inferred output type (json, list, text, etc.)
        """
        template_lower = template.lower()

        # Check for explicit format indicators
        if "json" in template_lower:
            return "json"
        elif any(word in template_lower for word in ["list", "enumerate", "bullet"]):
            return "list"
        elif "markdown" in template_lower:
            return "markdown"
        elif "code" in template_lower:
            return "code"
        else:
            return "text"

    def convert_prompt_template(self, langchain_prompt: Any, task_name: str, validator_class: Optional[Type[BaseValidator]] = None, validator_hints: Optional[List[str]] = None) -> Type[BaseTask]:
        """Convert a Langchain PromptTemplate to a validated-llm BaseTask.

        Args:
            langchain_prompt: Langchain PromptTemplate instance
            task_name: Name for the generated task class
            validator_class: Optional specific validator class to use
            validator_hints: Optional hints for validator selection

        Returns:
            A BaseTask subclass configured with the prompt template
        """
        from langchain.prompts import PromptTemplate

        if not isinstance(langchain_prompt, PromptTemplate):
            raise TypeError(f"Expected PromptTemplate, got {type(langchain_prompt)}")

        # Extract template and variables
        template = langchain_prompt.template
        input_variables = langchain_prompt.input_variables

        # Analyze prompt if no validator specified
        if validator_class is None:
            analysis = self.analyze_prompt(template)
            validator_class = self._get_validator_class(analysis["suggested_validators"][0] if analysis["suggested_validators"] else "RegexValidator")

        # validator_class should not be None after this point
        final_validator_class = validator_class

        # Create task class dynamically
        class ConvertedTask(BaseTask):
            prompt_template: str = template
            validator_class: Type[BaseValidator] = final_validator_class

            @classmethod
            def get_prompt_variables(cls) -> List[str]:
                """Get the list of variables needed for the prompt."""
                return list(input_variables)

        # Set the class name
        ConvertedTask.__name__ = task_name
        ConvertedTask.__qualname__ = task_name

        return ConvertedTask

    def _get_validator_class(self, validator_name: str) -> Type[BaseValidator]:
        """Get validator class by name.

        Args:
            validator_name: Name of the validator

        Returns:
            Validator class
        """
        # Import validators dynamically
        from validated_llm import validators

        validator_map = {
            "JSONValidator": validators.RegexValidator,  # Use RegexValidator as fallback for JSON
            "MarkdownValidator": validators.MarkdownValidator,
            "EmailValidator": validators.EmailValidator,
            "RegexValidator": validators.RegexValidator,
            "DateTimeValidator": validators.DateTimeValidator,
            "URLValidator": validators.URLValidator,
        }

        # Default to RegexValidator if not found
        return cast(Type[BaseValidator], validator_map.get(validator_name, validators.RegexValidator))
