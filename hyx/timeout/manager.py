import asyncio
from typing import Any

from hyx.timeout.exceptions import MaxDurationExceeded
from hyx.timeout.typing import FuncT, DurationT


class TimeoutManager:
    def __init__(self, max_duration: DurationT) -> None:
        self._max_duration = max_duration

    async def __call__(self, func: FuncT) -> Any:
        event_loop = asyncio.get_running_loop()

        try:
            watched_task: asyncio.Task = event_loop.create_task(func())

            return await asyncio.wait_for(watched_task, timeout=self._max_duration)
        except asyncio.TimeoutError:
            raise MaxDurationExceeded
