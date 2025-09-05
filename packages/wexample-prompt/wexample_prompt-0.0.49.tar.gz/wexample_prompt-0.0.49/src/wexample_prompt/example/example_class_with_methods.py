from __future__ import annotations

from wexample_prompt.testing.resources.classes.extended_base_model_with_io_methods import (
    ExtendedBaseModelWithIoMethods,
)


class ExampleClassWithMethods(ExtendedBaseModelWithIoMethods):
    def _format_context_prompt_message(self, message: str, indent: str) -> str:
        return f"{indent}[EXAMPLE|{self.__class__.__name__}]: {message}"
