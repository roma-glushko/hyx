import asyncio
from unittest.mock import Mock

import pytest

from hyx.bulkhead import BulkheadListener, bulkhead
from hyx.bulkhead.exceptions import BulkheadFull
from hyx.bulkhead.manager import BulkheadManager
from tests.conftest import event_manager


class Listener(BulkheadListener):
    def __init__(self) -> None:
        self.is_full = Mock()

    async def on_bulkhead_full(self, bulkhead: "BulkheadManager") -> None:
        self.is_full()


async def test__bulkhead__decorator() -> None:
    listener = Listener()

    @bulkhead(max_capacity=3, max_concurrency=2, listeners=(listener,))
    async def calculations() -> float:
        await asyncio.sleep(0.5)
        return 42

    assert await calculations() == 42

    await event_manager.wait_for_tasks()
    listener.is_full.assert_not_called()


async def test__bulkhead__context() -> None:
    async with bulkhead(max_capacity=3, max_concurrency=2):
        await asyncio.sleep(0.2)
        assert True


async def test__bulkhead__capacity_exceeded() -> None:
    listener = Listener()
    bh = bulkhead(max_capacity=2, max_concurrency=2, listeners=(listener,))

    with pytest.raises(BulkheadFull):
        async with bh:
            async with bh:
                async with bh:
                    assert True

    await event_manager.wait_for_tasks()
    listener.is_full.assert_called()


async def test__bulkhead__capacity_exceeded_from_different_coroutines() -> None:
    bh = bulkhead(max_capacity=3, max_concurrency=2)

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
    bh = bulkhead(max_capacity=3, max_concurrency=1)

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
