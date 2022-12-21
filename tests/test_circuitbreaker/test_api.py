import asyncio
import contextlib
from typing import cast

import pytest

from hyx.circuitbreaker import consecutive_breaker
from hyx.circuitbreaker.exceptions import BreakerFailing
from hyx.circuitbreaker.states import WorkingState, FailingState, RecoveringState


async def test__circuitbreaker__decorator_context_success() -> None:
    @consecutive_breaker(exceptions=(RuntimeError, ValueError), failure_threshold=2, recovery_delay_secs=0.1)
    async def faulty() -> float:
        return 42

    assert await faulty() == 42

    async with consecutive_breaker(failure_threshold=2, recovery_delay_secs=0.1):
        assert True


async def test__circuitbreaker__decorator__pass_known_exceptions() -> None:
    breaker = consecutive_breaker(exceptions=RuntimeError, failure_threshold=2, recovery_delay_secs=0.1)

    @breaker
    async def faulty() -> None:
        raise RuntimeError("cannot calculate value")

    with pytest.raises(RuntimeError):
        await faulty()

    assert cast(WorkingState, breaker.state).consecutive_exceptions == 1


async def test__circuitbreaker__decorator__pass_unknown_exceptions() -> None:
    breaker = consecutive_breaker(exceptions=(RuntimeError,), failure_threshold=2, recovery_delay_secs=0.1)

    @breaker
    async def faulty() -> None:
        raise ValueError("base is not a correct int")

    with pytest.raises(ValueError):
        await faulty()

    assert cast(WorkingState, breaker.state).consecutive_exceptions == 0


async def test__circuitbreaker__consecutive__state_transitions() -> None:
    fail_until: int = 2
    fails: int = 0

    breaker = consecutive_breaker(
        exceptions=(RuntimeError,),
        failure_threshold=2,
        recovery_delay_secs=1,
        recovery_threshold=2,
    )

    @breaker
    async def faulty() -> float:
        nonlocal fails, fail_until
        if fails < fail_until:
            fails += 1
            raise RuntimeError("error on calculation")

        return 42

    # cause the first failure
    with pytest.raises(RuntimeError):
        await faulty()

    assert isinstance(breaker.state, WorkingState)

    # cause the second failure, switch the breaker to failing state
    with pytest.raises(RuntimeError):
        await faulty()

    assert isinstance(breaker.state, FailingState)

    # make sure breaker is failing
    with pytest.raises(BreakerFailing):
        await faulty()

    # wait for the recovery delay
    await asyncio.sleep(1)

    # check recovering
    assert await faulty() == 42
    assert isinstance(breaker.state, RecoveringState)

    # check moving back to working state
    assert await faulty() == 42
    assert isinstance(breaker.state, WorkingState)

