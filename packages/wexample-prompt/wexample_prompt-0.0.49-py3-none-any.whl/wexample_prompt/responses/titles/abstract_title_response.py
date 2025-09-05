from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from pydantic import Field
from wexample_prompt.common.prompt_response_line import PromptResponseLine
from wexample_prompt.common.prompt_response_segment import PromptResponseSegment
from wexample_prompt.enums.verbosity_level import VerbosityLevel
from wexample_prompt.responses.messages.abstract_message_response import (
    AbstractMessageResponse,
)

if TYPE_CHECKING:
    from wexample_prompt.common.prompt_context import PromptContext
    from wexample_prompt.enums.terminal_color import TerminalColor


class AbstractTitleResponse(AbstractMessageResponse):
    """Base class for title-like responses that render:
    "❯ <text> ⫻⫻⫻⫻⫻⫻⫻⫻⫻⫻" with configurable fill character and width.
    """

    DEFAULT_PREFIX: ClassVar[str] = "❯"
    DEFAULT_CHARACTER: ClassVar[str] = "⫻"

    prefix_segment: PromptResponseSegment = Field(
        description="The prefix segment displayed before the title text"
    )
    text_segment: PromptResponseSegment = Field(description="The title text segment")
    fill_segment: PromptResponseSegment = Field(
        description="The trailing fill characters segment"
    )
    width: int | None = Field(
        default=None, description="Optional fixed width; if not set uses context width"
    )
    character: str | None = Field(
        default=DEFAULT_CHARACTER,
        description="Character used to fill the remaining line",
    )

    @classmethod
    def _create_title(
        cls,
        text: str,
        color: TerminalColor | None = None,
        character: str | None = None,
        width: int | None = None,
        verbosity: VerbosityLevel = None,
    ) -> AbstractTitleResponse:
        prefix = PromptResponseSegment(
            text=f"{cls.DEFAULT_PREFIX} ",
            color=color,
        )
        text_seg = PromptResponseSegment(
            text=f"{text} ",
            color=color,
        )
        fill = PromptResponseSegment(
            text="",
            color=color,
        )

        return cls(
            prefix_segment=prefix,
            text_segment=text_seg,
            fill_segment=fill,
            width=width,
            character=character or cls.DEFAULT_CHARACTER,
            lines=[
                PromptResponseLine(
                    segments=[
                        prefix,
                        text_seg,
                        fill,
                    ]
                )
            ],
            verbosity=verbosity,
        )

    def render(self, context: PromptContext | None = None) -> str | None:
        from wexample_prompt.common.prompt_context import PromptContext

        context = PromptContext.create_if_none(context=context)

        # Prefer provided context, else defer to super to resolve any defaulting
        width = self.width or context.get_width()

        # Compute remaining space after prefix + text and indentation
        remaining = width - len(context.render_indentation_text())

        remaining -= len(self.prefix_segment.text)
        remaining -= len(self.text_segment.text)
        self.fill_segment.text = max(0, remaining) * (
            self.character or self.DEFAULT_CHARACTER
        )

        return super().render(context=context)
