# Circuit Breakers

## Introduction

When a downstream microservice has been failing for some time, [retries](./retry.md) may not be the best approach.
Retries will keep sending requests to the microservice, trying to succeed no matter what.

That's a rather selfish strategy that can further overload the microservice
and waste time and resources of all upstream microservices waiting for the failed one.

What if we could **fail fast as soon as we understood that the odds of getting a successful response were small**?
Circuit breakers are designed exactly for this purpose.

Generally, circuit breakers track statistics about failed responses.
At some point, they **block all actions or requests** passing through them for a period of time.
That period is our hope that it will be enough for the downstream service to recover.

## Use Cases

* Monitor and isolate subsystems.
  Breakers are a great way to implement effective white-box monitoring, as they divide the system
  into subsystems. If one subsystem is failing, breakers dispatch the metrics needed to efficiently locate the problem.
* Fail fast and efficiently if the failure persists. Improve request latency during failures.
* Shed load from the downstream subsystem in case of failure.

## States

Circuit breakers are implemented as state machines. The following states are supported:

* `Working` *(a.k.a. the closed state)* - the system is healthy. Actions are executed.
* `Failing` *(a.k.a. the open state)* - the system is failing. No actions are executed.
* `Recovering` *(a.k.a. the half-open state)* - the recovery delay is over and the system is being probed.

!!! note
    Hyx doesn't follow the traditional state names inspired by electrical circuit breakers.
    We believe you can find more intuitive names if you look outside that analogy.

## Usage

Breakers come in two flavors:

=== "decorator"

    ```Python hl_lines="6 15-19 22"
    {!> ./snippets/circuit_breakers/breaker_decorator.py !}
    ```

=== "context manager"

    ```Python hl_lines="6 15-19 23"
    {!> ./snippets/circuit_breakers/breaker_context.py !}
    ```

!!! note
    Breakers are stateful components.
    The typical usage is to create a single breaker instance and use or inject it wherever you interact with the underlying subsystem that may fail.

!!! warning
    For the sake of simplicity, Hyx assumes that you are following AsyncIO best practices and not running CPU-intensive operations in the main thread.
    Otherwise, the breaker delays may fire later after the thread is unblocked.

## Breakers

### Consecutive Breaker

::: hyx.circuitbreaker.consecutive_breaker
    :docstring:
