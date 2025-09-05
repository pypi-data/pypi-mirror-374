from __future__ import annotations

from wexample_prompt.mixins.with_io_manager import WithIoManager


class ClassIndentationLevelOne(WithIoManager):
    def print_deep_log_one(self) -> None:
        from wexample_helpers.helpers.string import string_generate_lorem_ipsum
        from wexample_prompt.testing.resources.classes.class_indenation_level_two import (
            ClassIndentationLevelTwo,
        )

        self.io.log("test deep log one", context=self.io_context)
        self.io.log(string_generate_lorem_ipsum(1000), context=self.io_context)

        level_two = ClassIndentationLevelTwo(parent_io_handler=self)

        level_two.print_deep_log_two()
