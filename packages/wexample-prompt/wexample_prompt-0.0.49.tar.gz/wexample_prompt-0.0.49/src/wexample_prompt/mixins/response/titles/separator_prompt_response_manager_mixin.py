from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_helpers.const.types import Kwargs
from wexample_prompt.common.prompt_context import PromptContext

if TYPE_CHECKING:
    from wexample_prompt.common.io_manager import IoManager
    from wexample_prompt.enums.verbosity_level import VerbosityLevel
    from wexample_prompt.responses.abstract_prompt_response import (
        AbstractPromptResponse,
    )


class SeparatorPromptResponseManagerMixin:
    def separator(
        self: IoManager,
        label: str | None = None,
        width: int | None = None,
        verbosity: VerbosityLevel | None = None,
        character: str | None = None,
        context: PromptContext | None = None,
        **kwargs: Kwargs,
    ) -> AbstractPromptResponse:
        from wexample_prompt.responses.titles.separator_prompt_response import (
            SeparatorPromptResponse,
        )

        response = SeparatorPromptResponse.create_separator(
            label=label,
            width=width,
            character=character or SeparatorPromptResponse.DEFAULT_CHARACTER,
            verbosity=(
                verbosity if verbosity is not None else self.default_response_verbosity
            ),
        )

        return self.print_response(
            response=response,
            context=SeparatorPromptResponse.rebuild_context_for_kwargs(
                context=context, parent_kwargs=kwargs
            ),
        )
