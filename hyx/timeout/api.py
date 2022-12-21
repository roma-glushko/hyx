import functools
from types import TracebackType
from typing import Any, Optional, Type, cast

from hyx.common.typing import FuncT
from hyx.timeout.manager import TimeoutManager


class timeout:
    """
    Timeout Decontext. Can be used as a decorator or context manager
    """
    def __init__(self, max_duration: float) -> None:
        self._max_duration = max_duration
        self._timeout_manager: Optional[TimeoutManager] = None

    async def __aenter__(self) -> "timeout":
        if self._timeout_manager is not None:
            await self._timeout_manager.stop()
            self._timeout_manager = None

        self._timeout_manager = TimeoutManager(max_duration=self._max_duration)

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
        manager = TimeoutManager(max_duration=self._max_duration)

        @functools.wraps(func)
        async def _wrapper(*args: Any, **kwargs: Any) -> Any:
            return await manager(functools.partial(func, *args, **kwargs))

        _wrapper.__original__ = func
        _wrapper.__manager__ = manager

        return cast(FuncT, _wrapper)
