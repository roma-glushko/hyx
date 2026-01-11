# Fallbacks

## Introduction

When your downstream microservices fall apart, [retries](retry.md) are exhausted, or [circuit breakers](circuit_breakers.md) open,
you need a solid plan B to cover this failure for upstream microservices.
Otherwise, the entire request chain would fail in a cascading fashion all the way up.

This plan B is typically called a fallback,
and it comes in different forms depending on the context and functionality required.

## Use Cases

* Show a default or cached value if the downstream dependency is not responding (e.g., show a placeholder instead of the user's actual avatar)
* Log and silence the exception (e.g., if the message broker is not responding and you can afford to miss the message)
* Use functional redundancy in case of failure (e.g., request currency rates from another provider if the primary one is down)

## Usage

```Python hl_lines="4 8 15"
{!> ./snippets/fallback/fallback_decorator.py !}
```

::: hyx.fallback.fallback
    :docstring:
