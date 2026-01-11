import functools
from collections.abc import Sequence
from types import TracebackType
from typing import Any, cast

from hyx.bulkhead.events import _BULKHEAD_LISTENERS, BulkheadListener
from hyx.bulkhead.manager import BulkheadManager
from hyx.events import EventDispatcher, EventManager, get_default_name
from hyx.typing import FuncT


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

    def __init__(
        self,
        max_concurrency: int,
        max_capacity: int,
        *,
        name: str | None = None,
        listeners: Sequence[BulkheadListener] | None = None,
        event_manager: "EventManager | None" = None,
    ) -> None:
        event_dispatcher = EventDispatcher[BulkheadManager, BulkheadListener](
            listeners,
            _BULKHEAD_LISTENERS,
            event_manager=event_manager,
        )

        self._manager = BulkheadManager(
            name=name or get_default_name(),
            max_concurrency=max_concurrency,
            max_capacity=max_capacity,
            event_dispatcher=event_dispatcher.as_listener,
        )

        event_dispatcher.set_component(self._manager)

    async def __aenter__(self) -> "bulkhead":
        await self._manager.acquire()

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
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
