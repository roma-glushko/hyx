# Circuit Breakers

## Introduction

When the downstream microservice has been failing for some time, [retries](./retry.md) may not be the best thing to do.
Retries will keep sending requests to the microservices trying to succeed no matter what. 

That's a pretty selfish strategy that further leads to overloading the microservice, 
wasting time and resources of all upstream microservices that are waiting for the failed one.

What if we could **fail as soon as we understood that odds to get a successful response was small**? 
Circuit breakers are designed exactly for this.

Generally, circuit breakers are calculating some statistics about failed responses. 
At some point, they **block all actions or requests** that go through them for some time. 
That time is our hope that it's going to be enough for the downstream service to recover.

## Use Cases

* Monitor and isolate subsystems. 
  Breakers are a great way to implement the effective white-box monitoring as they divide the whole system 
  into subsystems. If one of the subsystems is failing, breakers dispatch metrics needed to efficiently locate the problem. 
* Fail fast and efficiently if the failure is persisting for a long time. Improve latency of the requests in case of failures
* Shed the load from the downstream subsystem in case of failure

## States

Circuit breakers are implemented as state machines. The following states are supported:

* `Working` *(a.k.a. the closed state)* - the system is healthy. Actions are executed.
* `Failing` *(a.k.a. the open state)* - the system is failing. No actions are executed.
* `Recovering` *(a.k.a. the half-open state)* - the recovery delay is over and now the system is being probed

!!! note
    Hyx doesn't follow the traditional state names inspired by the electrical circuit breaker.
    We believe that you could find more straightforward names if you look outside that analogy.

## Usage

The breakers come into two flavours:

=== "decorator"

    ```Python hl_lines="15 18"
    {!> ./snippets/circuit_breakers/breaker_decorator.py !}
    ```

=== "context manager"

    ```Python hl_lines="15 19"
    {!> ./snippets/circuit_breakers/breaker_context.py !}
    ```

!!! note
    Breakers are stateful components. 
    The regular usage is to create an instance of a breaker and use or inject it in all places that are working with the underlying subsystem that we anticipate to fail.

!!! warning
    For the sake of simplicity, Hyx assumes that you are following AsyncIO best practices and not running CPU-intensive operations in the main thread.
    Otherwise, the breaker delays may fire later after the thread is unblocked.

## Breakers

### Consecutive Breaker

::: hyx.circuitbreaker.consecutive_breaker
    :docstring:

## Best Practices

### Catch Server-Side Errors

TBU