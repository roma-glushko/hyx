from typing import TYPE_CHECKING

from hyx.common.events import ListenerRegistry

if TYPE_CHECKING:
    pass

_BULKHEAD_LISTENERS: ListenerRegistry["BulkheadListener"] = ListenerRegistry()


class BulkheadListener:
    async def on_limit_exceed(self) -> None:
        ...


def register_bulkhead_listener(listener: BulkheadListener) -> None:
    """
    Register a listener that will listen to all fallback components in the system
    """
    global _BULKHEAD_LISTENERS

    _BULKHEAD_LISTENERS.register(listener)
