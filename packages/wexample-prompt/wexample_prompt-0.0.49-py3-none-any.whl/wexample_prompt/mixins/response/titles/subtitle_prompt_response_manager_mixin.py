from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_helpers.const.types import Kwargs
from wexample_prompt.common.prompt_context import PromptContext
from wexample_prompt.const.types import LineMessage

if TYPE_CHECKING:
    from wexample_prompt.common.io_manager import IoManager
    from wexample_prompt.enums.terminal_color import TerminalColor
    from wexample_prompt.enums.verbosity_level import VerbosityLevel
    from wexample_prompt.responses.abstract_prompt_response import (
        AbstractPromptResponse,
    )


class SubtitlePromptResponseManagerMixin:
    def subtitle(
        self: IoManager,
        text: LineMessage,
        color: TerminalColor | None = None,
        character: str | None = None,
        width: int | None = None,
        verbosity: VerbosityLevel | None = None,
        context: PromptContext | None = None,
        **kwargs: Kwargs,
    ) -> AbstractPromptResponse:
        from wexample_prompt.responses.titles.subtitle_prompt_response import (
            SubtitlePromptResponse,
        )

        response = SubtitlePromptResponse.create_subtitle(
            text=text,
            color=color,
            character=character,
            width=width,
            verbosity=(
                verbosity if verbosity is not None else self.default_response_verbosity
            ),
        )

        return self.print_response(
            response=response,
            context=SubtitlePromptResponse.rebuild_context_for_kwargs(
                context=context, parent_kwargs=kwargs
            ),
        )
