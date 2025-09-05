"""Example for table response."""

from __future__ import annotations

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.data.table_prompt_response import TablePromptResponse


class TableExample(AbstractResponseExample):
    """Example for table response."""

    def get_example(self) -> str:
        headers = ["Name", "Age", "City"]
        data = [
            ["John", "30", "New York"],
            ["Jane", "25", "San Francisco"],
            ["Bob", "35", "Chicago"],
        ]
        response = TablePromptResponse.create_table(
            data=data,
            headers=headers,
            title="Employee List",
            context=self.io.create_context(),
        )
        return response.render()

    def example_class(self, indentation: int | None = None):
        """Example using class with context."""
        headers = ["Name", "Age", "City"]
        data = [
            ["John", "30", "New York"],
            ["Jane", "25", "San Francisco"],
            ["Bob", "35", "Chicago"],
        ]
        return TablePromptResponse.create_table(
            data=data,
            headers=headers,
            title="Employee List",
        )

    def example_manager(self) -> None:
        """Example using IoManager directly."""
        headers = ["Name", "Age", "City"]
        data = [
            ["John", "30", "New York"],
            ["Jane", "25", "San Francisco"],
            ["Bob", "35", "Chicago"],
        ]
        self.io.table(
            data=data,
            headers=headers,
            title="Employee List",
        )

    def example_extended(self) -> None:
        """Example using context."""
        headers = ["Name", "Age", "City"]
        data = [
            ["John", "30", "New York"],
            ["Jane", "25", "San Francisco"],
            ["Bob", "35", "Chicago"],
        ]
        self._class_with_methods.table(
            data=data,
            headers=headers,
            title="Employee List",
        )
