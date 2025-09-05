"""Example usage of FilePickerPromptResponse."""

from __future__ import annotations

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.interactive.file_picker_prompt_response import (
    FilePickerPromptResponse,
)


class FilePickerExample(AbstractResponseExample):
    """Example usage of FilePickerPromptResponse."""

    def example_class(self, indentation: int | None = None):
        """Example using the class directly."""
        return FilePickerPromptResponse.create_file_picker(
            question="Select a file:",
            base_dir=None,  # Will use current working directory
            predefined_answer="some_file",
        )

    def example_manager(self) -> None:
        """Example using the IoManager."""
        self.io.file_picker(question="Select a file:", predefined_answer="some_file")

    def example_extended(self) -> None:
        """Example using PromptContext."""
        self._class_with_methods.file_picker(
            question="Select a file:", predefined_answer="some_file"
        )
