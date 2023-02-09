# Rate Limiters

## Introduction

Rate limiting is a way to keep <abbr title="amount of request per time window">request rate</abbr> 
on the level that can be served sustainably by your microservice or system as a whole.

Rate limiting can be applied on:

* Server-side level
* Client-side level

Rate limiter can be classified in various ways. For example, by rate type, rate limiter can be divided into:

* [Static Rate Limiters](#static-rate-limiters)
* [Dynamic Rate Limiters](#dynamic-rate-limiters)

By state rate limiter can be grouped as:

* [Local (In-Memory) Rate Limiters](#localin-memory-rate-limiters)
* [Distributed Rate Limiters](#distributed-rate-limiters)

## Use Cases

* Protect the whole system from DoS by limiting rate of incoming requests to public API in <abbr title="a component, microservice or proxy that sits in front of all microservice API">Gateway</abbr>.
* Limit rate of requesting of external API or legacy systems on the client side
* Apply rate limiting in private API to avoid friendly-fire DoS by misbehaving peer microservices
* Ensure fair distribution of resources between API users

## By Rate

### Static Rate Limiters

In static rate limiters, you define the rate explicitly during the rate limiter configuration (e.g. 100 req/sec). 
Then limiters employ disparate algorithms to count and enforce that limits.

The rate value is usually determined by load testing of the microservice.

#### Token Bucket Rate Limiter

This rate limiter is based on the token bucket algorithm. 
In this approach, we have a notion of a bucket with tokens. 
If the bucket has some tokens, a new request takes one out to come through.
Otherwise, the request fails due reaching the limit.

The bucket gets replenished with new tokens with a constant rate that is equal to `1/request rate`.

=== "decorator"

    ```Python hl_lines="1 7"
    {!> ./snippets/ratelimiter/ratelimiter_decorator.py !}
    ```

=== "context manager"

    ```Python hl_lines="1 4 12"
    {!> ./snippets/ratelimiter/ratelimiter_context.py !}
    ```

::: hyx.ratelimit.tokenbucket
    :docstring:

### Dynamic Rate Limiters

The static rate can be resource consuming to determine as well as it may get stale very quickly (e.g. new versions of a microservice can make it slower to process requests).
When the rate value gets inappropriate, you are at risk of underutilizing your resources or making rate limiting inefficient.

The good news is that often you don't even need to know the exact rate value.

All you need is to make sure that microservices are utilizing all resources they have while shedding excessive load.

In this situation, you can apply Adaptive Request Concurrency (a dynamic form of [bulkhead](./bulkhead.md)).

!!! note
    Hyx doesn't provide ARC implementation at this moment. [Let us know](../../faq/#missing-a-feature) if this is useful for you.

## By State

### Local/In-memory Rate Limiters

The simplest form of the rate limiting state is a state stored in-memory. 
In this case, all instances of a microservice will have an own local state of requests served in a time window.

This is a simple, straightforward, database- and dependency less way to quickly introduce rate limiting. 
At the same, that simplicity comes with the following specifics.

As you scale microservice instance number up, the allowed rate limiting effectively grow as well. 
For example, if you have specified to handle 10 req/sec for one microservice instance, then:

* 1 instance handles 10 req/sec
* 2 instances handle 20 req/sec
* 10 instances handle 100 req/sec

This may look odd, but it's still useful and efficient as you don't need to introduce an external database 
to store your state, and you ensure that each particular instance is not going to be overloaded.

Another issue with this approach is that you miss the state on instance redeploying.

If this behavior is not intended, or you have a well-specified SLA on your request rate, 
you should look at more [complex distributed state](#distributed-rate-limiters).

!!! note
    This is the only type of state that Hyx is supporting at the moment. [Let us know](../../faq/#missing-a-feature) if this is useful for you.

### Distributed Rate Limiters

In distributed rate limiting, we store state outside the components that check for rate limiting. 
In this case, you can maintain the needed request rate despite microservice instance number or their redeployment.

The drawback here is that you need a database to store your state in. Usually, key-value databases (like Redis or Memcache) 
are the best choices for this type of work.

Having a database as a dependency is a reasonable overhead if you need to enforce some SLA around API request rate. 
Otherwise, if you don't have strong statements in favor of introducing a database, consider using [the local rate limiters](#localin-memory-rate-limiters).

!!! note
    Hyx doesn't support distributed components currently. This may change in [the future](../roadmap.md). 

    [Let us know](../../faq/#missing-a-feature) if this is useful for you.

## Best Practices

### Shard Rate Limits

Rate limiting rarely makes sense to apply on the global level. 
In that case, all requests would fall under the same shard.

In practice, it makes sense to shard rate limits on different levels.
For example, rate limits are often sharded by `user_id`, so each user has own rate quote.

Another popular way to shard limits is based on request routes. 
In this case, rate sharding can help to prioritize and separate traffic that microservice handles. 

A similar way to shard is based on read/write operations or based on more/less resource-consuming API

This can be seen as a some form of [bulkhead](./bulkhead.md).

### Rate Limit Public API

Public API is part of the system that are exposed to traffic sources outside your cluster like UI application, SDKs, etc.
This type of API is usually the most loaded and under the hood they trigger requests to other components.

If Public API has no rate limiting, this is the number one way to put your system down, 
trigger unneeded cluster scaling and disturb other users by having one that somehow managed to generate more traffic that you would imagine.

Hence, the common advice is to rate limit your Public API by having some sort of gateway in front of them.

If you are not selling your API (like Twitter, Meta or Stripe do) and you don't have some SLA on the request rate, 
you can apply a simple [local rate limiting](#localin-memory-rate-limiters).

Otherwise, you should prefer using [distributed rate limiting](#distributed-rate-limiters).
