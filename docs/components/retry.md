# Retry

## Introduction

Distributed systems are full of temporary issues - network failures, sudden latency increases, 
bandwidth exhaustion, node evictions and partial pods rescheduling, temporary overloading of some microservices, etc. 
All of that can create situations when your requests maybe delayed, queued or failed. 

What can you do in that case? The most natural answer is to **retry your request**. 
Hence, retry is the most fundamental, intuitive and commonly used component in our resilience toolkit.

However, retries might look deceptively simple and straightforward, the real usage of retries are more nuanced.

## Usage

Hyx provides a decorator that brings retry functionality to any function:

```Python hl_lines="4 7"
{!> ./snippets/retry_basic_usage.py !}
```

::: hyx.retry.retry
    :docstring:

## Backoffs

The backoff strategy is a crucial parameter to consider. 
Depending on the backoff, retry component can help your system or be a source of problems.

### Constant Backoff

The most basic backoff strategy is to wait the constant amount of time on each retry.

```Python hl_lines="7"
{!> ./snippets/retry_backoff_const.py !}
```

If you pass a list of delays, then it will pull delays from it <abbr title="starts taking delays from the beggining of the list if attemps are more than delays in the list">cyclically</abbr>.

```Python hl_lines="7"
{!> ./snippets/retry_backoff_const_intervals.py !}
```

The `float` or `list[float]` backoffs are just aliases for the `const` backoff.

::: hyx.retry.backoffs.const
    :docstring:

### Exponential Backoff

Exponential backoff is one of the most popular backoff strategies. 
It produces delays that growth rapidly. That gives the faulty functionality more and more time to recover on each retry.

Hyx implements the Capped Exponential Backoff that allows to specify the `max_delay_secs` bound:

```Python hl_lines="8"
{!> ./snippets/retry_backoff_expo.py !}
```

::: hyx.retry.backoffs.expo
    :docstring:

### Linear Backoff

Linear Backoff growth linearly by adding `additive_secs` on each retry:

```Python hl_lines="8"
{!> ./snippets/retry_backoff_linear.py !}
```

::: hyx.retry.backoffs.linear
    :docstring:

### Fibonacci Backoff

Another rapidly growing backoff is based on the Fibonacci sequence:

```Python hl_lines="8"
{!> ./snippets/retry_backoff_fibo.py !}
```

::: hyx.retry.backoffs.fibo
    :docstring:

### Decorrelated Exponential Backoff

This is a complex backoff strategy proposed by [AWS Research](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/).
It's based on [the exponential backoff](#exponential-backoff) and includes [the full jitter](#full-jitter). 
On every retry, it exponentially widens the range of possible delays.

```Python hl_lines="8"
{!> ./snippets/retry_backoff_decorrexp.py !}
```

::: hyx.retry.backoffs.decorrexp
    :docstring:

### Soft Exponential Backoff (Beta)

Soft Exponential Backoff is another variation of complex exponential backoffs with built-in [jitter](#jitters). 
It was authored by [the Polly community](https://github.com/App-vNext/Polly/issues/530) as a less spiky alternative to 
[Decorrelated Exponential Backoff](#decorrelated-exponential-backoff).

```Python hl_lines="8"
{!> ./snippets/retry_backoff_softexp.py !}
```

### Custom Backoffs

## Jitters

In the high-loaded setups, or when a few requesters that are trying to pull the same API, or just a set of background tasks that do something on schedule,
there may be situations when **they happen to do that action simultaneously**. 
That triggers traffic spikes or unusually high load on the backend system. 
When you use retries in a few clients, they may trigger the load spikes in the same way.

It may push your system to autoscale without many reasons that is not super efficient. 

In that case, we say that the requests were **correlated**. 

In order to mitigate this problem, we can use jitters which is essentially a way to **decorrelated your requests by adding some randomness**. 

!!! note
    [Constant](#constant-backoff), [exponential](#exponential-backoff), [linear](#linear-backoff) and [fibonacci](#fibonacci-backoff) backoffs supports
    jitters listed below as an optional argument.

### Full Jitter

Full Jitter is a decorrelation strategy proposed by [AWS Research](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/).

It takes a delay from the range between zero and your upper bound uniformly:

```Python hl_lines="9"
{!> ./snippets/retry_backoff_expo_jitter.py !}
```

!!! note
    Full jitter may decide to do the action right away without a delay

::: hyx.retry.jitters.full
    :docstring:

### Equal Jitter

Another jitter algorithm proposed by [AWS Research](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/).

It takes a middle of the given interval and tries to add some additional delay drawing it from the halved interval at random uniformly.

!!! note
    Equal Jitter guarantees that you will wait at least a half of given delay interval.

::: hyx.retry.jitters.equal
    :docstring:

### Jittered Backoffs

[Decorrelated Exponential](#decorrelated-exponential-backoff) and [Soft Exponential](#soft-exponential-backoff) backoffs 
provide built-in decorrelation as a part of their algorithm.

### Custom Jitters

TBU

## Backoffs Outside Retries

Backoffs and Jitters can be useful even outside of retries.

## Gotchas

### Infinite Retries

TBU

### Retry Storms

TBU