from __future__ import annotations

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.messages.task_prompt_response import TaskPromptResponse


class TaskExample(AbstractResponseExample):
    def get_test_message(self) -> str:
        return "Test task message"

    def example_manager(self) -> None:
        self.io.task(message=self.get_test_message())

    def example_class(self):
        return TaskPromptResponse.create_task(
            message=self.get_test_message(),
        )

    def example_extended(self) -> None:
        self._class_with_methods.task(message=self.get_test_message())
