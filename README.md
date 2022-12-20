# Hyx

🧘‍♀️Lightweight fault tolerance primitives for your modern Python microservices.

The goal of this library is to provide you with a toolkit that includes common fault tolerance patterns like:

- cache
- retries
- circuit breaker
- bulkhead
- circular buffer
- time limiter

All components are designed to be:

- asyncio-native
- in-memory first
- dependency-less

With that patterns you should be all set to start improving your resiliency right after the library installation.

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