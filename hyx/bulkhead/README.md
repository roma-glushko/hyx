# hyx.bulkhead

Bulkhead ensures that an action or code block doesn't consume all resources of the asyncio loop.
It defines a fixed limit on the number of concurrent executions of an action.

If the count rises above the configured maximum, the bulkhead becomes full and raises an exception.
This prevents requesters from overloading the application by triggering further actions.

Another way to think about a bulkhead is that it throttles executions of some code.

## Acknowledgements

- [App-vNext/Polly: Bulkhead](https://github.com/App-vNext/Polly/tree/master/src/Polly/Bulkhead)
