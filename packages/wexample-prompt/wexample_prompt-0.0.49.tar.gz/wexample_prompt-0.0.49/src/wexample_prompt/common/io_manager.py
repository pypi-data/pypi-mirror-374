from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import Field, PrivateAttr
from wexample_helpers.classes.extended_base_model import ExtendedBaseModel
from wexample_prompt.enums.verbosity_level import VerbosityLevel
from wexample_prompt.mixins.response.data.list_prompt_response_manager_mixin import (
    ListPromptResponseManagerMixin,
)
from wexample_prompt.mixins.response.data.multiple_prompt_response_manager_mixin import (
    MultiplePromptResponseManagerMixin,
)
from wexample_prompt.mixins.response.data.properties_prompt_response_manager_mixin import (
    PropertiesPromptResponseManagerMixin,
)
from wexample_prompt.mixins.response.data.suggestions_prompt_response_manager_mixin import (
    SuggestionsPromptResponseManagerMixin,
)
from wexample_prompt.mixins.response.data.table_prompt_response_manager_mixin import (
    TablePromptResponseManagerMixin,
)
from wexample_prompt.mixins.response.data.tree_prompt_response_manager_mixin import (
    TreePromptResponseManagerMixin,
)
from wexample_prompt.mixins.response.echo_prompt_response_manager_mixin import (
    EchoPromptResponseManagerMixin,
)
from wexample_prompt.mixins.response.interactive.choice_prompt_response_manager_mixin import (
    ChoicePromptResponseManagerMixin,
)
from wexample_prompt.mixins.response.interactive.confirm_prompt_response_manager_mixin import (
    ConfirmPromptResponseManagerMixin,
)
from wexample_prompt.mixins.response.interactive.file_picker_prompt_response_manager_mixin import (
    FilePickerPromptResponseManagerMixin,
)
from wexample_prompt.mixins.response.interactive.progress_prompt_response_manager_mixin import (
    ProgressPromptResponseManagerMixin,
)
from wexample_prompt.mixins.response.interactive.screen_prompt_response_manager_mixin import (
    ScreenPromptResponseManagerMixin,
)
from wexample_prompt.mixins.response.log_prompt_response_manager_mixin import (
    LogPromptResponseManagerMixin,
)
from wexample_prompt.mixins.response.messages.debug_prompt_response_manager_mixin import (
    DebugPromptResponseManagerMixin,
)
from wexample_prompt.mixins.response.messages.error_prompt_response_manager_mixin import (
    ErrorPromptResponseManagerMixin,
)
from wexample_prompt.mixins.response.messages.failure_prompt_response_manager_mixin import (
    FailurePromptResponseManagerMixin,
)
from wexample_prompt.mixins.response.messages.info_prompt_response_manager_mixin import (
    InfoPromptResponseManagerMixin,
)
from wexample_prompt.mixins.response.messages.success_prompt_response_manager_mixin import (
    SuccessPromptResponseManagerMixin,
)
from wexample_prompt.mixins.response.messages.task_prompt_response_manager_mixin import (
    TaskPromptResponseManagerMixin,
)
from wexample_prompt.mixins.response.messages.warning_prompt_response_manager_mixin import (
    WarningPromptResponseManagerMixin,
)
from wexample_prompt.mixins.response.titles.separator_prompt_response_manager_mixin import (
    SeparatorPromptResponseManagerMixin,
)
from wexample_prompt.mixins.response.titles.subtitle_prompt_response_manager_mixin import (
    SubtitlePromptResponseManagerMixin,
)
from wexample_prompt.mixins.response.titles.title_prompt_response_manager_mixin import (
    TitlePromptResponseManagerMixin,
)
from wexample_prompt.mixins.with_indentation import WithIndentation
from wexample_prompt.output.abstract_output_handler import AbstractOutputHandler

if TYPE_CHECKING:
    from wexample_prompt.common.prompt_context import PromptContext
    from wexample_prompt.responses.abstract_prompt_response import (
        AbstractPromptResponse,
    )


class IoManager(
    # Basics
    EchoPromptResponseManagerMixin,
    LogPromptResponseManagerMixin,
    # Messages
    InfoPromptResponseManagerMixin,
    DebugPromptResponseManagerMixin,
    WarningPromptResponseManagerMixin,
    ErrorPromptResponseManagerMixin,
    FailurePromptResponseManagerMixin,
    SuccessPromptResponseManagerMixin,
    TaskPromptResponseManagerMixin,
    # Titles
    SeparatorPromptResponseManagerMixin,
    TitlePromptResponseManagerMixin,
    SubtitlePromptResponseManagerMixin,
    # Data
    ListPromptResponseManagerMixin,
    MultiplePromptResponseManagerMixin,
    PropertiesPromptResponseManagerMixin,
    SuggestionsPromptResponseManagerMixin,
    TablePromptResponseManagerMixin,
    TreePromptResponseManagerMixin,
    # Interactive
    ChoicePromptResponseManagerMixin,
    FilePickerPromptResponseManagerMixin,
    ProgressPromptResponseManagerMixin,
    ScreenPromptResponseManagerMixin,
    ConfirmPromptResponseManagerMixin,
    # Parent classes
    WithIndentation,
    ExtendedBaseModel,
):
    _terminal_width: int = PrivateAttr(default=None)
    output: AbstractOutputHandler | None = Field(
        default=None,
        description="Manages what to do with the generated output (print, or store), "
        "by default print to stdout",
    )
    default_context_verbosity: VerbosityLevel = Field(
        default=VerbosityLevel.DEFAULT,
        description="The overall verbosity level used in contexts.",
    )
    default_response_verbosity: VerbosityLevel = Field(
        default=VerbosityLevel.DEFAULT,
        description="The default verbosity for every generated message.",
    )

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._init_output()

    @property
    def terminal_width(self, reload: bool = False) -> int:
        if reload or self._terminal_width is None:
            import shutil

            self._terminal_width = shutil.get_terminal_size().columns

        return self._terminal_width

    def _init_output(self) -> None:
        from wexample_prompt.output.stdout_output_handler import StdoutOutputHandler

        self.output = (
            self.output if (self.output is not None) else StdoutOutputHandler()
        )

    @classmethod
    def get_response_types(cls) -> list[type[AbstractPromptResponse]]:
        from wexample_prompt.responses.data.list_prompt_response import (
            ListPromptResponse,
        )
        from wexample_prompt.responses.data.multiple_prompt_response import (
            MultiplePromptResponse,
        )
        from wexample_prompt.responses.data.properties_prompt_response import (
            PropertiesPromptResponse,
        )
        from wexample_prompt.responses.data.suggestions_prompt_response import (
            SuggestionsPromptResponse,
        )
        from wexample_prompt.responses.data.table_prompt_response import (
            TablePromptResponse,
        )
        from wexample_prompt.responses.data.tree_prompt_response import (
            TreePromptResponse,
        )
        from wexample_prompt.responses.echo_prompt_response import EchoPromptResponse
        from wexample_prompt.responses.interactive.choice_prompt_response import (
            ChoicePromptResponse,
        )
        from wexample_prompt.responses.interactive.confirm_prompt_response import (
            ConfirmPromptResponse,
        )
        from wexample_prompt.responses.interactive.file_picker_prompt_response import (
            FilePickerPromptResponse,
        )
        from wexample_prompt.responses.interactive.progress_prompt_response import (
            ProgressPromptResponse,
        )
        from wexample_prompt.responses.interactive.screen_prompt_response import (
            ScreenPromptResponse,
        )
        from wexample_prompt.responses.log_prompt_response import LogPromptResponse
        from wexample_prompt.responses.messages.debug_prompt_response import (
            DebugPromptResponse,
        )
        from wexample_prompt.responses.messages.error_prompt_response import (
            ErrorPromptResponse,
        )
        from wexample_prompt.responses.messages.failure_prompt_response import (
            FailurePromptResponse,
        )
        from wexample_prompt.responses.messages.info_prompt_response import (
            InfoPromptResponse,
        )
        from wexample_prompt.responses.messages.success_prompt_response import (
            SuccessPromptResponse,
        )
        from wexample_prompt.responses.messages.task_prompt_response import (
            TaskPromptResponse,
        )
        from wexample_prompt.responses.messages.warning_prompt_response import (
            WarningPromptResponse,
        )
        from wexample_prompt.responses.titles.separator_prompt_response import (
            SeparatorPromptResponse,
        )
        from wexample_prompt.responses.titles.subtitle_prompt_response import (
            SubtitlePromptResponse,
        )
        from wexample_prompt.responses.titles.title_prompt_response import (
            TitlePromptResponse,
        )

        return [
            # Basics
            EchoPromptResponse,
            LogPromptResponse,
            InfoPromptResponse,
            # Messages
            DebugPromptResponse,
            WarningPromptResponse,
            ErrorPromptResponse,
            FailurePromptResponse,
            SuccessPromptResponse,
            TaskPromptResponse,
            # Titles
            SeparatorPromptResponse,
            TitlePromptResponse,
            SubtitlePromptResponse,
            # Data
            ListPromptResponse,
            MultiplePromptResponse,
            PropertiesPromptResponse,
            SuggestionsPromptResponse,
            TablePromptResponse,
            TreePromptResponse,
            # Interactive
            ChoicePromptResponse,
            FilePickerPromptResponse,
            ProgressPromptResponse,
            ScreenPromptResponse,
            ConfirmPromptResponse,
        ]

    def erase_response(
        self,
        response: AbstractPromptResponse,
    ) -> None:
        self.output.erase(response=response)

    def create_context(self, context: PromptContext | None = None) -> PromptContext:
        from wexample_prompt.common.prompt_context import PromptContext

        context = PromptContext.create_if_none(context=context)

        context.verbosity = (
            context.verbosity
            if context.verbosity is not None
            else self.default_context_verbosity
        )
        context.indentation = context.indentation or self.indentation
        context.width = context.width or self.terminal_width
        return context

    def print_response(
        self,
        response: AbstractPromptResponse,
        context: PromptContext | None = None,
    ) -> AbstractPromptResponse:
        self.output.print(
            response=response, context=self.create_context(context=context)
        )

        return response
