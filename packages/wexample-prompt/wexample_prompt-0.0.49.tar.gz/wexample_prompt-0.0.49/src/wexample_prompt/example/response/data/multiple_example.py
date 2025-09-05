"""Example usage of MultiplePromptResponse."""

from __future__ import annotations

from typing import Any

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.data.list_prompt_response import ListPromptResponse
from wexample_prompt.responses.data.multiple_prompt_response import (
    MultiplePromptResponse,
)
from wexample_prompt.responses.log_prompt_response import LogPromptResponse


class MultipleExample(AbstractResponseExample):
    """Example usage of MultiplePromptResponse."""

    def example_class(self, indentation: int | None = None):
        """Example using the class directly."""
        responses = [
            LogPromptResponse.create_log("First response"),
            ListPromptResponse.create_list(items=["Item 1", "Item 2"]),
            LogPromptResponse.create_log("Last response"),
        ]
        return MultiplePromptResponse.create_multiple(
            responses=responses,
        )

    def example_manager(self) -> None:
        """Example using the IoManager."""
        responses = [
            LogPromptResponse.create_log("First response"),
            ListPromptResponse.create_list(items=["Item 1", "Item 2"]),
            LogPromptResponse.create_log("Last response"),
        ]
        self.io.multiple(responses=responses)

    def example_extended(self) -> None:
        """Example using PromptContext."""
        responses = [
            LogPromptResponse.create_log("First response"),
            ListPromptResponse.create_list(items=["Item 1", "Item 2"]),
            LogPromptResponse.create_log("Last response"),
        ]
        self._class_with_methods.multiple(responses=responses)

    def get_examples(self) -> list[dict[str, Any]]:
        """Get list of examples.

        Returns:
            List[Dict[str, Any]]: List of example configurations
        """
        return [
            {
                "title": "Simple Multiple",
                "description": "Display multiple responses in sequence",
                "callback": self.simple_multiple,
            },
            {
                "title": "Mixed Types",
                "description": "Display different types of responses together",
                "callback": self.mixed_types,
            },
            {
                "title": "Dynamic Multiple",
                "description": "Build multiple responses dynamically",
                "callback": self.dynamic_multiple,
            },
        ]

    def simple_multiple(self) -> MultiplePromptResponse | None:
        """Show a simple multiple response example."""
        responses = [
            LogPromptResponse.create_log("First message"),
            LogPromptResponse.create_log("Second message"),
            LogPromptResponse.create_log("Third message"),
        ]
        return self.io.multiple(responses=responses)

    def mixed_types(self) -> MultiplePromptResponse | None:
        """Show different response types together."""
        responses = [
            LogPromptResponse.create_log("Log response"),
            ListPromptResponse.create_list(
                items=["List item 1", "List item 2"],
            ),
            LogPromptResponse.create_log("Another log response"),
        ]
        return self.io.multiple(responses=responses)

    def dynamic_multiple(self) -> MultiplePromptResponse | None:
        """Show building responses dynamically."""
        response = MultiplePromptResponse.create_multiple(
            responses=[LogPromptResponse.create_log("Initial response")],
            context=self.io.create_context(),
        )

        # Add more responses
        response.append_response(
            ListPromptResponse.create_list(items=["Dynamic item 1"])
        )
        response.extend_responses(
            [
                LogPromptResponse.create_log("Added later"),
                ListPromptResponse.create_list(items=["Dynamic item 2"]),
            ]
        )

        return response
