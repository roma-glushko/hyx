import asyncio
from typing import List, cast
from unittest.mock import Mock

import pytest

from hyx.circuitbreaker import BreakerListener, consecutive_breaker
from hyx.circuitbreaker.context import BreakerContext
from hyx.circuitbreaker.exceptions import BreakerFailing
from hyx.circuitbreaker.states import BreakerState, FailingState, RecoveringState, WorkingState
from hyx.events import EventManager


class Listener(BreakerListener):
    def __init__(self) -> None:
        self.state_history: List[str] = []
        self.succeed = Mock()

    async def on_working(
        self,
        context: BreakerContext,
        current_state: BreakerState,
        next_state: WorkingState,
    ) -> None:
        self.state_history.append(next_state.NAME)

    async def on_recovering(
        self,
        context: BreakerContext,
        current_state: BreakerState,
        next_state: RecoveringState,
    ) -> None:
        self.state_history.append(next_state.NAME)

    async def on_failing(
        self,
        context: BreakerContext,
        current_state: BreakerState,
        next_state: FailingState,
    ) -> None:
        self.state_history.append(next_state.NAME)

    async def on_success(
        self,
        context: BreakerContext,
        state: "BreakerState"
    ) -> None:
        self.state_history.append(state.NAME)
        self.succeed()


async def test__circuitbreaker__decorator_context_success() -> None:
    event_manager = EventManager()
    listener = Listener()

    @consecutive_breaker(
        exceptions=(RuntimeError, ValueError),
        failure_threshold=2,
        recovery_time_secs=0.1,
        listeners=(listener,),
        event_manager=event_manager,
    )
    async def faulty() -> float:
        return 42

    assert await faulty() == 42

    async with consecutive_breaker(failure_threshold=2, recovery_time_secs=0.1):
        assert True

    await event_manager.wait_for_tasks()

    listener.succeed.assert_called()



async def test__circuitbreaker__decorator__pass_known_exceptions() -> None:
    breaker = consecutive_breaker(exceptions=RuntimeError, failure_threshold=2, recovery_time_secs=0.1)

    @breaker
    async def faulty() -> None:
        raise RuntimeError("cannot calculate value")

    with pytest.raises(RuntimeError):
        await faulty()

    assert cast(WorkingState, breaker.state).consecutive_exceptions == 1


async def test__circuitbreaker__decorator__pass_unknown_exceptions() -> None:
    breaker = consecutive_breaker(exceptions=(RuntimeError,), failure_threshold=2, recovery_time_secs=0.1)

    @breaker
    async def faulty() -> None:
        raise ValueError("base is not a correct int")

    with pytest.raises(ValueError):
        await faulty()

    assert cast(WorkingState, breaker.state).consecutive_exceptions == 0


async def test__circuitbreaker__consecutive__state_transitions_with_success_in_the_end() -> None:
    event_manager = EventManager()
    listener = Listener()

    fail_until: int = 2
    fails: int = 0

    breaker = consecutive_breaker(
        exceptions=(RuntimeError,),
        failure_threshold=2,
        recovery_time_secs=1,
        recovery_threshold=2,
        listeners=(listener,),
        event_manager=event_manager,
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

    await event_manager.wait_for_tasks()

    listener.succeed.assert_called()
    assert listener.state_history == ['failing', 'recovering', 'recovering', 'recovering', 'working']



async def test__circuitbreaker__consecutive__state_transitions_with_failure_in_the_end() -> None:
    breaker = consecutive_breaker(
        exceptions=(RuntimeError,),
        failure_threshold=1,
        recovery_time_secs=0.5,
        recovery_threshold=2,
    )

    @breaker
    async def faulty() -> float:
        raise RuntimeError("error on calculation")

    # cause the first failure
    with pytest.raises(RuntimeError):
        await faulty()

    assert isinstance(breaker.state, FailingState)

    # wait for the recovery delay
    await asyncio.sleep(0.5)

    # cause the second failure and switch to the failure mode again
    with pytest.raises(RuntimeError):
        await faulty()

    assert isinstance(breaker.state, FailingState)
