"""
StatsD instrumentation for Hyx components.

This module provides listeners that emit StatsD metrics for all Hyx
fault tolerance components. Install with: pip install hyx[statsd]

Usage:
    from hyx.telemetry.statsd import register_listeners

    # Register listeners for all components with default client (localhost:8125)
    register_listeners()

    # Or with custom client
    import statsd
    client = statsd.StatsClient('statsd.example.com', 8125, prefix='myapp')
    register_listeners(client=client)

    # Or register individual listeners
    from hyx.telemetry.statsd import RetryListener
    from hyx.retry import register_retry_listener
    register_retry_listener(RetryListener())
"""

from typing import TYPE_CHECKING, Any

try:
    from statsd import StatsClient
except ImportError as e:
    raise ImportError("statsd is required for StatsD instrumentation. Install it with: pip install hyx[statsd]") from e

if TYPE_CHECKING:
    from hyx.bulkhead.manager import BulkheadManager
    from hyx.circuitbreaker.context import BreakerContext
    from hyx.circuitbreaker.states import BreakerState, FailingState, RecoveringState, WorkingState
    from hyx.fallback.manager import FallbackManager
    from hyx.fallback.typing import ResultT
    from hyx.retry.counters import Counter
    from hyx.retry.manager import RetryManager
    from hyx.timeout.manager import TimeoutManager


DEFAULT_PREFIX = "hyx"


def _get_client(client: StatsClient | None = None, prefix: str = DEFAULT_PREFIX) -> StatsClient:
    return client if client is not None else StatsClient(prefix=prefix)


class RetryListener:
    """StatsD metrics listener for retry components."""

    def __init__(self, client: StatsClient | None = None) -> None:
        self._client = _get_client(client)

    async def on_retry(
        self,
        retry: "RetryManager",
        exception: Exception,
        counter: "Counter",
        backoff: float,
    ) -> None:
        self._client.incr(f"retry.{retry.name}.attempts")
        self._client.incr(f"retry.{retry.name}.attempts.{type(exception).__name__}")

    async def on_attempts_exceeded(self, retry: "RetryManager") -> None:
        self._client.incr(f"retry.{retry.name}.exhausted")

    async def on_success(self, retry: "RetryManager", counter: "Counter") -> None:
        self._client.incr(f"retry.{retry.name}.success")


class TimeoutListener:
    """StatsD metrics listener for timeout components."""

    def __init__(self, client: StatsClient | None = None) -> None:
        self._client = _get_client(client)

    async def on_timeout(self, timeout: "TimeoutManager") -> None:
        self._client.incr(f"timeout.{timeout.name}.exceeded")


class CircuitBreakerListener:
    """StatsD metrics listener for circuit breaker components."""

    def __init__(self, client: StatsClient | None = None) -> None:
        self._client = _get_client(client)

    async def on_working(
        self,
        context: "BreakerContext",
        current_state: "BreakerState",
        next_state: "WorkingState",
    ) -> None:
        self._client.incr(f"circuitbreaker.{context.name}.state.working")

    async def on_recovering(
        self,
        context: "BreakerContext",
        current_state: "BreakerState",
        next_state: "RecoveringState",
    ) -> None:
        self._client.incr(f"circuitbreaker.{context.name}.state.recovering")

    async def on_failing(
        self,
        context: "BreakerContext",
        current_state: "BreakerState",
        next_state: "FailingState",
    ) -> None:
        self._client.incr(f"circuitbreaker.{context.name}.state.failing")

    async def on_success(self, context: "BreakerContext", state: "BreakerState") -> None:
        self._client.incr(f"circuitbreaker.{context.name}.success")


class FallbackListener:
    """StatsD metrics listener for fallback components."""

    def __init__(self, client: StatsClient | None = None) -> None:
        self._client = _get_client(client)

    async def on_fallback(
        self,
        fallback: "FallbackManager",
        result: "ResultT",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        reason = "exception" if isinstance(result, Exception) else "predicate"
        self._client.incr(f"fallback.{fallback.name}.triggered")
        self._client.incr(f"fallback.{fallback.name}.triggered.{reason}")


class BulkheadListener:
    """StatsD metrics listener for bulkhead components."""

    def __init__(self, client: StatsClient | None = None) -> None:
        self._client = _get_client(client)

    async def on_bulkhead_full(self, bulkhead: "BulkheadManager") -> None:
        self._client.incr(f"bulkhead.{bulkhead.name}.rejected")


def register_listeners(client: StatsClient | None = None) -> None:
    """
    Register StatsD listeners for all Hyx components.

    This is a convenience function that registers metric-emitting listeners
    for retry, circuit breaker, timeout, bulkhead, and fallback components.

    Args:
        client: Optional StatsClient instance. If not provided, a default
                client connecting to localhost:8125 with prefix 'hyx' is used.

    Example:
        from hyx.telemetry.statsd import register_listeners

        # Use default client
        register_listeners()

        # Or with custom client
        import statsd
        client = statsd.StatsClient('statsd.example.com', 8125, prefix='myapp')
        register_listeners(client=client)
    """
    from hyx.bulkhead.events import register_bulkhead_listener
    from hyx.circuitbreaker.events import register_breaker_listener
    from hyx.fallback.events import register_fallback_listener
    from hyx.retry.events import register_retry_listener
    from hyx.timeout.events import register_timeout_listener

    resolved_client = _get_client(client)

    register_retry_listener(RetryListener(client=resolved_client))
    register_breaker_listener(CircuitBreakerListener(client=resolved_client))
    register_timeout_listener(TimeoutListener(client=resolved_client))
    register_bulkhead_listener(BulkheadListener(client=resolved_client))
    register_fallback_listener(FallbackListener(client=resolved_client))
