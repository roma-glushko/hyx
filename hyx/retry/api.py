import functools
import warnings
from collections.abc import Callable, Sequence
from typing import Any, cast

from hyx.events import EventDispatcher, EventManager, get_default_name
from hyx.ratelimit.buckets import TokenBucket
from hyx.retry.events import _RETRY_LISTENERS, RetryListener
from hyx.retry.manager import RetryManager
from hyx.retry.typing import AttemptsT, BackoffsT, BucketRetryT
from hyx.typing import ExceptionsT, FuncT


def retry(
    *,
    on: ExceptionsT = Exception,
    attempts: AttemptsT = 3,
    backoff: BackoffsT = 0.5,
    name: str | None = None,
    per_time_secs: BucketRetryT | None = None,
    bucket_size: BucketRetryT | None = None,
    listeners: Sequence[RetryListener] | None = None,
    event_manager: "EventManager | None" = None,
) -> Callable[[Callable], Callable]:
    """
    `@retry()` decorator retries the function `on` exceptions for the given number of `attempts`.
        Delays after each retry is defined by `backoff` strategy.

    **Parameters:**

    * **on** - Exception or tuple of Exceptions we need to retry on.
    * **attempts** - How many times do we need to retry. If `None`, it will infinitely retry until the success.
    * **backoff** - Backoff Strategy that defines delays on each retry.
        Takes `float` numbers (delay in secs), `list[floats]` (delays on each retry attempt), or `Iterator[float]`
    * **name** *(None | str)* - A component name or ID (will be passed to listeners and mention in metrics)
    * **per_time_secs** *(None | float)* - Token bucket: time period in seconds for token replenishment.
        When specified with `bucket_size`, enables rate-limited retries using a token bucket algorithm.
    * **bucket_size** *(None | int)* - Token bucket: maximum number of tokens (retry attempts) that can be stored.
        Defaults to `attempts` if `per_time_secs` is specified but `bucket_size` is not.
    * **listeners** *(None | Sequence[RetryListener])* - List of listeners of this concrete component state
    * **event_manager** *(None | EventManager)* - Event manager for tracking listener tasks
    """

    def _decorator(func: FuncT) -> FuncT:
        # Create token bucket limiter if bucket parameters are provided
        limiter = None
        if per_time_secs is not None and attempts:
            effective_bucket_size = bucket_size if bucket_size is not None else attempts
            limiter = TokenBucket(attempts, per_time_secs, effective_bucket_size)

        event_dispatcher = EventDispatcher[RetryManager, RetryListener](
            listeners,
            _RETRY_LISTENERS,
            event_manager=event_manager,
        )

        manager = RetryManager(
            name=name or get_default_name(func),
            exceptions=on,
            attempts=attempts,
            backoff=backoff,
            event_dispatcher=event_dispatcher.as_listener,
            limiter=limiter,
        )

        event_dispatcher.set_component(manager)

        @functools.wraps(func)
        async def _wrapper(*args: Any, **kwargs: Any) -> Any:
            return await manager(cast(FuncT, functools.partial(func, *args, **kwargs)))

        _wrapper._original = func  # type: ignore[attr-defined]
        _wrapper._manager = manager  # type: ignore[attr-defined]

        return cast(FuncT, _wrapper)

    return _decorator


def bucket_retry(
    *,
    on: ExceptionsT = Exception,
    attempts: AttemptsT = 3,
    backoff: BackoffsT = 0.5,
    name: str | None = None,
    per_time_secs: BucketRetryT = 1,
    bucket_size: BucketRetryT = 3,
    listeners: Sequence[RetryListener] | None = None,
    event_manager: "EventManager | None" = None,
) -> Callable[[Callable], Callable]:
    """
    Deprecated: Use `retry()` with `per_time_secs` and `bucket_size` parameters instead.

    `@bucket_retry()` decorator retries until we have tokens in the bucket and at most that number of times per request.
    """
    warnings.warn(
        "bucket_retry() is deprecated. Use retry() with per_time_secs and bucket_size parameters instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return retry(
        on=on,
        attempts=attempts,
        backoff=backoff,
        name=name,
        per_time_secs=per_time_secs,
        bucket_size=bucket_size,
        listeners=listeners,
        event_manager=event_manager,
    )
