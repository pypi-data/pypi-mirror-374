from __future__ import annotations

from wexample_helpers.classes.extended_base_model import ExtendedBaseModel
from wexample_prompt.mixins.with_io_manager import WithIoManager


class ExtendedBaseModelWithIoManager(WithIoManager, ExtendedBaseModel):
    """
    A Pydantic class with an io manager.
    """

    def __init__(self, **kwargs) -> None:
        ExtendedBaseModel.__init__(self, **kwargs)
        WithIoManager.__init__(self, **kwargs)
