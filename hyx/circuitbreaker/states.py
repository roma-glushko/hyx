from datetime import datetime, timedelta
from typing import Optional, Self

from hyx.circuitbreaker.config import BreakerConfig


class BreakerState:
    NAME: str = "base"

    def __init__(self, config: BreakerConfig) -> None:
        self._config = config

    @property
    def name(self) -> str:
        return self.NAME

    async def before_execution(self) -> Self:
        return self

    async def on_success(self) -> Self:
        return self

    async def on_exception(self, exception: BaseException) -> Self:
        return self


class WorkingState(BreakerState):
    """
    The breaker executes given code.

    Also known as the "closed" state
    """
    NAME = "working"

    def __init__(self, config: BreakerConfig) -> None:
        super().__init__(config)

        self._consecutive_exceptions: int = 0

    @property
    def consecutive_exceptions(self) -> int:
        return self._consecutive_exceptions

    def _reset_exceptions_count(self) -> None:
        self._consecutive_exceptions = 0

    async def on_success(self) -> Self:
        """
        Reset the failure counter
        """
        self._reset_exceptions_count()

        return self

    async def on_exception(self, exception: BaseException) -> "BreakerState":
        """
        Transit the breaker to the failing state if number of consecutive errors is beyond the threshold
        """
        self._consecutive_exceptions += 1

        if self._consecutive_exceptions >= self._config.failure_threshold:
            return FailingState(self._config)

        return self


class FailingState(BreakerState):
    """
    Execution of the code is blocked.
    The breaker has detected that given code is failing, so it stops executing the code temporarily

    Also known as the "open" state
    """

    NAME = "failing"

    def __init__(self, config: BreakerConfig) -> None:
        super().__init__(config)

        self._failing_since = self._get_failing_since()
        self._failing_until = self._get_failing_until(self._failing_since)

    @staticmethod
    def _get_failing_since() -> datetime:
        return datetime.utcnow()

    def _get_failing_until(self, since: datetime) -> datetime:
        return since + timedelta(self._config.recovery_delay_secs)

    @property
    def until(self) -> datetime:
        """
        The breaker is going to fail until
        """
        return self._failing_until

    @property
    def remain(self) -> Optional[timedelta]:
        """
        Remaining time the breaker is going to fail
        """
        now = datetime.utcnow()

        if now >= self.until:
            return None

        return self.until - now

    @property
    def since(self) -> datetime:
        """
        The breaker is failing since
        """
        return self._failing_since

    async def before_execution(self) -> Self:
        if self.remain:
            raise RuntimeError

        return RecoveringState(self._config)


class RecoveringState(BreakerState):
    """
    Recovering is an intermediate trial state where we allow to call the code after the specified delay.
    If the code execution has been successful for a given number of time, we transmit to the working state.
    Otherwise, the delay was not enough, and we need to give another round of waiting.

    Also known as the "half-open" state.
    """
    NAME = "recovering"

    def __init__(self, config: BreakerConfig) -> None:
        super().__init__(config)

        self._consecutive_successes: int = 0

    @property
    def consecutive_successes(self) -> int:
        return self._consecutive_successes

    async def on_success(self) -> Self:
        self._consecutive_successes += 1

        if self.consecutive_successes >= self._config.recovery_threshold:
            return WorkingState(self._config)

        return self

    async def on_exception(self, exception: BaseException) -> Self:
        return FailingState(self._config)
