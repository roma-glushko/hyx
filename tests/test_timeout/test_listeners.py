import asyncio
from unittest.mock import Mock

import pytest

from hyx.common.events import set_event_manager, EventManager
from hyx.timeout import timeout
from hyx.timeout.exceptions import MaxDurationExceeded
from hyx.timeout.listeners import TimeoutListener
from hyx.timeout.manager import TimeoutManager

event_manager = EventManager()
set_event_manager(event_manager)


class Listener(TimeoutListener):
    def __init__(self) -> None:
        self.on_timeout_mock = Mock()

    async def on_timeout(self, timeout: TimeoutManager) -> None:
        self.on_timeout_mock()


async def test__timeout__execute_listener_in_decorator() -> None:
    listener1, listener2 = Listener(), Listener()

    @timeout(0.1, listeners=(listener1, listener2))
    async def slow_func() -> float:
        await asyncio.sleep(10)
        return 42

    with pytest.raises(MaxDurationExceeded):
        await slow_func()

    await event_manager.wait_for_tasks()

    listener1.on_timeout_mock.assert_called()
    listener2.on_timeout_mock.assert_called()


async def test__timeout__execute_listener_in_context() -> None:
    listener = Listener()

    with pytest.raises(MaxDurationExceeded):
        async with timeout(0.1, listeners=(listener,)):
            await asyncio.sleep(1)

    await event_manager.wait_for_tasks()

    listener.on_timeout_mock.assert_called()
