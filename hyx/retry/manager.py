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

    def _next_delay(self, backoff: BackoffT) -> float:
        delay = next(backoff)

        if self._jitter:
            return self._jitter(delay)

        return delay

    async def __call__(self, func: FuncT) -> Any:
        counter = create_counter(self._attempts)
        backoff = iter(self._backoff)

        while bool(counter):
            try:
                return await func()
            except self._exceptions:
                counter += 1

                next_delay = self._next_delay(backoff)
                await self._waiter(next_delay)
