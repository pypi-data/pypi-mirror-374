"""
OpenAI provider implementation.
"""

import os
from typing import Any, Optional

from openai import OpenAI

from .base import LLMProvider


class OpenAIProvider(LLMProvider):
    """
    OpenAI LLM provider implementation.

    Supports OpenAI API and compatible endpoints (including Anthropic via OpenAI SDK).
    """

    def __init__(
        self,
        model: str = "gpt-4o",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize OpenAI provider.

        Args:
            model: Model name (e.g., "gpt-4o", "gpt-4", "claude-3-5-sonnet-latest")
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            base_url: Custom base URL (e.g., for Anthropic: "https://api.anthropic.com/v1")
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens in response
            **kwargs: Additional OpenAI client parameters
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.extra_kwargs = kwargs

        # Initialize OpenAI client
        client_kwargs = {}
        if api_key is not None:
            client_kwargs["api_key"] = api_key
        elif "OPENAI_API_KEY" in os.environ:
            client_kwargs["api_key"] = os.environ["OPENAI_API_KEY"]
        else:
            # Let OpenAI SDK handle default key discovery
            pass

        if base_url is not None:
            client_kwargs["base_url"] = base_url

        self.client = OpenAI(**client_kwargs)

    def generate(self, system_prompt: str, user_message: str) -> str:
        """
        Generate response using OpenAI API.

        Args:
            system_prompt: System prompt for context/instructions
            user_message: User's message/query

        Returns:
            LLM response content

        Raises:
            Exception: If API request fails
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

        # Make API request
        response = self.client.chat.completions.create(**params)

        # Extract content from response
        if not response.choices:
            raise ValueError("No response choices returned from OpenAI API")

        content = response.choices[0].message.content
        if content is None:
            raise ValueError("Empty content returned from OpenAI API")

        return str(content)
