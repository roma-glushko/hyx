from typing import Optional

from hyx.ratelimit.buckets import LeakyBucket, TokenBucket
from hyx.ratelimit.exceptions import EmptyBucket, FilledBucket, RateLimitExceeded


class RateLimiter:
    async def acquire(self) -> None:
        raise NotImplementedError


class TokenBucketLimiter(RateLimiter):
    """
    Token Bucket Rate Limiter
    Replenish tokens as time passes on. If tokens are available, executions can be allowed.
    Otherwise, it's going to be rejected with RateLimitExceeded
    """

    __slots__ = ("_token_bucket",)

    def __init__(self, max_executions: float, per_time_secs: float, bucket_size: Optional[float] = None) -> None:
        self._token_bucket = TokenBucket(max_executions, per_time_secs, bucket_size)

    @property
    def bucket(self) -> TokenBucket:
        return self._token_bucket

    async def acquire(self) -> None:
        try:
            await self._token_bucket.take()
        except EmptyBucket as e:
            raise RateLimitExceeded from e


class LeakyTokenBucketLimiter(RateLimiter):
    def __init__(self) -> None:
        ...

    async def acquire(self) -> None:
        ...


class LeakyBucketLimiter(RateLimiter):
    def __init__(self, max_executions: float, per_time_secs: float) -> None:
        self._leaky_bucket = LeakyBucket(max_executions, per_time_secs)

    @property
    def bucket(self) -> LeakyBucket:
        return self._leaky_bucket

    async def acquire(self) -> None:
        try:
            await self._leaky_bucket.fill()
        except FilledBucket as e:
            raise RateLimitExceeded from e
