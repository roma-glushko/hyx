from unittest.mock import Mock

import pytest
from hyx.ratelimit.exceptions import RateLimitExceeded

from hyx.retry import retry
from hyx.retry.api import bucket_retry
from hyx.retry.counters import Counter
from hyx.retry.exceptions import AttemptsExceeded
from hyx.retry.listeners import RetryListener
from hyx.retry.manager import RetryManager
from tests.conftest import event_manager

class Listener(RetryListener):
    def __init__(self) -> None:
        self.retries = 0
        self.attempts_exceeded = Mock()

    async def on_retry(self, retry: "RetryManager", exception: Exception, counter: "Counter") -> None:
        self.retries += 1

    async def on_attempts_exceeded(self, retry: "RetryManager") -> None:
        self.attempts_exceeded()


async def test__retry__decorate_async_func() -> None:
    @retry()
    async def simple_func() -> int:
        return 2022

    await simple_func()


async def test__retry__max_retry_exceeded() -> None:
    listener = Listener()

    @retry(listeners=(listener,))
    async def faulty_func() -> float:
        return 1 / 0

    with pytest.raises(AttemptsExceeded):
        await faulty_func()

    await event_manager.wait_for_tasks()

    listener.attempts_exceeded.assert_called()


async def test__retry__pass_different_error() -> None:
    @retry(on=ValueError)
    async def faulty_func() -> float:
        return 1 / 0

    @retry(on=(ValueError, ZeroDivisionError))
    async def runtime_func() -> float:
        raise RuntimeError("unhandled error")

    with pytest.raises(ZeroDivisionError):
        await faulty_func()

    with pytest.raises(RuntimeError):
        await runtime_func()


async def test__retry__infinite_retries() -> None:
    execs = 0
    listener = Listener()

    @retry(on=RuntimeError, attempts=None, listeners=(listener,))
    async def flaky_error() -> int:
        nonlocal execs

        if execs < 3:
            execs += 1
            raise RuntimeError

        return 42

    await event_manager.wait_for_tasks()

    assert await flaky_error() == 42
    assert listener.retries == execs

async def test__retry__global_retry_limit() -> None:
    listener = Listener()
    attempts=4
    per_time_secs = 1
    bucket_size = 4

    @bucket_retry(on=RuntimeError, attempts=attempts, per_time_secs=per_time_secs, bucket_size=bucket_size, listeners=(listener,))
    async def faulty_func() -> int:
        raise RuntimeError

    with pytest.raises(AttemptsExceeded):
        for _ in range(5):
            assert await faulty_func()

    await event_manager.wait_for_tasks()

    assert listener.retries == attempts

async def test__retry__token_bucket_limiter():
    listener = Listener()
    attempts = 5
    per_time_secs = 2
    bucket_size = 3
    
    calls = 0
    exceptions = 0

    @bucket_retry(on=RuntimeError,attempts=attempts, per_time_secs=per_time_secs, bucket_size=bucket_size, listeners=(listener,))
    async def faulty_func():
        nonlocal calls, exceptions
        calls += 1
        if calls <= attempts:
            exceptions += 1
            raise RuntimeError
        return True

    result = await faulty_func()
    assert result is True

    assert exceptions <= attempts
