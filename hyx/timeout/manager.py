import asyncio
from typing import Any, Optional, Type

from hyx.common.typing import FuncT
from hyx.timeout.exceptions import MaxDurationExceeded
from hyx.timeout.typing import DurationT


class TimeoutManager:
    def __init__(self, max_duration: DurationT) -> None:
        self._max_duration = max_duration
        self._event_loop = asyncio.get_running_loop()

        self._is_timeout: Optional[asyncio.Event] = None
        self._timeout_task: Optional[asyncio.Task] = None

    def _on_timeout(self, watched_task: asyncio.Task) -> None:
        if self._is_timeout:
            self._is_timeout.set()

        watched_task.cancel()
        self._timeout_task = None

    async def start(self) -> None:
        """
        Start measuring some code block execution time
        """
        self._is_timeout = asyncio.Event()
        watched_task = asyncio.current_task()

        self._timeout_task = self._event_loop.call_later(self._max_duration, self._on_timeout, watched_task)

    async def stop(self, error: Optional[Type[BaseException]] = None) -> None:
        """
        Stop measuring the code block execution time
        """
        if error is asyncio.CancelledError and self._is_timeout and self._is_timeout.is_set():
            raise MaxDurationExceeded

        if self._timeout_task:
            self._timeout_task.cancel()
            self._timeout_task = None

        if self._is_timeout is not None:
            self._is_timeout = None

    async def __call__(self, func: FuncT) -> Any:
        try:
            watched_task: asyncio.Task = self._event_loop.create_task(func())

            return await asyncio.wait_for(watched_task, timeout=self._max_duration)
        except asyncio.TimeoutError:
            raise MaxDurationExceeded from None
