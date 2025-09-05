from __future__ import annotations

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.data.list_prompt_response import ListPromptResponse


class ListExample(AbstractResponseExample):
    def get_test_items(self) -> list[str]:
        return [
            "Item A",
            "  Sub-item A1",
            "  Sub-item A2",
            "Item B",
        ]

    def example_manager(self) -> None:
        self.io.list(items=self.get_test_items())

    def example_class(self):
        return ListPromptResponse.create_list(
            items=self.get_test_items(),
        )

    def example_extended(self) -> None:
        self._class_with_methods.list(items=self.get_test_items())
