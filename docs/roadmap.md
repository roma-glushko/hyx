# Roadmap

This page provides some transparency on Hyx roadmap and future plans.
This may give some ideas on what to expect from the project and what we might miss.

!!! note
    Hyx is an open source community-driven project.
    Hence, we don't have any well-defined deadlines for our milestones like you would expect from financially baked projects.
    The current project pace is based on the best effort.

## M0: The First Public Release

**Status**: Complete :white_check_mark:

### Github Milestones

* [Implement main components](https://github.com/roma-glushko/hyx/milestone/5)
* [Documentation / The baseline functionality](https://github.com/roma-glushko/hyx/milestone/1)
* [Implement CI/CD](https://github.com/roma-glushko/hyx/milestone/6)

### Goals

* ~~Provide the baseline implementation for all general reliability components~~
* ~~Init documentation. Document the components~~
* ~~Implement project's infrastructure~~

## M1: Observability

**Status**: Complete :white_check_mark:

Implemented metrics support for white-box monitoring of all components.

### Github Milestones

* [Observability / Integrate with OpenTelemetry](https://github.com/roma-glushko/hyx/milestone/2)
* [Observability / Integrate with Prometheus](https://github.com/roma-glushko/hyx/milestone/3)

### Completed

* ~~Design an [event system](./events.md) to hook into the component's lifecycle~~
* ~~Provide integration with [OpenTelemetry](https://opentelemetry.io/) metrics~~ (`pip install hyx[otel]`)
* ~~Provide integration with [Prometheus](https://prometheus.io/) metrics~~ (`pip install hyx[prometheus]`)
* ~~Provide integration with [StatsD](https://github.com/statsd/statsd) metrics~~ (`pip install hyx[statsd]`)

See the [Telemetry documentation](./telemetry.md) for usage details.

## M2: Pixi

**Status**: Future

Pixi is an example system that uses Hyx to ensure resiliency and self-healing.

### Goals

* Create an example microservice system that uses Hyx as a resiliency toolkit
* Test Hyx components in composition
* Provide real-world usage patterns and best practices

## M3: Advanced Breakers

**Status**: Future

Expand circuit breaker capabilities with more sophisticated failure detection.

### Goals

* Implement error-rate-based sliding window breaker
* Implement error-count-based sliding window breaker
* Add configurable health check probes during recovery

## M4: API Framework Integration

**Status**: Future

Integrate with popular frameworks to provide easy low-code solutions to common problems.

### Goals

* Implement middleware for Starlette/FastAPI
* Implement middleware for Flask
* Rate limiting middlewares with request identification
* Distributed timeouts across service boundaries

## M5: Tracing Support

**Status**: Future

Extend observability with distributed tracing capabilities.

### Goals

* OpenTelemetry tracing integration (spans for retries, breaker states, etc.)
* Correlation ID propagation through fault tolerance components
* Context preservation across async boundaries

## MX: Distributed Components

**Status**: Distant Future

Implement distributed versions of the components for multi-instance deployments.

### Goals

* Distributed rate limiting based on Redis
* Distributed circuit breakers with shared state
* Distributed bulkheads for cluster-wide concurrency limits
* Leader election for coordinated recovery
