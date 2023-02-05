# Fallbacks

## Introduction

When your downstream microservices fall apart, [retries](retry.md) exceed or [breakers](circuit_breakers.md) fire on, 
you need to have a solid plan B that will cover this failure up for the upstream microservices. 
Otherwise, the whole request chain would fail in a cascading fashion all the way up. 

This plan B is normally called a fallback, 
and it comes in different forms depending on the context and functionality to fill.

## Use Cases

* Show a default or cached value if the downstream dependency is not responding (e.g. show a placeholder instead of the actual user's avatar)
* Log and silence the exception (e.g. if the message broker is not responding, and you can miss the message)
* Use some functional redundancy in a case of failure (e.g. request currency rates from another provider if the primary one is down)

## Usage

```Python hl_lines="4 8 15"
{!> ./snippets/fallback/fallback_decorator.py !}
```

::: hyx.fallback.fallback
    :docstring: