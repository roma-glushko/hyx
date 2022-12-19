import asyncio

import pytest

from hyx.timeout import timeout
from hyx.timeout.exceptions import MaxDurationExceeded


async def test__timeout__decorator() -> None:
    @timeout(max_duration=0.5)
    async def quick_func() -> float:
        await asyncio.sleep(0.1)
        return 42

    assert (await quick_func()) == 42


async def test__timeout__context() -> None:
    var = 0
    async with timeout(max_duration=0.5):
        await asyncio.sleep(0.1)
        var = 42

    assert var == 42


async def test__timeout__context_timeout_exceeded() -> None:
    with pytest.raises(MaxDurationExceeded):
        async with timeout(max_duration=0.2):
            await asyncio.sleep(1)


async def test__timeout__duration_equal() -> None:
    @timeout(max_duration=0.3)
    async def func() -> float:
        await asyncio.sleep(0.3)
        return 42

    with pytest.raises(MaxDurationExceeded):
        await func()


async def test__timeout__max_duration_exceeded() -> None:
    @timeout(max_duration=0.2)
    async def slow_func() -> float:
        await asyncio.sleep(10)
        return 42

    with pytest.raises(MaxDurationExceeded):
        await slow_func()
