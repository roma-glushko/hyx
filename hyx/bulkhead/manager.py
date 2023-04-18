import asyncio
from typing import Any

from hyx.bulkhead.exceptions import BulkheadFull
from hyx.common.typing import FuncT


class BulkheadManager:
    """
    Semaphore-based bulkhead implementation
    """

    __slots__ = ("_total_execs_limiter", "_concurrency_limiter")

    def __init__(self, max_concurrency: int, max_capacity: int) -> None:
        if max_concurrency <= 0:
            raise ValueError(f'max_concurrency should be greater than zero ("{max_concurrency}" given)')

        if max_capacity <= 0:
            raise ValueError(f'max_capacity should be greater than zero ("{max_capacity}" given)')

        if max_capacity < max_concurrency:
            raise ValueError("max_capacity should be equal or greater than max_concurrency")

        self._concurrency_limiter = asyncio.Semaphore(max_concurrency)
        self._total_execs_limiter = asyncio.Semaphore(max_capacity)

    def _raise_on_exceed(self) -> None:
        if self._total_execs_limiter.locked():
            raise BulkheadFull

    async def acquire(self) -> None:
        self._raise_on_exceed()

        await self._total_execs_limiter.acquire()
        await self._concurrency_limiter.acquire()

    async def release(self) -> None:
        self._concurrency_limiter.release()
        self._total_execs_limiter.release()

    async def __call__(self, func: FuncT) -> Any:
        self._raise_on_exceed()

        async with self._total_execs_limiter:
            async with self._concurrency_limiter:
                return await func()
