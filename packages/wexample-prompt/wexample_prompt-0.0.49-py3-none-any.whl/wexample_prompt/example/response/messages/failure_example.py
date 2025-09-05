from __future__ import annotations

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.messages.failure_prompt_response import (
    FailurePromptResponse,
)


class FailureExample(AbstractResponseExample):
    def get_test_message(self) -> str:
        return "Test failure message"

    def example_manager(self) -> None:
        self.io.failure(message=self.get_test_message())

    def example_class(self):
        return FailurePromptResponse.create_failure(
            message=self.get_test_message(),
        )

    def example_extended(self) -> None:
        self._class_with_methods.failure(message=self.get_test_message())
