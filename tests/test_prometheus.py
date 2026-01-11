import pytest
from prometheus_client import CollectorRegistry

from hyx.events import EventManager


@pytest.fixture
def registry():
    """Create a fresh CollectorRegistry for testing."""
    return CollectorRegistry()


def get_metric_value(registry: CollectorRegistry, metric_name: str, labels: dict | None = None) -> float:
    """Extract a metric value from the registry."""
    for metric in registry.collect():
        if metric.name == metric_name:
            for sample in metric.samples:
                if sample.name == f"{metric_name}_total":
                    if labels is None:
                        return sample.value
                    if all(sample.labels.get(k) == v for k, v in labels.items()):
                        return sample.value
    return 0.0


async def test__prometheus_retry_listener__on_retry(registry):
    from hyx.telemetry.prometheus import RetryListener
    from hyx.retry import retry

    event_manager = EventManager()
    listener = RetryListener(registry=registry)

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

    # Check retry attempts metric
    retry_attempts = get_metric_value(registry, "hyx_retry_attempts", {"exception": "ValueError"})
    assert retry_attempts == 2

    # Check success metric
    success = get_metric_value(registry, "hyx_retry_success")
    assert success == 1


async def test__prometheus_retry_listener__attempts_exceeded(registry):
    from hyx.telemetry.prometheus import RetryListener
    from hyx.retry import retry
    from hyx.retry.exceptions import AttemptsExceeded

    event_manager = EventManager()
    listener = RetryListener(registry=registry)

    @retry(attempts=2, backoff=0, listeners=[listener], event_manager=event_manager)
    async def always_fails():
        raise RuntimeError("always fails")

    with pytest.raises(AttemptsExceeded):
        await always_fails()

    await event_manager.wait_for_tasks()

    # Check exhausted metric
    exhausted = get_metric_value(registry, "hyx_retry_exhausted")
    assert exhausted == 1


async def test__prometheus_breaker_listener__state_transitions(registry):
    from hyx.telemetry.prometheus import CircuitBreakerListener
    from hyx.circuitbreaker import consecutive_breaker

    event_manager = EventManager()
    listener = CircuitBreakerListener(registry=registry)

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
    state_transition = get_metric_value(
        registry,
        "hyx_circuitbreaker_state_transitions",
        {"from_state": "working", "to_state": "failing"},
    )
    assert state_transition == 1


async def test__prometheus_timeout_listener__on_timeout(registry):
    import asyncio

    from hyx.telemetry.prometheus import TimeoutListener
    from hyx.timeout import timeout
    from hyx.timeout.exceptions import MaxDurationExceeded

    event_manager = EventManager()
    listener = TimeoutListener(registry=registry)

    @timeout(timeout_secs=0.01, listeners=[listener], event_manager=event_manager)
    async def slow_func():
        await asyncio.sleep(1)

    with pytest.raises(MaxDurationExceeded):
        await slow_func()

    await event_manager.wait_for_tasks()

    # Check timeout metric
    exceeded = get_metric_value(registry, "hyx_timeout_exceeded")
    assert exceeded == 1


async def test__prometheus_bulkhead_listener__on_bulkhead_full(registry):
    import asyncio

    from hyx.telemetry.prometheus import BulkheadListener
    from hyx.bulkhead import bulkhead
    from hyx.bulkhead.exceptions import BulkheadFull

    event_manager = EventManager()
    listener = BulkheadListener(registry=registry)

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
    rejected = get_metric_value(registry, "hyx_bulkhead_rejected")
    assert rejected == 1


async def test__prometheus_fallback_listener__on_fallback(registry):
    from hyx.telemetry.prometheus import FallbackListener
    from hyx.fallback import fallback

    event_manager = EventManager()
    listener = FallbackListener(registry=registry)

    async def fallback_handler(result, *args, **kwargs):
        return "fallback_value"

    @fallback(handler=fallback_handler, on=ValueError, listeners=[listener], event_manager=event_manager)
    async def failing_func():
        raise ValueError("error")

    result = await failing_func()
    await event_manager.wait_for_tasks()

    assert result == "fallback_value"

    # Check fallback metric
    triggered = get_metric_value(registry, "hyx_fallback_triggered", {"reason": "exception"})
    assert triggered == 1
