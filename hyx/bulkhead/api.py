import functools
from types import TracebackType
from typing import Any, Optional, Type, cast

from hyx.bulkhead.manager import BulkheadManager
from hyx.common.typing import FuncT


class bulkhead:
    """
    Bulkhead defines a fix-size action "queue" to constrain number of times the operation is executed at the same time
    as well as number of requests to postpone/queue.
    Bulkhead can be seen as a throttling mechanist for parallel executions.

    **Parameters**

    * **max_concurrency** *(int)* - Max executions at the same time.
        If the number is exceeded and max_execs allows, remaining executions are going to be queued
    * **max_capacity** *(int)* - Overall max number of executions (concurrent and queued).
        If the number is exceeded, new executions are going to be rejected
    """

    __slots__ = ("_manager",)

    def __init__(self, max_concurrency: int, max_capacity: int) -> None:
        self._manager = BulkheadManager(
            max_concurrency=max_concurrency,
            max_capacity=max_capacity,
        )

    async def __aenter__(self) -> "bulkhead":
        await self._manager.acquire()

        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> Optional[bool]:
        await self._manager.release()

        return None

    def __call__(self, func: FuncT) -> FuncT:
        """
        Apply bulkhead as a decorator
        """

        @functools.wraps(func)
        async def _wrapper(*args: Any, **kwargs: Any) -> Any:
            return await self._manager(cast(FuncT, functools.partial(func, *args, **kwargs)))

        _wrapper._original = func  # type: ignore[attr-defined]
        _wrapper._manager = self._manager  # type: ignore[attr-defined]

        return cast(FuncT, _wrapper)
