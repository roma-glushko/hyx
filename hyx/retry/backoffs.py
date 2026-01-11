import itertools
import math
import random
from collections.abc import Iterator, Sequence

from hyx.retry.typing import BackoffsT, BackoffT, JittersT

SECS_TO_MS = 1000
MS_TO_SECS = 1 / SECS_TO_MS


class const(Iterator[float]):
    """
    Constant Delay(s) Backoff

    **Parameters:**

    * **delay_secs** *(float, int)* - How much time do we wait on each retry.
    * **jitter** *(optional)* - Decorrelate delays with the jitter. No jitter by default
    """

    def __init__(self, delay_secs: int | float, *, jitter: JittersT = None) -> None:
        self._delay_secs = delay_secs
        self._jitter = jitter

    def __next__(self) -> float:
        delay_ms = self._delay_secs * SECS_TO_MS

        if self._jitter:
            delay_ms = self._jitter(delay_ms)

        return delay_ms * MS_TO_SECS


class interval(Iterator[float]):
    """
    Interval Delay(s) Backoff

    **Parameters:**

    * **delay_secs** *(Sequence[float])* - How much time do we wait on each retry.
        It will take next delay from that list on each retry.
        It will repeat from the beginning if the list is shorter than number of attempts
    * **jitter** *(optional)* - Decorrelate delays with the jitter. No jitter by default
    """

    def __init__(self, delay_secs: Sequence[float], *, jitter: JittersT = None) -> None:
        self._delay_secs = delay_secs
        self._jitter = jitter

        self._intervals: Iterator[float] = itertools.cycle(self._delay_secs)

    def __iter__(self) -> "interval":
        self._intervals = itertools.cycle(self._delay_secs)

        return self

    def __next__(self) -> float:
        delay_ms = next(self._intervals) * SECS_TO_MS

        if self._jitter:
            delay_ms = self._jitter(delay_ms)

        return delay_ms * MS_TO_SECS


class linear(Iterator[float]):
    """
    Linear Backoff

    **Parameters:**

    * **min_delay_secs** - The minimal initial delay
    * **additive_secs** - How many seconds to add on each retry
    * **max_delay_secs** *(optional)* - Limit the longest possible delay
    * **jitter** *(optional)* - Decorrelate delays with the jitter. No jitter by default

    """

    def __init__(
        self,
        *,
        min_delay_secs: float = 1,
        additive_secs: float = 1.0,
        max_delay_secs: float | None = None,
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
    Exponential Backoff (delay = min_delay_secs * base ** attempt)

    **Parameters:**

    * **min_delay_secs** - The minimal initial delay
    * **base** - The base of the exponential function
    * **max_delay_secs** *(optional)* - Limit the longest possible delay
    * **jitter** *(optional)* - Decorrelate delays with the jitter. No jitter by default

    """

    def __init__(
        self,
        *,
        min_delay_secs: float = 1,
        base: float = 2,
        max_delay_secs: float | None = None,
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
    Fibonacci Backoff

    **Parameters:**

    * **min_delay_secs** - The minimal initial delay
    * **factor_secs** - Defines the second element in the initial Fibonacci sequence
    * **max_delay_secs** *(optional)* - Limit the longest possible delay
    * **jitter** *(optional)* - Decorrelate delays with the jitter. No jitter by default

    """

    def __init__(
        self,
        *,
        min_delay_secs: float = 1,
        factor_secs: float = 1,
        max_delay_secs: float | None = None,
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

    **Parameters:**

    * **min_delay_secs** - The minimal initial delay
    * **base** - The base of the exponential function
    * **max_delay_secs** *(optional)* - Limit the longest possible delay

    """

    def __init__(self, min_delay_secs: float, max_delay_secs: float, base: float = 3) -> None:
        self._min_delay_ms = min_delay_secs * SECS_TO_MS
        self._max_delay_ms = max_delay_secs * SECS_TO_MS if max_delay_secs else None
        self._base = base

        self._current_delay_ms: float = self._min_delay_ms

    def __iter__(self) -> "decorrexp":
        self._current_delay_ms = self._min_delay_ms

        return self

    def __next__(self) -> float:
        """
        References:
        - https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
        - https://github.com/Polly-Contrib/Polly.Contrib.WaitAndRetry/blob/master/src/Polly.Contrib.WaitAndRetry/Backoff.AwsDecorrelatedJitter.cs
        """  # noqa: E501

        upper_bound_delay_ms = self._current_delay_ms * self._base

        if self._max_delay_ms and upper_bound_delay_ms > self._max_delay_ms:
            upper_bound_delay_ms = self._max_delay_ms

        self._current_delay_ms = random.uniform(self._min_delay_ms, upper_bound_delay_ms)

        return self._current_delay_ms * MS_TO_SECS


class softexp(Iterator[float]):
    """
    Soft Exponential Backoff with Build-in Jitter

    **Parameters:**

    * **median_delay_secs** - The minimal initial delay
    * **max_delay_secs** *(optional)* - Limit the longest possible delay
    * **pfactor** -
    * **rp_scaling_factor** -

    """

    def __init__(
        self,
        *,
        median_delay_secs: int | float,
        max_delay_secs: None | int | float = None,
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
        """
        References:
        - https://github.com/App-vNext/Polly/issues/530
        - https://github.com/Polly-Contrib/Polly.Contrib.WaitAndRetry/blob/master/src/Polly.Contrib.WaitAndRetry/Backoff.DecorrelatedJitterV2.cs
        """  # noqa: E501

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

    if isinstance(backoff_config, (list, tuple)):
        return interval(delay_secs=backoff_config)

    if isinstance(backoff_config, Iterator):
        return backoff_config

    raise ValueError(f"Unsupported backoff type: {backoff_config.__class__}")
