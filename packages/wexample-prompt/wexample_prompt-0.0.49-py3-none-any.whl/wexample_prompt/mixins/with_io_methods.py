from __future__ import annotations

from typing import Any

from wexample_prompt.mixins.with_io_manager import WithIoManager


class WithIoMethods(WithIoManager):
    """
    Allow class to provide Io methods like .log(), .title() etc.
    """

    def __getattr__(self, name: str) -> Any:
        io_response = self._get_io_methods(name)
        return io_response if io_response is not None else super().__getattr__(name)

    def _get_io_methods(self, name: str) -> Any:
        if hasattr(self.io, name):
            attr = getattr(self.io, name)

            if callable(attr):

                def wrapper(*args, **kwargs):
                    kwargs["context"] = self.io_context
                    return attr(*args, **kwargs)

                return wrapper

            return attr
        return None
