from __future__ import annotations

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.messages.info_prompt_response import InfoPromptResponse


class InfoExample(AbstractResponseExample):
    def get_test_message(self) -> str:
        return "Test info message"

    def example_manager(self) -> None:
        self.io.info(message=self.get_test_message())

    def example_class(self):
        return InfoPromptResponse.create_info(
            message=self.get_test_message(),
        )

    def example_extended(self) -> None:
        self._class_with_methods.info(message=self.get_test_message())
