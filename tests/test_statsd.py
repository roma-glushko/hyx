import pytest

from hyx.events import EventManager


class MockStatsClient:
    """A mock StatsD client that records all metric calls."""

    def __init__(self, prefix: str = "hyx") -> None:
        self._prefix = prefix
        self.metrics: list[dict] = []

    def incr(self, stat: str, count: int = 1, rate: float = 1) -> None:
        self.metrics.append(
            {
                "type": "incr",
                "stat": f"{self._prefix}.{stat}" if self._prefix else stat,
                "count": count,
            }
        )

    def get_metrics_containing(self, substring: str) -> list[dict]:
        """Get all metrics containing a substring."""
        return [m for m in self.metrics if substring in m["stat"]]


@pytest.fixture
def statsd_client():
    """Create a mock StatsD client for testing."""
    return MockStatsClient()


async def test__statsd_retry_listener__on_retry(statsd_client):
    from hyx.retry import retry
    from hyx.telemetry.statsd import RetryListener

    event_manager = EventManager()
    listener = RetryListener(client=statsd_client)

    call_count = 0

    @retry(attempts=3, backoff=0, listeners=[listener], event_manager=event_manager)
    async def flaky_func():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("not yet")
        return "success"

    result = await flaky_func()
    await event_manager.wait_for_tasks()

    assert result == "success"

    # Check retry attempts metrics
    attempts = statsd_client.get_metrics_containing("retry.")
    assert any("attempts" in m["stat"] for m in attempts)
    assert any("ValueError" in m["stat"] for m in attempts)

    # Check success metric
    success = statsd_client.get_metrics_containing("success")
    assert len(success) == 1


async def test__statsd_retry_listener__attempts_exceeded(statsd_client):
    from hyx.retry import retry
    from hyx.retry.exceptions import AttemptsExceeded
    from hyx.telemetry.statsd import RetryListener

    event_manager = EventManager()
    listener = RetryListener(client=statsd_client)

    @retry(attempts=2, backoff=0, listeners=[listener], event_manager=event_manager)
    async def always_fails():
        raise RuntimeError("always fails")

    with pytest.raises(AttemptsExceeded):
        await always_fails()

    await event_manager.wait_for_tasks()

    # Check exhausted metric
    exhausted = statsd_client.get_metrics_containing("exhausted")
    assert len(exhausted) == 1


async def test__statsd_breaker_listener__state_transitions(statsd_client):
    from hyx.circuitbreaker import consecutive_breaker
    from hyx.telemetry.statsd import CircuitBreakerListener

    event_manager = EventManager()
    listener = CircuitBreakerListener(client=statsd_client)

    breaker = consecutive_breaker(
        failure_threshold=2,
        recovery_time_secs=0.1,
        recovery_threshold=1,
        listeners=[listener],
        event_manager=event_manager,
    )

    # Trigger failures to open the breaker
    for _ in range(2):
        try:
            async with breaker:
                raise RuntimeError("fail")
        except RuntimeError:
            pass

    await event_manager.wait_for_tasks()

    # Check state transition metric
    failing = statsd_client.get_metrics_containing("circuitbreaker")
    assert any("state.failing" in m["stat"] for m in failing)


async def test__statsd_timeout_listener__on_timeout(statsd_client):
    import asyncio

    from hyx.telemetry.statsd import TimeoutListener
    from hyx.timeout import timeout
    from hyx.timeout.exceptions import MaxDurationExceeded

    event_manager = EventManager()
    listener = TimeoutListener(client=statsd_client)

    @timeout(timeout_secs=0.01, listeners=[listener], event_manager=event_manager)
    async def slow_func():
        await asyncio.sleep(1)

    with pytest.raises(MaxDurationExceeded):
        await slow_func()

    await event_manager.wait_for_tasks()

    # Check timeout metric
    exceeded = statsd_client.get_metrics_containing("timeout")
    assert any("exceeded" in m["stat"] for m in exceeded)


async def test__statsd_bulkhead_listener__on_bulkhead_full(statsd_client):
    import asyncio

    from hyx.bulkhead import bulkhead
    from hyx.bulkhead.exceptions import BulkheadFull
    from hyx.telemetry.statsd import BulkheadListener

    event_manager = EventManager()
    listener = BulkheadListener(client=statsd_client)

    bh = bulkhead(
        max_concurrency=1,
        max_capacity=1,
        listeners=[listener],
        event_manager=event_manager,
    )

    async def slow_task():
        async with bh:
            await asyncio.sleep(0.1)

    # Start one task that holds the bulkhead
    task = asyncio.create_task(slow_task())
    await asyncio.sleep(0.01)  # Let it acquire

    # Try to acquire again - should be rejected
    with pytest.raises(BulkheadFull):
        async with bh:
            pass

    await task
    await event_manager.wait_for_tasks()

    # Check rejected metric
    rejected = statsd_client.get_metrics_containing("bulkhead")
    assert any("rejected" in m["stat"] for m in rejected)


async def test__statsd_fallback_listener__on_fallback(statsd_client):
    from hyx.fallback import fallback
    from hyx.telemetry.statsd import FallbackListener

    event_manager = EventManager()
    listener = FallbackListener(client=statsd_client)

    async def fallback_handler(result, *args, **kwargs):
        return "fallback_value"

    @fallback(handler=fallback_handler, on=ValueError, listeners=[listener], event_manager=event_manager)
    async def failing_func():
        raise ValueError("error")

    result = await failing_func()
    await event_manager.wait_for_tasks()

    assert result == "fallback_value"

    # Check fallback metrics
    triggered = statsd_client.get_metrics_containing("fallback")
    assert any("triggered" in m["stat"] for m in triggered)
    assert any("exception" in m["stat"] for m in triggered)
