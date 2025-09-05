from __future__ import annotations

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.messages.debug_prompt_response import DebugPromptResponse


class DebugExample(AbstractResponseExample):
    def get_test_message(self) -> str:
        return "Test debug message"

    def example_manager(self) -> None:
        self.io.debug(message=self.get_test_message())

    def example_class(self):
        return DebugPromptResponse.create_debug(
            message=self.get_test_message(),
        )

    def example_extended(self) -> None:
        self._class_with_methods.debug(message=self.get_test_message())
