# Telemetry

Hyx provides built-in telemetry support to help you monitor your fault tolerance components in production.
All components emit events that can be captured by listeners and forwarded to your observability stack.

## Supported Backends

| Backend | Installation | Description |
|---------|--------------|-------------|
| [OpenTelemetry](#opentelemetry) | `pip install hyx[otel]` | Industry-standard observability framework |
| [Prometheus](#prometheus) | `pip install hyx[prometheus]` | Popular metrics and alerting toolkit |
| [StatsD](#statsd) | `pip install hyx[statsd]` | Simple daemon for aggregating statistics |

## OpenTelemetry

[OpenTelemetry](https://opentelemetry.io/) is the industry-standard observability framework for cloud-native software.

### Installation

```sh
pip install hyx[otel]
```

### Quick Start

Register listeners for all components with a single call:

```python
from hyx.telemetry.otel import register_listeners

# Uses the global meter provider
register_listeners()
```

Or with a custom meter:

```python
from opentelemetry import metrics
from hyx.telemetry.otel import register_listeners

meter = metrics.get_meter("my-service")
register_listeners(meter=meter)
```

### Individual Listeners

You can also register listeners for specific components:

```python
from hyx.telemetry.otel import RetryListener
from hyx.retry import retry

listener = RetryListener()

@retry(attempts=3, listeners=[listener])
async def my_function():
    ...
```

### Metrics Reference

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `hyx.retry.attempts` | Counter | `component`, `exception` | Number of retry attempts |
| `hyx.retry.exhausted` | Counter | `component` | Retry attempts exhausted |
| `hyx.retry.success` | Counter | `component` | Successful operations |
| `hyx.circuitbreaker.state_transitions` | Counter | `component`, `from_state`, `to_state` | State transitions |
| `hyx.circuitbreaker.success` | Counter | `component`, `state` | Successful operations |
| `hyx.timeout.exceeded` | Counter | `component` | Timeout exceeded |
| `hyx.bulkhead.rejected` | Counter | `component` | Rejected due to capacity |
| `hyx.fallback.triggered` | Counter | `component`, `reason` | Fallback triggered |

## Prometheus

[Prometheus](https://prometheus.io/) is an open-source monitoring and alerting toolkit.

### Installation

```sh
pip install hyx[prometheus]
```

### Quick Start

Register listeners for all components:

```python
from hyx.telemetry.prometheus import register_listeners

# Uses the default global registry
register_listeners()
```

Or with a custom registry:

```python
from prometheus_client import CollectorRegistry
from hyx.telemetry.prometheus import register_listeners

registry = CollectorRegistry()
register_listeners(registry=registry)
```

### Individual Listeners

```python
from hyx.telemetry.prometheus import CircuitBreakerListener
from hyx.circuitbreaker import consecutive_breaker

listener = CircuitBreakerListener()

breaker = consecutive_breaker(
    failure_threshold=5,
    recovery_time_secs=30,
    listeners=[listener],
)
```

### Metrics Reference

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `hyx_retry_attempts_total` | Counter | `component`, `exception` | Number of retry attempts |
| `hyx_retry_exhausted_total` | Counter | `component` | Retry attempts exhausted |
| `hyx_retry_success_total` | Counter | `component` | Successful operations |
| `hyx_circuitbreaker_state_transitions_total` | Counter | `component`, `from_state`, `to_state` | State transitions |
| `hyx_circuitbreaker_success_total` | Counter | `component`, `state` | Successful operations |
| `hyx_timeout_exceeded_total` | Counter | `component` | Timeout exceeded |
| `hyx_bulkhead_rejected_total` | Counter | `component` | Rejected due to capacity |
| `hyx_fallback_triggered_total` | Counter | `component`, `reason` | Fallback triggered |

## StatsD

[StatsD](https://github.com/statsd/statsd) is a simple daemon for aggregating statistics.

### Installation

```sh
pip install hyx[statsd]
```

### Quick Start

Register listeners for all components:

```python
from hyx.telemetry.statsd import register_listeners

# Uses default client (localhost:8125, prefix='hyx')
register_listeners()
```

Or with a custom client:

```python
import statsd
from hyx.telemetry.statsd import register_listeners

client = statsd.StatsClient('statsd.example.com', 8125, prefix='myapp')
register_listeners(client=client)
```

### Individual Listeners

```python
import statsd
from hyx.telemetry.statsd import TimeoutListener
from hyx.timeout import timeout

client = statsd.StatsClient(prefix='myapp')
listener = TimeoutListener(client=client)

@timeout(timeout_secs=5, listeners=[listener])
async def slow_operation():
    ...
```

### Metrics Reference

All metrics are prefixed with the client prefix (default: `hyx`).

| Metric | Type | Description |
|--------|------|-------------|
| `retry.<name>.attempts` | Counter | Retry attempt made |
| `retry.<name>.attempts.<exception>` | Counter | Retry attempt by exception type |
| `retry.<name>.exhausted` | Counter | Retry attempts exhausted |
| `retry.<name>.success` | Counter | Successful operation |
| `circuitbreaker.<name>.state.working` | Counter | Transitioned to working state |
| `circuitbreaker.<name>.state.recovering` | Counter | Transitioned to recovering state |
| `circuitbreaker.<name>.state.failing` | Counter | Transitioned to failing state |
| `circuitbreaker.<name>.success` | Counter | Successful operation |
| `timeout.<name>.exceeded` | Counter | Timeout exceeded |
| `bulkhead.<name>.rejected` | Counter | Rejected due to capacity |
| `fallback.<name>.triggered` | Counter | Fallback triggered |
| `fallback.<name>.triggered.<reason>` | Counter | Fallback by reason (exception/predicate) |

## Custom Listeners

You can create custom listeners by implementing the appropriate event handler methods. Each component type has its own listener interface:

```python
class MyRetryListener:
    async def on_retry(self, retry, exception, counter, backoff):
        print(f"Retrying {retry.name} after {type(exception).__name__}")

    async def on_attempts_exceeded(self, retry):
        print(f"Retry exhausted for {retry.name}")

    async def on_success(self, retry, counter):
        print(f"Success for {retry.name}")
```

Then register it globally or per-component:

```python
from hyx.retry.events import register_retry_listener
from hyx.retry import retry

# Global registration
register_retry_listener(MyRetryListener())

# Or per-component
@retry(attempts=3, listeners=[MyRetryListener()])
async def my_function():
    ...
```

## Event Manager

For advanced use cases, you can use the `EventManager` to control event processing:

```python
from hyx.events import EventManager
from hyx.retry import retry

event_manager = EventManager()

@retry(attempts=3, event_manager=event_manager)
async def my_function():
    ...

# Wait for all listener tasks to complete
await event_manager.wait_for_tasks()
```

This is useful in tests or when you need to ensure all telemetry events have been processed before shutting down.
