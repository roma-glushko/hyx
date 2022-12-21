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
    """
    def __init__(self, max_execs: int, max_parallel_execs: int) -> None:
        self._max_execs = max_execs
        self._max_parallel_execs = max_parallel_execs

        self._manager = BulkheadManager(
            max_execs=self._max_execs,
            max_parallel_execs=self._max_parallel_execs,
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
            return await self._manager(functools.partial(func, *args, **kwargs))

        _wrapper.__original__ = func
        _wrapper.__manager__ = self._manager

        return cast(FuncT, _wrapper)
