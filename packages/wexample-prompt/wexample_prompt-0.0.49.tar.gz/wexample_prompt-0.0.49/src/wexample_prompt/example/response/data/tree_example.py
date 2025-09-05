"""Example for tree response."""

from __future__ import annotations

from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.data.tree_prompt_response import TreePromptResponse


class TreeExample(AbstractResponseExample):
    """Example for tree response."""

    def get_example(self) -> str:
        data = {
            "root": {
                "folder1": {
                    "file1": "content1",
                    "file2": "content2",
                },
                "folder2": {
                    "subfolder": {
                        "file3": "content3",
                    }
                },
            }
        }
        response = TreePromptResponse.create_tree(
            data=data,
            context=self.io.create_context(),
        )
        return response.render()

    def example_class(self, indentation: int | None = None):
        """Example using class with context."""
        data = {
            "root": {
                "folder1": {
                    "file1": "content1",
                    "file2": "content2",
                },
                "folder2": {
                    "subfolder": {
                        "file3": "content3",
                    }
                },
            }
        }
        return TreePromptResponse.create_tree(
            data=data,
        )

    def example_manager(self) -> None:
        """Example using IoManager directly."""
        data = {
            "root": {
                "folder1": {
                    "file1": "content1",
                    "file2": "content2",
                },
                "folder2": {
                    "subfolder": {
                        "file3": "content3",
                    }
                },
            }
        }
        self.io.tree(data=data)

    def example_extended(self) -> None:
        """Example using context."""
        data = {
            "root": {
                "folder1": {
                    "file1": "content1",
                    "file2": "content2",
                },
                "folder2": {
                    "subfolder": {
                        "file3": "content3",
                    }
                },
            }
        }
        self._class_with_methods.tree(data=data)
