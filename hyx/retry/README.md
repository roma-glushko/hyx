# hyx.retry

Retry is the most basic component in our resiliency toolkit.
It wraps a function and listens for exceptions it raises.
If specified exceptions are thrown, it retries after a delay according to the configured strategy.

## Acknowledgements

- [invl/retry](https://github.com/invl/retry)
- [litl/backoff](https://github.com/litl/backoff)
