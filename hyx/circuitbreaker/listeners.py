from typing import TYPE_CHECKING

from hyx.common.events import ListenerRegistry

if TYPE_CHECKING:
    ...

_BREAKER_LISTENERS: ListenerRegistry["BreakerListener"] = ListenerRegistry()


class BreakerListener:
    ...


def register_breaker_listener(listener: BreakerListener) -> None:
    """
    Register a listener that will listen to all circuit breaker components in the system
    """
    global _BREAKER_LISTENERS

    _BREAKER_LISTENERS.register(listener)
