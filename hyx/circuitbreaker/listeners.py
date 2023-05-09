from typing import TYPE_CHECKING

from hyx.circuitbreaker.states import BreakerState, FailingState, RecoveringState, WorkingState
from hyx.common.events import ListenerRegistry

if TYPE_CHECKING:
    ...

_BREAKER_LISTENERS: ListenerRegistry["BreakerListener"] = ListenerRegistry()


class BreakerListener:
    async def on_working(self, current_state: BreakerState, next_state: WorkingState) -> None:
        ...

    async def on_recovering(self, current_state: BreakerState, next_state: RecoveringState) -> None:
        ...

    async def on_failing(self, current_state: BreakerState, next_state: FailingState) -> None:
        ...


def register_breaker_listener(listener: BreakerListener) -> None:
    """
    Register a listener that will listen to all circuit breaker components in the system
    """
    global _BREAKER_LISTENERS

    _BREAKER_LISTENERS.register(listener)
