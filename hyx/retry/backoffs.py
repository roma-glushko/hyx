from collections.abc import AsyncIterator
from typing import AsyncGenerator, Optional, Union

from hyx.retry.typing import BackoffsT, BackoffT


class const(AsyncIterator[float]):
    """
    Constant Delay Backoff
    """

    def __init__(self, wait: Union[int, float]) -> None:
        self._wait = wait

    def __aiter__(self) -> "const":
        return self

    async def __anext__(self) -> float:
        return float(self._wait)


class expo(AsyncIterator[float]):
    """
    Exponential Backoff (delay = factor * base ** attempt)
    """

    def __init__(
        self,
        initial_delay: float = 1,
        base: float = 2,
        max_delay: Optional[float] = None,
    ) -> None:
        self._initial_delay = initial_delay
        self._base = base
        self._max_delay = max_delay

        self._attempt = 0

    def __aiter__(self) -> "expo":
        self._attempt = 0
        return self

    async def __anext__(self) -> float:
        delay = self._initial_delay * self._base ** self._attempt

        if not self._max_delay or delay < self._max_delay:
            self._attempt += 1
            return delay

        # no needs to further increment attempt if we have reached delays > max_delay
        #  in any case we are going to return max_delay

        return self._max_delay


def create_backoff(backoff_config: BackoffsT) -> BackoffT:
    if isinstance(backoff_config, (int, float)):
        return const(wait=backoff_config)

    if isinstance(backoff_config, AsyncGenerator):
        return backoff_config

    raise ValueError(f"Unsupported backoff type: {backoff_config.__class__}")
