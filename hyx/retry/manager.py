import asyncio
from typing import Any

from hyx.common.typing import ExceptionsT, FuncT
from hyx.retry.backoffs import create_backoff
from hyx.retry.counters import create_counter
from hyx.retry.typing import AttemptsT, BackoffsT


class RetryManager:
    __slots__ = ("_exceptions", "_attempts", "_backoff", "_waiter")

    def __init__(
        self,
        exceptions: ExceptionsT,
        attempts: AttemptsT,
        backoff: BackoffsT,
    ) -> None:
        self._exceptions = exceptions
        self._attempts = attempts
        self._backoff = create_backoff(backoff)

    async def __call__(self, func: FuncT) -> Any:
        counter = create_counter(self._attempts)
        backoff = iter(self._backoff)

        while bool(counter):
            try:
                return await func()
            except self._exceptions:
                counter += 1
                await asyncio.sleep(next(backoff))
