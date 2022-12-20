import asyncio

import pytest

from hyx.bulkhead.api import bulkhead
from hyx.bulkhead.exceptions import BulkheadFull


async def test__bulkhead__decorator() -> None:
    @bulkhead(max_execs=3, max_parallel_execs=2)
    async def calculations() -> float:
        await asyncio.sleep(0.5)
        return 42

    assert await calculations() == 42


async def test__bulkhead__context() -> None:
    async with bulkhead(max_execs=3, max_parallel_execs=2):
        await asyncio.sleep(0.2)
        assert True


async def test__bulkhead__capacity_exceeded() -> None:
    bh = bulkhead(max_execs=2, max_parallel_execs=2)

    with pytest.raises(BulkheadFull):
        async with bh:
            async with bh:
                async with bh:
                    assert True


async def test__bulkhead__capacity_exceeded_from_different_coroutines() -> None:
    bh = bulkhead(max_execs=3, max_parallel_execs=2)

    async def calc() -> None:
        async with bh:
            await asyncio.sleep(0.2)

    tasks = [
        asyncio.create_task(calc()),
        asyncio.create_task(calc()),
        asyncio.create_task(calc()),
        asyncio.create_task(calc()),
    ]

    with pytest.raises(BulkheadFull):
        await asyncio.gather(
            *tasks,
            return_exceptions=False,
        )

    for task in tasks:
        task.cancel()


async def test__bulkhead__execution_order() -> None:
    bh = bulkhead(max_execs=3, max_parallel_execs=1)

    actual_result = []

    async def calc1() -> None:
        await asyncio.sleep(0.2)
        async with bh:
            actual_result.append(1)

    async def calc2() -> None:
        async with bh:
            await asyncio.sleep(0.1)
            actual_result.append(2)

    async def calc3() -> None:
        await asyncio.sleep(0.1)
        async with bh:
            actual_result.append(3)

    await asyncio.gather(
        asyncio.create_task(calc1()),
        asyncio.create_task(calc2()),
        asyncio.create_task(calc3()),
        return_exceptions=False,
    )

    assert actual_result == [2, 3, 1]
