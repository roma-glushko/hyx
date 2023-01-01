import random
from typing import Iterator, Optional, Union

from hyx.retry.typing import BackoffsT, BackoffT


class const(Iterator[float]):
    """
    Constant Delay Backoff
    """

    def __init__(self, delay: Union[int, float]) -> None:
        self._delay = delay

    def __iter__(self) -> "const":
        return self

    def __next__(self) -> float:
        return float(self._delay)


class expo(Iterator[float]):
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

    def __iter__(self) -> "expo":
        self._attempt = 0

        return self

    def __next__(self) -> float:
        delay = self._initial_delay * self._base**self._attempt

        if not self._max_delay or delay < self._max_delay:
            self._attempt += 1
            return delay

        # no needs to further increment attempt if we have reached delays > max_delay
        #  in any case we are going to return max_delay

        return self._max_delay


class decorrexp(Iterator[float]):
    """
    Decorrelated Exponential Backoff with Build-in Jitter

    References:
    - https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
    - https://github.com/Polly-Contrib/Polly.Contrib.WaitAndRetry/blob/master/src/Polly.Contrib.WaitAndRetry/Backoff.AwsDecorrelatedJitter.cs
    """  # noqa: E501

    def __init__(self, min_delay: float, max_delay: float, multiplier: float = 3) -> None:
        self._multiplier = multiplier
        self._min_delay = min_delay
        self._max_delay = max_delay

        self._current_delay: float = self._min_delay

    def __iter__(self) -> "decorrexp":
        self._current_delay = self._min_delay

        return self

    def __next__(self) -> float:
        upper_bound_delay = min(self._max_delay, self._current_delay * self._multiplier)

        self._current_delay = random.uniform(self._min_delay, upper_bound_delay)

        return self._current_delay


class softexp(Iterator[float]):
    """
    Soft Exponential Backoff with Build-in Jitter

    References:
    - https://github.com/App-vNext/Polly/issues/530
    - https://github.com/Polly-Contrib/Polly.Contrib.WaitAndRetry/blob/master/src/Polly.Contrib.WaitAndRetry/Backoff.DecorrelatedJitterV2.cs
    """  # noqa: E501

    def __init__(self, wait: Union[int, float]) -> None:
        ...

    def __iter__(self) -> "softexp":
        return self

    def __next__(self) -> float:
        ...


def create_backoff(backoff_config: BackoffsT) -> BackoffT:
    if isinstance(backoff_config, (int, float)):
        return const(wait=backoff_config)

    if isinstance(backoff_config, Iterator):
        return backoff_config

    raise ValueError(f"Unsupported backoff type: {backoff_config.__class__}")
