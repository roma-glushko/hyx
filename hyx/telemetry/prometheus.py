"""
Prometheus instrumentation for Hyx components.

This module provides listeners that emit Prometheus metrics for all Hyx
fault tolerance components. Install with: pip install hyx[prometheus]

Usage:
    from hyx.telemetry.prometheus import register_listeners

    # Register listeners for all components
    register_listeners()

    # Or register individual listeners
    from hyx.telemetry.prometheus import RetryListener
    from hyx.retry import register_retry_listener
    register_retry_listener(RetryListener())
"""

from typing import TYPE_CHECKING, Any

try:
    from prometheus_client import REGISTRY, CollectorRegistry, Counter
except ImportError as e:
    raise ImportError(
        "prometheus-client is required for Prometheus instrumentation. "
        "Install it with: pip install hyx[prometheus]"
    ) from e

if TYPE_CHECKING:
    from hyx.bulkhead.manager import BulkheadManager
    from hyx.circuitbreaker.context import BreakerContext
    from hyx.circuitbreaker.states import BreakerState, FailingState, RecoveringState, WorkingState
    from hyx.fallback.manager import FallbackManager
    from hyx.fallback.typing import ResultT
    from hyx.retry.counters import Counter as RetryCounter
    from hyx.retry.manager import RetryManager
    from hyx.timeout.manager import TimeoutManager


class RetryListener:
    """Prometheus metrics listener for retry components."""

    def __init__(self, registry: CollectorRegistry | None = None) -> None:
        registry = registry if registry is not None else REGISTRY

        self._retry_counter = Counter(
            name="hyx_retry_attempts_total",
            documentation="Number of retry attempts",
            labelnames=["component", "exception"],
            registry=registry,
        )
        self._exhausted_counter = Counter(
            name="hyx_retry_exhausted_total",
            documentation="Number of times retry attempts were exhausted",
            labelnames=["component"],
            registry=registry,
        )
        self._success_counter = Counter(
            name="hyx_retry_success_total",
            documentation="Number of successful operations (with or without retries)",
            labelnames=["component"],
            registry=registry,
        )

    async def on_retry(
        self,
        retry: "RetryManager",
        exception: Exception,
        counter: "RetryCounter",
        backoff: float,
    ) -> None:
        self._retry_counter.labels(component=retry.name, exception=type(exception).__name__).inc()

    async def on_attempts_exceeded(self, retry: "RetryManager") -> None:
        self._exhausted_counter.labels(component=retry.name).inc()

    async def on_success(self, retry: "RetryManager", counter: "RetryCounter") -> None:
        self._success_counter.labels(component=retry.name).inc()


class CircuitBreakerListener:
    """Prometheus metrics listener for circuit breaker components."""

    def __init__(self, registry: CollectorRegistry | None = None) -> None:
        registry = registry if registry is not None else REGISTRY

        self._state_counter = Counter(
            name="hyx_circuitbreaker_state_transitions_total",
            documentation="Number of circuit breaker state transitions",
            labelnames=["component", "from_state", "to_state"],
            registry=registry,
        )
        self._success_counter = Counter(
            name="hyx_circuitbreaker_success_total",
            documentation="Number of successful operations through the circuit breaker",
            labelnames=["component", "state"],
            registry=registry,
        )

    async def on_working(
        self,
        context: "BreakerContext",
        current_state: "BreakerState",
        next_state: "WorkingState",
    ) -> None:
        self._state_counter.labels(
            component=context.name, from_state=current_state.name, to_state="working"
        ).inc()

    async def on_recovering(
        self,
        context: "BreakerContext",
        current_state: "BreakerState",
        next_state: "RecoveringState",
    ) -> None:
        self._state_counter.labels(
            component=context.name, from_state=current_state.name, to_state="recovering"
        ).inc()

    async def on_failing(
        self,
        context: "BreakerContext",
        current_state: "BreakerState",
        next_state: "FailingState",
    ) -> None:
        self._state_counter.labels(
            component=context.name, from_state=current_state.name, to_state="failing"
        ).inc()

    async def on_success(self, context: "BreakerContext", state: "BreakerState") -> None:
        self._success_counter.labels(component=context.name, state=state.name).inc()


class TimeoutListener:
    """Prometheus metrics listener for timeout components."""

    def __init__(self, registry: CollectorRegistry | None = None) -> None:
        registry = registry if registry is not None else REGISTRY

        self._timeout_counter = Counter(
            name="hyx_timeout_exceeded_total",
            documentation="Number of operations that exceeded the timeout",
            labelnames=["component"],
            registry=registry,
        )

    async def on_timeout(self, timeout: "TimeoutManager") -> None:
        self._timeout_counter.labels(component=timeout.name).inc()


class BulkheadListener:
    """Prometheus metrics listener for bulkhead components."""

    def __init__(self, registry: CollectorRegistry | None = None) -> None:
        registry = registry if registry is not None else REGISTRY

        self._rejected_counter = Counter(
            name="hyx_bulkhead_rejected_total",
            documentation="Number of operations rejected due to bulkhead capacity",
            labelnames=["component"],
            registry=registry,
        )

    async def on_bulkhead_full(self, bulkhead: "BulkheadManager") -> None:
        self._rejected_counter.labels(component=bulkhead.name).inc()


class FallbackListener:
    """Prometheus metrics listener for fallback components."""

    def __init__(self, registry: CollectorRegistry | None = None) -> None:
        registry = registry if registry is not None else REGISTRY

        self._fallback_counter = Counter(
            name="hyx_fallback_triggered_total",
            documentation="Number of times the fallback was triggered",
            labelnames=["component", "reason"],
            registry=registry,
        )

    async def on_fallback(
        self,
        fallback: "FallbackManager",
        result: "ResultT",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        reason = "exception" if isinstance(result, Exception) else "predicate"
        self._fallback_counter.labels(component=fallback.name, reason=reason).inc()


def register_listeners(registry: CollectorRegistry | None = None) -> None:
    """
    Register Prometheus listeners for all Hyx components.

    This is a convenience function that registers metric-emitting listeners
    for retry, circuit breaker, timeout, bulkhead, and fallback components.

    Args:
        registry: Optional CollectorRegistry instance. If not provided,
                  uses the default REGISTRY.

    Example:
        from hyx.telemetry.prometheus import register_listeners

        register_listeners()

        # Now all Hyx components will emit Prometheus metrics
    """
    from hyx.bulkhead.events import register_bulkhead_listener
    from hyx.circuitbreaker.events import register_breaker_listener
    from hyx.fallback.events import register_fallback_listener
    from hyx.retry.events import register_retry_listener
    from hyx.timeout.events import register_timeout_listener

    register_retry_listener(RetryListener(registry=registry))
    register_breaker_listener(CircuitBreakerListener(registry=registry))
    register_timeout_listener(TimeoutListener(registry=registry))
    register_bulkhead_listener(BulkheadListener(registry=registry))
    register_fallback_listener(FallbackListener(registry=registry))
