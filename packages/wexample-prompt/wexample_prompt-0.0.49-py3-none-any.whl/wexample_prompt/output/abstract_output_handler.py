from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any

from wexample_helpers.classes.extended_base_model import ExtendedBaseModel

if TYPE_CHECKING:
    from wexample_prompt.common.prompt_context import PromptContext
    from wexample_prompt.responses.abstract_prompt_response import (
        AbstractPromptResponse,
    )


class AbstractOutputHandler(ExtendedBaseModel):
    @abstractmethod
    def print(
        self,
        response: AbstractPromptResponse,
        context: PromptContext | None = None,
    ) -> Any:
        self._raise_not_implemented_error()

    @abstractmethod
    def erase(
        self,
        response: AbstractPromptResponse,
    ) -> Any:
        self._raise_not_implemented_error()
