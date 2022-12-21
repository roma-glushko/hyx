from typing import Any

from hyx.common.typing import ExceptionsT, FuncT
from hyx.common.waiter import wait
from hyx.retry.backoffs import create_backoff
from hyx.retry.counters import create_counter
from hyx.retry.typing import AttemptsT, BackoffsT, BackoffT, JittersT


class RetryManager:
    def __init__(
        self,
        exceptions: ExceptionsT,
        attempts: AttemptsT,
        backoff: BackoffsT,
        jitter: JittersT,
    ) -> None:
        self._exceptions = exceptions
        self._attempts = attempts
        self._backoff = create_backoff(backoff)
        self._jitter = jitter
        self._waiter = wait

    async def _next_delay(self, backoff: BackoffT) -> float:
        delay = await backoff.__anext__()

        if self._jitter:
            delay += await self._jitter.__anext__()

        return delay

    async def __call__(self, func: FuncT) -> Any:
        counter = create_counter(self._attempts)
        backoff = self._backoff.__aiter__()

        while bool(counter):
            try:
                return await func()
            except self._exceptions:
                counter += 1

                next_delay = await self._next_delay(backoff)
                await self._waiter(next_delay)
