import asyncio
import weakref
from typing import Callable, Generic, TypeVar, Optional

ListenerT = TypeVar("ListenerT", covariant=True)

_EVENT_MANAGER: Optional["EventManager"] = None


class EventManager:
    """
    Keeps track of currently active listeners tasks dispatched on the recent events
    """

    def __init__(self) -> None:
        self._listener_tasks: weakref.WeakSet[asyncio.Task] = weakref.WeakSet()

    def add(self, listener_task: asyncio.Task) -> None:
        self._listener_tasks.add(listener_task)

    async def wait_for_tasks(self) -> None:
        # TODO: allow to specify a timeout
        await asyncio.gather(*list(self._listener_tasks))

    async def cancel_tasks(self) -> None:
        """
        Cancel all inflight listener tasks
        """
        for task in self._listener_tasks:
            task.cancel()

        await self.wait_for_tasks()


def set_event_manager(event_manager: EventManager) -> None:
    # TODO: Do we need any locking?
    global _EVENT_MANAGER

    if _EVENT_MANAGER:
        # TODO: Log this when the logging part is figured out
        # logger.warning("Overriding of current EventManager is not allowed")
        return

    _EVENT_MANAGER = event_manager


class EventDispatcher:
    """
    Dispatches specific sets of listeners that correspond to the specific component on events
    """

    def __init__(self, listeners) -> None:
        self._event_manager = _EVENT_MANAGER
        self._listeners = listeners

    async def execute_listeners(self, event_handler_name: str, *args, **kwargs) -> None:
        """
        Execute all relevant listeners in parallel
        """
        listeners = [
            getattr(listener, event_handler_name)(*args, **kwargs)
            for listener in self._listeners
            if hasattr(listener, event_handler_name)
        ]

        if not listeners:
            return

        await asyncio.gather(*listeners)

    def __getattr__(self, event_handler_name: str) -> Callable:  # TODO: improve return type
        """
        Dispatch listeners on events in highly async way
        """

        async def handle_event(*args, **kwargs) -> None:
            listener_task = asyncio.create_task(self.execute_listeners(
                event_handler_name,
                *args,
                **kwargs,
            ))

            if self._event_manager:
                self._event_manager.add(listener_task)

        return handle_event


class ListenerRegistry(Generic[ListenerT]):
    """
    A listener registry that helps to register component-wide listeners
    """

    def __init__(self) -> None:
        self._listeners: list[ListenerT] = []

    @property
    def listeners(self) -> list[ListenerT]:
        return self._listeners

    def register(self, listener: ListenerT) -> None:
        self._listeners.append(listener)
