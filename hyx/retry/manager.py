import asyncio
from typing import Any, Optional

from hyx.common.typing import ExceptionsT, FuncT
from hyx.ratelimit.managers import TokenBucketLimiter
from hyx.retry.backoffs import create_backoff
from hyx.retry.counters import create_counter
from hyx.retry.exceptions import AttemptsExceeded
from hyx.retry.listeners import RetryListener
from hyx.retry.typing import AttemptsT, BackoffsT


class RetryManager:
    __slots__ = ("_name", "_exceptions", "_attempts", "_backoff", "_waiter", "_event_dispatcher", "_limiter")

    def __init__(
        self,
        exceptions: ExceptionsT,
        attempts: AttemptsT,
        backoff: BackoffsT,
        event_dispatcher: RetryListener,
        limiter: Optional[TokenBucketLimiter] = None,
        name: Optional[str] = None,
    ) -> None:
        self._name = name
        self._exceptions = exceptions
        self._attempts = attempts
        self._backoff = create_backoff(backoff)
        self._event_dispatcher = event_dispatcher
        self._limiter = limiter

    async def __call__(self, func: FuncT) -> Any:
        counter = create_counter(self._attempts)
        backoff = iter(self._backoff)

        try:
            while bool(counter):
                try:
                    if self._limiter is not None:
                        await self._limiter.acquire()
                    return await func()
                except self._exceptions as e:
                    counter += 1
                    await self._event_dispatcher.on_retry(self, e, counter)
                    await asyncio.sleep(next(backoff))

        except AttemptsExceeded:
            await self._event_dispatcher.on_attempts_exceeded(self)
            raise
