# Timeouts

## Introduction

Not all actions or requests complete immediately.
Most actions take some time to finish, and that time may depend on various factors like user input, current load, etc.
At the same time, we don't want to wait forever, as waiting consumes resources, and resources are limited.

One way to address this problem is to specify a timeout: the maximum time you're willing to wait for an action to complete.

Some functionality comes with built-in timeouts. For example, if you're using an HTTP or RPC client, chances are there's a timeout parameter available:

* [HTTPX: Timeouts](https://www.python-httpx.org/compatibility/#timeouts)
* [AIOHTTP: Timeouts](https://docs.aiohttp.org/en/stable/client_quickstart.html#timeouts)
* [gRPC: ClientCallDetails](https://grpc.github.io/grpc/python/grpc_asyncio.html#grpc.aio.ClientCallDetails)
* [IOTHRIFT: Client Timeout](https://aiothrift.readthedocs.io/en/latest/examples.html?highlight=timeout#aio-thrift-client)

For situations where this is not the case,
Hyx provides a decorator and a context manager to help with setting up timeouts.

## Use Cases

* Ensure that the caller waits no longer than a given delay. [Local timeouts](#local-timeouts) work best when limiting actions that don't touch other microservices.
* Limit a microservice request chain by using a [distributed timeout](#distributed-timeout)

## By Locality

### Local Timeouts

=== "decorator"

    ```Python hl_lines="3 6"
    {!> ./snippets/timeout/timeout_decorator.py !}
    ```

=== "context manager"

    ```Python hl_lines="3 10"
    {!> ./snippets/timeout/timeout_context.py !}
    ```

::: hyx.timeout.timeout
    :docstring:

!!! warning
    For the sake of simplicity, Hyx assumes that you are following AsyncIO best practices and not running CPU-intensive operations in the main thread.
    Otherwise, the timeout functionality may fire with a delay after the thread is unblocked.

### Distributed Timeout

Distributed systems make things more complicated when it comes to timeouts.
When you send a request to a downstream service with a timeout, there's a possibility that the request will be queued for a while.
As a result, the caller may give up waiting and move on to handling other requests.

But what eventually happens to that queued request?
If it doesn't fail at the load balancing level, it will simply be processed when its turn comes.
This wastes resources since the result won't be used anyway.

A common solution is to let all microservices in the request chain know how much time they have to respond.
If that limit is exceeded, microservices can ignore requests that have already timed out.
This is called a distributed timeout (a.k.a. deadlines or timeout budget).

!!! info
    Hyx doesn't yet provide a way to easily add a distributed budget,
    as it would require integration with the API framework of your choice. We have [some plans](../roadmap.md) to support that.
    [Let us know](../faq.md#missing-a-feature) if this is useful for you.
