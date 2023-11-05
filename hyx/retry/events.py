from typing import TYPE_CHECKING

from hyx.events import ListenerFactoryT, ListenerRegistry

if TYPE_CHECKING:
    from hyx.retry.counters import Counter
    from hyx.retry.manager import RetryManager

_RETRY_LISTENERS: ListenerRegistry["RetryManager", "RetryListener"] = ListenerRegistry()


class RetryListener:
    async def on_retry(self, retry: "RetryManager", exception: Exception, counter: "Counter", backoff: float) -> None:
        ...

    async def on_attempts_exceeded(self, retry: "RetryManager") -> None:
        ...

    async def on_success(self, retry: "RetryManager", counter: "Counter"):
        ...


def register_retry_listener(listener: RetryListener | ListenerFactoryT) -> None:
    """
    Register a listener that will dispatch on all retry components in the system
    """
    global _RETRY_LISTENERS

    _RETRY_LISTENERS.register(listener)
