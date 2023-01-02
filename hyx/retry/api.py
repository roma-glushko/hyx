import functools
from typing import Any, Callable, cast

from hyx.common.typing import ExceptionsT, FuncT
from hyx.retry.manager import RetryManager
from hyx.retry.typing import AttemptsT, BackoffsT


def retry(
    *,
    on: ExceptionsT = Exception,
    attempts: AttemptsT = 3,
    backoff: BackoffsT = 0.5,
) -> Callable[[Callable], Callable]:
    """
    `@retry()` decorator retries the function `on` exceptions for the given number of `attempts`.
        Delays after each retry is defined by `backoff` strategy.

    **Parameters:**

    * **on** - Exception or tuple of Exceptions we need to retry on.
    * **attempts** - How many times do we need to retry. If `None`, it will infinitely retry until the success.
    * **backoff** - Backoff Strategy that defines delays on each retry.
        Takes `float` numbers (delay in secs), `list[floats]` (delays on each retry attempt), or `Iterator[float]`

    """
    manager = RetryManager(
        exceptions=on,
        attempts=attempts,
        backoff=backoff,
    )

    def _decorator(func: FuncT) -> FuncT:
        @functools.wraps(func)
        async def _wrapper(*args: Any, **kwargs: Any) -> Any:
            return await manager(functools.partial(func, *args, **kwargs))

        _wrapper.__original__ = func
        _wrapper.__manager__ = manager

        return cast(FuncT, _wrapper)

    return _decorator
