import asyncio

import pytest

from hyx.ratelimit import TokenBucketLimiter, ratelimiter, tokenbucket
from hyx.ratelimit.exceptions import RateLimitExceeded


async def test__ratelimiter__decorator() -> None:
    @ratelimiter(limiter=TokenBucketLimiter(max_execs=4, time_period_secs=1, bucket_size=4))
    async def calc() -> float:
        return 42

    for _ in range(4):
        assert await calc() == 42


async def test__ratelimiter__token_bucket_decorator() -> None:
    @tokenbucket(max_execs=4, time_period_secs=1, bucket_size=4)
    async def calc() -> float:
        return 42

    for _ in range(4):
        assert await calc() == 42


async def test__ratelimiter__context_manager() -> None:
    limiter = ratelimiter(limiter=TokenBucketLimiter(max_execs=4, time_period_secs=1, bucket_size=4))

    for _ in range(4):
        async with limiter:
            assert True


async def test__ratelimiter__token_bucket_context_manager() -> None:
    limiter = tokenbucket(max_execs=4, time_period_secs=1, bucket_size=4)

    for _ in range(4):
        async with limiter:
            assert True


async def test__ratelimiter__limit_exceeded() -> None:
    @ratelimiter(limiter=TokenBucketLimiter(max_execs=3, time_period_secs=1, bucket_size=3))
    async def calc() -> float:
        return 42

    with pytest.raises(RateLimitExceeded):
        for _ in range(4):
            assert await calc() == 42


async def test__ratelimiter__replenish_after_full_bucket() -> None:
    @ratelimiter(limiter=TokenBucketLimiter(max_execs=3, time_period_secs=1, bucket_size=3))
    async def calc() -> float:
        return 42

    for _ in range(3):
        assert await calc() == 42

    await asyncio.sleep(1)

    assert await calc() == 42


async def test__ratelimiter__fully_replenish_after_time_period() -> None:
    @tokenbucket(max_execs=3, time_period_secs=1, bucket_size=3)
    async def calc() -> float:
        return 42

    for _ in range(3):
        assert await calc() == 42

    await asyncio.sleep(1)

    for _ in range(3):
        assert await calc() == 42
