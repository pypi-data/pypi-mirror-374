"""
Base class for LLM validation tasks.

Tasks represent complete LLM workflows that pair prompts with validators.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Type

from ..base_validator import BaseValidator


class BaseTask(ABC):
    """
    Abstract base class for LLM validation tasks.

    A task combines a prompt template with its corresponding validator,
    ensuring they work together as a cohesive unit.
    """

    @property
    @abstractmethod
    def prompt_template(self) -> str:
        """The prompt template for this task."""

    @property
    @abstractmethod
    def validator_class(self) -> Type[BaseValidator]:
        """The validator class for this task."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name for this task."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what this task does."""

    def create_validator(self, **kwargs: Any) -> BaseValidator:
        """
        Create a validator instance for this task.

        Args:
            **kwargs: Arguments to pass to the validator constructor

        Returns:
            Configured validator instance
        """
        return self.validator_class(**kwargs)

    def get_prompt_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Prepare data for the prompt template.

        Args:
            **kwargs: Input data for the prompt

        Returns:
            Dictionary to format the prompt template
        """
        return kwargs

    def format_prompt(self, **kwargs: Any) -> str:
        """
        Format the prompt template with provided data.

        Args:
            **kwargs: Input data for the prompt

        Returns:
            Formatted prompt string
        """
        prompt_data = self.get_prompt_data(**kwargs)
        return self.prompt_template.format(**prompt_data)

    def __str__(self) -> str:
        return f"{self.name} ({self.__class__.__name__})"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name}>"
