import functools
from typing import Any, Callable, Optional, cast

from hyx.common.typing import ExceptionsT, FuncT
from hyx.fallback.manager import FallbackManager
from hyx.fallback.typing import FallbackT, PredicateT


def fallback(
    handler: FallbackT,
    *,
    on: Optional[ExceptionsT] = Exception,
    if_: Optional[PredicateT] = None,
) -> Callable[[Callable], Callable]:
    """
    Provides a fallback on exceptions and/or specific result of the original function

    **Parameters**

    * **handler** *(Callable)* - The fallback handler
    * **on** *(None | Exception | tuple[Exception, ...])* - Fall back on the give exception(s)
    * **if_** *(None | Callable)* - Fall back if the given predicate function returns True
        on the original function result
    """
    if not on and not if_:
        raise ValueError("Either on or if_ param should be specified when using the fallback decorator")

    manager = FallbackManager(
        handler=handler,
        exceptions=on,
        predicate=if_,
    )

    def _decorator(func: FuncT) -> FuncT:
        @functools.wraps(func)
        async def _wrapper(*args: Any, **kwargs: Any) -> Any:
            return await manager(func, *args, **kwargs)

        _wrapper._original = func  # type: ignore[attr-defined]
        _wrapper._manager = manager  # type: ignore[attr-defined]

        return cast(FuncT, _wrapper)

    return _decorator
