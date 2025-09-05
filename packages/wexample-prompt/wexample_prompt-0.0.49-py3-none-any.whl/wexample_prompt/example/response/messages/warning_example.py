from __future__ import annotations

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.messages.warning_prompt_response import (
    WarningPromptResponse,
)


class WarningExample(AbstractResponseExample):
    def get_test_message(self) -> str:
        return "Test warning message"

    def example_manager(self) -> None:
        self.io.warning(message=self.get_test_message())

    def example_class(self):
        return WarningPromptResponse.create_warning(
            message=self.get_test_message(),
        )

    def example_extended(self) -> None:
        self._class_with_methods.warning(message=self.get_test_message())
