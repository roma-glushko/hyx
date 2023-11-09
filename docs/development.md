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

TBU

### Expressive

TBU

## Workflows

The main [Makefile](https://github.com/roma-glushko/hyx/blob/main/Makefile) contains commands useful during development
like linting or full test suite run. 

Those checks are being applied on each pull request via Github Actions, so we keep the main branch as stable as possible.

### Installation

Hyx uses [Poetry](https://python-poetry.org/docs/) as a dependency manager, so it should be installed before installing Hyx's dependencies locally.
We recommend to use [Pyenv](https://github.com/pyenv/pyenv) to manage your Python environments, but you could really use any alternative you prefer.

```bash
 ~/.pyenv/versions/3.11.3/bin/python -m venv .venv
 make install
```

### Linting

Hyx cares about typing as it makes Hyx use easier. Avoid using vague typings (e.g. typing.Any). 
Hyx uses mypy, black, ruff to ensure code style and statically analyze the code. All of that could be run via:

```bash
make lint
```

### Tests

Hyx strives to keep high test coverage of the codebase. We focus on covering usecases rather than "running through each line".
All test suite could be executed via (takes about 8s):

```bash
make tests
```

Additionally, to ensure test coverage, Hyx is integrated with [CodeCov](https://app.codecov.io/github/roma-glushko/hyx).

### Docs

[Mkdocs](https://squidfunk.github.io/mkdocs-material/getting-started/) and [Readthedocs](https://readthedocs.io) power [the Hyx's documentation](https://hyx.readthedocs.io/en/latest/). 
These are the main commands you may need while dealing with the docs:

```bash
make docs-serve  # start a local documentation server
make docs-build  # build a publishable files out of the documentation
```

Any update to Hyx's API is only considered as done when the corresponding documentation is updated. 
So users have a simple way to discover all improvements and adjustments.
