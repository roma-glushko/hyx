# Development

This page collects information useful during contributing to 🧘‍♀️Hyx.

## Use Cases

- **Hyx as a ready-to-use solution**. A good part of our users just want to import Hyx's components into their codebase and solve their typical problems with ease and no friction. In this case, users don't care about Hyx internals, but they want us to give them a convenient API, sane defaults and that it plays nicely with the technologies of their choice (API frameworks, dependency injectors, etc).
- **Hyx as a resiliency framework**. Some users have situations that requires Hyx's resiliency patterns to be incorporated into their domain-specific use cases. In that case, they may want to use low-level primitives that Hyx provides as a basis for a higher level custom toolkit. 

## API Design Principles

When developing or modifying Hyx's API, we want to stick to the following strategies:

### Common Case Fast and Advance Case Possible

It's useful to divide functionality into these buckets:

- **common case** which is what the most users look for and need
- **advance case** which is needed for advance users (or simply rarer use cases)

The common case also includes **sane and safe defaults**. 
We should not assume our users are experts in configuring circuit breakers, for example, 
and know the exact error rate to tolerate. 
Our defaults should be reasonable to serve them well until they mature to fine-tune our components.

### Predictable



### Expressive

TBU

## Workflows

### Linting

TBU

### Tests

TBU

### Docs

TBU
