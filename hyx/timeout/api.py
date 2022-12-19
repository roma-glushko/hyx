import functools
from typing import Any, cast, Callable

from hyx.timeout.manager import TimeoutManager
from hyx.timeout.typing import FuncT


class Timeout:
    def __init__(self, max_duration: float) -> None:
        self._max_duration = max_duration

    async def __aenter__(self):
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        ...

    async def __call__(self, func: FuncT) -> FuncT:
        manager = TimeoutManager(max_duration=self._max_duration)

        @functools.wraps(func)
        async def _wrapper(*args: Any, **kwargs: Any) -> Any:
            return await manager(functools.partial(func, *args, **kwargs))

        _wrapper.__original__ = func
        _wrapper.__manager__ = manager

        return cast(FuncT, _wrapper)


def timeout(max_duration: float) -> Callable[[Callable], Callable]:
    def _decorator(func: FuncT) -> FuncT:
        manager = TimeoutManager(max_duration=max_duration)

        @functools.wraps(func)
        async def _wrapper(*args: Any, **kwargs: Any) -> Any:
            return await manager(functools.partial(func, *args, **kwargs))

        _wrapper.__original__ = func
        _wrapper.__manager__ = manager

        return cast(FuncT, _wrapper)

    return _decorator
