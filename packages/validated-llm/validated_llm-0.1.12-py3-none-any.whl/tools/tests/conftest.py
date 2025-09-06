"""
Pytest configuration for tools tests.
"""

import os
import tempfile
from typing import Generator

import pytest


@pytest.fixture(autouse=True)
def clean_test_environment(monkeypatch: pytest.MonkeyPatch) -> Generator[str, None, None]:
    """
    Ensure tests run in a clean temporary directory to avoid
    creating files in the project root.
    """
    # Set TESTING environment variable
    monkeypatch.setenv("TESTING", "true")

    # Store original directory
    original_dir = os.getcwd()

    # Create and change to temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        try:
            yield temp_dir
        finally:
            # Always return to original directory
            os.chdir(original_dir)


@pytest.fixture
def in_project_dir() -> str:
    """
    Fixture for tests that need to run in the actual project directory.
    Use sparingly - most tests should use the clean environment.
    """
    return os.getcwd()
