<p align="center">
  <img loading="lazy" src="https://raw.githubusercontent.com/roma-glushko/hyx/main/img/hyx-logo.png" alt="Hyx">
</p>
<p align="center">
    <em>🧘‍♂️️Lightweight fault tolerance primitives for your resilient and modern Python microservices</em>
</p>
<p align="center">
<a href="https://pypi.org/project/hyx" target="_blank">
    <img loading="lazy" src="https://img.shields.io/pypi/v/hyx?color=%2318afba&label=pypi%20package" alt="Package Version">
</a>
<a href="https://pypi.org/project/hyx" target="_blank">
    <img loading="lazy" src="https://img.shields.io/pypi/dm/hyx?color=%2318afba" alt="Downloads">
</a>
<a href="https://pypi.org/project/hyx" target="_blank">
  <img loading="lazy" src="https://img.shields.io/pypi/pyversions/hyx.svg?color=%2318afba" alt="Supported Python Versions">
</a>

<a href="https://discord.gg/EUt2P9jrU7" target="_blank">
    <img alt="Discord" src="https://img.shields.io/discord/1124268798699118633?label=discord">
</a>

<br/>

<a href="https://hyx.readthedocs.io/en/latest/?badge=latest">
    <img loading="lazy" src="https://readthedocs.org/projects/hyx/badge/?version=latest&color=%2318afba" alt='Documentation Status' />
</a>
  
<a href="https://github.com/roma-glushko/hyx/actions/workflows/tests.yml">
    <img loading="lazy" src="https://github.com/roma-glushko/hyx/actions/workflows/tests.yml/badge.svg?branch=main" alt='Test Status' />
</a>

<a href="https://app.codecov.io/github/roma-glushko/hyx">
    <img loading="lazy" src="https://img.shields.io/codecov/c/gh/roma-glushko/hyx" alt="Coverage" />
</a>

</p>

---

**Hyx** (/ˈhʌɪx/) is a set of well-known stability patterns that are commonly needed
when you build [microservice-based](https://en.wikipedia.org/wiki/Microservices) applications.
Hyx is meant to be [Hystrix (Java)](https://github.com/Netflix/Hystrix), [resilience4j (Java)](https://github.com/resilience4j/resilience4j) or [Polly (C#)](https://github.com/App-vNext/Polly) but for the Python world.

## Key Features

- Implements five commonly used resiliency patterns with various configurations based on advice and experience of industry leaders (e.g. AWS, Google, Netflix)
- Idiomatic Pythonic implementation based on [decorators](https://realpython.com/primer-on-python-decorators) and [context managers](https://realpython.com/python-with-statement)
- [AsyncIO](https://docs.python.org/3/library/asyncio.html) Native Implementation
- Lightweight. Readable Codebase. High Test Coverage

## Requirements

- Python 3.9+
- AsyncIO-powered applications ([no sync support?](https://hyx.readthedocs.io/en/latest/faq/#no-sync-support))

## Installation

Hyx can be installed from [PyPi](https://pypi.org/project/hyx):

```sh
pip install hyx

# or via uv
uv add hyx
```

## Component Map
| Component         | Problem                                                                                                                                                                            | Solution                                                                                                                                                                      | Implemented? |
|-------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------|
| 🔁 Retry           | Failures happen sometimes, but they self-recover after a short time                                                                                                                | Automatically retry operations on temporary failures                                                                                                                          | ✅            |
| 💾 Cache           |                                                                                                                                                                                    |                                                                                                                                                                               |              |
| ⚡️ Circuit Breaker | When downstream microservices become overloaded, sending even more load only makes things worse                                                                                    | Temporarily stop sending requests to failing microservices when error thresholds are exceeded. Then check if the pause helped them recover                                    | ✅            |
| ⏱ Timeout         | Sometimes operations take too long. We can't wait forever, and after a certain point success becomes unlikely                                                                      | Bound waiting to a reasonable amount of time                                                                                                                                  | ✅            |
| 🚰 Bulkhead        | Without limits, some code can consume too many resources, bringing down the whole application (and upstream services) or slowing down other parts                                  | Limit the number of concurrent calls, queue excess calls, and fail calls that exceed capacity                                                                                 | ✅            |
| 🏃‍♂️ Rate Limiter   | A microservice can be called at any rate, including one that could bring it down if triggered accidentally                                                                         | Limit the rate at which your system can be accessed                                                                                                                           | ✅            |
| 🤝 Fallback        | Nothing guarantees that your dependencies will work. What do you do when they fail?                                                                                                | Degrade gracefully by providing default values or placeholders when dependencies are down                                                                                     | ✅            |

<p align="right">
Inspired by <a href="https://github.com/App-vNext/Polly#resilience-policies" target="_blank">Polly's Resiliency Policies</a>
</p>

## Acknowledgements

- [resilience4j/resilience4j](https://github.com/resilience4j/resilience4j)
- [Netflix/Hystrix](https://github.com/Netflix/Hystrix)
- [slok/goresilience](https://github.com/slok/goresilience)
- [App-vNext/Polly](https://github.com/App-vNext/Polly)
- [Diplomatiq/resily](https://github.com/Diplomatiq/resily)
