# Fallbacks

## Introduction

When your downstream microservices fall apart, retries exceed or breakers fire on, 
you need to have a solid plan B that will make this failure transient for the upstream microservices.

This plan B is normally called a fallback, 
and it comes in different forms depending on the context and functionality to fill.

## Use Cases

* Show a default or cached value if the downstream dependency is not responding (e.g. show a placeholder instead of the user's avatar)
* Log and silence the exception (e.g. if the message broker is not responding, and you can miss the message)
* Use some functional redundancy in a case of failure (e.g. request currency rates from another provider if the primary one is down)

## Usage

TBU