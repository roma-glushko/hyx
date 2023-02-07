# Bulkheads

## Introduction

The cloud engineering world loves ocean/ship analogies a lot. 
Kubernetes, docker, containers, helm, pods, harbor, spinnaker, werf, shipwright, etc.
One word from that vocabulary was actually reserved by resiliency engineering as well. It's bulkhead.

Bulkhead (a.k.a. bulwark) can be viewed a virtual room of certain capacity. That capacity is your resources that you allow to be used at the same time to process that action.
You can define multiple bulkheads per different functionality in your microservice. 
That will ensure that **one part of functionality won't be working at the expense of another**.

There is a different ways to implement bulkheads:

* In multithreaded applications it may take a form of a queue with a fixed-size worker pool
* In a single-thread event-loop-based application (the Hyx case), it takes a form of concurrency limiting

Hence, the bulkhead is essentially a **concurrency limiting mechanism**. In turn, concurrency limiting can be seen as a form of
[rate limiting](rate_limiter.md).

## Use Cases

* Limit the number of concurrent requests in one part of the microservice, so it won't take resources from other parts in case of load increase
* Shed excessive loads off the microservice

## Usage

TBU

## Adaptive Limiting

TBU

