# hyx.bulkhead

Bulkhead ensures that some action or code block is not going to consume all resources of the asyncio loop. 
It defines a fixed amount of executions (along with concurrent executions) of the action.

If the amount raise above configured maximum, the bulkhead gets full and raise an exception. 
Hence, the requester won't be able to overload the application by triggering the action further.

Another way to think about bulkhead is that it throttles executions of some code.

## Acknowledgements

- (App-vNext/Polly: Bulkhead)[https://github.com/App-vNext/Polly/tree/master/src/Polly/Bulkhead]