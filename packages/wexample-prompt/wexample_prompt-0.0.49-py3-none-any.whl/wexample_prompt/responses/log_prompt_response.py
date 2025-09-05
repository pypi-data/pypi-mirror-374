from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_prompt.const.types import LineMessage
from wexample_prompt.enums.verbosity_level import VerbosityLevel
from wexample_prompt.example.abstract_response_example import AbstractResponseExample
from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse

if TYPE_CHECKING:
    from wexample_prompt.enums.terminal_color import TerminalColor


class LogPromptResponse(AbstractPromptResponse):
    """Response for log messages."""

    @classmethod
    def create_log(
        cls: LogPromptResponse,
        message: LineMessage,
        color: TerminalColor = None,
        verbosity: VerbosityLevel | None = None,
    ) -> LogPromptResponse:
        from wexample_prompt.common.prompt_response_line import PromptResponseLine
        from wexample_prompt.enums.terminal_color import TerminalColor

        return cls(
            lines=PromptResponseLine.create_from_string(
                text=message, color=color or TerminalColor.WHITE
            ),
            verbosity=verbosity,
        )

    @classmethod
    def get_example_class(cls) -> type[AbstractResponseExample]:
        from wexample_prompt.example.response.log_example import LogExample

        return LogExample
