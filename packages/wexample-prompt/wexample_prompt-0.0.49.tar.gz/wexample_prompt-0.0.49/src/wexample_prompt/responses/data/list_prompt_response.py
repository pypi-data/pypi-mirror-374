from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_prompt.common.prompt_response_line import PromptResponseLine
from wexample_prompt.common.prompt_response_segment import PromptResponseSegment
from wexample_prompt.enums.verbosity_level import VerbosityLevel
from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.messages.abstract_message_response import (
    AbstractMessageResponse,
)

if TYPE_CHECKING:
    from wexample_prompt.enums.terminal_color import TerminalColor


class ListPromptResponse(AbstractMessageResponse):
    """Display items as a bulleted list, supporting nested indentation via leading spaces."""

    @classmethod
    def create_list(
        cls,
        items: list[str],
        bullet: str = "•",
        color: TerminalColor | None = None,
        verbosity: VerbosityLevel | None = None,
    ) -> ListPromptResponse:
        lines: list[PromptResponseLine] = []

        for item in items:
            # Determine indentation level by counting leading double-spaces
            indent_level = 0
            content = item
            while content.startswith("  "):
                indent_level += 1
                content = content[2:]

            # If the content already starts with the bullet, strip it
            if content.startswith(f"{bullet} "):
                content = content[len(bullet) + 1 :]

            bullet_text = ("  " * indent_level) + f"{bullet} "

            bullet_segment = PromptResponseSegment(text=bullet_text, color=color)
            text_segment = PromptResponseSegment(text=content, color=color)

            lines.append(PromptResponseLine(segments=[bullet_segment, text_segment]))

        return cls(lines=lines, verbosity=verbosity)

    @classmethod
    def get_example_class(cls) -> type[AbstractResponseExample]:
        from wexample_prompt.example.response.data.list_example import ListExample

        return ListExample
