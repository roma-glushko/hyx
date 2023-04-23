from typing import TYPE_CHECKING

from hyx.common.events import ListenerRegistry

if TYPE_CHECKING:
    from hyx.retry.counters import Counter
    from hyx.retry.manager import RetryManager

_RETRY_LISTENERS: ListenerRegistry["RetryListener"] = ListenerRegistry()


class RetryListener:
    async def on_retry(self, retry: "RetryManager", exception: Exception, counter: "Counter") -> None:
        ...

    async def on_attempts_exceeded(self, retry: "RetryManager") -> None:
        ...


def register_retry_listener(listener: RetryListener) -> None:
    """
    Register a listener that will listen to all retry components in the system
    """
    global _RETRY_LISTENERS

    _RETRY_LISTENERS.register(listener)
