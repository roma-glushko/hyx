# Roadmap

This page provides some transparency on Hyx roadmap and future plans. 
This may give some ideas on what to expect from the project and what we might miss.

!!! note
    Hyx is an open source community-driven project. 
    Hence, we don't have any well-defined deadlines for our milestones like you would expect from financially baked projects.
    The current project pace is based on the best effort.

## M0: The First Public Release

**Status**: Ongoing

### Github Milestones

* [Implement main components](https://github.com/roma-glushko/hyx/milestone/5)
* [Documentation / The baseline functionality](https://github.com/roma-glushko/hyx/milestone/1)
* [Implement CI/CD](https://github.com/roma-glushko/hyx/milestone/6)

### Goals

* Provide the baseline implementation for all general reliability components
* Init documentation. Document the components
* Implement project's infrastructure

## M1: Observability

**Status**: Future

Implement metrics to support white-box monitoring of the components

### Github Milestones

* [Observability / Integrate with OpenTelemetry](https://github.com/roma-glushko/hyx/milestone/2)
* [Observability / Integrate with Prometheus](https://github.com/roma-glushko/hyx/milestone/3)

### Goals

* Design an event system to hook into the component's lifecycle
* Provide a standalone library to integrate with [OpenTelemetry](https://opentelemetry.io/) metrics
* Provide a standalone library to integrate with [Prometheus](https://prometheus.io/) metrics
* Provide a standalone library to integrate with [StatsD](https://github.com/statsd/statsd) metrics

## M2: Pixi

**Status**: Future

Pixi is an example system that uses Hyx to ensure resiliency and self-healing. 

### Goals

* Create an example microservice system that uses Hyx as a resiliency toolkit
* Test Hyx components in composition

## M3: Advanced Breakers

**Status**: Future

### Goals

* Implement error-rate-based sliding window breaker
* Implement error-count-based sliding window breaker

## M4: API Framework Integration

**Status**: Future

Integrate with some popular frameworks to provide easy low-code solutions to common problems.

### Goals

* Implement a standalone library to integrate with Starlette/FastAPI
* Implement a standalone library to integrate with Flask
* Implement rate limiting middlewares
* Implement distributed timeouts 

## MX: Distributed components

**Status**: Distinct Future

Implement a distributed versions of the components based on Redis

### Goals

* Implement distributed rate limiting based on Redis
* Implement distributed circuit breakers based on Redis
