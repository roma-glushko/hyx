from typing import TYPE_CHECKING

from hyx.ratelimit.buckets import TokenBucket
from hyx.ratelimit.exceptions import EmptyBucket, RateLimitExceeded

if TYPE_CHECKING:
    from hyx.ratelimit.events import RateLimiterListener


class RateLimiter:
    _name: str | None
    _event_dispatcher: "RateLimiterListener | None"

    @property
    def name(self) -> str | None:
        return self._name

    async def acquire(self) -> None:
        raise NotImplementedError


class TokenBucketLimiter(RateLimiter):
    """
    Token Bucket Rate Limiter
    Replenish tokens as time passes on. If tokens are available, executions can be allowed.
    Otherwise, it's going to be rejected with RateLimitExceeded
    """

    __slots__ = ("_token_bucket", "_name", "_event_dispatcher")

    def __init__(
        self,
        max_executions: float,
        per_time_secs: float,
        bucket_size: float | None = None,
        name: str | None = None,
        event_dispatcher: "RateLimiterListener | None" = None,
    ) -> None:
        self._token_bucket = TokenBucket(max_executions, per_time_secs, bucket_size)
        self._name = name
        self._event_dispatcher = event_dispatcher

    @property
    def bucket(self) -> TokenBucket:
        return self._token_bucket

    async def acquire(self) -> None:
        try:
            await self._token_bucket.take()
        except EmptyBucket as e:
            if self._event_dispatcher:
                await self._event_dispatcher.on_rate_limited(self)
            raise RateLimitExceeded from e


class LeakyTokenBucketLimiter(RateLimiter):
    __slots__ = ("_name", "_event_dispatcher")

    def __init__(
        self,
        name: str | None = None,
        event_dispatcher: "RateLimiterListener | None" = None,
    ) -> None:
        self._name = name
        self._event_dispatcher = event_dispatcher

    async def acquire(self) -> None: ...
