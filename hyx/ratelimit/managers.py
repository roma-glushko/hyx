import asyncio

from hyx.ratelimit.exceptions import RateLimitExceeded


class RateLimiter:
    async def acquire(self) -> None:
        raise NotImplementedError


class TokenBucketLimiter(RateLimiter):
    """
    Token Bucket Rate Limiter
    Replenish tokens as time passes on. If tokens are available, executions can be allowed.
    Otherwise, it's going to be rejected with RateLimitExceeded
    """

    def __init__(self, max_execs: float, time_period_secs: float, bucket_size: float) -> None:
        self._max_execs = max_execs
        self._time_period_secs = time_period_secs
        self._bucket_size = bucket_size

        self._loop = asyncio.get_running_loop()
        self._token_per_secs = self._time_period_secs / self._max_execs

        self._tokens = self._bucket_size
        self._next_replenish_at = self._loop.time() + self._token_per_secs

    @property
    def tokens(self) -> float:
        return self._tokens

    @property
    def empty(self) -> bool:
        return self._tokens <= 0

    async def acquire(self) -> None:
        if not self.empty:
            self._tokens -= 1
            return

        now = self._loop.time()

        next_replenish = self._next_replenish_at
        until_next_replenish = next_replenish - now

        if until_next_replenish > 0:
            raise RateLimitExceeded

        tokens_to_add = min(self._bucket_size, 1 + abs(until_next_replenish / self._token_per_secs))

        self._next_replenish_at = max(
            next_replenish + tokens_to_add * self._token_per_secs,
            now + self._token_per_secs,
        )

        # account for the current call
        self._tokens = tokens_to_add - 1
        return


class LeakyTokenBucketLimiter(RateLimiter):
    def __init__(self) -> None:
        ...

    async def acquire(self) -> None:
        ...
