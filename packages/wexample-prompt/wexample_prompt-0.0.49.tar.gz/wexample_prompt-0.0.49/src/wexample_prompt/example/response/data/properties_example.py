"""Example for properties response."""

from __future__ import annotations

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.data.properties_prompt_response import (
    PropertiesPromptResponse,
)


class PropertiesExample(AbstractResponseExample):
    """Example for properties response."""

    def get_example(self) -> str:
        properties = {
            "name": "John Doe",
            "age": 30,
            "contact": {
                "email": "john@example.com",
                "phone": "123-456-7890",
            },
        }
        response = PropertiesPromptResponse.create_properties(
            properties=properties,
            title="User Information",
            context=self.io.create_context(),
        )
        return response.render()

    def example_class(self, indentation: int | None = None):
        """Example using class with context."""
        properties = {
            "name": "John Doe",
            "age": 30,
            "contact": {
                "email": "john@example.com",
                "phone": "123-456-7890",
            },
        }

        return PropertiesPromptResponse.create_properties(
            properties=properties,
            title="User Information",
        )

    def example_manager(self) -> None:
        """Example using IoManager directly."""
        properties = {
            "server": "localhost",
            "port": 8080,
            "config": {
                "debug": True,
                "log_level": "INFO",
            },
        }
        self.io.properties(
            properties=properties,
            title="Server Configuration",
        )

    def example_extended(self) -> None:
        """Example using context."""
        properties = {
            "status": "success",
            "duration": "2.5s",
            "details": {
                "processed": 100,
                "failed": 0,
            },
        }
        self._class_with_methods.properties(
            properties=properties,
            title="Operation Results",
        )
