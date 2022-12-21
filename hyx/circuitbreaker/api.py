import functools
from types import TracebackType
from typing import Any, Optional, Type, cast

from hyx.circuitbreaker.managers import ConsecutiveCircuitBreaker
from hyx.circuitbreaker.states import BreakerState
from hyx.circuitbreaker.typing import DelayT
from hyx.common.typing import ExceptionsT, FuncT


class consecutive_breaker:
    """
    Circuit Breaker that watches for consecutive errors
    """
    def __init__(
        self,
        exceptions: ExceptionsT = Exception,
        failure_threshold: int = 5,
        recovery_delay_secs: DelayT = 30,
        recovery_threshold: int = 1,
    ) -> None:
        self._exceptions = exceptions
        self._failure_threshold = failure_threshold
        self._recovery_delay_secs = recovery_delay_secs

        self._manager = ConsecutiveCircuitBreaker(
            exceptions=exceptions,
            failure_threshold=failure_threshold,
            recovery_delay_secs=recovery_delay_secs,
            recovery_threshold=recovery_threshold,
        )

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
            return await self._manager(functools.partial(func, *args, **kwargs))

        _wrapper.__original__ = func
        _wrapper.__manager__ = self._manager

        return cast(FuncT, _wrapper)
