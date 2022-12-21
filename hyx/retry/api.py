import functools
from typing import Any, Callable, cast

from hyx.common.typing import ExceptionsT, FuncT
from hyx.retry.manager import RetryManager
from hyx.retry.typing import AttemptsT, BackoffsT, JittersT


def retry(
    *,
    on: ExceptionsT = Exception,
    attempts: AttemptsT = 3,
    backoff: BackoffsT = 0.5,
    jitter: JittersT = None,
) -> Callable[[Callable], Callable]:
    """
    Retry given function on specified exceptions using defined wait strategy and jitter
    """
    manager = RetryManager(
        exceptions=on,
        attempts=attempts,
        backoff=backoff,
        jitter=jitter,
    )

    def _decorator(func: FuncT) -> FuncT:
        @functools.wraps(func)
        async def _wrapper(*args: Any, **kwargs: Any) -> Any:
            return await manager(functools.partial(func, *args, **kwargs))

        _wrapper.__original__ = func
        _wrapper.__manager__ = manager

        return cast(FuncT, _wrapper)

    return _decorator
