import functools
from types import TracebackType
from typing import Any, Optional, Type, cast

from hyx.common.typing import FuncT
from hyx.ratelimit.managers import RateLimiter, TokenBucketLimiter


class ratelimiter:
    __slots__ = ("_limiter",)

    def __init__(self, limiter: RateLimiter) -> None:
        self._limiter = limiter

    async def __aenter__(self) -> "ratelimiter":
        await self._limiter.acquire()

        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> Optional[bool]:
        return None

    def __call__(self, func: FuncT) -> FuncT:
        """
        Apply ratelimiter as a decorator
        """

        @functools.wraps(func)
        async def _wrapper(*args: Any, **kwargs: Any) -> Any:
            await self._limiter.acquire()

            return await func(*args, **kwargs)

        _wrapper._original = func
        _wrapper._manager = self._limiter

        return cast(FuncT, _wrapper)


class tokenbucket:
    __slots__ = ("_limiter",)

    def __init__(self, max_execs: float, time_period_secs: float, bucket_size: float) -> None:
        self._limiter = TokenBucketLimiter(
            max_execs=max_execs,
            time_period_secs=time_period_secs,
            bucket_size=bucket_size,
        )

    async def __aenter__(self) -> "tokenbucket":
        await self._limiter.acquire()

        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> Optional[bool]:
        return None

    def __call__(self, func: FuncT) -> FuncT:
        """
        Apply ratelimiter as a decorator
        """

        @functools.wraps(func)
        async def _wrapper(*args: Any, **kwargs: Any) -> Any:
            await self._limiter.acquire()

            return await func(*args, **kwargs)

        _wrapper._original = func
        _wrapper._manager = self._limiter

        return cast(FuncT, _wrapper)
