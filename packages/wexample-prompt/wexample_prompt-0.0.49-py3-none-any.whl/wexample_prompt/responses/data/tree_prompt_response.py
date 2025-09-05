"""Tree response implementation."""

from __future__ import annotations

from typing import Any

from pydantic import Field
from wexample_prompt.common.prompt_context import PromptContext
from wexample_prompt.common.prompt_response_line import PromptResponseLine
from wexample_prompt.common.prompt_response_segment import PromptResponseSegment
from wexample_prompt.enums.verbosity_level import VerbosityLevel
from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse


class TreePromptResponse(AbstractPromptResponse):
    """Response for displaying hierarchical data in a tree structure."""

    data: dict[str, Any] = Field(description="The data to display")
    branch_style: str = Field(
        default="├", description="The character used to render branch"
    )
    leaf_style: str = Field(
        default="└", description="The character used to render leaf"
    )
    pipe_style: str = Field(
        default="│", description="The character used to render pipe"
    )
    dash_style: str = Field(
        default="──", description="The character used to render dash"
    )

    @classmethod
    def get_example_class(cls) -> type:
        from wexample_prompt.example.response.data.tree_example import TreeExample

        return TreeExample

    @classmethod
    def create_tree(
        cls,
        data: dict[str, Any],
        verbosity: VerbosityLevel | None = None,
    ) -> TreePromptResponse:
        return cls(
            lines=[],
            data=data,
            verbosity=verbosity,
        )

    def render(self, context: PromptContext | None = None) -> str | None:
        if not self.data:
            return ""

        lines: list[PromptResponseLine] = []
        lines.append(PromptResponseLine(segments=[PromptResponseSegment(text="")]))

        self._build_tree(self.data, "", lines)

        lines.append(PromptResponseLine(segments=[PromptResponseSegment(text="")]))
        self.lines = lines
        return super().render(context=context)

    def _build_tree(
        self, data: dict[str, Any], prefix: str, lines: list[PromptResponseLine]
    ) -> None:
        items = list(data.items())
        for i, (key, value) in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = (
                f"{self.leaf_style}{self.dash_style} "
                if is_last
                else f"{self.branch_style}{self.dash_style} "
            )

            segments = [PromptResponseSegment(text=f"{prefix}{current_prefix}{key}")]
            lines.append(PromptResponseLine(segments=segments))

            if isinstance(value, dict):
                next_prefix = prefix + ("    " if is_last else f"{self.pipe_style}   ")
                self._build_tree(value, next_prefix, lines)
            elif value is not None:
                next_prefix = prefix + ("    " if is_last else f"{self.pipe_style}   ")
                segments = [
                    PromptResponseSegment(
                        text=f"{next_prefix}{self.leaf_style}{self.dash_style} {value}"
                    )
                ]
                lines.append(PromptResponseLine(segments=segments))
