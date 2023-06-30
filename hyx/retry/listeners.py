from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hyx.retry.counters import Counter
    from hyx.retry.manager import RetryManager


class RetryListener:
    async def on_retry(self, retry: "RetryManager", exception: Exception, counter: "Counter") -> None:
        ...

    async def on_attempts_exceeded(self, retry: "RetryManager") -> None:
        ...
