import functools
from types import TracebackType
from typing import Any, Optional, Type, cast

from hyx.ratelimit.managers import RateLimiter, TokenBucketLimiter
from hyx.typing import FuncT


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

        _wrapper._original = func  # type: ignore[attr-defined]
        _wrapper._manager = self._limiter  # type: ignore[attr-defined]

        return cast(FuncT, _wrapper)


class tokenbucket:
    """
    Constant Rate Limiting based on the Token Bucket algorithm.

    **Parameters**

    * **max_executions** *(float)* - How many executions are permitted?
    * **per_time_secs** *(float)* - Per what time span? (in seconds)
    * **bucket_size** *(None | float)* - The token bucket size. Defines the max number of executions
        that are permitted to happen during bursts.
        The burst is when no executions have happened for a long time, and then you are receiving a
        bunch of them at the same time. Equal to *max_executions* by default.
    """

    __slots__ = ("_limiter",)

    def __init__(self, max_executions: float, per_time_secs: float, bucket_size: Optional[float] = None) -> None:
        self._limiter = TokenBucketLimiter(
            max_executions=max_executions,
            per_time_secs=per_time_secs,
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

        _wrapper._original = func  # type: ignore[attr-defined]
        _wrapper._manager = self._limiter  # type: ignore[attr-defined]

        return cast(FuncT, _wrapper)
