<p align="center">
  <img src="https://raw.githubusercontent.com/roma-glushko/hyx/main/img/hyx-logo.png" alt="Hyx">
</p>
<p align="center">
    <em>🧘‍♂️️Lightweight fault tolerance primitives for your resilient and modern Python microservices</em>
</p>
<p align="center">
<a href="https://pypi.org/project/hyx" target="_blank">
    <img src="https://img.shields.io/pypi/v/hyx?color=%2318afba&label=pypi%20package" alt="Package Version">
</a>
<a href="https://pypi.org/project/hyx" target="_blank">
    <img src="https://img.shields.io/pypi/dm/hyx?color=%2318afba" alt="Downloads">
</a>
<a href="https://pypi.org/project/hyx" target="_blank">
  <img src="https://img.shields.io/pypi/pyversions/hyx.svg?color=%2318afba" alt="Supported Python Versions">
</a>
</p>

---

Hyx provides you with a toolkit that includes common fault tolerance patterns like:

- bulkhead
- cache
- circuit breaker
- circular buffer
- fallback
- rate limiter
- retries
- timeout / time limiter

All components are designed to be:

- asyncio-native
- in-memory first
- dependency-less

With that patterns you should be all set to start improving your resiliency right after the library installation.

## Component Map

TBU

## Implementation Plan

- [ ] cache
- [x] retry
- [x] bulkhead
- [ ] circuit breaker
- [ ] circular buffer
- [x] time limiter

## Acknowledgements

- [resilience4j/resilience4j](https://github.com/resilience4j/resilience4j)
- [Netflix/Hystrix](https://github.com/Netflix/Hystrix)
- [slok/goresilience](https://github.com/slok/goresilience)
- [App-vNext/Polly](https://github.com/App-vNext/Polly)
- [Diplomatiq/resily](https://github.com/Diplomatiq/resily)
