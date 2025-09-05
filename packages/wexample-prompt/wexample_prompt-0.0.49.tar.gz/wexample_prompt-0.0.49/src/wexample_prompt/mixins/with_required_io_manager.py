from __future__ import annotations

from wexample_prompt.common.io_manager import IoManager
from wexample_prompt.mixins.with_io_manager import WithIoManager


class WithRequiredIoManager(WithIoManager):
    """Mixin that requires an IoManager instance."""

    def __init__(
        self,
        io: IoManager,
        parent_io_handler: WithIoManager | None = None,
    ) -> None:
        super().__init__(io=io, parent_io_handler=parent_io_handler)
