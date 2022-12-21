import functools
from typing import Any, Callable, Optional, cast

from hyx.common.typing import ExceptionsT, FuncT
from hyx.fallback.manager import FallbackManager
from hyx.fallback.typing import FallbackT, PredicateT


def fallback(
    handler: FallbackT,
    *,
    on: Optional[ExceptionsT] = Exception,
    if_: Optional[PredicateT] = None
) -> Callable[[Callable], Callable]:
    """
    Provides a fallback on exceptions
    """
    manager = FallbackManager(
        handler=handler,
        exceptions=on,
        predicate=if_,
    )

    def _decorator(func: FuncT) -> FuncT:
        @functools.wraps(func)
        async def _wrapper(*args: Any, **kwargs: Any) -> Any:
            return await manager(func, *args, **kwargs)

        _wrapper.__original__ = func
        _wrapper.__manager__ = manager

        return cast(FuncT, _wrapper)

    return _decorator
