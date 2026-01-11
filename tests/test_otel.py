import pytest
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import InMemoryMetricReader

from hyx.events import EventManager
from hyx.telemetry.otel import METER_NAME


@pytest.fixture
def otel_setup():
    """Create an InMemoryMetricReader and a Meter for testing."""
    reader = InMemoryMetricReader()
    provider = MeterProvider(metric_readers=[reader])
    meter = provider.get_meter(METER_NAME)

    return reader, meter


def get_metric_value(reader: InMemoryMetricReader, metric_name: str) -> list[dict]:
    """Extract metric data points from the reader."""
    metrics_data = reader.get_metrics_data()
    results: list[dict] = []

    if metrics_data is None:
        return results

    for resource_metrics in metrics_data.resource_metrics:
        for scope_metrics in resource_metrics.scope_metrics:
            if scope_metrics.scope.name == METER_NAME:
                for metric in scope_metrics.metrics:
                    if metric.name == metric_name:
                        for data_point in metric.data.data_points:
                            # NumberDataPoint has .value, histograms don't
                            value = getattr(data_point, "value", None)
                            attrs = dict(data_point.attributes) if data_point.attributes else {}
                            results.append({"value": value, "attributes": attrs})

    return results


async def test__otel_retry_listener__on_retry(otel_setup):
    from hyx.retry import retry
    from hyx.telemetry.otel import RetryListener

    reader, meter = otel_setup
    event_manager = EventManager()
    listener = RetryListener(meter=meter)

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
    retry_metrics = get_metric_value(reader, "hyx.retry.attempts")
    assert len(retry_metrics) == 1
    assert retry_metrics[0]["value"] == 2
    assert retry_metrics[0]["attributes"]["exception"] == "ValueError"

    # Check success metric
    success_metrics = get_metric_value(reader, "hyx.retry.success")
    assert len(success_metrics) == 1
    assert success_metrics[0]["value"] == 1


async def test__otel_retry_listener__attempts_exceeded(otel_setup):
    from hyx.retry import retry
    from hyx.retry.exceptions import AttemptsExceeded
    from hyx.telemetry.otel import RetryListener

    reader, meter = otel_setup
    event_manager = EventManager()
    listener = RetryListener(meter=meter)

    @retry(attempts=2, backoff=0, listeners=[listener], event_manager=event_manager)
    async def always_fails():
        raise RuntimeError("always fails")

    with pytest.raises(AttemptsExceeded):
        await always_fails()

    await event_manager.wait_for_tasks()

    # Check exhausted metric
    exhausted_metrics = get_metric_value(reader, "hyx.retry.exhausted")
    assert len(exhausted_metrics) == 1
    assert exhausted_metrics[0]["value"] == 1


async def test__otel_breaker_listener__state_transitions(otel_setup):
    from hyx.circuitbreaker import consecutive_breaker
    from hyx.telemetry.otel import CircuitBreakerListener

    reader, meter = otel_setup
    event_manager = EventManager()
    listener = CircuitBreakerListener(meter=meter)

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
    state_metrics = get_metric_value(reader, "hyx.circuitbreaker.state_transitions")
    assert len(state_metrics) == 1
    assert state_metrics[0]["attributes"]["from_state"] == "working"
    assert state_metrics[0]["attributes"]["to_state"] == "failing"


async def test__otel_timeout_listener__on_timeout(otel_setup):
    import asyncio

    from hyx.telemetry.otel import TimeoutListener
    from hyx.timeout import timeout
    from hyx.timeout.exceptions import MaxDurationExceeded

    reader, meter = otel_setup
    event_manager = EventManager()
    listener = TimeoutListener(meter=meter)

    @timeout(timeout_secs=0.01, listeners=[listener], event_manager=event_manager)
    async def slow_func():
        await asyncio.sleep(1)

    with pytest.raises(MaxDurationExceeded):
        await slow_func()

    await event_manager.wait_for_tasks()

    # Check timeout metric
    timeout_metrics = get_metric_value(reader, "hyx.timeout.exceeded")
    assert len(timeout_metrics) == 1
    assert timeout_metrics[0]["value"] == 1


async def test__otel_bulkhead_listener__on_bulkhead_full(otel_setup):
    import asyncio

    from hyx.bulkhead import bulkhead
    from hyx.bulkhead.exceptions import BulkheadFull
    from hyx.telemetry.otel import BulkheadListener

    reader, meter = otel_setup
    event_manager = EventManager()
    listener = BulkheadListener(meter=meter)

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
    rejected_metrics = get_metric_value(reader, "hyx.bulkhead.rejected")
    assert len(rejected_metrics) == 1
    assert rejected_metrics[0]["value"] == 1


async def test__otel_ratelimiter_listener__on_rate_limited(otel_setup):
    from hyx.ratelimit import tokenbucket
    from hyx.ratelimit.exceptions import RateLimitExceeded
    from hyx.telemetry.otel import RateLimiterListener

    reader, meter = otel_setup
    event_manager = EventManager()
    listener = RateLimiterListener(meter=meter)

    limiter = tokenbucket(
        max_executions=1,
        per_time_secs=10,
        bucket_size=1,
        name="test_limiter",
        listeners=[listener],
        event_manager=event_manager,
    )

    # First call should succeed
    async with limiter:
        pass

    # Second call should be rate limited
    with pytest.raises(RateLimitExceeded):
        async with limiter:
            pass

    await event_manager.wait_for_tasks()

    # Check rate limited metric
    rate_limited_metrics = get_metric_value(reader, "hyx.ratelimiter.rejected")
    assert len(rate_limited_metrics) == 1
    assert rate_limited_metrics[0]["value"] == 1


async def test__otel_fallback_listener__on_fallback(otel_setup):
    from hyx.fallback import fallback
    from hyx.telemetry.otel import FallbackListener

    reader, meter = otel_setup
    event_manager = EventManager()
    listener = FallbackListener(meter=meter)

    async def fallback_handler(result, *args, **kwargs):
        return "fallback_value"

    @fallback(handler=fallback_handler, on=ValueError, listeners=[listener], event_manager=event_manager)
    async def failing_func():
        raise ValueError("error")

    result = await failing_func()
    await event_manager.wait_for_tasks()

    assert result == "fallback_value"

    # Check fallback metric
    fallback_metrics = get_metric_value(reader, "hyx.fallback.triggered")
    assert len(fallback_metrics) == 1
    assert fallback_metrics[0]["value"] == 1
    assert fallback_metrics[0]["attributes"]["reason"] == "exception"
