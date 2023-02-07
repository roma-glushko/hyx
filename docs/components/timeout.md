# Timeouts

## Introduction

Not all actions or requests complete immediately. 
Most of the actions take a bit of time to finish and that time may depend on various variables like user input, current load, etc.
At the same time, we don't want to wait forever as any waiting takes resources, and we are limited in terms of resources.

One way to go about this problem is to specify a timeout which is how much time you can wait in the worst case for the action to happen.

Some functionality comes with built-in timeouts. For example, if you are using a HTTP or RPC client, chances are there is timeout parameter in there:

* [HTTPX: Timeouts](https://www.python-httpx.org/compatibility/#timeouts)
* [AIOHTTP: Timeouts](https://docs.aiohttp.org/en/stable/client_quickstart.html#timeouts)
* [gRPC: ClientCallDetails](https://grpc.github.io/grpc/python/grpc_asyncio.html#grpc.aio.ClientCallDetails)
* [IOTHRIFT: Client Timeout](https://aiothrift.readthedocs.io/en/latest/examples.html?highlight=timeout#aio-thrift-client)

For situations where this is not a case, 
Hyx provides a decorator and a context manager that can help with setting up timeouts.

## Use Case

* Ensure that the caller has to wait no more than a given delay. [Local timeouts](#local-timeouts) work best when limiting action that doesn't touch other microservices.
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
When you request a downstream service with a timeout, there is a possibility that the request will be queued for a while.
Hence, the caller will give up waiting on the timeout and move on handling other requests.

But what will eventually happen with that queued request? 
If not failed on the load balancing level, it will simply be processed when the turn comes to it. 
That will be a waste of resources as the result of the request is not going to be used anyhow. That's a problem.

A common solution is to let all microservices in the request chain know how much time they have to respond. 
If we exceed that limit, microservices can ignore the requests as they are already timed out. 
This is called a distributed timeout (a.k.a. deadlines, timeout budget).

!!! info
    Hyx doesn't yet provide a way to easily add a distributed budget 
    as it will require to integrate with the API framework of your choice. We have [some plans](../roadmap.md) to support that.
    [Let us know](./faq/#missing-a-feature) if this is useful for you.