from hyx.retry.exceptions import MaxAttemptsExceeded
from hyx.retry.typing import AttemptsT


class Counter:
    """
    Base class for all retry counters
    """

    def __init__(self) -> None:
        self._current_attempt: int = 0

    @property
    def current_attempt(self) -> int:
        return self._current_attempt

    def __bool__(self) -> bool:
        raise NotImplementedError

    def __iadd__(self, attempts: int) -> "Counter":
        self._current_attempt += attempts

        return self


class UntilSuccessCounter(Counter):
    def __bool__(self) -> bool:
        """
        We are waiting until the successful function call
        """
        return True


class AttemptCounter(Counter):
    """
    Bound the max possible attempts
    """

    def __init__(self, max_attempts: int) -> None:
        super().__init__()

        self._max_attempts = max_attempts

    def __bool__(self) -> bool:
        return self._current_attempt <= self._max_attempts

    def __iadd__(self, attempts: int) -> "AttemptCounter":
        super().__iadd__(attempts)

        if not self:
            raise MaxAttemptsExceeded()

        return self


def create_counter(max_attempts: AttemptsT) -> Counter:
    if max_attempts is None:
        return UntilSuccessCounter()

    return AttemptCounter(max_attempts=max_attempts)
