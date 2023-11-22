from typing import Optional

from hyx.ratelimit.tokenbucket import TokenBucket


class RateLimiter:
    async def acquire(self) -> None:
        raise NotImplementedError


class TokenBucketLimiter(RateLimiter):
    """
    Token Bucket Rate Limiter
    Replenish tokens as time passes on. If tokens are available, executions can be allowed.
    Otherwise, it's going to be rejected with RateLimitExceeded
    """
    
     __slots__ = (
        "_token_bucket",
    )

    def __init__(self, max_executions: float, per_time_secs: float, bucket_size: Optional[float] = None) -> None:
        self._token_bucket = TokenBucket(max_executions, per_time_secs, bucket_size)

    @property
    def tokens(self) -> float:
        return self._token_bucket.tokens

    @property
    def empty(self) -> bool:
        return self._token_bucket.empty

    async def acquire(self) -> None:
        await self._token_bucket.acquire()


class LeakyTokenBucketLimiter(RateLimiter):
    def __init__(self) -> None:
        ...

    async def acquire(self) -> None:
        ...
