"""Example usage of ConfirmPromptResponse."""

from __future__ import annotations

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.interactive.confirm_prompt_response import (
    ConfirmPromptResponse,
)


class ConfirmExample(AbstractResponseExample):
    """Example usage of confirmation dialog responses."""

    def example_class(self, indentation: int | None = None):
        """Use the response class directly."""
        return ConfirmPromptResponse.create_confirm(
            question="Proceed?",
            choices=ConfirmPromptResponse.MAPPING_PRESET_YES_NO_ALL,
            reset_on_finish=True,
            predefined_answer="yes",
        )

    def example_manager(self) -> None:
        """Use IoManager mixin method."""
        self.io.confirm(
            question="Proceed?",
            choices=ConfirmPromptResponse.MAPPING_PRESET_OK_CANCEL,
            reset_on_finish=True,
            predefined_answer="cancel",
        )

    def example_extended(self) -> None:
        """Use extended context with _class_with_methods."""
        self._class_with_methods.confirm(
            question="Proceed?",
            choices=ConfirmPromptResponse.MAPPING_PRESET_YES_NO_ALL,
            reset_on_finish=True,
            predefined_answer="no",
        )
