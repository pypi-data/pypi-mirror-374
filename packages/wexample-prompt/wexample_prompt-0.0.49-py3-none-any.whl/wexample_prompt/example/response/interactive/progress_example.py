"""Example usage of ProgressPromptResponse."""

from __future__ import annotations

import time

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.interactive.progress_prompt_response import (
    ProgressPromptResponse,
)


def step1() -> None:
    """First step: Initialize system."""
    time.sleep(0.2)


def step2() -> None:
    """Second step: Process data."""
    time.sleep(0.4)


def step3() -> None:
    """Third step: Cleanup."""
    time.sleep(0.2)


class ProgressExample(AbstractResponseExample):
    """Example usage of progress responses."""

    def example_class(self, indentation: int | None = None):
        """Example using the response class directly."""
        return ProgressPromptResponse.create_progress(
            total=5,
            current=3,
            label="Processing",
        )

    def example_manager(self) -> None:
        """Example using the IoManager."""
        self.io.progress(
            total=5,
            current=3,
            label="Processing",
        )

    def example_extended(self) -> None:
        """Example using a context class."""
        self._class_with_methods.progress(
            total=5,
            current=3,
            label="Processing",
        )
