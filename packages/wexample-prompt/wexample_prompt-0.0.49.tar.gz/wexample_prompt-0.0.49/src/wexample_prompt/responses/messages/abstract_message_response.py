from __future__ import annotations

from typing import ClassVar

from wexample_prompt.common.prompt_response_line import PromptResponseLine
from wexample_prompt.common.prompt_response_segment import PromptResponseSegment
from wexample_prompt.const.types import LineMessage
from wexample_prompt.enums.terminal_color import TerminalColor
from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse


class AbstractMessageResponse(AbstractPromptResponse):
    # Symbol to display before the message, override in subclasses
    SYMBOL: ClassVar[str] = ""

    @classmethod
    def _create_symbol_message(
        cls,
        text: LineMessage,
        color: TerminalColor,
        symbol: str | None = None,
        **kwargs,
    ) -> AbstractMessageResponse:
        """Create a message with a symbol"""
        # Determine effective symbol (explicit > class default)
        effective_symbol = symbol if symbol is not None else cls.SYMBOL

        # Build lines from message handling multi-line inputs like PromptResponseLine.create_from_string
        raw_lines = PromptResponseLine.create_from_string(text=text, color=color)

        # Prepend symbol (if any) to the first line only
        if effective_symbol and raw_lines:
            first = raw_lines[0]
            first.segments.insert(
                0, PromptResponseSegment(text=f"{effective_symbol} ", color=color)
            )

        return cls._create(lines=raw_lines, **kwargs)
