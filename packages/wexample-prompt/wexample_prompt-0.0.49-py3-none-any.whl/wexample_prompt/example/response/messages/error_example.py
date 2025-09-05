from __future__ import annotations

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.messages.error_prompt_response import ErrorPromptResponse


class ErrorExample(AbstractResponseExample):
    def get_test_message(self) -> str:
        return "Test error message"

    def example_manager(self) -> None:
        self.io.error(message=self.get_test_message())

    def example_class(self):
        return ErrorPromptResponse.create_error(
            message=self.get_test_message(),
        )

    def example_extended(self) -> None:
        self._class_with_methods.error(message=self.get_test_message())
