import functools
from types import TracebackType
from typing import Any, Optional, Sequence, Type, cast

from hyx.events import EventDispatcher, get_default_name, EventManager
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
        name: Optional[str] = None,
        listeners: Optional[Sequence[TimeoutListener]] = None,
        event_manager: Optional["EventManager"] = None,
    ) -> None:
        self._timeout_secs = timeout_secs
        self._timeout_manager: Optional[TimeoutManager] = None

        self._name = name or get_default_name()

        self._event_manager = event_manager
        self._local_listeners = listeners

    def _create_timeout(self) -> TimeoutManager:
        event_dispatcher = EventDispatcher[TimeoutManager, TimeoutListener](
            self._local_listeners,
            _TIMEOUT_LISTENERS,
            event_manager=self._event_manager,
        )

        timeout = TimeoutManager(
            name=self._name,
            timeout_secs=self._timeout_secs,
            event_dispatcher=event_dispatcher.as_listener,
        )

        event_dispatcher.set_component(timeout)

        return timeout

    async def __aenter__(self) -> "timeout":
        if self._timeout_manager is not None:
            await self._timeout_manager.stop()
            self._timeout_manager = None

        self._timeout_manager = self._create_timeout()

        await self._timeout_manager.start()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[Exception]],
        exc_val: Optional[Exception],
        exc_tb: Optional[TracebackType],
    ) -> Optional[bool]:
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
