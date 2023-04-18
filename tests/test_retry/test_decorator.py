import pytest

from hyx.retry import retry
from hyx.retry.exceptions import AttemptsExceeded


async def test__retry__decorate_async_func() -> None:
    @retry()
    async def simple_func() -> int:
        return 2022

    await simple_func()


async def test__retry__max_retry_exceeded() -> None:
    @retry()
    async def faulty_func() -> float:
        return 1 / 0

    with pytest.raises(AttemptsExceeded):
        await faulty_func()


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

    @retry(on=RuntimeError, attempts=None)
    async def flaky_error() -> int:
        nonlocal execs

        if execs < 3:
            execs += 1
            raise RuntimeError

        return 42

    assert await flaky_error() == 42
