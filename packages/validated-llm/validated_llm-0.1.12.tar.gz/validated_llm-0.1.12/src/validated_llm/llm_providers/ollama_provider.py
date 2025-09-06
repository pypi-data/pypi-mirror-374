"""
Ollama provider implementation.
"""

from typing import Any, Optional

from openai import OpenAI

from .base import LLMProvider


class OllamaProvider(LLMProvider):
    """
    Ollama LLM provider implementation.

    Uses OpenAI-compatible API provided by Ollama at http://localhost:11434/v1
    """

    def __init__(
        self,
        model: str = "smollm2:latest",
        api_key: Optional[str] = None,
        base_url: str = "http://localhost:11434/v1",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize Ollama provider.

        Args:
            model: Ollama model name (e.g., "llama3.1", "smollm2:latest")
            api_key: Not used for Ollama (compatibility parameter)
            base_url: Ollama API base URL
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens in response
            **kwargs: Additional parameters
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.extra_kwargs = kwargs

        # Initialize OpenAI client pointing to Ollama
        # Ollama doesn't require an API key, but OpenAI client requires one
        self.client = OpenAI(
            api_key="ollama",  # Dummy API key for Ollama
            base_url=base_url,
        )

    def generate(self, system_prompt: str, user_message: str) -> str:
        """
        Generate response using Ollama API.

        Args:
            system_prompt: System prompt for context/instructions
            user_message: User's message/query

        Returns:
            LLM response content

        Raises:
            Exception: If API request fails or Ollama is not available
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        # Build request parameters
        params = {
            "model": self.model,
            "messages": messages,
            **self.extra_kwargs,
        }

        if self.temperature is not None:
            params["temperature"] = self.temperature
        if self.max_tokens is not None:
            params["max_tokens"] = self.max_tokens

        try:
            # Make API request to Ollama
            response = self.client.chat.completions.create(**params)

            # Extract content from response
            if not response.choices:
                raise ValueError("No response choices returned from Ollama API")

            content = response.choices[0].message.content
            if content is None:
                raise ValueError("Empty content returned from Ollama API")

            return str(content)

        except Exception as e:
            # Provide helpful error message for common Ollama issues
            error_msg = str(e).lower()
            if "connection" in error_msg or "refused" in error_msg:
                raise ConnectionError(f"Cannot connect to Ollama at {self.client.base_url}. " "Make sure Ollama is running (try: ollama serve)") from e
            elif "not found" in error_msg or "does not exist" in error_msg:
                raise ValueError(f"Model '{self.model}' not found in Ollama. " f"Try: ollama pull {self.model}") from e
            else:
                raise
