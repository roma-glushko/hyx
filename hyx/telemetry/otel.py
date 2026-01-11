"""
OpenTelemetry instrumentation for Hyx components.

This module provides listeners that emit OpenTelemetry metrics for all Hyx
fault tolerance components. Install with: pip install hyx[otel]

Usage:
    from hyx.telemetry.otel import register_listeners

    # Register listeners for all components
    register_listeners()

    # Or register individual listeners
    from hyx.telemetry.otel import RetryListener
    from hyx.retry import register_retry_listener
    register_retry_listener(RetryListener())
"""

from typing import TYPE_CHECKING, Any

from hyx.bulkhead.events import BulkheadListener as BaseBulkheadListener
from hyx.circuitbreaker.events import BreakerListener as BaseBreakerListener
from hyx.fallback.events import FallbackListener as BaseFallbackListener
from hyx.retry.events import RetryListener as BaseRetryListener
from hyx.timeout.events import TimeoutListener as BaseTimeoutListener

try:
    from opentelemetry import metrics
    from opentelemetry.metrics import Meter
except ImportError as e:
    raise ImportError(
        "OpenTelemetry is required for OTel instrumentation. Install it with: pip install hyx[otel]"
    ) from e

if TYPE_CHECKING:
    from hyx.bulkhead.manager import BulkheadManager
    from hyx.circuitbreaker.context import BreakerContext
    from hyx.circuitbreaker.states import BreakerState, FailingState, RecoveringState, WorkingState
    from hyx.fallback.manager import FallbackManager
    from hyx.fallback.typing import ResultT
    from hyx.retry.counters import Counter
    from hyx.retry.manager import RetryManager
    from hyx.timeout.manager import TimeoutManager


METER_NAME = "hyx"


def _get_meter(meter: Meter | None = None) -> Meter:
    return meter if meter is not None else metrics.get_meter(METER_NAME)


class RetryListener(BaseRetryListener):
    """OpenTelemetry metrics listener for retry components."""

    def __init__(self, meter: Meter | None = None) -> None:
        meter = _get_meter(meter)

        self._retry_counter = meter.create_counter(
            name="hyx.retry.attempts",
            description="Number of retry attempts",
            unit="1",
        )
        self._exhausted_counter = meter.create_counter(
            name="hyx.retry.exhausted",
            description="Number of times retry attempts were exhausted",
            unit="1",
        )
        self._success_counter = meter.create_counter(
            name="hyx.retry.success",
            description="Number of successful operations (with or without retries)",
            unit="1",
        )

    async def on_retry(
        self,
        retry: "RetryManager",
        exception: Exception,
        counter: "Counter",
        backoff: float,
    ) -> None:
        self._retry_counter.add(1, {"component": retry.name or "", "exception": type(exception).__name__})

    async def on_attempts_exceeded(self, retry: "RetryManager") -> None:
        self._exhausted_counter.add(1, {"component": retry.name or ""})

    async def on_success(self, retry: "RetryManager", counter: "Counter") -> None:
        self._success_counter.add(1, {"component": retry.name or ""})


class CircuitBreakerListener(BaseBreakerListener):
    """OpenTelemetry metrics listener for circuit breaker components."""

    def __init__(self, meter: Meter | None = None) -> None:
        meter = _get_meter(meter)

        self._state_counter = meter.create_counter(
            name="hyx.circuitbreaker.state_transitions",
            description="Number of circuit breaker state transitions",
            unit="1",
        )
        self._success_counter = meter.create_counter(
            name="hyx.circuitbreaker.success",
            description="Number of successful operations through the circuit breaker",
            unit="1",
        )

    async def on_working(
        self,
        context: "BreakerContext",
        current_state: "BreakerState",
        next_state: "WorkingState",
    ) -> None:
        self._state_counter.add(
            1,
            {"component": context.name or "", "from_state": current_state.name, "to_state": "working"},
        )

    async def on_recovering(
        self,
        context: "BreakerContext",
        current_state: "BreakerState",
        next_state: "RecoveringState",
    ) -> None:
        self._state_counter.add(
            1,
            {"component": context.name or "", "from_state": current_state.name, "to_state": "recovering"},
        )

    async def on_failing(
        self,
        context: "BreakerContext",
        current_state: "BreakerState",
        next_state: "FailingState",
    ) -> None:
        self._state_counter.add(
            1,
            {"component": context.name or "", "from_state": current_state.name, "to_state": "failing"},
        )

    async def on_success(self, context: "BreakerContext", state: "BreakerState") -> None:
        self._success_counter.add(1, {"component": context.name or "", "state": state.name})


class TimeoutListener(BaseTimeoutListener):
    """OpenTelemetry metrics listener for timeout components."""

    def __init__(self, meter: Meter | None = None) -> None:
        meter = _get_meter(meter)

        self._timeout_counter = meter.create_counter(
            name="hyx.timeout.exceeded",
            description="Number of operations that exceeded the timeout",
            unit="1",
        )

    async def on_timeout(self, timeout: "TimeoutManager") -> None:
        self._timeout_counter.add(1, {"component": timeout.name or ""})


class BulkheadListener(BaseBulkheadListener):
    """OpenTelemetry metrics listener for bulkhead components."""

    def __init__(self, meter: Meter | None = None) -> None:
        meter = _get_meter(meter)

        self._rejected_counter = meter.create_counter(
            name="hyx.bulkhead.rejected",
            description="Number of operations rejected due to bulkhead capacity",
            unit="1",
        )

    async def on_bulkhead_full(self, bulkhead: "BulkheadManager") -> None:
        self._rejected_counter.add(1, {"component": bulkhead.name or ""})


class FallbackListener(BaseFallbackListener):
    """OpenTelemetry metrics listener for fallback components."""

    def __init__(self, meter: Meter | None = None) -> None:
        meter = _get_meter(meter)

        self._fallback_counter = meter.create_counter(
            name="hyx.fallback.triggered",
            description="Number of times the fallback was triggered",
            unit="1",
        )

    async def on_fallback(
        self,
        fallback: "FallbackManager",
        result: "ResultT",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        # Determine if fallback was triggered by exception or predicate
        reason = "exception" if isinstance(result, Exception) else "predicate"
        self._fallback_counter.add(1, {"component": fallback.name or "", "reason": reason})


def register_listeners(meter: Meter | None = None) -> None:
    """
    Register OpenTelemetry listeners for all Hyx components.

    This is a convenience function that registers metric-emitting listeners
    for retry, circuit breaker, timeout, bulkhead, and fallback components.

    Args:
        meter: Optional Meter instance. If not provided, uses the global meter provider.

    Example:
        from hyx.telemetry.otel import register_listeners

        register_listeners()

        # Now all Hyx components will emit OTel metrics
    """
    from hyx.bulkhead.events import register_bulkhead_listener
    from hyx.circuitbreaker.events import register_breaker_listener
    from hyx.fallback.events import register_fallback_listener
    from hyx.retry.events import register_retry_listener
    from hyx.timeout.events import register_timeout_listener

    register_retry_listener(RetryListener(meter=meter))
    register_breaker_listener(CircuitBreakerListener(meter=meter))
    register_timeout_listener(TimeoutListener(meter=meter))
    register_bulkhead_listener(BulkheadListener(meter=meter))
    register_fallback_listener(FallbackListener(meter=meter))
