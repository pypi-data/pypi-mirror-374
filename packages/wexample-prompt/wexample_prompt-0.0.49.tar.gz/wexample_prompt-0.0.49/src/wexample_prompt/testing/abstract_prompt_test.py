"""Base class for testing prompt responses."""

from __future__ import annotations

import unittest
from abc import ABC
from typing import TYPE_CHECKING

from wexample_prompt.common.io_manager import IoManager

if TYPE_CHECKING:
    from wexample_prompt.responses.abstract_prompt_response import (
        AbstractPromptResponse,
    )


class AbstractPromptTest(unittest.TestCase, ABC):
    """Base class for testing prompt responses.

    This class provides common functionality for testing prompt responses at three levels:
    1. Response class behavior
    2. IoManager integration
    3. PromptContext implementation
    """

    _test_message: str = "Test message"
    _test_message_multiline: str = "\n".join(["Line 1", "Line 2", "Line 3"])
    _io: IoManager

    def setUp(self) -> None:
        """Set up common test fixtures."""
        self._io = IoManager()

    def _asset_response_render_is_multiline(
        self, response: AbstractPromptResponse
    ) -> None:
        rendered = response.render()
        self._assert_contains_text(rendered, "Line 1")
        self._assert_contains_text(rendered, "Line 2")
        self._assert_contains_text(rendered, "Line 3")

    def _assert_contains_text(self, rendered: str, text: str) -> None:
        """Assert that rendered output contains specific text."""
        self.assertIn(text, rendered)

    def _assert_rendered_lines_count(
        self, response: AbstractPromptResponse, lines_count: int
    ) -> None:
        assert len(response.rendered_content.split("\n")) == lines_count
