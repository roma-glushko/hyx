import asyncio
from typing import Callable


class EventManager:
    """
    EventManager dispatches specific sets of listeners that correspond to the specific component
    """

    def __init__(self, listeners) -> None:
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
            # TODO: Should we keep the task reference to eventually cancel it on app shutdown?
            asyncio.create_task(self.execute_listeners(
                event_handler_name,
                *args,
                **kwargs,
            ))

        return handle_event
