from __future__ import annotations

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.messages.success_prompt_response import (
    SuccessPromptResponse,
)


class SuccessExample(AbstractResponseExample):
    def get_test_message(self) -> str:
        return "Test success message"

    def example_manager(self) -> None:
        self.io.success(message=self.get_test_message())

    def example_class(self):
        return SuccessPromptResponse.create_success(
            message=self.get_test_message(),
        )

    def example_extended(self) -> None:
        self._class_with_methods.success(message=self.get_test_message())
