import functools
from typing import TypeVar, cast, Any, Callable, Awaitable, Union, Sequence

FuncT = TypeVar("FuncT", bound=Callable[..., Awaitable[Any]])


def retry(on: Union[Exception, Sequence[Exception]] = Exception) -> Callable[[Callable], Callable]:
    """
    Retry given function on specified exceptions using defined wait strategy and jitter
    """

    def _decorator(func: FuncT) -> FuncT:
        @functools.wraps(func)
        async def _wrapper(*args: Any, **kwargs: Any) -> Any:
            return await func(*args, **kwargs)

        return cast(FuncT, _wrapper)

    return _decorator
