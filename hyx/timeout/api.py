import functools
from collections.abc import Sequence
from types import TracebackType
from typing import Any, cast

from hyx.events import EventManager, create_manager, get_default_name
from hyx.timeout.events import _TIMEOUT_LISTENERS, TimeoutListener
from hyx.timeout.manager import TimeoutManager
from hyx.typing import FuncT


class timeout:
    """
    Timeout Decontext

    **Parameters:**

    * **timeout_secs** *(float)* - Max amount of time to wait for the action in seconds
    * **name** *(None | str)* - A component name or ID (will be passed to listeners and mention in metrics)
    * **listeners** *(None | Sequence[TimeoutListener])* - List of listeners of this concreate component state
    """

    __slots__ = (
        "_timeout_secs",
        "_timeout_manager",
        "_name",
        "_event_manager",
        "_local_listeners",
    )

    def __init__(
        self,
        timeout_secs: float,
        *,
        name: str | None = None,
        listeners: Sequence[TimeoutListener] | None = None,
        event_manager: "EventManager | None" = None,
    ) -> None:
        self._timeout_secs = timeout_secs
        self._timeout_manager: TimeoutManager | None = None

        self._name = name or get_default_name()

        self._event_manager = event_manager
        self._local_listeners = listeners

    def _create_timeout(self) -> TimeoutManager:
        return create_manager(
            TimeoutManager,
            self._local_listeners,
            _TIMEOUT_LISTENERS,
            event_manager=self._event_manager,
            name=self._name,
            timeout_secs=self._timeout_secs,
        )

    async def __aenter__(self) -> "timeout":
        if self._timeout_manager is not None:
            await self._timeout_manager.stop()
            self._timeout_manager = None

        self._timeout_manager = self._create_timeout()

        await self._timeout_manager.start()
        return self

    async def __aexit__(
        self,
        exc_type: type[Exception] | None,
        exc_val: Exception | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
        if self._timeout_manager:
            await self._timeout_manager.stop(error=exc_type)
            self._timeout_manager = None

        return None

    def __call__(self, func: FuncT) -> FuncT:
        """
        Apply timeout as a decorator
        """
        manager = self._create_timeout()

        @functools.wraps(func)
        async def _wrapper(*args: Any, **kwargs: Any) -> Any:
            return await manager(cast(FuncT, functools.partial(func, *args, **kwargs)))

        _wrapper._original = func  # type: ignore[attr-defined]
        _wrapper._manager = manager  # type: ignore[attr-defined]

        return cast(FuncT, _wrapper)
