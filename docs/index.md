---
hide:
  - feedback
---

# Hyx

<p align="center">
  <a href="https://github.com/roma-glushko/hyx" target="_blank">
    <img loading="lazy" src="https://raw.githubusercontent.com/roma-glushko/hyx/main/img/hyx-logo.png" alt="Hyx">
  </a>
</p>
<p align="center">
    <em>🧘‍♂️️ Lightweight fault tolerance primitives for your resilient and modern Python microservices</em>
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
</p>

---

**Hyx** (/ˈhʌɪx/) is a set of well-known stability patterns that are commonly needed
when you build [microservice-based](https://en.wikipedia.org/wiki/Microservices) applications.
Hyx is meant to be [Hystrix (Java)](https://github.com/Netflix/Hystrix), [resilience4j (Java)](https://github.com/resilience4j/resilience4j) or [Polly (C#)](https://github.com/App-vNext/Polly) but for the Python world.

!!! note

    This project is under active development and testing in production. Your feedback and help are highly appreciated!

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

=== "pip"

    ``` sh
    pip install hyx
    ```

=== "poetry"

    ``` sh
    poetry add hyx
    ```

## Components

Here is a short overview of Hyx's components:

| Component         | Problem                                                                                                                                                                            | Solution                                                                                                                                                                      | Implemented? |
|-------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------|
| 🔁 Retry           | The failures happen sometimes, but they self-recover after a short time                                                                                                            | Automatically retry operation on temporary failures                                                                                                                           | ✅            |
| 💾 Cache           |                                                                                                                                                                                    |                                                                                                                                                                               |              |
| ⚡️ Circuit Breaker | When downstream microservices have got overloaded, sending even more load can make the situation only worse.                                                                       | Stop doing requests to your failing microservice temporarily if amount of errors exceeded expected thresholds. Then see if the given time helped the microservice to recover  | ✅            |
| ⏱ Timeout         | Sometimes operations may take too much time. We cannot wait that long or after that time the success is unlikely                                                                   | Bound waiting to a reasonable amount of time                                                                                                                                  | ✅            |
| 🚰 Bulkhead        | If executed without control, some code can take too much resources and put down the whole application (and upstream services) or cause slowness of other places of the application | Fix the amount of calls to the code, queue other calls and fail calls that goes beyond your capacity                                                                          | ✅            |
| 🏃‍♂️ Rate Limiter   | The microservice can be requested with any rate even one that can put it down if happens by accident                                                                               | Limit the rate your system can be accessed by                                                                                                                                 | ✅            |
| 🤝 Fallback        | Nothing can guarantee you that your dependencies will work. What would you do when it's failing?                                                                                   | Degrade gracefully by defining some default values or placeholders if your dependencies are down                                                                              | ✅            |

<p align="right">
    Inspired by <a href="https://github.com/App-vNext/Polly#resilience-policies" target="_blank">Polly's Resiliency Policies</a>
</p>

## Thanks

!!! quote

    We are staying on the shoulders of giants (c)

There are some open source projects and other resources that heavily influenced and inspired Hyx to emerge.
Without those projects and people behind them, Hyx wouldn't have been created. 
So I wanted to pause for a moment to say a huge thanks wholeheartedly :heart: to:

- [App-vNext/Polly](https://github.com/App-vNext/Polly)
- [resilience4j/resilience4j](https://github.com/resilience4j/resilience4j)
- and tons of other projects previously published on the similar topics

## License

This project is licensed under the terms of the [Apache 2.0 license](https://github.com/roma-glushko/hyx/blob/main/LICENSE).
