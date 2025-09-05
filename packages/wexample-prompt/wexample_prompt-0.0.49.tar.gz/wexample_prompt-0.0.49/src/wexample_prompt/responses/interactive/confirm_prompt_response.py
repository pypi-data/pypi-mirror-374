"""Confirmation dialog interactive response (box style)."""

from __future__ import annotations

from typing import Any, ClassVar

from pydantic import Field
from wexample_prompt.common.color_manager import ColorManager
from wexample_prompt.common.prompt_context import PromptContext
from wexample_prompt.common.prompt_response_line import PromptResponseLine
from wexample_prompt.common.prompt_response_segment import PromptResponseSegment
from wexample_prompt.const.types import LineMessage
from wexample_prompt.enums.terminal_color import TerminalColor
from wexample_prompt.enums.text_style import TextStyle
from wexample_prompt.enums.verbosity_level import VerbosityLevel
from wexample_prompt.responses.interactive.abstract_interactive_prompt_response import (
    AbstractInteractivePromptResponse,
)


class ConfirmPromptResponse(AbstractInteractivePromptResponse):
    """Confirmation dialog with a boxed layout and keyboard shortcuts."""

    # Preset mappings (key -> (value, label))
    MAPPING_PRESET_YES_NO: ClassVar[dict[str, tuple[str, str]]] = {
        "y": ("yes", "Yes"),
        "n": ("no", "No"),
    }
    MAPPING_PRESET_OK_CANCEL: ClassVar[dict[str, tuple[str, str]]] = {
        "y": ("ok", "Ok"),
        "n": ("cancel", "Cancel"),
    }
    MAPPING_PRESET_YES_NO_ALL: ClassVar[dict[str, tuple[str, str]]] = {
        "y": ("yes", "Yes"),
        "Y": ("yes_all", "Yes for all"),
        "n": ("no", "No"),
    }
    MAPPING_PRESET_CONTINUE_CANCEL: ClassVar[dict[str, tuple[str, str]]] = {
        "y": ("continue", "Continue"),
        "n": ("cancel", "Cancel"),
    }

    question: LineMessage = Field(
        default="Please confirm:", description="The question to ask to the user"
    )
    width: int | None = Field(
        default=None,
        description="Total width of the box (in characters). If None, uses context width or content width.",
    )
    # Map pressed key -> (value, label)
    options: dict[str, tuple[str, str]] = Field(
        default_factory=dict,
        description="Keyboard shortcuts mapping to (return value, display label)",
    )
    default_value: str | None = Field(
        default=None, description="The value to return when quitting"
    )
    allow_abort: bool = Field(
        default=True, description="ESC/q aborts and returns None when allowed."
    )
    predefined_answer: Any = Field(
        default=None,
        description="The answer of the question, in order to make the response non interactive",
    )

    @classmethod
    def get_example_class(cls) -> type:
        from wexample_prompt.example.response.interactive.confirm_example import (
            ConfirmExample,
        )

        return ConfirmExample

    # Internal helper to create a full-width separator line using a given character
    @staticmethod
    def _separator(
        ch: str, width: int, color: TerminalColor = TerminalColor.WHITE
    ) -> PromptResponseLine:
        return PromptResponseLine(
            segments=[PromptResponseSegment(text=(ch * width), color=color)]
        )

    @classmethod
    def create_confirm(
        cls,
        question: LineMessage = "Please confirm:",
        choices: dict[str, tuple[str, str]] | None = None,
        default: str | None = None,
        width: int | None = None,
        predefined_answer: Any = None,
        reset_on_finish: bool = False,
        verbosity: VerbosityLevel | None = None,
    ) -> ConfirmPromptResponse:
        """Create a confirmation dialog with explicit key mappings.

        choices expects a mapping of key -> (value, label).
        If not provided, defaults to MAPPING_PRESET_YES_NO for convenience.
        """
        mapping: dict[str, tuple[str, str]] = choices or cls.MAPPING_PRESET_YES_NO

        return cls(
            question=question,
            options=mapping,
            default_value=default,
            width=width,
            reset_on_finish=reset_on_finish,
            verbosity=verbosity,
            predefined_answer=predefined_answer,
            # allow_abort is True by default; ESC/q return None
        )

    def is_ok(self) -> bool:
        """Response match with one of common positive value"""
        return (
            self._answer == True
            or self._answer == 1
            or self._answer == "yes"
            or self._answer == "yes_all"
            or self._answer == "ok"
            or self._answer == "continue"
        )

    def _build_lines(self, context: PromptContext) -> None:
        # No centering/truncation: allow natural terminal wrapping.

        # Compute box width: clamp to terminal/context width so it is NEVER exceeded.
        term_width = context.get_width()

        # Build options text in the order provided by the mapping (insertion order)
        parts: list[tuple[str, str, str]] = []  # (key, value, label)
        for k, (v, label) in self.options.items():
            parts.append((k, v, label))
        options_text = " / ".join([f"[{k}: {label}]" for k, _, label in parts])

        # Determine question lines. We do NOT adapt the box width to content; we
        # strictly use the terminal/context width as the fixed width.
        q_lines = PromptResponseLine.create_from_string(self.question)
        question_texts = ["".join(seg.text for seg in ln.segments) for ln in q_lines]
        # Fixed width: use get_width() strictly; if unavailable, fallback to self.width or 80
        if term_width and term_width > 0:
            box_width = term_width
        else:
            box_width = self.width or 80

        # Compose a boxed layout using lines and segments
        self.lines = []
        # top border
        self.lines.append(self._separator("━", box_width, TerminalColor.WHITE))

        # Question lines LEFT-ALIGNED, no truncation. Let terminal wrapping do its job.
        # Left padding rule: use two spaces by default, but if any line would wrap
        # with padding, drop padding entirely for the question block.
        from wexample_helpers.helpers.ansi import ansi_display_width

        q_pad = "  "
        # Account for the visible width of the '? ' prefix on the first line
        prefix_width = 2  # visible width of '? '
        for idx_chk, t_chk in enumerate(question_texts):
            extra = prefix_width if idx_chk == 0 else 0
            if ansi_display_width(t_chk) + len(q_pad) + extra > box_width:
                q_pad = ""
                break
        for idx, t in enumerate(question_texts):
            segs: list[PromptResponseSegment] = []
            # Left padding (if any)
            if q_pad:
                segs.append(
                    PromptResponseSegment(text=q_pad, color=TerminalColor.RESET)
                )
            # Blue question mark only on the first line
            if idx == 0:
                segs.append(
                    PromptResponseSegment(
                        text=ColorManager.colorize(text="?", color=TerminalColor.BLUE),
                        color=TerminalColor.RESET,
                    )
                )
                segs.append(PromptResponseSegment(text=" ", color=TerminalColor.RESET))
            # The question text itself
            segs.append(
                PromptResponseSegment(
                    text=t,
                    color=TerminalColor.LIGHT_WHITE,
                    styles=[TextStyle.BOLD],
                )
            )
            self.lines.append(PromptResponseLine(segments=segs))
        # empty line
        self.lines.append(
            PromptResponseLine(
                segments=[PromptResponseSegment(text="", color=TerminalColor.RESET)]
            )
        )
        # Separator line between question and options (different char)
        self.lines.append(self._separator("·", box_width, TerminalColor.WHITE))
        # Options line LEFT-ALIGNED; let terminal wrap naturally. Highlight default_value if set.
        # Apply the same left padding rule: two spaces if it fits on one line; otherwise none.
        option_segments: list[PromptResponseSegment] = []
        raw_options = " ".join([f"〔{k}: {label}〕" for k, _, label in parts])
        o_pad = "  " if ansi_display_width(raw_options) + 2 <= box_width else ""
        if o_pad:
            option_segments.append(
                PromptResponseSegment(text=o_pad, color=TerminalColor.RESET)
            )
        for idx, (k, v, label) in enumerate(parts):
            text = f"〔{k}: {label}〕"
            if self.default_value is not None and v == self.default_value:
                option_segments.append(
                    PromptResponseSegment(
                        text=text,
                        color=TerminalColor.LIGHT_WHITE,
                        styles=[TextStyle.BOLD],
                    )
                )
            else:
                option_segments.append(
                    PromptResponseSegment(text=text, color=TerminalColor.WHITE)
                )
            if idx < len(parts) - 1:
                option_segments.append(
                    PromptResponseSegment(text=" ", color=TerminalColor.WHITE)
                )
        self.lines.append(PromptResponseLine(segments=option_segments))

        # bottom border (thicker look using lower half block)
        self.lines.append(self._separator("▄", box_width, TerminalColor.WHITE))
        self.lines.append(self._separator("░", box_width, TerminalColor.WHITE))

    def render(self, context: PromptContext | None = None) -> None:
        from wexample_prompt.common.prompt_context import PromptContext

        context = PromptContext.create_if_none(context=context)

        printed = 0
        # render once per frame until a valid key or injected answer
        while True:
            self._partial_clear(printed)
            self._build_lines(context=context)
            printed = self._print_render(context=context)

            if self.predefined_answer is not None:
                if self.reset_on_finish and printed > 0:
                    self._partial_clear(printed)
                self._answer = str(self.predefined_answer)
                return

            key = self._read_key()
            # Support left/right arrows to cycle the current default selection among options
            # Arrow sequences typically are: left='\x1b[D', right='\x1b[C'
            if key in ("\x1b[C", "\x1b[D"):
                items = list(
                    self.options.items()
                )  # [(k, (value, label)), ...] preserving insertion order
                if items:
                    # Determine current index from default_value
                    current_idx = None
                    if self.default_value is not None:
                        for i, (_k, (v, _label)) in enumerate(items):
                            if v == self.default_value:
                                current_idx = i
                                break
                    if key == "\x1b[C":  # right
                        if current_idx is None:
                            new_idx = 0
                        else:
                            new_idx = (current_idx + 1) % len(items)
                    else:  # left
                        if current_idx is None:
                            new_idx = len(items) - 1
                        else:
                            new_idx = (current_idx - 1) % len(items)
                    # Update the default_value to new selection, will re-render highlighted next iteration
                    self.default_value = items[new_idx][1][0]
                # Continue to next loop to re-render with updated highlight
                continue
            # normalize single-char keys for mapping
            if key in self.options:
                value, _ = self.options[key]
                if self.reset_on_finish and printed > 0:
                    self._partial_clear(printed)
                self._answer = value
                return
            elif key in ("\r", "\n") and self.default_value is not None:
                if self.reset_on_finish and printed > 0:
                    self._partial_clear(printed)
                self._answer = self.default_value
                return
            elif key in ("\x1b", "q", "Q") and self.allow_abort:
                if self.reset_on_finish and printed > 0:
                    self._partial_clear(printed)
                self._answer = None
                return
