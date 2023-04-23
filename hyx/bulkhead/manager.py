import asyncio
from typing import Any, Optional

from hyx.bulkhead.exceptions import BulkheadFull
from hyx.bulkhead.listeners import BulkheadListener
from hyx.common.typing import FuncT


class BulkheadManager:
    """
    Semaphore-based bulkhead implementation
    """

    __slots__ = ("_total_execs_limiter", "_concurrency_limiter", "_name", "_event_dispatcher")

    def __init__(
        self,
        max_concurrency: int,
        max_capacity: int,
        event_dispatcher: BulkheadListener,
        name: Optional[str] = None,
    ) -> None:
        if max_concurrency <= 0:
            raise ValueError(f'max_concurrency should be greater than zero ("{max_concurrency}" given)')

        if max_capacity <= 0:
            raise ValueError(f'max_capacity should be greater than zero ("{max_capacity}" given)')

        if max_capacity < max_concurrency:
            raise ValueError("max_capacity should be equal or greater than max_concurrency")

        self._concurrency_limiter = asyncio.Semaphore(max_concurrency)
        self._total_execs_limiter = asyncio.Semaphore(max_capacity)
        self._name = name
        self._event_dispatcher = event_dispatcher

    async def _raise_on_exceed(self) -> None:
        if self._total_execs_limiter.locked():
            await self._event_dispatcher.on_limit_exceed()

            raise BulkheadFull

    async def acquire(self) -> None:
        await self._raise_on_exceed()

        await self._total_execs_limiter.acquire()
        await self._concurrency_limiter.acquire()

    async def release(self) -> None:
        self._concurrency_limiter.release()
        self._total_execs_limiter.release()

    async def __call__(self, func: FuncT) -> Any:
        await self._raise_on_exceed()

        async with self._total_execs_limiter:
            async with self._concurrency_limiter:
                return await func()
