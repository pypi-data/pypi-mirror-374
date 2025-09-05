from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_prompt.mixins.with_io_methods import WithIoMethods

if TYPE_CHECKING:
    from wexample_prompt.mixins.with_io_manager import WithIoManager


class ClassIndentationLevelTwo(WithIoMethods):
    def __init__(self, parent_io_handler: WithIoManager) -> None:
        WithIoMethods.__init__(
            self, io=parent_io_handler.io, parent_io_handler=parent_io_handler
        )

    def print_deep_log_two(self) -> None:
        from wexample_prompt.enums.verbosity_level import VerbosityLevel
        from wexample_prompt.testing.resources.classes.class_indenation_level_three import (
            ClassIndentationLevelThree,
        )

        self.log(message="test deep log two", context=self.io_context)

        self.log(
            message="test deep log two",
            context=self._create_io_context(colorized=False),
        )

        level_three = ClassIndentationLevelThree(parent_io_handler=self)

        level_three.print_deep_log_three()

        self.separator("Try class level three in quiet mode")
        self.io_context.verbosity = VerbosityLevel.QUIET

        level_three = ClassIndentationLevelThree(parent_io_handler=self)

        level_three.print_deep_log_three()

        self.io_context.verbosity = VerbosityLevel.DEFAULT
        self.separator("Quiet end")
