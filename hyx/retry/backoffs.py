import random
from typing import Iterator, Optional, Union

from hyx.retry.typing import BackoffsT, BackoffT, JittersT


class const(Iterator[float]):
    """
    Constant Delay Backoff
    """

    def __init__(self, delay: Union[int, float], *, jitter: JittersT = None) -> None:
        self._delay = delay
        self._jitter = jitter

    def __iter__(self) -> "const":
        return self

    def __next__(self) -> float:
        delay = float(self._delay)

        if self._jitter:
            return self._jitter(delay)

        return delay


class expo(Iterator[float]):
    """
    Exponential Backoff (delay = factor * base ** attempt)
    """

    def __init__(
        self,
        *,
        min_delay: float = 1,
        base: float = 2,
        max_delay: Optional[float] = None,
        jitter: JittersT = None,
    ) -> None:
        self._min_delay = min_delay
        self._base = base
        self._max_delay = max_delay
        self._jitter = jitter

        self._attempt = 0

    def __iter__(self) -> "expo":
        self._attempt = 0

        return self

    def __next__(self) -> float:
        delay = self._min_delay * self._base**self._attempt

        if self._max_delay and delay > self._max_delay:
            delay = self._max_delay
        else:
            # no needs to further increment attempt if we have reached delays > max_delay
            #  in any case we are going to return max_delay
            self._attempt += 1

        if self._jitter:
            return self._jitter(delay)

        return delay


class linear(Iterator[float]):
    """
    Linear Backoff
    """

    def __init__(
        self,
        *,
        min_delay: float = 1,
        additive: float = 1.0,
        max_delay: Optional[float] = None,
        jitter: JittersT = None,
    ) -> None:
        self._min_delay = min_delay
        self._max_delay = max_delay
        self._additive = additive
        self._jitter = jitter

        self._current_attempt = 0

    def __iter__(self) -> "linear":
        self._current_attempt = 0

        return self

    def __next__(self) -> float:
        delay = self._min_delay + self._current_attempt * self._additive

        self._current_attempt += 1

        if self._jitter:
            return self._jitter(delay)

        return delay


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

    def __init__(self, delay: Union[int, float]) -> None:
        ...

    def __iter__(self) -> "softexp":
        return self

    def __next__(self) -> float:
        ...


def create_backoff(backoff_config: BackoffsT) -> BackoffT:
    if isinstance(backoff_config, (int, float)):
        return const(delay=backoff_config)

    if isinstance(backoff_config, Iterator):
        return backoff_config

    raise ValueError(f"Unsupported backoff type: {backoff_config.__class__}")
