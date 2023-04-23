from unittest.mock import Mock

import pytest

from hyx.retry import retry
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
