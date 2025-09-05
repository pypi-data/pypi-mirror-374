from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from wexample_helpers.classes.extended_base_model import ExtendedBaseModel
from wexample_prompt.mixins.with_io_manager import WithIoManager

if TYPE_CHECKING:
    from wexample_prompt.common.io_manager import IoManager
    from wexample_prompt.example.example_class_with_methods import (
        ExampleClassWithMethods,
    )


class AbstractResponseExample(WithIoManager, ExtendedBaseModel):
    _class_with_methods: ExampleClassWithMethods | None = None

    def __init__(self, io: IoManager | None = None, **kwargs) -> None:
        from wexample_prompt.example.example_class_with_methods import (
            ExampleClassWithMethods,
        )

        ExtendedBaseModel.__init__(self, **kwargs)
        WithIoManager.__init__(self, io=io)

        self._init_io_manager()
        self._class_with_methods = ExampleClassWithMethods(io=self._io)

    @abstractmethod
    def example_class(self) -> None:
        pass

    @abstractmethod
    def example_manager(self) -> None:
        pass

    @abstractmethod
    def example_extended(self) -> None:
        pass
