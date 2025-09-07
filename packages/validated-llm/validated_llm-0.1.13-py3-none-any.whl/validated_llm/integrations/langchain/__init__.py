"""
Langchain integration for validated-llm.

This module provides tools to convert Langchain prompts and chains
to validated-llm tasks with automatic validation.
"""

from typing import Optional

try:
    import langchain

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


def check_langchain_installed() -> None:
    """Check if langchain is installed and raise helpful error if not."""
    if not LANGCHAIN_AVAILABLE:
        raise ImportError("Langchain is not installed. Please install it with:\n" "pip install langchain")


__all__ = ["check_langchain_installed", "LANGCHAIN_AVAILABLE"]
