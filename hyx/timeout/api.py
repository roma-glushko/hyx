import functools
from types import TracebackType
from typing import Any, Optional, Sequence, Type, cast

from hyx.common.events import EventDispatcher
from hyx.common.typing import FuncT
from hyx.timeout.listeners import TimeoutListener
from hyx.timeout.manager import TimeoutManager


class timeout:
    """
    Timeout Decontext

    **Parameters:**

    * **timeout_secs** - Max amount of time to wait for the action in seconds
    """

    def __init__(self, timeout_secs: float, *, listeners: Optional[Sequence[TimeoutListener]] = None) -> None:
        self._timeout_secs = timeout_secs
        self._timeout_manager: Optional[TimeoutManager] = None

        self._listeners = listeners

    def _create_timeout(self) -> TimeoutManager:
        return TimeoutManager(
            timeout_secs=self._timeout_secs,
            events=cast(TimeoutListener, EventDispatcher(listeners=self._listeners))
        )

    async def __aenter__(self) -> "timeout":
        if self._timeout_manager is not None:
            await self._timeout_manager.stop()
            self._timeout_manager = None

        self._timeout_manager = self._create_timeout()

        await self._timeout_manager.start()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> Optional[bool]:
        if self._timeout_manager:
            await self._timeout_manager.stop(error=exc_type)
            self._timeout_manager = None

        return None

    def __call__(self, func: FuncT) -> FuncT:
        """
        Apply timeout as a decorator
        """
        manager = self._create_timeout()

        @functools.wraps(func)
        async def _wrapper(*args: Any, **kwargs: Any) -> Any:
            return await manager(cast(FuncT, functools.partial(func, *args, **kwargs)))

        _wrapper._original = func  # type: ignore[attr-defined]
        _wrapper._manager = manager  # type: ignore[attr-defined]

        return cast(FuncT, _wrapper)
