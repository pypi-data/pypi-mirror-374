from __future__ import annotations

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.interactive.choice_prompt_response import (
    ChoicePromptResponse,
)


class ChoiceExample(AbstractResponseExample):

    def example_class(self, indentation: int | None = None):
        return ChoicePromptResponse.create_choice(
            question="Select an option:",
            choices={
                "value1": "Choice 1",
                "value2": "Choice 2",
                "value3": "Choice 3",
            },
            default="value2",
            predefined_answer="value3",
        )

    def example_manager(self) -> None:
        choices = ["Option 1", "Option 2", "Option 3"]
        self.io.choice(
            question="Select an option:", choices=choices, predefined_answer="Option 2"
        )

    def example_extended(self) -> None:
        choices = ["Option 1", "Option 2", "Option 3"]
        self._class_with_methods.choice(
            question="Select an option:", choices=choices, predefined_answer="Option 2"
        )
