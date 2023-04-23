import asyncio
from unittest.mock import Mock

import pytest

from hyx.timeout import TimeoutListener, timeout
from hyx.timeout.exceptions import MaxDurationExceeded
from hyx.timeout.manager import TimeoutManager
from tests.conftest import event_manager


class Listener(TimeoutListener):
    def __init__(self) -> None:
        self.timed_out = Mock()

    async def on_timeout(self, timeout: TimeoutManager) -> None:
        self.timed_out()


async def test__timeout__decorator() -> None:
    @timeout(0.2)
    async def quick_func() -> float:
        await asyncio.sleep(0.01)
        return 42

    assert (await quick_func()) == 42


async def test__timeout__context() -> None:
    var = 41
    listener = Listener()

    async with timeout(0.5, listeners=(listener,)):
        var += 1
        await asyncio.sleep(0.01)

    assert var == 42

    await event_manager.wait_for_tasks()
    listener.timed_out.assert_not_called()


async def test__timeout__context_timeout_exceeded() -> None:
    listener = Listener()

    with pytest.raises(MaxDurationExceeded):
        async with timeout(0.01, listeners=(listener,)):
            await asyncio.sleep(1)

    await event_manager.wait_for_tasks()

    listener.timed_out.assert_called()


async def test__timeout__duration_equal() -> None:
    listener1, listener2 = Listener(), Listener()

    @timeout(0.1, listeners=(listener1, listener2))
    async def func() -> float:
        await asyncio.sleep(0.1)
        return 42

    with pytest.raises(MaxDurationExceeded):
        await func()

    await event_manager.wait_for_tasks()

    listener1.timed_out.assert_called()
    listener2.timed_out.assert_called()


async def test__timeout__max_duration_exceeded() -> None:
    @timeout(0.01)
    async def slow_func() -> float:
        await asyncio.sleep(10)
        return 42

    with pytest.raises(MaxDurationExceeded):
        await slow_func()
