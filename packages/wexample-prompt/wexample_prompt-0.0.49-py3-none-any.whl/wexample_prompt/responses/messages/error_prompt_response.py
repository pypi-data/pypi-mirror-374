from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from wexample_prompt.enums.verbosity_level import VerbosityLevel
from wexample_prompt.responses.messages.abstract_message_response import (
    AbstractMessageResponse,
)

if TYPE_CHECKING:
    from wexample_prompt.enums.terminal_color import TerminalColor
    from wexample_prompt.example.abstract_response_example import (
        AbstractResponseExample,
    )


class ErrorPromptResponse(AbstractMessageResponse):
    SYMBOL: ClassVar[str] = "❌"

    @classmethod
    def get_example_class(cls) -> type[AbstractResponseExample]:
        from wexample_prompt.example.response.messages.error_example import ErrorExample

        return ErrorExample

    @classmethod
    def create_error(
        cls: ErrorPromptResponse,
        message: str | None = None,
        exception: BaseException | None = None,
        color: TerminalColor | None = None,
        symbol: str | None = None,
        verbosity: VerbosityLevel | None = None,
    ) -> ErrorPromptResponse:
        from wexample_prompt.enums.terminal_color import TerminalColor

        # Build content: if there's an exception, create a red header line (symbol + message)
        # and append the formatted trace as raw lines (no added color) so its own formatting stays intact.
        if exception is not None:
            from wexample_helpers.helpers.error import error_format
            from wexample_prompt.common.prompt_response_line import PromptResponseLine
            from wexample_prompt.common.prompt_response_segment import (
                PromptResponseSegment,
            )

            header_text = (
                message
                if (message is not None and message != "")
                else "An error occurred"
            )

            # First line: symbol + header in red
            effective_symbol = cls.SYMBOL
            header_segments: list[PromptResponseSegment] = []
            if effective_symbol:
                header_segments.append(
                    PromptResponseSegment(
                        text=f"{effective_symbol} ", color=(color or TerminalColor.RED)
                    )
                )
            header_segments.append(
                PromptResponseSegment(
                    text=header_text, color=(color or TerminalColor.RED)
                )
            )

            lines: list[PromptResponseLine] = [
                PromptResponseLine(segments=header_segments)
            ]

            # Trace lines: preserve helper formatting (may include ANSI), no extra color
            formatted = error_format(exception)
            lines.extend(PromptResponseLine.create_from_string(formatted.splitlines()))
            return cls._create(lines=lines, symbol=symbol, verbosity=verbosity)

        else:
            text = (
                message
                if (message is not None and message != "")
                else "An error occurred"
            )
            return cls._create_symbol_message(
                text=text, color=(color or TerminalColor.RED), verbosity=verbosity
            )
