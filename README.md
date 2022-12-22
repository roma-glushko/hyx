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

<a href="https://hyx.readthedocs.io/en/latest/?badge=latest">
    <img loading="lazy" src="https://readthedocs.org/projects/hyx/badge/?version=latest&color=%2318afba" alt='Documentation Status' />
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
- AsyncIO-powered applications ([no sync support?](./faq.md))

## Installation

Hyx can be installed from [PyPi](https://pypi.org/project/hyx):

``` sh
pip install hyx

# or via poetry
poetry add hyx
```

## Component Map

|     Component     | Problem                                                                                                                                                                            | Solution                                                                                                                                                                      | Implemented? |
|:-----------------:|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------|
|      🔁 Retry      | The failures happen sometimes, but they self-recover after a short time                                                                                                            | Automatically retry operation on temporary failures                                                                                                                           | ✅            |
|      💾 Cache      |                                                                                                                                                                                    |                                                                                                                                                                               |              |
| ⚡️ Circuit Breaker | When downstream microservices have got overloaded, sending even more load can make the situation only worse.                                                                       | Stop doing requests to your failing microservice temporarily if amount of errors exceeded expected thresholds. Then see if the given time helped the microservice to recover  | ✅            |
|     ⏱ Timeout     | Sometimes operations may take too much time. We cannot wait that long or after that time the success is unlikely                                                                   | Bound waiting to a reasonable amount of time                                                                                                                                  | ✅            |
|    🚰 Bulkhead     | If executed without control, some code can take too much resources and put down the whole application (and upstream services) or cause slowness of other places of the application | Fix the amount of calls to the code, queue other calls and fail calls that goes beyond your capacity                                                                          | ✅            |
|  🏃‍♂️ Rate Limiter  |                                                                                                                                                                                    |                                                                                                                                                                               |              |
|    🤝 Fallback     | Nothing can guarantee you that your dependencies will work. What would you do when it's failing?                                                                                   | Degrade gracefully by defining some default values or placeholders if your dependencies are down                                                                              | ✅            |

<p align="right">
Inspired by <a href="https://github.com/App-vNext/Polly#resilience-policies" target="_blank">Polly's Resiliency Policies</a>
</p>

## Acknowledgements

- [resilience4j/resilience4j](https://github.com/resilience4j/resilience4j)
- [Netflix/Hystrix](https://github.com/Netflix/Hystrix)
- [slok/goresilience](https://github.com/slok/goresilience)
- [App-vNext/Polly](https://github.com/App-vNext/Polly)
- [Diplomatiq/resily](https://github.com/Diplomatiq/resily)
