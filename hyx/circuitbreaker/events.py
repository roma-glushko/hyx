from typing import TYPE_CHECKING, Union

from hyx.circuitbreaker.context import BreakerContext
from hyx.circuitbreaker.managers import ConsecutiveCircuitBreaker
from hyx.events import ListenerFactoryT, ListenerRegistry

if TYPE_CHECKING:
    from hyx.circuitbreaker.states import BreakerState, FailingState, RecoveringState, WorkingState

_BREAKER_LISTENERS: ListenerRegistry["ConsecutiveCircuitBreaker", "BreakerListener"] = ListenerRegistry()


class BreakerListener:
    # TODO: add on success and on exception methods

    async def on_working(
        self,
        context: BreakerContext,
        current_state: "BreakerState",
        next_state: "WorkingState",
    ) -> None:
        ...

    async def on_recovering(
        self,
        context: BreakerContext,
        current_state: "BreakerState",
        next_state: "RecoveringState",
    ) -> None:
        ...

    async def on_failing(
        self,
        context: BreakerContext,
        current_state: "BreakerState",
        next_state: "FailingState",
    ) -> None:
        ...

    async def on_success(self, context: BreakerContext, state: "BreakerState") -> None:
        ...


def register_breaker_listener(listener: Union[BreakerListener, ListenerFactoryT]) -> None:
    """
    Register a listener that will listen to all circuit breaker components in the system
    """
    global _BREAKER_LISTENERS

    _BREAKER_LISTENERS.register(listener)
