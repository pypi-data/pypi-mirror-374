from __future__ import annotations

from typing import Any

from pydantic import Field
from wexample_prompt.common.prompt_context import PromptContext
from wexample_prompt.common.prompt_response_line import PromptResponseLine
from wexample_prompt.common.prompt_response_segment import PromptResponseSegment
from wexample_prompt.enums.verbosity_level import VerbosityLevel
from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse


class PropertiesPromptResponse(AbstractPromptResponse):
    """Render a dictionary of properties as a formatted block, with optional title.

    The visual width adapts to the provided render context. Lines are generated during
    render, so the response remains context-agnostic until displayed.
    """

    properties: dict[str, Any] = Field(
        default_factory=dict, description="The list of properties to display"
    )
    title: str | None = Field(
        default=None, description="The title of the properties list"
    )
    nested_indent: int = Field(
        default=2,
        description="Indentation inside the properties list, when rendering sub list of items",
    )

    @classmethod
    def get_example_class(cls) -> type:
        from wexample_prompt.example.response.data.properties_example import (
            PropertiesExample,
        )

        return PropertiesExample

    @classmethod
    def create_properties(
        cls,
        properties: dict[str, Any],
        title: str | None = None,
        nested_indent: int = 2,
        verbosity: VerbosityLevel | None = None,
    ) -> PropertiesPromptResponse:
        return cls(
            lines=[],  # Lines will be built in render() because we neet context with to create them.
            properties=properties,
            title=title,
            nested_indent=nested_indent,
            verbosity=verbosity,
        )

    def render(self, context: PromptContext | None = None) -> str | None:
        """Render the properties into lines using the provided context width."""
        if not self.properties:
            return ""

        context = PromptContext.create_if_none(context=context)

        # Determine content width
        total_width = context.get_width()
        content_width = max(10, total_width - 2)

        max_key_width = 0

        def scan_keys(obj: dict[str, Any]) -> None:
            nonlocal max_key_width
            for k, v in obj.items():
                max_key_width = max(max_key_width, len(str(k)))
                if isinstance(v, dict):
                    scan_keys(v)

        scan_keys(self.properties)

        content_lines = self._format_properties(
            self.properties, max_key_width, self.nested_indent
        )

        lines: list[PromptResponseLine] = []
        # Empty top spacer
        lines.append(PromptResponseLine(segments=[PromptResponseSegment(text="")]))

        if self.title:
            title_len = len(self.title)
            left_pad = max(0, (content_width - title_len) // 2)
            right_pad = max(0, content_width - title_len - left_pad)
            lines.append(
                PromptResponseLine(
                    segments=[
                        PromptResponseSegment(text="-" * left_pad),
                        PromptResponseSegment(text=f" {self.title} "),
                        PromptResponseSegment(text="-" * max(0, right_pad - 2)),
                    ]
                )
            )
        else:
            lines.append(self._create_border_line(content_width))

        for content in content_lines:
            lines.append(
                PromptResponseLine(
                    segments=[
                        PromptResponseSegment(text=" "),
                        PromptResponseSegment(text=content),
                    ]
                )
            )

        lines.append(self._create_border_line(content_width))

        # Replace and delegate to base to apply verbosity and segment rendering
        self.lines = lines
        return super().render(context=context)

    @staticmethod
    def _format_properties(
        properties: dict[str, Any],
        key_width: int,
        indent: int,
        current_indent: int = 0,
    ) -> list[str]:
        lines: list[str] = []
        indent_str = " " * current_indent
        for key, value in properties.items():
            if isinstance(value, dict):
                lines.append(f"{indent_str}{str(key)}:")
                lines.extend(
                    PropertiesPromptResponse._format_properties(
                        value, key_width, indent, current_indent + indent
                    )
                )
            else:
                key_str = str(key).ljust(key_width)
                lines.append(f"{indent_str}{key_str} : {str(value)}")
        return lines

    @staticmethod
    def _create_border_line(width: int) -> PromptResponseLine:
        return PromptResponseLine(
            segments=[PromptResponseSegment(text=f"{'-' * width}")]
        )
