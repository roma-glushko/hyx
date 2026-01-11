import functools
from collections.abc import Sequence
from types import TracebackType
from typing import Any, cast

from hyx.events import EventDispatcher, EventManager, get_default_name
from hyx.ratelimit.events import _RATELIMITER_LISTENERS, RateLimiterListener
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
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
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
    * **name** *(None | str)* - A component name or ID (will be passed to listeners and mentioned in metrics)
    * **listeners** *(None | Sequence[RateLimiterListener])* - List of listeners for this component
    * **event_manager** *(None | EventManager)* - Event manager for tracking listener tasks
    """

    __slots__ = ("_limiter", "_name")

    def __init__(
        self,
        max_executions: float,
        per_time_secs: float,
        bucket_size: float | None = None,
        name: str | None = None,
        listeners: Sequence[RateLimiterListener] | None = None,
        event_manager: EventManager | None = None,
    ) -> None:
        self._name = name

        event_dispatcher: EventDispatcher[TokenBucketLimiter, RateLimiterListener] = EventDispatcher(
            listeners,
            _RATELIMITER_LISTENERS,
            event_manager=event_manager,
        )

        self._limiter = TokenBucketLimiter(
            max_executions=max_executions,
            per_time_secs=per_time_secs,
            bucket_size=bucket_size,
            name=name,
            event_dispatcher=event_dispatcher.as_listener,
        )

        event_dispatcher.set_component(self._limiter)

    async def __aenter__(self) -> "tokenbucket":
        await self._limiter.acquire()

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
        return None

    def __call__(self, func: FuncT) -> FuncT:
        """
        Apply ratelimiter as a decorator
        """
        # Set name from function if not provided
        if self._limiter._name is None:
            self._limiter._name = get_default_name(func)

        @functools.wraps(func)
        async def _wrapper(*args: Any, **kwargs: Any) -> Any:
            await self._limiter.acquire()

            return await func(*args, **kwargs)

        _wrapper._original = func  # type: ignore[attr-defined]
        _wrapper._manager = self._limiter  # type: ignore[attr-defined]

        return cast(FuncT, _wrapper)
