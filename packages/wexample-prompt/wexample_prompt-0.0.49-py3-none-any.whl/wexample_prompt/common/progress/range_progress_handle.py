from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import Field
from wexample_helpers.classes.extended_base_model import ExtendedBaseModel
from wexample_prompt.common.progress.progress_handle import ProgressHandle

if TYPE_CHECKING:
    from wexample_prompt.enums.terminal_color import TerminalColor


class RangeProgressHandle(ExtendedBaseModel):
    """A handle that controls a specific sub-range of a parent ProgressHandle.

    It maps the child range [0..total] to the parent range [start..end].
    Percentages provided to update/advance are relative to this child range.
    """

    parent: ProgressHandle = Field(
        description="The parent progress handle that this range controls"
    )
    start: int = Field(
        description="Inclusive start position of the mapped range on the parent"
    )
    end: int = Field(
        description="Exclusive end position (start + total) of the mapped range on the parent"
    )
    total: int = Field(description="Total size of the child range (end - start)")

    def render(self) -> str:
        return self.parent.render()

    def _child_current(self) -> int:
        # Current child value derived from parent's current
        cur = max(self.start, min(self.end, self.parent.response.current))
        return max(0, min(self.total, cur - self.start))

    def update(
        self,
        current: float | int | str | None = None,
        label: str | None = None,
        color: TerminalColor | None = None,
        auto_render: bool = True,
    ) -> str | None:
        if current is not None:
            # Normalize against child total; percentages like '50%' are relative to the sub-range
            from wexample_prompt.responses.interactive.progress_prompt_response import (
                ProgressPromptResponse,
            )

            normalized = ProgressPromptResponse._normalize_value(self.total, current)
            mapped = self.start + max(0, min(self.total, normalized))
            return self.parent.update(
                current=mapped, label=label, color=color, auto_render=auto_render
            )
        else:
            # Only update label/color/render
            return self.parent.update(
                current=None, label=label, color=color, auto_render=auto_render
            )

    def advance(
        self,
        step: float | int | str | None = None,
        **kwargs,
    ) -> str | None:
        from wexample_prompt.responses.interactive.progress_prompt_response import (
            ProgressPromptResponse,
        )

        step_norm = ProgressPromptResponse._normalize_value(self.total, step)
        cur_child = self._child_current()
        return self.update(current=cur_child + step_norm, **kwargs)

    def finish(self, **kwargs) -> str | None:
        return self.parent.update(current=self.end, **kwargs)
