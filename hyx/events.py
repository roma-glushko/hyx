import asyncio
import traceback
import weakref
from typing import Callable, Generic, List, Optional, Protocol, Sequence, TypeVar, Union, cast, runtime_checkable

ComponentT = TypeVar("ComponentT")
ListenerT = TypeVar("ListenerT")

_EVENT_MANAGER: Optional["EventManager"] = None


class EventManager:
    """
    Keeps track of currently active listeners tasks dispatched on the recent events
    """

    __slots__ = ("_listener_tasks",)

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


@runtime_checkable
class ListenerFactoryT(Protocol):
    async def __call__(self, component: ComponentT) -> ListenerT:
        ...


class ListenerRegistry(Generic[ComponentT, ListenerT]):
    """
    A listener registry that helps to register component-wide listeners
    """

    __slots__ = ("_listeners",)

    def __init__(self) -> None:
        self._listeners: list[Union[ListenerT, ListenerFactoryT]] = []

    @property
    def listeners(self) -> list[Union[ListenerT, ListenerFactoryT]]:
        return self._listeners

    def register(self, listener: Union[ListenerT, ListenerFactoryT]) -> None:
        self._listeners.append(listener)


class EventDispatcher(Generic[ComponentT, ListenerT]):
    """
    Dispatches specific sets of listeners that correspond to the specific component on events
    """

    __slots__ = (
        "_event_manager",
        "_local_listeners",
        "_global_listener_registry",
        "_component",
        "_listeners_inited",
        "_inited_listeners",
    )

    def __init__(
        self,
        local_listeners: Optional[Sequence[Union[ListenerT, ListenerFactoryT]]] = None,
        global_listener_registry: Optional[ListenerRegistry] = None,
        event_manager: Optional["EventManager"] = None,
    ) -> None:
        self._event_manager = event_manager if event_manager else _EVENT_MANAGER

        self._local_listeners = local_listeners or []
        self._global_listener_registry = global_listener_registry

        self._component: Optional[ComponentT] = None
        self._inited_listeners: Optional[List[ListenerT]] = None

    @property
    def as_listener(self) -> ListenerT:
        return cast(ListenerT, self)

    def set_component(self, component: ComponentT) -> None:
        self._component = component

    def __getattr__(self, event_handler_name: str) -> Callable:  # TODO: improve return type
        """
        Dispatch listeners on events in highly async way
        """

        async def handle_event(*args, **kwargs) -> None:
            if not await self._get_or_init_listeners():
                return

            listener_task = asyncio.create_task(
                self.execute_listeners(
                    event_handler_name,
                    *args,
                    **kwargs,
                )
            )

            if self._event_manager:
                self._event_manager.add(listener_task)

        return handle_event

    async def execute_listeners(self, event_handler_name: str, *args, **kwargs) -> None:
        """
        Execute all relevant listeners in parallel
        """
        listeners = await self._get_or_init_listeners()

        if not listeners:
            return

        listeners_to_wakeup = [
            getattr(listener, event_handler_name)(*args, **kwargs)
            for listener in listeners
            if hasattr(listener, event_handler_name)
        ]

        if not listeners_to_wakeup:
            return

        await asyncio.gather(*listeners_to_wakeup)

    async def _get_or_init_listeners(self) -> List[ListenerT]:
        if self._inited_listeners is not None:
            return self._inited_listeners

        assert self._component is not None, "Component has not been assigned to event dispatcher"

        self._inited_listeners = []

        global_listeners = self._global_listener_registry.listeners if self._global_listener_registry else []

        for listeners in [self._local_listeners, global_listeners]:
            for listener in listeners:
                if isinstance(listener, ListenerFactoryT):
                    # factory
                    self._inited_listeners.append(await listener(self._component))
                    continue

                # singletons
                self._inited_listeners.append(listener)

        return self._inited_listeners


def get_default_name(func: Optional[Callable] = None) -> str:
    """
    Get the default name of the component based on code context where it's being used
    """
    if func:
        # we have function when we are in the decorator mode
        try:
            return func.__qualname__
        except AttributeError:
            return func.__name__

    # this is more for context managers
    traceback.extract_stack(limit=3)
    # TODO:
    return ""
