from typing import Any, Optional

from hyx.circuitbreaker import BreakerListener
from hyx.circuitbreaker.config import BreakerConfig
from hyx.circuitbreaker.states import BreakerState, WorkingState
from hyx.circuitbreaker.typing import DelayT
from hyx.common.typing import ExceptionsT, FuncT


class ConsecutiveCircuitBreaker:
    """
    Watch for consecutive exceptions that exceed a given threshold
    """

    __slots__ = ("_config", "_name", "_state", "_event_dispatcher")

    def __init__(
        self,
        exceptions: ExceptionsT,
        failure_threshold: int,
        recovery_time_secs: DelayT,
        recovery_threshold: int,
        event_dispatcher: BreakerListener,
        name: Optional[str] = None,
    ) -> None:
        self._name = name

        self._config = BreakerConfig(
            exceptions=exceptions,
            failure_threshold=failure_threshold,
            recovery_time_secs=recovery_time_secs,
            recovery_threshold=recovery_threshold,
        )

        self._state: BreakerState = WorkingState(self._config)
        self._event_dispatcher = event_dispatcher

    @property
    def state(self) -> BreakerState:
        return self._state

    async def _transit_state(self, new_state: BreakerState) -> None:
        self._state = new_state

    async def acquire(self) -> None:
        await self._transit_state(await self._state.before_execution())

    async def release(self, exception: Optional[BaseException]) -> None:
        if exception and isinstance(exception, self._config.exceptions):
            await self._transit_state(await self._state.on_exception())
            raise exception

        await self._transit_state(await self._state.on_success())

    async def __call__(self, func: FuncT) -> Any:
        await self._transit_state(await self._state.before_execution())

        try:
            result = await func()

            await self._transit_state(await self._state.on_success())

            return result
        except self._config.exceptions as e:
            await self._transit_state(await self._state.on_exception())
            # breaker is not hiding the error like retry or fallback
            raise e
