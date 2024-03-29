import functools
from types import TracebackType
from typing import Any, Optional, Sequence, Type, cast

from hyx.circuitbreaker.events import _BREAKER_LISTENERS, BreakerListener
from hyx.circuitbreaker.managers import ConsecutiveCircuitBreaker
from hyx.circuitbreaker.states import BreakerState
from hyx.circuitbreaker.typing import DelayT
from hyx.events import EventDispatcher, EventManager, get_default_name
from hyx.typing import ExceptionsT, FuncT


class consecutive_breaker:
    """
    Consecutive breaker is the most basic implementation of the circuit breaker pattern.
    It counts the absolute amount of times the system has been **consecutively failed** and
    turns into the `failing` state if the threshold is exceeded.

    Then the breaker waits for the `recovery` delay and moves into the `recovering` state.
    If the action is successful, the breaker gets back to the `working` state.
    Otherwise, it goes back to the `failing` state and waits again.

    Graphically, these transitions look like this:

    ``` mermaid
    stateDiagram
        [*] --> Working: start from
        Working --> Failing: failure threshold is exceeded
        Failing --> Recovering: after the recovery delay
        Recovering --> Working: after the recovery threshold is passed
        Recovering --> Failing: at least one failing result
    ```

    **Parameters**

    * **exceptions** - Exception or list of exceptions that are considered as a failure
    * **failure_threshold** - Consecutive number of failures that turns breaker into the `failing` state
    * **recovery_time_secs** - Time in seconds we give breaker to recover from the `failing` state
    * **recovery_threshold** - Number of consecutive successes that is needed to be pass to
        turn breaker back to the `working` state
    """

    __slots__ = ("_manager",)

    def __init__(
        self,
        exceptions: ExceptionsT = Exception,
        failure_threshold: int = 5,
        recovery_time_secs: DelayT = 30,
        recovery_threshold: int = 3,
        listeners: Optional[Sequence[BreakerListener]] = None,
        name: Optional[str] = None,
        event_manager: Optional["EventManager"] = None,
    ) -> None:
        event_dispatcher = EventDispatcher[ConsecutiveCircuitBreaker, BreakerListener](
            listeners,
            _BREAKER_LISTENERS,
            event_manager=event_manager,
        )

        self._manager = ConsecutiveCircuitBreaker(
            name=name or get_default_name(),
            exceptions=exceptions,
            failure_threshold=failure_threshold,
            recovery_time_secs=recovery_time_secs,
            recovery_threshold=recovery_threshold,
            event_dispatcher=event_dispatcher.as_listener,
        )

        event_dispatcher.set_component(self._manager)

    @property
    def state(self) -> "BreakerState":
        return self._manager.state

    async def __aenter__(self) -> "consecutive_breaker":
        await self._manager.acquire()

        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> Optional[bool]:
        await self._manager.release(exc_val)

        return None

    def __call__(self, func: FuncT) -> FuncT:
        """
        Apply Consecutive Circuit Breaker as decorator
        """

        @functools.wraps(func)
        async def _wrapper(*args: Any, **kwargs: Any) -> Any:
            return await self._manager(cast(FuncT, functools.partial(func, *args, **kwargs)))

        _wrapper._original = func  # type: ignore[attr-defined]
        _wrapper._manager = self._manager  # type: ignore[attr-defined]

        return cast(FuncT, _wrapper)
