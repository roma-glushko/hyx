import asyncio
from typing import Any

from hyx.bulkhead.exceptions import BulkheadFull
from hyx.common.typing import FuncT


class BulkheadManager:
    """
    Semaphore-based bulkhead implementation
    """

    def __init__(self, max_execs: int, max_parallel_execs: int) -> None:
        self._max_execs = max_execs
        self._max_parallel_execs = max_parallel_execs

        self._execs_limiter = asyncio.Semaphore(self._max_execs)
        self._parallel_execs_limiter = asyncio.Semaphore(self._max_parallel_execs)

    def _raise_on_exceed(self) -> None:
        if self._execs_limiter.locked():
            raise BulkheadFull

    async def acquire(self) -> None:
        self._raise_on_exceed()

        await self._execs_limiter.acquire()
        await self._parallel_execs_limiter.acquire()

    async def release(self) -> None:
        self._parallel_execs_limiter.release()
        self._execs_limiter.release()

    async def __call__(self, func: FuncT) -> Any:
        self._raise_on_exceed()

        async with self._execs_limiter:
            async with self._parallel_execs_limiter:
                return await func()
