from __future__ import annotations

from wexample_prompt.example.abstract_response_example import AbstractResponseExample


class EchoExample(AbstractResponseExample):
    def get_test_message(self) -> str:
        return "Test echo message"

    def example_manager(self) -> None:
        self.io.echo(message=self.get_test_message())

    def example_class(self):
        from wexample_prompt.responses.echo_prompt_response import EchoPromptResponse

        return EchoPromptResponse.create_echo(
            message=self.get_test_message(),
        )

    def example_extended(self) -> None:
        self._class_with_methods.echo(self.get_test_message())
