# Event System

Hyx includes an event system that allows you to observe and react to component lifecycle events.
This is the foundation for telemetry integrations and enables building custom monitoring solutions.

## Overview

The event system follows the **Observer pattern** with these key concepts:

- **Events** - Lifecycle moments (retry attempt, circuit breaker state change, timeout, etc.)
- **Listeners** - Objects that react to events by implementing handler methods
- **EventDispatcher** - Routes events to registered listeners
- **EventManager** - Tracks async listener tasks for graceful shutdown

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│  Component  │────▶│  EventDispatcher │────▶│  Listeners  │
│  (Retry,    │     │                  │     │  (OTel,     │
│   Breaker)  │     │                  │     │   Custom)   │
└─────────────┘     └──────────────────┘     └─────────────┘
                            │
                            ▼
                    ┌──────────────────┐
                    │   EventManager   │
                    │  (task tracking) │
                    └──────────────────┘
```

## Listener Interfaces

Each component type defines its own listener interface. Implement only the methods you need.

### RetryListener

```python
from hyx.retry.events import RetryListener

class MyRetryListener(RetryListener):
    async def on_retry(self, retry, exception, counter, backoff):
        """Called when a retry attempt is made."""
        print(f"Retry #{counter.current} for {retry.name}: {exception}")

    async def on_attempts_exceeded(self, retry):
        """Called when all retry attempts are exhausted."""
        print(f"All retries exhausted for {retry.name}")

    async def on_success(self, retry, counter):
        """Called when the operation succeeds (with or without retries)."""
        print(f"Success for {retry.name} after {counter.current} attempts")
```

| Method | Parameters | Description |
|--------|------------|-------------|
| `on_retry` | `retry`, `exception`, `counter`, `backoff` | Retry attempt made |
| `on_attempts_exceeded` | `retry` | All attempts exhausted |
| `on_success` | `retry`, `counter` | Operation succeeded |

### CircuitBreakerListener (BreakerListener)

```python
from hyx.circuitbreaker.events import BreakerListener

class MyBreakerListener(BreakerListener):
    async def on_working(self, context, current_state, next_state):
        """Called when breaker transitions to working state."""
        print(f"{context.name}: {current_state.name} -> working")

    async def on_recovering(self, context, current_state, next_state):
        """Called when breaker transitions to recovering state."""
        print(f"{context.name}: {current_state.name} -> recovering")

    async def on_failing(self, context, current_state, next_state):
        """Called when breaker transitions to failing (open) state."""
        print(f"{context.name}: {current_state.name} -> failing")

    async def on_success(self, context, state):
        """Called on successful operation through the breaker."""
        print(f"{context.name}: success in {state.name} state")
```

| Method | Parameters | Description |
|--------|------------|-------------|
| `on_working` | `context`, `current_state`, `next_state` | Transitioned to working |
| `on_recovering` | `context`, `current_state`, `next_state` | Transitioned to recovering |
| `on_failing` | `context`, `current_state`, `next_state` | Transitioned to failing |
| `on_success` | `context`, `state` | Operation succeeded |

### TimeoutListener

```python
from hyx.timeout.events import TimeoutListener

class MyTimeoutListener(TimeoutListener):
    async def on_timeout(self, timeout):
        """Called when an operation exceeds the timeout."""
        print(f"Timeout exceeded for {timeout.name}")
```

| Method | Parameters | Description |
|--------|------------|-------------|
| `on_timeout` | `timeout` | Operation timed out |

### BulkheadListener

```python
from hyx.bulkhead.events import BulkheadListener

class MyBulkheadListener(BulkheadListener):
    async def on_bulkhead_full(self, bulkhead):
        """Called when an operation is rejected due to capacity."""
        print(f"Bulkhead {bulkhead.name} is full, request rejected")
```

| Method | Parameters | Description |
|--------|------------|-------------|
| `on_bulkhead_full` | `bulkhead` | Request rejected (capacity exceeded) |

### RateLimiterListener

```python
from hyx.ratelimit.events import RateLimiterListener

class MyRateLimiterListener(RateLimiterListener):
    async def on_rate_limited(self, limiter):
        """Called when an operation is rejected due to rate limiting."""
        print(f"Rate limiter {limiter.name} rejected request")
```

| Method | Parameters | Description |
|--------|------------|-------------|
| `on_rate_limited` | `limiter` | Request rejected (rate limit exceeded) |

### FallbackListener

```python
from hyx.fallback.events import FallbackListener

class MyFallbackListener(FallbackListener):
    async def on_fallback(self, fallback, result, *args, **kwargs):
        """Called when the fallback handler is triggered."""
        reason = "exception" if isinstance(result, Exception) else "predicate"
        print(f"Fallback triggered for {fallback.name}: {reason}")
```

| Method | Parameters | Description |
|--------|------------|-------------|
| `on_fallback` | `fallback`, `result`, `*args`, `**kwargs` | Fallback was triggered |

## Registering Listeners

There are two ways to register listeners: **globally** (for all components of a type) or **locally** (for a specific component instance).

### Global Registration

Global listeners receive events from all components of that type in your application:

```python
from hyx.retry.events import register_retry_listener
from hyx.circuitbreaker.events import register_breaker_listener
from hyx.timeout.events import register_timeout_listener
from hyx.bulkhead.events import register_bulkhead_listener
from hyx.ratelimit.events import register_ratelimiter_listener
from hyx.fallback.events import register_fallback_listener

# Register once at application startup
register_retry_listener(MyRetryListener())
register_breaker_listener(MyBreakerListener())
register_timeout_listener(MyTimeoutListener())
register_bulkhead_listener(MyBulkheadListener())
register_ratelimiter_listener(MyRateLimiterListener())
register_fallback_listener(MyFallbackListener())
```

### Local Registration

Local listeners are attached to specific component instances:

```python
from hyx.retry import retry

listener = MyRetryListener()

@retry(attempts=3, listeners=[listener])
async def my_function():
    ...
```

```python
from hyx.circuitbreaker import consecutive_breaker

listener = MyBreakerListener()

breaker = consecutive_breaker(
    failure_threshold=5,
    recovery_time_secs=30,
    listeners=[listener],
)
```

### Combining Global and Local

Both global and local listeners can be active simultaneously. Events are dispatched to all registered listeners:

```python
from hyx.retry.events import register_retry_listener
from hyx.retry import retry

# Global listener for metrics
register_retry_listener(MetricsListener())

# Local listener for specific logging
debug_listener = DebugListener()

@retry(attempts=3, listeners=[debug_listener])
async def critical_operation():
    ...
```

## Event Manager

The `EventManager` tracks all async listener tasks, enabling graceful shutdown and testing.

### Basic Usage

```python
from hyx.events import EventManager
from hyx.retry import retry

event_manager = EventManager()

@retry(attempts=3, event_manager=event_manager)
async def my_function():
    ...

# Run your operations
await my_function()

# Wait for all listener tasks to complete
await event_manager.wait_for_tasks()
```

### Graceful Shutdown

```python
import signal
from hyx.events import EventManager

event_manager = EventManager()

async def shutdown():
    # Cancel all pending listener tasks
    await event_manager.cancel_tasks()

# Register shutdown handler
loop = asyncio.get_event_loop()
loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(shutdown()))
```

### Testing

The EventManager is essential for testing to ensure all events are processed:

```python
import pytest
from hyx.events import EventManager
from hyx.retry import retry

async def test_retry_events():
    event_manager = EventManager()
    captured_events = []

    class TestListener:
        async def on_retry(self, retry, exception, counter, backoff):
            captured_events.append(("retry", retry.name))

        async def on_success(self, retry, counter):
            captured_events.append(("success", retry.name))

    @retry(attempts=3, listeners=[TestListener()], event_manager=event_manager)
    async def flaky():
        if len(captured_events) < 2:
            raise ValueError("not yet")
        return "ok"

    await flaky()
    await event_manager.wait_for_tasks()  # Important!

    assert len(captured_events) == 3  # 2 retries + 1 success
```

## Listener Factories

For advanced use cases, you can use **listener factories** - callables that create listeners dynamically based on the component:

```python
from hyx.retry.events import register_retry_listener

async def create_listener(component):
    """Factory that creates a listener with component context."""
    class DynamicListener:
        async def on_retry(self, retry, exception, counter, backoff):
            # Access component info at creation time
            print(f"Retry for component created at startup: {component.name}")

    return DynamicListener()

# Register the factory (not an instance)
register_retry_listener(create_listener)
```

Factories are useful when:

- Listeners need component-specific configuration
- You want lazy initialization
- The listener needs to reference the component it's attached to

## Architecture

### EventDispatcher

The `EventDispatcher` is the core routing mechanism. It:

1. Collects local and global listeners
2. Initializes listener factories on first event
3. Dispatches events to all listeners in parallel
4. Tracks tasks via EventManager (if provided)

```python
from hyx.events import EventDispatcher, ListenerRegistry

# Internal usage (you typically don't need this directly)
dispatcher = EventDispatcher(
    local_listeners=[listener1, listener2],
    global_listener_registry=registry,
    event_manager=event_manager,
)
```

### ListenerRegistry

Each component type has a global `ListenerRegistry`:

```python
from hyx.events import ListenerRegistry

# Defined in each component's events module
_RETRY_LISTENERS: ListenerRegistry["RetryManager", "RetryListener"] = ListenerRegistry()
```

### Event Flow

1. Component calls event method (e.g., `self._event_dispatcher.on_retry(...)`)
2. EventDispatcher creates an async task
3. Task is registered with EventManager (if present)
4. All listeners receive the event in parallel via `asyncio.gather`
5. Errors in listeners are isolated (don't affect the main operation)

## Best Practices

1. **Keep listeners fast** - Events are processed asynchronously but slow listeners can accumulate
2. **Handle errors gracefully** - Listener errors don't propagate to the main operation
3. **Use EventManager in tests** - Always call `await event_manager.wait_for_tasks()` before assertions
4. **Prefer global registration for observability** - Use local listeners only for component-specific behavior
5. **Don't block in listeners** - Use `asyncio.create_task()` for long-running operations
