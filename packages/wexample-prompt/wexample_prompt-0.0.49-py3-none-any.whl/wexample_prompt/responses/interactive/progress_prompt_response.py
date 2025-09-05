"""Progress bar response implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from pydantic import Field
from wexample_prompt.common.prompt_context import PromptContext
from wexample_prompt.common.prompt_response_line import PromptResponseLine
from wexample_prompt.common.prompt_response_segment import PromptResponseSegment
from wexample_prompt.enums.terminal_color import TerminalColor
from wexample_prompt.enums.verbosity_level import VerbosityLevel
from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse

if TYPE_CHECKING:
    from wexample_prompt.common.progress.progress_handle import ProgressHandle


class ProgressPromptResponse(AbstractPromptResponse):
    """Response for displaying progress bars."""

    # Style characters
    FILL_CHAR: ClassVar[str] = "▰"
    EMPTY_CHAR: ClassVar[str] = "▱"

    # Instance fields
    total: int = Field(description="Total number of items (must be > 0)")
    current: int = Field(description="Current progress (must be >= 0)")
    width: int | None = Field(
        default=None, description="Width of the progress bar in characters"
    )
    label: str | None = Field(
        default=None, description="Optional label displayed before the bar"
    )
    color: TerminalColor | None = Field(
        default=None, description="Optional color applied to the bar"
    )
    _handle: ProgressHandle | None = None

    @classmethod
    def get_example_class(cls) -> type:
        from wexample_prompt.example.response.interactive.progress_example import (
            ProgressExample,
        )

        return ProgressExample

    @classmethod
    def set_style(cls, fill_char: str = "▰", empty_char: str = "▱") -> None:
        """Set the progress bar characters."""
        cls.FILL_CHAR = fill_char
        cls.EMPTY_CHAR = empty_char

    @staticmethod
    def _normalize_value(total: int, current: float | int | str) -> int:
        """Accept int or percentage string like '54%' and return an int current.

        Clamps the result to [0, total].
        """
        if isinstance(current, str):
            s = current.strip()
            if s.endswith("%"):
                try:
                    pct = float(s[:-1].strip())
                except ValueError:
                    raise ValueError(f"Invalid percentage value: {current}")
                pct = max(0.0, min(100.0, pct))
                return int(round(total * (pct / 100.0)))
            else:
                # Try parse as int fallback
                try:
                    val = int(s)
                except ValueError:
                    raise ValueError(f"Invalid current value: {current}")
                return max(0, min(total, val))
        # int path
        return max(0, min(total, int(current)))

    @classmethod
    def create_progress(
        cls,
        total: int = 100,
        current: float | int | str = 0,
        width: int | None = None,
        label: str | None = None,
        color: TerminalColor | None = None,
        verbosity: VerbosityLevel | None = None,
    ) -> ProgressPromptResponse:
        if total <= 0:
            raise ValueError("Total must be greater than 0")
        if width is not None and width < 1:
            raise ValueError("Width must be at least 1")

        norm_current = cls._normalize_value(total, current)

        return cls(
            lines=[],
            total=total,
            current=norm_current,
            width=width,
            label=label,
            color=color or TerminalColor.BLUE,
            verbosity=verbosity,
        )

    def get_handle(self) -> ProgressHandle:
        from wexample_prompt.common.progress.progress_handle import ProgressHandle

        assert isinstance(self._handle, ProgressHandle)
        return self._handle

    def init_handle(self, context: PromptContext | None = None) -> PromptContext:
        from wexample_prompt.common.progress.progress_handle import ProgressHandle

        # Normalize context
        context = PromptContext.create_if_none(context=context)

        # Create once.
        if not self._handle:
            # Create/update the handle bound to this response and the effective context
            self._handle = ProgressHandle(
                response=self,
                context=context,
            )

            # In case of context change.
            self._handle.context = context

        return context

    def render(self, context: PromptContext | None = None) -> str | None:
        context = self.init_handle(context=context)

        # Progress values
        current = min(self.current, self.total)
        percentage = min(100, int(100 * current / self.total))

        # Compute available content width (context width minus indentation)
        indent_text = context.render_indentation()
        from wexample_helpers.helpers.ansi import ansi_strip

        visible_indent = len(ansi_strip(indent_text))
        total_width = self.width or context.get_width()
        max_content_width = max(0, total_width - visible_indent)

        # Compose left label and right percentage parts
        left_label = f"{self.label} " if self.label else ""
        right_percent = f" {percentage}%"

        # Determine bar width to perfectly fit the line
        bar_width = max(
            0,
            max_content_width
            - len(ansi_strip(left_label))
            - len(ansi_strip(right_percent)),
        )

        # Build colored bar of exact computed width
        if bar_width > 0:
            filled = int(bar_width * current / self.total)
            empty = max(0, bar_width - filled)
        else:
            filled = 0
            empty = 0

        # Build plain bar text (ANSI will be applied by segment color handling, after splitting)
        bar_text = (
            f"{self.FILL_CHAR * filled}{self.EMPTY_CHAR * empty}"
            if bar_width > 0
            else ""
        )

        segments = []
        if left_label:
            segments.append(PromptResponseSegment(text=left_label))
        if bar_text:
            segments.append(PromptResponseSegment(text=bar_text, color=self.color))
        # percentage (always shown)
        segments.append(PromptResponseSegment(text=right_percent))

        self.lines = [PromptResponseLine(segments=segments)]
        return super().render(context=context)
