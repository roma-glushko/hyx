# Bulkheads

## Introduction

The cloud engineering world loves ocean and ship analogies:
Kubernetes, Docker, containers, Helm, pods, Harbor, Spinnaker, Werf, Shipwright, etc.
One word from that vocabulary has been adopted by resiliency engineering as well: the bulkhead.

A bulkhead (a.k.a. bulwark) can be viewed as a virtual room of a certain capacity. That capacity represents the resources you allow to be used simultaneously to process a given action.
You can define multiple bulkheads for different functionality in your microservice,
ensuring that **one part of the system won't consume resources at the expense of another**.

There are different ways to implement bulkheads:

* In multithreaded applications, it may take the form of a queue with a fixed-size worker pool
* In single-threaded, event-loop-based applications (like Hyx), it takes the form of concurrency limiting

Hence, the bulkhead is essentially a **concurrency limiting mechanism**. In turn, concurrency limiting can be seen as a form of
[rate limiting](rate_limiter.md).

## Use Cases

* Limit the number of concurrent requests in one part of the microservice, preventing it from consuming resources needed by other parts during load spikes
* Shed excessive load from the microservice

## Usage

=== "decorator"

    ```Python hl_lines="1 7"
    {!> ./snippets/bulkhead/bulkhead_decorator.py !}
    ```

=== "context manager"

    ```Python hl_lines="1 4 12"
    {!> ./snippets/bulkhead/bulkhead_context.py !}
    ```

::: hyx.bulkhead.bulkhead
    :docstring:

## Adaptive Limiting

Concurrency can be limited adaptively based on latency statistics from completed requests and a latency objective.

!!! note
    Hyx doesn't provide an ARC implementation at this moment. [Let us know](../faq.md#missing-a-feature) if this is useful for you.

