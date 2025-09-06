"""
Base LLM provider abstraction.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    Provides a minimal interface for LLM communication focused on
    single request/response interactions with system prompts.
    """

    @abstractmethod
    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ):
        """
        Initialize the LLM provider.

        Args:
            model: The model name to use
            api_key: API key for authentication (if required)
            base_url: Base URL for the API endpoint
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            **kwargs: Additional provider-specific parameters
        """
        pass

    @abstractmethod
    def generate(self, system_prompt: str, user_message: str) -> str:
        """
        Generate a response from the LLM.

        Args:
            system_prompt: The system prompt to set context/instructions
            user_message: The user's message/query

        Returns:
            The LLM's response as a string

        Raises:
            Exception: If the LLM request fails
        """
        pass
