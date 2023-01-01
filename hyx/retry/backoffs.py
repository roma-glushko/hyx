import itertools
import math
import random
from collections.abc import Sequence
from typing import Any, Iterator, Optional, Union

from hyx.retry.typing import BackoffsT, BackoffT, JittersT

SECS_TO_MS = 1000
MS_TO_SECS = 1 / SECS_TO_MS


class const(Iterator[float]):
    """
    Constant Delay(s) Backoff
    """

    def __init__(self, delay_secs: Union[float, Sequence[float]], *, jitter: JittersT = None) -> None:
        self._delay_secs = delay_secs
        self._jitter = jitter

        self._intervals: Optional[Iterator[float]] = None

        if self._is_sequence(self._delay_secs):
            self._intervals = itertools.cycle(self._delay_secs)

    def _is_sequence(self, delay: Any) -> bool:
        return isinstance(delay, Sequence)

    def __iter__(self) -> "const":
        self._intervals = itertools.cycle(self._delay_secs) if self._is_sequence(self._delay_secs) else None

        return self

    def __next__(self) -> float:
        delay_secs = self._delay_secs

        if self._is_sequence(delay_secs):
            delay_secs = next(self._intervals)

        delay_ms = delay_secs * SECS_TO_MS

        if self._jitter:
            delay_ms = self._jitter(delay_ms)

        return delay_ms * MS_TO_SECS


class linear(Iterator[float]):
    """
    Linear Backoff
    """

    def __init__(
        self,
        *,
        min_delay_secs: float = 1,
        additive_secs: float = 1.0,
        max_delay_secs: Optional[float] = None,
        jitter: JittersT = None,
    ) -> None:
        self._min_delay_ms = min_delay_secs * SECS_TO_MS
        self._additive_ms = additive_secs * SECS_TO_MS
        self._max_delay_ms = max_delay_secs * SECS_TO_MS if max_delay_secs else None
        self._jitter = jitter

        self._current_attempt = 0

    def __iter__(self) -> "linear":
        self._current_attempt = 0

        return self

    def __next__(self) -> float:
        delay_ms = self._min_delay_ms + self._current_attempt * self._additive_ms

        self._current_attempt += 1

        if self._jitter:
            delay_ms = self._jitter(delay_ms)

        if self._max_delay_ms and delay_ms > self._max_delay_ms:
            delay_ms = self._max_delay_ms

        return delay_ms * MS_TO_SECS


class expo(Iterator[float]):
    """
    Exponential Backoff (delay = factor * base ** attempt)
    """

    def __init__(
        self,
        *,
        min_delay_secs: float = 1,
        base: float = 2,
        max_delay_secs: Optional[float] = None,
        jitter: JittersT = None,
    ) -> None:
        self._min_delay_ms = min_delay_secs * SECS_TO_MS

        self._max_delay_ms = max_delay_secs * SECS_TO_MS if max_delay_secs else None

        self._base = base
        self._jitter = jitter

        self._attempt = 0

    def __iter__(self) -> "expo":
        self._attempt = 0

        return self

    def __next__(self) -> float:
        delay_ms = self._min_delay_ms * self._base**self._attempt

        if self._max_delay_ms and delay_ms > self._max_delay_ms:
            delay_ms = self._max_delay_ms
        else:
            # no needs to further increment attempt if we have reached delays > max_delay
            #  in any case we are going to return max_delay
            self._attempt += 1

        if self._jitter:
            delay_ms = self._jitter(delay_ms)

        return delay_ms * MS_TO_SECS


class fibo(Iterator[float]):
    """
    Fibonacci Backoff without Jitter
    """

    def __init__(
        self,
        *,
        min_delay_secs: float = 1,
        factor_secs: float = 1,
        max_delay_secs: Optional[float] = None,
        jitter: JittersT = None,
    ) -> None:
        self._min_delay_ms = min_delay_secs * SECS_TO_MS
        self._factor_ms = factor_secs * SECS_TO_MS
        self._max_delay_ms = max_delay_secs * SECS_TO_MS if max_delay_secs else None

        self._jitter = jitter

        self._current_delay_ms = self._min_delay_ms
        self._next_delay_ms = self._min_delay_ms + self._factor_ms

    def __iter__(self) -> "fibo":
        self._current_delay_ms = self._min_delay_ms
        self._next_delay_ms = self._min_delay_ms + self._factor_ms

        return self

    def __next__(self) -> float:
        delay_ms = self._current_delay_ms

        self._current_delay_ms, self._next_delay_ms = self._next_delay_ms, self._current_delay_ms + self._next_delay_ms

        if self._jitter:
            delay_ms = self._jitter(delay_ms)

        if self._max_delay_ms and delay_ms > self._max_delay_ms:
            delay_ms = self._max_delay_ms

        return delay_ms * MS_TO_SECS


class decorrexp(Iterator[float]):
    """
    Decorrelated Exponential Backoff with Build-in Jitter

    References:
    - https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
    - https://github.com/Polly-Contrib/Polly.Contrib.WaitAndRetry/blob/master/src/Polly.Contrib.WaitAndRetry/Backoff.AwsDecorrelatedJitter.cs
    """  # noqa: E501

    def __init__(self, min_delay_secs: float, max_delay_secs: float, multiplier: float = 3) -> None:
        self._min_delay_ms = min_delay_secs * SECS_TO_MS
        self._max_delay_ms = max_delay_secs * SECS_TO_MS if max_delay_secs else None
        self._multiplier = multiplier

        self._current_delay_ms: float = self._min_delay_ms

    def __iter__(self) -> "decorrexp":
        self._current_delay_ms = self._min_delay_ms

        return self

    def __next__(self) -> float:
        upper_bound_delay_ms = self._current_delay_ms * self._multiplier

        if self._max_delay_ms and upper_bound_delay_ms > self._max_delay_ms:
            upper_bound_delay_ms = self._max_delay_ms

        self._current_delay_ms = random.uniform(self._min_delay_ms, upper_bound_delay_ms)

        return self._current_delay_ms * MS_TO_SECS


class softexp(Iterator[float]):
    """
    Soft Exponential Backoff with Build-in Jitter

    References:
    - https://github.com/App-vNext/Polly/issues/530
    - https://github.com/Polly-Contrib/Polly.Contrib.WaitAndRetry/blob/master/src/Polly.Contrib.WaitAndRetry/Backoff.DecorrelatedJitterV2.cs
    """  # noqa: E501

    def __init__(
        self,
        *,
        median_delay_secs: Union[int, float],
        max_delay_secs: Union[None, int, float] = None,
        pfactor: float = 4.0,
        rp_scaling_factor: float = 1 / 1.4,
    ) -> None:
        self._median_delay_ms = median_delay_secs * SECS_TO_MS
        self._max_delay_ms = max_delay_secs * SECS_TO_MS if max_delay_secs else None

        self._pfactor = pfactor
        self._rp_scaling_factor = rp_scaling_factor

        self._current_attempt = 0
        self._current_factor = 0.0

    def __iter__(self) -> "softexp":
        self._current_attempt = 0
        self._current_factor = 0.0

        return self

    def __next__(self) -> float:
        t = self._current_attempt + random.random()
        next_factor = 2**t * math.tanh(math.sqrt(self._pfactor * t))
        delta = next_factor - self._current_factor

        self._current_factor = next_factor
        self._current_attempt += 1

        delay_ms = delta * self._rp_scaling_factor * self._median_delay_ms

        if self._max_delay_ms and delay_ms > self._max_delay_ms:
            delay_ms = self._max_delay_ms

        return delay_ms * MS_TO_SECS


def create_backoff(backoff_config: BackoffsT) -> BackoffT:
    if isinstance(backoff_config, (int, float)):
        return const(delay_secs=backoff_config)

    if isinstance(backoff_config, Iterator):
        return backoff_config

    raise ValueError(f"Unsupported backoff type: {backoff_config.__class__}")
