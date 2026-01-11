import asyncio
from typing import Any

from hyx.timeout.events import TimeoutListener
from hyx.timeout.exceptions import MaxDurationExceeded
from hyx.timeout.typing import DurationT
from hyx.typing import FuncT


class TimeoutManager:
    __slots__ = (
        "_name",
        "_timeout_secs",
        "_event_dispatcher",
        "_is_timeout",
        "_timeout_task",
    )

    def __init__(
        self,
        timeout_secs: DurationT,
        event_dispatcher: TimeoutListener,
        name: str | None = None,
    ) -> None:
        self._timeout_secs = timeout_secs

        self._is_timeout: asyncio.Event | None = None
        self._timeout_task: asyncio.TimerHandle | None = None

        self._name = name or ""
        self._event_dispatcher = event_dispatcher

    @property
    def name(self) -> str:
        return self._name

    def _on_timeout(self, watched_task: asyncio.Task | None) -> None:
        if self._is_timeout:
            self._is_timeout.set()

        if watched_task:
            watched_task.cancel()

        self._timeout_task = None
        asyncio.ensure_future(self._event_dispatcher.on_timeout(self))

    async def start(self) -> None:
        """
        Start measuring some code block execution time
        """
        self._is_timeout = asyncio.Event()
        watched_task = asyncio.current_task()

        self._timeout_task = asyncio.get_running_loop().call_later(self._timeout_secs, self._on_timeout, watched_task)

    async def stop(self, error: type[Exception] | None = None) -> None:
        """
        Stop measuring the code block execution time
        """
        if error is asyncio.CancelledError and self._is_timeout and self._is_timeout.is_set():
            await self._event_dispatcher.on_timeout(self)
            raise MaxDurationExceeded

        if self._timeout_task:
            self._timeout_task.cancel()
            self._timeout_task = None

        if self._is_timeout is not None:
            self._is_timeout = None

    async def __call__(self, func: FuncT) -> Any:
        try:
            watched_task: asyncio.Task = asyncio.get_running_loop().create_task(func())

            return await asyncio.wait_for(watched_task, timeout=self._timeout_secs)
        except asyncio.TimeoutError:
            await self._event_dispatcher.on_timeout(self)

            raise MaxDurationExceeded from None
