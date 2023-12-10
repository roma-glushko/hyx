import asyncio

import pytest

from hyx.ratelimit import LeakyBucketLimiter, TokenBucketLimiter, leakybucket, ratelimiter, tokenbucket
from hyx.ratelimit.exceptions import RateLimitExceeded


async def test__ratelimiter__decorator() -> None:
    @ratelimiter(limiter=TokenBucketLimiter(max_executions=4, per_time_secs=1, bucket_size=4))
    async def calc() -> float:
        return 42

    for _ in range(4):
        assert await calc() == 42


async def test__ratelimiter__token_bucket_decorator() -> None:
    @tokenbucket(max_executions=4, per_time_secs=1, bucket_size=4)
    async def calc() -> float:
        return 42

    for _ in range(4):
        assert await calc() == 42


async def test__ratelimiter__leaky_bucket_decorator() -> None:
    @leakybucket(max_executions=4, per_time_secs=1, bucket_size=4)
    async def calc() -> float:
        return 42

    for _ in range(4):
        assert await calc() == 42


async def test__ratelimiter__context_manager() -> None:
    limiter = ratelimiter(limiter=TokenBucketLimiter(max_executions=4, per_time_secs=1, bucket_size=4))

    for _ in range(4):
        async with limiter:
            assert True


async def test__ratelimiter__token_bucket_context_manager() -> None:
    limiter = tokenbucket(max_executions=4, per_time_secs=1, bucket_size=4)

    for _ in range(4):
        async with limiter:
            assert True


async def test__ratelimiter__leaky_bucket_context_manager() -> None:
    leakybucket(max_executions=4, per_time_secs=1, bucket_size=4)

    async def calc() -> float:
        return 42

    for _ in range(4):
        assert await calc() == 42


async def test__ratelimiter__leaky_bucket_limit_exceeded() -> None:
    @ratelimiter(limiter=LeakyBucketLimiter(max_executions=3, per_time_secs=1))
    async def calc() -> float:
        return 42

    with pytest.raises(RateLimitExceeded):
        for _ in range(4):
            assert await calc() == 42


async def test__ratelimiter__token_bucket_limit_exceeded() -> None:
    @ratelimiter(limiter=TokenBucketLimiter(max_executions=3, per_time_secs=1, bucket_size=3))
    async def calc() -> float:
        return 42

    with pytest.raises(RateLimitExceeded):
        for _ in range(4):
            assert await calc() == 42


async def test__ratelimiter__replenish_after_full_bucket() -> None:
    @ratelimiter(limiter=TokenBucketLimiter(max_executions=3, per_time_secs=1, bucket_size=3))
    async def calc() -> float:
        return 42

    for _ in range(3):
        assert await calc() == 42

    await asyncio.sleep(1)

    assert await calc() == 42


async def test__ratelimiter__fully_replenish_after_time_period() -> None:
    @tokenbucket(max_executions=3, per_time_secs=1, bucket_size=3)
    async def calc() -> float:
        return 42

    for _ in range(3):
        assert await calc() == 42

    await asyncio.sleep(1)

    for _ in range(3):
        assert await calc() == 42


async def test__ratelimiter__token_bucket_leak_after_time_period() -> None:
    @ratelimiter(limiter=LeakyBucketLimiter(max_executions=3, per_time_secs=1))
    async def calc() -> float:
        return 42

    for _ in range(3):
        assert await calc() == 42

    await asyncio.sleep(1)

    for _ in range(3):
        assert await calc() == 42
