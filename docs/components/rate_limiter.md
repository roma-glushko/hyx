# Rate Limiters

## Introduction

Rate limiting is a way to keep the <abbr title="amount of requests per time window">request rate</abbr>
at a level that can be sustainably served by your microservice or system as a whole.

Rate limiting can be applied at:

* Server-side level
* Client-side level

Rate limiters can be classified in various ways. For example, by rate type, rate limiters can be divided into:

* [Static Rate Limiters](#static-rate-limiters)
* [Dynamic Rate Limiters](#dynamic-rate-limiters)

By state, rate limiters can be grouped as:

* [Local (In-Memory) Rate Limiters](#localin-memory-rate-limiters)
* [Distributed Rate Limiters](#distributed-rate-limiters)

## Use Cases

* Protect the entire system from DoS attacks by limiting the rate of incoming requests to public APIs in a <abbr title="a component, microservice, or proxy that sits in front of all microservice APIs">Gateway</abbr>
* Limit the rate of requests to external APIs or legacy systems on the client side
* Apply rate limiting to private APIs to avoid friendly-fire DoS from misbehaving peer microservices
* Ensure fair distribution of resources among API users

## By Rate

### Static Rate Limiters

With static rate limiters, you define the rate explicitly during configuration (e.g., 100 req/sec).
The limiters then employ various algorithms to count and enforce those limits.

The rate value is usually determined through load testing of the microservice.

#### Token Bucket Rate Limiter

This rate limiter is based on the token bucket algorithm.
In this approach, we have a bucket containing tokens.
If the bucket has tokens available, a new request takes one to pass through.
Otherwise, the request fails due to reaching the limit.

The bucket is replenished with new tokens at a constant rate equal to `1/request rate`.

=== "decorator"

    ```Python hl_lines="1 6"
    {!> ./snippets/ratelimiter/ratelimiter_decorator.py !}
    ```

=== "context manager"

    ```Python hl_lines="1 4 12"
    {!> ./snippets/ratelimiter/ratelimiter_context.py !}
    ```

::: hyx.ratelimit.tokenbucket
    :docstring:

### Dynamic Rate Limiters

Determining a static rate can be resource-intensive, and the value may become stale quickly (e.g., new versions of a microservice may process requests more slowly).
When the rate value becomes outdated, you risk underutilizing your resources or making rate limiting ineffective.

The good news is that often you don't need to know the exact rate value.
All you need is to ensure that microservices utilize all available resources by controlling concurrency levels while shedding excessive load.

In this situation, you can apply Adaptive Request Concurrency (a dynamic form of [bulkhead](./bulkhead.md#adaptive-limiting)).

## By State

### Local/In-memory Rate Limiters

The simplest form of rate limiting state is stored in-memory.
In this case, each instance of a microservice maintains its own local state of requests served within a time window.

This is a simple, straightforward, database-free and dependency-free way to quickly introduce rate limiting.
However, that simplicity comes with the following trade-offs.

As you scale up the number of microservice instances, the effective rate limit grows proportionally.
For example, if you've configured a limit of 10 req/sec for one microservice instance, then:

* 1 instance handles 10 req/sec
* 2 instances handle 20 req/sec
* 10 instances handle 100 req/sec

This may seem odd, but it's still useful and efficient since you don't need an external database
to store state, and you ensure that each individual instance won't be overloaded.

Another issue with this approach is that you lose state when instances are redeployed.

If this behavior is unintended, or you have a well-defined SLA for your request rate,
you should consider [distributed rate limiters](#distributed-rate-limiters).

!!! note
    This is the only type of state that Hyx currently supports. [Let us know](../faq.md#missing-a-feature) if this is useful for you.

### Distributed Rate Limiters

In distributed rate limiting, state is stored outside the components that enforce rate limits.
This allows you to maintain the desired request rate regardless of the number of microservice instances or their redeployment.

The drawback is that you need a database to store state. Key-value databases (like Redis or Memcached)
are typically the best choices for this type of workload.

Having a database dependency is a reasonable overhead if you need to enforce an SLA around API request rates.
Otherwise, if you don't have strong reasons for introducing a database, consider using [local rate limiters](#localin-memory-rate-limiters).

!!! note
    Hyx doesn't currently support distributed components. This may change in [the future](../roadmap.md).

    [Let us know](../faq.md#missing-a-feature) if this is useful for you.

## Best Practices

### Shard Rate Limits

Rate limiting rarely makes sense at the global level,
where all requests would fall under the same limit.

In practice, it makes sense to shard rate limits at different levels.
For example, rate limits are often sharded by `user_id`, so each user has their own rate quota.

Another popular way to shard limits is by request routes.
Rate sharding can help prioritize and separate traffic that a microservice handles.

A similar approach is to shard based on read/write operations or by more versus less resource-consuming APIs.

This can be seen as a form of [bulkhead](./bulkhead.md).

### Rate Limit Public APIs

Public APIs are parts of the system exposed to traffic sources outside your cluster, such as UI applications, SDKs, etc.
This type of API is usually the most heavily loaded, and under the hood, these requests trigger calls to other components.

If public APIs have no rate limiting, that's the easiest way to bring your system down,
trigger unnecessary cluster scaling, and disturb other users when one user manages to generate more traffic than you'd expect.

Hence, the common advice is to rate limit your public APIs by placing some sort of gateway in front of them.

If you're not monetizing your API (like Twitter, Meta, or Stripe do) and don't have an SLA for request rates,
you can apply simple [local rate limiting](#localin-memory-rate-limiters).

Otherwise, you should prefer [distributed rate limiting](#distributed-rate-limiters).
