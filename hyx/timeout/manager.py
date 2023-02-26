import asyncio
from typing import Any, Optional, Type

from hyx.common.typing import FuncT
from hyx.timeout.exceptions import MaxDurationExceeded
from hyx.timeout.listeners import TimeoutListener
from hyx.timeout.typing import DurationT


class TimeoutManager:
    __slots__ = (
        "_name",
        "_timeout_secs",
        "_events",
        "_is_timeout",
        "_timeout_task",
    )

    def __init__(
        self,
        timeout_secs: DurationT,
        name: Optional[str] = None,
        events: Optional[TimeoutListener] = None,
    ) -> None:
        self._timeout_secs = timeout_secs

        self._is_timeout: Optional[asyncio.Event] = None
        self._timeout_task: Optional[asyncio.TimerHandle] = None

        self._name = name
        self._events = events

    @property
    def name(self) -> str:
        return self._name

    async def _on_timeout(self, watched_task: asyncio.Task) -> None:
        if self._is_timeout:
            self._is_timeout.set()

        watched_task.cancel()
        self._timeout_task = None

        if self._events:
            await self._events.on_timeout(self)

    async def start(self) -> None:
        """
        Start measuring some code block execution time
        """
        self._is_timeout = asyncio.Event()
        watched_task = asyncio.current_task()

        self._timeout_task = asyncio.get_running_loop().call_later(
            self._timeout_secs,
            asyncio.ensure_future(self._on_timeout(watched_task)),
        )

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
            watched_task: asyncio.Task = asyncio.get_running_loop().create_task(func())

            return await asyncio.wait_for(watched_task, timeout=self._timeout_secs)
        except asyncio.TimeoutError:
            if self._events:
                await self._events.on_timeout(self)

            raise MaxDurationExceeded from None
