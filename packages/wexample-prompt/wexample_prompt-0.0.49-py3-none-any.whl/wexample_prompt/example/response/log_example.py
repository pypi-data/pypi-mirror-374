from __future__ import annotations

from wexample_prompt.example.abstract_response_example import AbstractResponseExample


class LogExample(AbstractResponseExample):
    def get_test_message(self) -> str:
        return "Test log message"

    def example_manager(self) -> None:
        self.io.log(message=self.get_test_message())

    def example_class(self):
        from wexample_prompt.responses.log_prompt_response import LogPromptResponse

        return LogPromptResponse.create_log(
            message=self.get_test_message(),
        )

    def example_extended(self) -> None:
        self._class_with_methods.log(message=self.get_test_message())
