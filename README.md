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

| Component         | Problem                                                                                                                                                                            | Solution                                                                                                                                                                      | Implemented? |
|-------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------|
| 🔁 Retry           | The failures happen sometimes, but they self-recover after a short time                                                                                                            | Automatically retry operation on temporary failures                                                                                                                           | ✅            |
| 💾 Cache           |                                                                                                                                                                                    |                                                                                                                                                                               |              |
| ⚡️ Circuit Breaker | When downstream microservices have got overloaded, sending even more load can make the situation only worse.                                                                       | Stop doing requests to your failing microservice temporarily if amount of errors exceeded expected thresholds. Then see if the given time helped the microservice to recover  | ✅            |
| ⏱ Timeout         | Sometimes operations may take too much time. We cannot wait that long or after that time the success is unlikely                                                                   | Bound waiting to a reasonable amount of time                                                                                                                                  | ✅            |
| 🚰 Bulkhead        | If executed without control, some code can take too much resources and put down the whole application (and upstream services) or cause slowness of other places of the application | Fix the amount of calls to the code, queue other calls and fail calls that goes beyond your capacity                                                                          | ✅            |
| 🏃‍♂️ Rate Limiter   |                                                                                                                                                                                    |                                                                                                                                                                               |              |
| 🤝 Fallback        | Nothing can guarantee you that your dependencies will work. What would you do when it's failing?                                                                                   | Degrade gracefully by defining some default values or placeholders if your dependencies are down                                                                              | ✅            |

<p align="right">
Inspired by <a href="https://github.com/App-vNext/Polly#resilience-policies" target="_blank">Polly's Resiliency Policies</a>
</p>

## Acknowledgements

- [resilience4j/resilience4j](https://github.com/resilience4j/resilience4j)
- [Netflix/Hystrix](https://github.com/Netflix/Hystrix)
- [slok/goresilience](https://github.com/slok/goresilience)
- [App-vNext/Polly](https://github.com/App-vNext/Polly)
- [Diplomatiq/resily](https://github.com/Diplomatiq/resily)
