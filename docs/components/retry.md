# Retries

## Introduction

Distributed systems are full of temporary issues: network failures, sudden latency increases,
bandwidth exhaustion, node evictions, partial pod rescheduling, temporary overloading of microservices, etc.
All of these can create situations where your requests may be delayed, queued, or failed.

What can you do in that case? The most natural answer is to **retry your request**.
Hence, retry is the most fundamental, intuitive, and commonly used component in our resilience toolkit.

However, retries may look deceptively simple and straightforward.
The real usage of retries is more nuanced, as you will discover throughout this page.

## Use Cases

- Retries hide temporary, short-lived errors
- Jitters are useful to reduce congestion on resources

## Usage

Hyx provides a decorator that brings retry functionality to any function:

```Python hl_lines="5 8"
{!> ./snippets/retry/retry_basic_usage.py !}
```

::: hyx.retry.retry
    :docstring:

## Backoffs

The backoff strategy is a crucial parameter to consider.
Depending on the backoff, the retry component can either help your system or become a source of problems.

!!! warning
    For the sake of simplicity, Hyx assumes that you are following AsyncIO best practices and not running CPU-intensive operations in the main thread.
    Otherwise, the backoff delays may fire later after the thread is unblocked.

### Constant Backoff

The most basic backoff strategy is to wait a constant amount of time on each retry.

```Python hl_lines="8"
{!> ./snippets/retry/retry_backoff_const.py !}
```

The `float` backoffs are just aliases for the `const` backoff.

::: hyx.retry.backoffs.const
    :docstring:

### Interval Backoff

You can also provide a list or tuple of floats to pull delays from in a sequential and <abbr title="starts taking delays from the beginning of the list if attempts exceed the number of delays in the list">cyclical</abbr> manner.

```Python hl_lines="8"
{!> ./snippets/retry/retry_backoff_const_intervals.py !}
```

The `list[float]` and `tuple[float, ...]` backoffs are just aliases for the `interval` backoff.

::: hyx.retry.backoffs.interval
    :docstring:

### Exponential Backoff

Exponential backoff is one of the most popular backoff strategies.
Its delays grow rapidly, giving the faulty functionality more and more time to recover on each retry.

Hyx implements Capped Exponential Backoff, which allows you to specify a `max_delay_secs` bound:

```Python hl_lines="9"
{!> ./snippets/retry/retry_backoff_expo.py !}
```

::: hyx.retry.backoffs.expo
    :docstring:

### Linear Backoff

Linear Backoff grows linearly by adding `additive_secs` on each retry:

```Python hl_lines="9"
{!> ./snippets/retry/retry_backoff_linear.py !}
```

::: hyx.retry.backoffs.linear
    :docstring:

### Fibonacci Backoff

Another rapidly growing backoff is based on the Fibonacci sequence:

```Python hl_lines="9"
{!> ./snippets/retry/retry_backoff_fibo.py !}
```

::: hyx.retry.backoffs.fibo
    :docstring:

### Decorrelated Exponential Backoff

This is a complex backoff strategy proposed by [AWS Research](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/).
It's based on [exponential backoff](#exponential-backoff) and includes [full jitter](#full-jitter).
On every retry, it exponentially widens the range of possible delays.

```Python hl_lines="9"
{!> ./snippets/retry/retry_backoff_decorrexp.py !}
```

::: hyx.retry.backoffs.decorrexp
    :docstring:

### Soft Exponential Backoff (Beta)

Soft Exponential Backoff is another variation of complex exponential backoffs with built-in [jitter](#jitters).
It was authored by [the Polly community](https://github.com/App-vNext/Polly/issues/530) as a less spiky alternative to
[Decorrelated Exponential Backoff](#decorrelated-exponential-backoff).

```Python hl_lines="9"
{!> ./snippets/retry/retry_backoff_softexp.py !}
```

::: hyx.retry.backoffs.softexp
    :docstring:

### Custom Backoffs

In Hyx's design, backoffs are simply iterators that return float numbers and can continue indefinitely.

Here is how a factorial backoff could be implemented:

```Python hl_lines="10-34 37"
{!> ./snippets/retry/retry_backoff_custom.py !}
```

!!! note
    The built-in backoffs accept delay parameters in seconds but work with milliseconds internally.
    This improves the granularity of generated delays.
    The delays are then returned in seconds.

## Jitters

In high-load setups, or when multiple requesters are trying to access the same API, or with a set of background tasks running on a schedule,
situations may arise where **they happen to perform actions simultaneously**.
This triggers traffic spikes or unusually high load on the backend system.
When you use retries across multiple clients, they can trigger load spikes in the same way.

This may push your system to autoscale unnecessarily.

In such cases, we say the requests are **correlated**.

To mitigate this problem, we can use jitters, which essentially **decorrelate your requests by adding randomness**.
This helps distribute load more evenly and process the same volume of requests with less capacity.

In Hyx's design, jitters are part of the backoff strategy.

!!! note
    [Constant](#constant-backoff), [exponential](#exponential-backoff), [linear](#linear-backoff), and [fibonacci](#fibonacci-backoff) backoffs support
    the jitters listed below as an optional argument.

### Full Jitter

Full Jitter is a decorrelation strategy proposed by [AWS Research](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/).

It uniformly selects a delay from the range between zero and your upper bound:

```Python hl_lines="9"
{!> ./snippets/retry/retry_backoff_expo_jitter.py !}
```

!!! note
    Full jitter may choose to perform the action immediately without any delay.

::: hyx.retry.jitters.full
    :docstring:

### Equal Jitter

Another jitter algorithm proposed by [AWS Research](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/).

It takes the middle of the given interval and adds some additional delay, drawn uniformly at random from the halved interval.

!!! note
    Equal Jitter guarantees that you will wait at least half of the given delay interval.

::: hyx.retry.jitters.equal
    :docstring:

### Jittered Backoffs

[Decorrelated Exponential](#decorrelated-exponential-backoff) and [Soft Exponential](#soft-exponential-backoff-beta) backoffs
provide built-in decorrelation as part of their algorithm.

### Custom Jitters

Hyx uses jitters as part of backoff strategies.
Jitters are callables that take a delay in milliseconds generated by the backoff and return the final delay in milliseconds.

!!! note
    Jitters can modify the final delay returned by the backoff algorithm.

```Python hl_lines="11-16 19"
{!> ./snippets/retry/retry_backoff_custom_jitter.py !}
```

## Backoffs Outside Retries

Backoffs and jitters can be useful even outside of retries.

### Worker Pools

In the following example, we create a pool of in-process workers.
If there were no delays between their scheduling, they would start almost instantaneously
and compete with each other when pulling tasks from the database.

To avoid this, we introduce a small jitter that decorrelates their startup times:

```Python hl_lines="12 24"
{!> ./snippets/retry/jitter_out_retries.py !}
```

Additionally, we jitter each worker's rest time, increasing the chances that their lifecycles end up being different.

## Best Practices

### Limit Retry Attempts

Hyx supports an option to retry infinitely, but this should generally be considered **an antipattern**.

```Python hl_lines="10"
{!> ./snippets/retry/retry_infinite_attempts.py !}
```

Always prefer limiting the number of retries over infinite attempts.

### Specify Delays

You can disable delays between retries, but that's **another antipattern** you should avoid:

```Python hl_lines="11"
{!> ./snippets/retry/retry_no_delays.py !}
```

Without delays, retries can easily overwhelm your system and create a situation known as [the retry storm](#avoid-retry-storms).

### When and What to Retry

It's important to realize that not every action should be retried.
When dealing with non-idempotent APIs, retrying can introduce duplicate entries in the system.

When it comes to HTTP requests, you should retry based on server response errors and consider error codes that
are temporary in nature (e.g., 5xx errors).

### Avoid Retry Storms

The retry storm is a well-known issue that occurs when retries are poorly configured or placed in the wrong part of the system.

Excessive retries can overload parts of your system and bring it down.
The two antipatterns above are common ways to misconfigure retries.
That's why you should always limit the number of retry attempts and allow time between retries for the downstream system to recover.

The placement of retries is equally important for avoiding retry storms. Consider the following case:

<figure markdown>
  ![Image title](../img/retry/retry-storm.svg){ loading=lazy, align=center }
  <figcaption>A system with retries configured on multiple levels</figcaption>
</figure>

This system has retries configured at two levels: `gateway` (level 1) and `orders` microservice (level 2).
If the `inventory` microservice fails,
it will first exhaust all retries on the `orders` side, then return to the `gateway`.
The `gateway` will then retry two more times.

The total number of requests to the `inventory` microservice will be 3 * 3 = 9.
If there were a deeper request chain with more retries along the way,
they would all multiply and create even worse load on the system.

The general rule of thumb is to retry only in the component directly above the failed one.
In this case, it would be appropriate to retry only at the `orders` level.
