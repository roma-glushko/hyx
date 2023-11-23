import asyncio
from typing import Any, Optional

from hyx.ratelimit.buckets import TokenBucket
from hyx.retry.backoffs import create_backoff
from hyx.retry.counters import create_counter
from hyx.retry.events import RetryListener
from hyx.retry.exceptions import AttemptsExceeded
from hyx.retry.typing import AttemptsT, BackoffsT
from hyx.typing import ExceptionsT, FuncT


class RetryManager:
    __slots__ = (
        "_name",
        "_exceptions",
        "_attempts",
        "_backoff",
        "_waiter",
        "_event_dispatcher",
        "_limiter",
    )

    def __init__(
        self,
        name: str,
        exceptions: ExceptionsT,
        attempts: AttemptsT,
        backoff: BackoffsT,
        event_dispatcher: RetryListener,
        limiter: Optional[TokenBucket] = None,
    ) -> None:
        self._name = name
        self._exceptions = exceptions
        self._attempts = attempts
        self._backoff = create_backoff(backoff)
        self._event_dispatcher = event_dispatcher
        self._limiter = limiter

    @property
    def name(self) -> str:
        return self._name

    async def __call__(self, func: FuncT) -> Any:
        counter = create_counter(self._attempts)
        backoff_generator = iter(self._backoff)

        try:
            while bool(counter):
                try:
                    if self._limiter is not None:
                        await self._limiter.acquire()

                    result = await func()

                    await self._event_dispatcher.on_success(self, counter)

                    return result
                except self._exceptions as e:
                    counter += 1
                    backoff = next(backoff_generator)

                    await self._event_dispatcher.on_retry(self, e, counter, backoff)
                    await asyncio.sleep(backoff)

        except AttemptsExceeded:
            await self._event_dispatcher.on_attempts_exceeded(self)
            raise
