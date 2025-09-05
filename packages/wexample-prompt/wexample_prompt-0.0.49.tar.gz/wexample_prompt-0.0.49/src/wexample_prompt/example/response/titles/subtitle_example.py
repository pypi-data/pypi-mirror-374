from __future__ import annotations

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.titles.subtitle_prompt_response import (
    SubtitlePromptResponse,
)


class SubtitleExample(AbstractResponseExample):
    def get_test_message(self) -> str:
        return "Test subtitle"

    def example_manager(self) -> None:
        self.io.subtitle(message=self.get_test_message())

    def example_class(self):
        return SubtitlePromptResponse.create_subtitle(
            text=self.get_test_message() + " (from response)"
        )

    def example_extended(self) -> None:
        self._class_with_methods.title(
            message=self.get_test_message() + " (class method)"
        )
