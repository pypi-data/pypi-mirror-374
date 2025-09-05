"""Table response for displaying data in a formatted table layout."""

from __future__ import annotations

from typing import Any

from pydantic import Field
from wexample_prompt.common.prompt_context import PromptContext
from wexample_prompt.common.prompt_response_line import PromptResponseLine
from wexample_prompt.common.prompt_response_segment import PromptResponseSegment
from wexample_prompt.enums.verbosity_level import VerbosityLevel
from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse


class TablePromptResponse(AbstractPromptResponse):
    """Response for displaying data in a table layout with borders and formatting."""

    data: list[list[Any]] = Field(
        description="Table body rows: list of rows, each row a list of cell values"
    )
    headers: list[str] | None = Field(
        default=None, description="Optional list of column headers"
    )
    title: str | None = Field(default=None, description="Optional table title")

    @classmethod
    def get_example_class(cls) -> type:
        from wexample_prompt.example.response.data.table_example import TableExample

        return TableExample

    @classmethod
    def create_table(
        cls,
        data: list[list[Any]],
        headers: list[str] | None = None,
        title: str | None = None,
        verbosity: VerbosityLevel | None = None,
    ) -> TablePromptResponse:
        return cls(
            lines=[], data=data, headers=headers, title=title, verbosity=verbosity
        )

    def render(self, context: PromptContext | None = None) -> str | None:
        if not self.data and not self.headers:
            return ""

        all_rows: list[list[Any]] = []
        if self.headers:
            all_rows.append(self.headers)
        all_rows.extend(self.data)

        max_widths = self._calculate_max_widths(all_rows)
        total_width = sum(max_widths) + (len(max_widths) * 3) - 1

        lines: list[PromptResponseLine] = []
        lines.append(PromptResponseLine(segments=[PromptResponseSegment(text="")]))

        if self.title:
            title_padding = max(0, (total_width - len(self.title)) // 2)
            title_line = PromptResponseLine(
                segments=[
                    PromptResponseSegment(text="+" + "-" * title_padding),
                    PromptResponseSegment(text=f" {self.title} "),
                    PromptResponseSegment(
                        text="-" * (total_width - title_padding - len(self.title) - 2)
                        + "+"
                    ),
                ]
            )
            lines.append(title_line)
        else:
            lines.append(self._create_border_line(total_width))

        if self.headers:
            header_segments = self._create_row_segments(self.headers, max_widths)
            lines.append(PromptResponseLine(segments=header_segments))
            lines.append(self._create_border_line(total_width))

        for row in self.data:
            row_segments = self._create_row_segments(row, max_widths)
            lines.append(PromptResponseLine(segments=row_segments))

        lines.append(self._create_border_line(total_width))
        lines.append(PromptResponseLine(segments=[PromptResponseSegment(text="")]))

        self.lines = lines
        return super().render(context=context)

    @staticmethod
    def _calculate_max_widths(rows: list[list[Any]]) -> list[int]:
        if not rows:
            return []
        num_columns = max(len(row) for row in rows)
        max_widths = [0] * num_columns
        for row in rows:
            for i in range(num_columns):
                cell = str(row[i]) if i < len(row) else ""
                max_widths[i] = max(max_widths[i], len(cell))
        return max_widths

    @staticmethod
    def _create_row_segments(
        row: list[Any], widths: list[int]
    ) -> list[PromptResponseSegment]:
        segments = [PromptResponseSegment(text="|")]
        for i in range(len(widths)):
            cell = str(row[i]) if i < len(row) else ""
            segments.append(PromptResponseSegment(text=f" {cell:<{widths[i]}} |"))
        return segments

    @staticmethod
    def _create_border_line(width: int) -> PromptResponseLine:
        return PromptResponseLine(
            segments=[PromptResponseSegment(text="+" + "-" * width + "+")]
        )
