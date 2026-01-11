# Bulkheads

## Introduction

The cloud engineering world loves ocean/ship analogies a lot. 
Kubernetes, docker, containers, helm, pods, harbor, spinnaker, werf, shipwright, etc.
One word from that vocabulary was actually reserved by resiliency engineering as well. It's a bulkhead.

Bulkhead (a.k.a. bulwark) can be viewed as a virtual room of certain capacity. That capacity is your resources that you allow to be used at the same time to process that action.
You can define multiple bulkheads per different functionality in your microservice. 
That will ensure that **one part of functionality won't be working at the expense of another**.

There is a different ways to implement bulkheads:

* In multithreaded applications it may take a form of a queue with a fixed-size worker pool
* In a single-thread event-loop-based application (the Hyx case), it takes a form of concurrency limiting

Hence, the bulkhead is essentially a **concurrency limiting mechanism**. In turn, concurrency limiting can be seen as a form of
[rate limiting](rate_limiter.md).

## Use Cases

* Limit the number of concurrent requests in one part of the microservice, so it won't take resources from other parts in case of load increase
* Shed excessive loads off the microservice

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

Concurrency is possible to limit adaptively based on statistics around latency of completed requests and some latency objective.

!!! note
    Hyx doesn't provide ARC implementation at this moment. [Let us know](../faq.md#missing-a-feature) if this is useful for you.

