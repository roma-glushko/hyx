from typing import TYPE_CHECKING

from hyx.events import ListenerFactoryT, ListenerRegistry

if TYPE_CHECKING:
    from hyx.bulkhead.manager import BulkheadManager

_BULKHEAD_LISTENERS: ListenerRegistry["BulkheadManager", "BulkheadListener"] = ListenerRegistry()


class BulkheadListener:
    async def on_bulkhead_full(self, bulkhead: "BulkheadManager") -> None: ...


def register_bulkhead_listener(listener: BulkheadListener | ListenerFactoryT) -> None:
    """
    Register a listener that will listen to all fallback components in the system
    """
    global _BULKHEAD_LISTENERS

    _BULKHEAD_LISTENERS.register(listener)
