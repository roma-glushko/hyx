# Cache

## Introduction

Cache pattern is so popular that it doesn't require any introduction. 
Instead of constantly requesting similar information from downstream services or
recalculating it, we could temporarily store it in memory and then retrieve it from there. This is known as read-through cache-aside pattern.

This can help to improve the service latency and significantly lower request rate and corresponding load on downstream services. 

Cache efficiency can be described by comparing transactions that *hit* the cache and those which were *missing*. 
When caching implemented effectively, the major part of transactions are served from the cache.

Cache should be limited in terms of amount of items or space it can span in order to avoid out-of-memory issues in the microservice that uses it.
Usually, cache is bounded by max item number and supports [some eviction policy](#by-eviction) that comes to play when there is no free space left.

Besides that, cache items can have the lifetime they are considered to be actual. After that, items get expired and are being removed from the cache.

Cache can have two types of state:

* [Local In-Memory State](#localin-memory-cache)
* [Distributed State](#distributed-cache)

## Use Cases

* Store information that doesn't change frequently, but needs to be accessed a lot (e.g. some access tokens that lives for hours)
* Store the last response from the downstream service to use in case the service is unavailable (see [fallbacks](fallback.md))
* Reduce load on downstream services by caching their responses for some short time (e.g. user personal information)

## By Eviction

Eviction policy is an important consideration when you choose to implement caching. 
The idea here is to recycle items that have the least impact on cache efficiency (so the hit rate keeps to be high).

### LRU Cache

TBU

## By State

### Local/In-memory Cache

Local cache is the simplest, quickest, database-free form of caching. 

Each microservice instance has its own independent copy of data and some information may repeat across those copies. 
If you redeploy or restart your instances, cache is going to be cleaned, too.

Local caching has a big chance to get inconsistent as peer instance may update the source of truth 
and your local copy should get invalidated or evicted to pull this change.

Unless that's the issue, you should always consider using local cache first. Otherwise, you can try to introduce [distributed caching](#distributed-cache)

### Distributed Cache

Distributed caching is a way to decouple and share cache state from your microservices by storing it in a key-value database (like Redis or Memecache).

Distributed cache solves inconveniences and inconsistency issues of [local caching](#localin-memory-cache) at the expense of blowing off your infrastructural blueprint or adding a new dependency to your microservices.

If that feels like a lot, feel free to begin with [local caching](#localin-memory-cache) and try to overgrow it.

!!! note
    Hyx doesn't support distributed components currently. This may change in [the future](../roadmap.md).

    [Let us know](../../faq/#missing-a-feature) if this is useful for you.


## Best Practices

### Cache Only What You Need

You should not put any unneeded information into your cache. While this may sound obvious, it's frequently overlooked.

For example, if you are obtaining an access token and your response looks like:

```json
{
    "access_token": "AwXce1xSd...Axiop",
    "expires_in": 86400
}
```

Then you probably want to put the `access_token` value only to the cache (instead of caching the whole payload).

This may look like a nit peak, but when you cache hundreds, thousands or millions of items, 
these redundant information adds up into a noticeable overhead.  

### Cache Simple Types Over Complex

The default value type will be a `dict` or some `object` in most cases. 
When you have a few fields to store that maybe be inefficient.

For example, to store a simple `dict` with three keys you need around 230 bytes. 
It's more than 70% more than if you were storing it in tuples:

```python
import sys


sys.getsizeof({
    "id": "63f13528a6ebc96d95d37205",
    "first_name": "John",
    "last_name": "Doe",
})  # 232 bytes

sys.getsizeof((
    "63f13528a6ebc96d95d37205",
    "John",
    "Doe",
))  # 64 bytes
```

The more simple value type (e.g. `strs`, `ints`, `floats`, `tuples`), the less memory it takes to store it.

