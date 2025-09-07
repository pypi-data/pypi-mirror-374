"""
LLM provider abstractions for validated-llm.

This module provides a simple abstraction layer for different LLM providers,
replacing the external chatbot dependency with lightweight, focused implementations.
"""

from .base import LLMProvider
from .ollama_provider import OllamaProvider
from .openai_provider import OpenAIProvider

__all__ = [
    "LLMProvider",
    "OpenAIProvider",
    "OllamaProvider",
]
