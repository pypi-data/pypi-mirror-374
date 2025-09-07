"""
Common types and data structures for batch conversion.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional


class ConversionStatus(Enum):
    """Status of a single file conversion."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ConversionResult:
    """Result of converting a single prompt file."""

    input_file: Path
    output_file: Optional[Path] = None
    status: ConversionStatus = ConversionStatus.PENDING
    error_message: Optional[str] = None
    task_name: Optional[str] = None
    validators_used: List[str] = field(default_factory=list)
    processing_time: float = 0.0


@dataclass
class BatchConfig:
    """Configuration for batch conversion."""

    output_dir: Optional[Path] = None
    output_suffix: str = "_task.py"
    skip_existing: bool = True
    parallel: bool = True
    max_workers: int = 4
    dry_run: bool = False
    interactive: bool = False
    template_name: Optional[str] = None
    common_validators: List[str] = field(default_factory=list)
    file_patterns: List[str] = field(default_factory=lambda: ["*.txt", "*.prompt", "*.md"])
    exclude_patterns: List[str] = field(default_factory=lambda: ["*_task.py", "README.md"])
