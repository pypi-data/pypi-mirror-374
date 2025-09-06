"""
Progress reporting for batch conversion operations.

Provides different progress reporting backends including rich and tqdm.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .batch_types import ConversionResult, ConversionStatus


class ProgressReporter(ABC):
    """Abstract base class for progress reporting."""

    @abstractmethod
    def start(self, total: int, description: str = "Converting files") -> None:
        """Start progress reporting."""
        pass

    @abstractmethod
    def update(self, result: ConversionResult) -> None:
        """Update progress with a conversion result."""
        pass

    @abstractmethod
    def finish(self) -> None:
        """Finish progress reporting."""
        pass


class SimpleProgressReporter(ProgressReporter):
    """Simple text-based progress reporter."""

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.total = 0
        self.completed = 0

    def start(self, total: int, description: str = "Converting files") -> None:
        self.total = total
        self.completed = 0
        if self.verbose:
            print(f"\n{description}: {total} files")
            print("-" * 50)

    def update(self, result: ConversionResult) -> None:
        self.completed += 1
        if self.verbose:
            status_symbol = {ConversionStatus.SUCCESS: "✅", ConversionStatus.FAILED: "❌", ConversionStatus.SKIPPED: "⏭️"}.get(result.status, "❓")

            print(f"{status_symbol} [{self.completed}/{self.total}] {result.input_file.name}")

            if result.status == ConversionStatus.FAILED and result.error_message:
                print(f"   Error: {result.error_message}")

    def finish(self) -> None:
        if self.verbose:
            print("-" * 50)


class RichProgressReporter(ProgressReporter):
    """Progress reporter using rich library for beautiful output."""

    def __init__(self) -> None:
        try:
            from rich.console import Console
            from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeRemainingColumn
            from rich.table import Table

            self.console = Console()
            self.Progress = Progress
            self.SpinnerColumn = SpinnerColumn
            self.BarColumn = BarColumn
            self.TextColumn = TextColumn
            self.TimeRemainingColumn = TimeRemainingColumn
            self.Table = Table
            self.available = True
        except ImportError:
            self.available = False

        self.progress: Optional[Any] = None
        self.task: Optional[Any] = None
        self.results: List[ConversionResult] = []

    def start(self, total: int, description: str = "Converting files") -> None:
        if not self.available:
            return

        self.results = []
        self.progress = self.Progress(
            self.SpinnerColumn(),
            self.TextColumn("[progress.description]{task.description}"),
            self.BarColumn(),
            self.TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            self.TimeRemainingColumn(),
        )
        self.progress.start()
        self.task = self.progress.add_task(description, total=total)

    def update(self, result: ConversionResult) -> None:
        if not self.available or not self.progress:
            return

        self.results.append(result)
        self.progress.update(self.task, advance=1)

        # Update description with current file
        status_symbol = {ConversionStatus.SUCCESS: "✅", ConversionStatus.FAILED: "❌", ConversionStatus.SKIPPED: "⏭️"}.get(result.status, "❓")

        self.progress.update(self.task, description=f"{status_symbol} {result.input_file.name}")

    def finish(self) -> None:
        if not self.available or not self.progress:
            return

        self.progress.stop()

        # Show summary table
        table = self.Table(title="Conversion Summary")
        table.add_column("Status", style="cyan", no_wrap=True)
        table.add_column("Count", justify="right", style="magenta")

        status_counts: Dict[ConversionStatus, int] = {}
        for result in self.results:
            status_counts[result.status] = status_counts.get(result.status, 0) + 1

        for status, count in status_counts.items():
            status_symbol = {ConversionStatus.SUCCESS: "✅ Success", ConversionStatus.FAILED: "❌ Failed", ConversionStatus.SKIPPED: "⏭️  Skipped"}.get(status, str(status))

            table.add_row(status_symbol, str(count))

        self.console.print(table)


class TqdmProgressReporter(ProgressReporter):
    """Progress reporter using tqdm library."""

    def __init__(self) -> None:
        try:
            from tqdm import tqdm

            self.tqdm = tqdm
            self.available = True
        except ImportError:
            self.available = False

        self.pbar: Optional[Any] = None

    def start(self, total: int, description: str = "Converting files") -> None:
        if not self.available:
            return

        self.pbar = self.tqdm(total=total, desc=description, unit="file", ncols=80)

    def update(self, result: ConversionResult) -> None:
        if not self.available or not self.pbar:
            return

        status_symbol = {ConversionStatus.SUCCESS: "✅", ConversionStatus.FAILED: "❌", ConversionStatus.SKIPPED: "⏭️"}.get(result.status, "❓")

        self.pbar.set_postfix_str(f"{status_symbol} {result.input_file.name}")
        self.pbar.update(1)

    def finish(self) -> None:
        if not self.available or not self.pbar:
            return

        self.pbar.close()


def create_progress_reporter(reporter_type: str = "auto", verbose: bool = True) -> ProgressReporter:
    """Factory function to create appropriate progress reporter."""
    if reporter_type == "auto":
        # Try rich first, then tqdm, fallback to simple
        rich_reporter = RichProgressReporter()
        if rich_reporter.available:
            return rich_reporter

        tqdm_reporter = TqdmProgressReporter()
        if tqdm_reporter.available:
            return tqdm_reporter

        return SimpleProgressReporter(verbose=verbose)

    elif reporter_type == "rich":
        reporter = RichProgressReporter()
        if reporter.available:
            return reporter
        return SimpleProgressReporter(verbose=verbose)

    elif reporter_type == "tqdm":
        tqdm_reporter = TqdmProgressReporter()
        if tqdm_reporter.available:
            return tqdm_reporter
        return SimpleProgressReporter(verbose=verbose)

    elif reporter_type == "simple":
        return SimpleProgressReporter(verbose=verbose)

    elif reporter_type == "none":
        return SimpleProgressReporter(verbose=False)

    else:
        return SimpleProgressReporter(verbose=verbose)
