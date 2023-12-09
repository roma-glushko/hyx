import asyncio

import pytest

from hyx.ratelimit.buckets import TokenBucket
from hyx.ratelimit.exceptions import EmptyBucket


async def test__token_bucket_success() -> None:
    bucket = TokenBucket(3, 1, 3)

    for i in range(3):
        assert bucket.tokens == (3 - i)
        await bucket.take()
    assert bucket.empty is True


async def test__token_bucket_limit_exceeded() -> None:
    bucket = TokenBucket(3, 1, 3)

    with pytest.raises(EmptyBucket):
        for _ in range(4):
            await bucket.take()


async def test__token_bucket__fully_replenish_after_time_period() -> None:
    bucket = TokenBucket(3, 1, 3)

    for _ in range(3):
        await bucket.take()

    await asyncio.sleep(3)

    assert bucket.tokens == 3
    assert bucket.empty is False
