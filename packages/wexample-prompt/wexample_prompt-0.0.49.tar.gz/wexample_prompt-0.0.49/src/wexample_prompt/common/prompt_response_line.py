"""Prompt response line implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import Field
from wexample_helpers.classes.extended_base_model import ExtendedBaseModel
from wexample_prompt.common.prompt_context import PromptContext
from wexample_prompt.common.prompt_response_segment import PromptResponseSegment
from wexample_prompt.const.types import LineMessage

if TYPE_CHECKING:
    from wexample_prompt.enums.terminal_color import TerminalColor


class PromptResponseLine(ExtendedBaseModel):
    """A line of text composed of one or more segments with optional styling and layout."""

    segments: list[PromptResponseSegment] = Field(
        default_factory=list, description="List of text segments that constitute a line"
    )

    @classmethod
    def create_from_string(
        cls, text: LineMessage, color: TerminalColor | None = None
    ) -> list[PromptResponseLine]:
        """
        Create a line from a single text string.
        """
        # Normalize input to a list of raw lines without newline characters
        raw_lines: list[str] = []
        if isinstance(text, str):
            # splitlines() handles \r\n, \r, \n and does not keep separators
            raw_lines = text.splitlines()
        else:
            for item in text:
                raw_lines.extend(item.splitlines())

        lines: list[PromptResponseLine] = []
        for raw in raw_lines:
            lines.append(
                cls(
                    segments=[
                        PromptResponseSegment(
                            text=raw,
                            color=color,
                        )
                    ]
                )
            )

        return lines

    def render(self, context: PromptContext) -> str:
        """Render the line within the context width, wrapping segments as needed.
        Respect context.formatting: when False, do not reflow/wrap lines.
        """
        indentation = context.render_indentation()
        # If formatting is disabled, bypass wrapping logic entirely.
        if context.formatting is False:
            return self._render_no_formatting(context, indentation)

        max_content_width = self._compute_max_content_width(context, indentation)

        if not max_content_width:
            return self._render_unbounded(context, indentation)

        return self._render_wrapped(context, indentation, max_content_width)

    def _render_no_formatting(self, context: PromptContext, indentation: str) -> str:
        """Render all segments on a single line, without wrapping."""
        rendered_segments = []
        for seg in self.segments:
            # Provide a very large remaining width to avoid splitting segments
            rendered, _ = seg.render(context, line_remaining_width=10**9)
            rendered_segments.append(rendered)
        return f"{indentation}{''.join(rendered_segments)}"

    def _compute_max_content_width(
        self, context: PromptContext, indentation: str
    ) -> int | None:
        """Compute the maximum visible width available for content on a line, or None if unbounded."""
        return (
            max(0, (context.get_width()) - self._visible_len(indentation))
            if context.width
            else None
        )

    def _render_unbounded(self, context: PromptContext, indentation: str) -> str:
        """Render without width restriction (no wrapping)."""
        rendered_segments = []
        for seg in self.segments:
            rendered, _ = seg.render(context, line_remaining_width=10**9)
            rendered_segments.append(rendered)
        return f"{indentation}{''.join(rendered_segments)}"

    def _render_wrapped(
        self, context: PromptContext, indentation: str, max_content_width: int
    ) -> str:
        """Render with wrapping according to max_content_width."""
        lines: list[str] = []
        current_line = ""
        remaining = max_content_width

        queue = list(self.segments)
        carry_over: PromptResponseSegment | None = None

        while queue or carry_over:
            if carry_over is not None:
                rendered, remainder = carry_over.render(context, remaining)
                current_line += rendered
                remaining -= self._visible_len(rendered)
                carry_over = remainder
            else:
                seg = queue.pop(0)
                rendered, remainder = seg.render(context, remaining)
                current_line += rendered
                remaining -= self._visible_len(rendered)
                carry_over = remainder

            if remaining <= 0 or (carry_over is not None and remaining == 0):
                lines.append(f"{indentation}{current_line}")
                current_line = ""
                remaining = max_content_width
                continue

            if carry_over is None and not queue:
                lines.append(f"{indentation}{current_line}")
                current_line = ""
                remaining = max_content_width

        if current_line:
            lines.append(f"{indentation}{current_line}")

        return "\n".join(lines)

    def _visible_len(self, s: str) -> int:
        from wexample_helpers.helpers.ansi import ansi_strip

        return len(ansi_strip(s))
