# Introduction

## From Monoliths to Distributed Systems

Last decade has been a wild ride for software engineering. 

We were building systems as a single deployable piece of code. 
Then those systems became successful and popular. 

They were in need of rapid evolution and keeping up with ever-growing traffic load. 
Vertical scaling was not the option anymore. The scaling demand was much higher than the velocity of hardware improvements. 
Plus, high-profile machines are extremely expensive.

The scale is only one facet. Yet another is availability. 
Users' expectations rose high. Now it's unexceptionable to show the 503 maintenance page for hours. 
They expect our system to always be accessible and working.

Consequently, we needed to scale our teams. There used to be a team of dozens of engineers who had designed, implemented and maintained the system.
Now there might be several teams with thousands of people involved. It's even unclear anymore who could fully reason about the system.

The need for scale has paved our way to alternative system architectures. 
The experience of the current industry giants like Google, AWS, Netflix, Meta showed that the new way is all about 
splitting down the monoliths into smaller self-contained deployable pieces that we have called `microservices`. 
Those microservices can be deployed on commodity machines and scale horizontally without the bound (except for your budget).

## The Microservice Era

Splitting the monoliths into pieces turned out to be **much harder** to do than it had sounded. 
Microservices are distributed on several machines over the network and that increases the amount of moving parts by far.

Now instead of watching for one machine's health, we need to watch for `N` of them. 
That only increases chances that hardware will go wrong somewhere. 
You can do as much as you are allowed by laws of nature.

The network itself is an inherently unreliable medium. 
Packets get missed, cables get broken and routers die as any other components.

Additionally, now we need to think about latency, bandwidth and sometimes about network topology.

The microservice world is a total mess. 
The only useful thing you can do about it is to embrace the fact that **failures are inevitable** and build around that fact.

Failures are not exceptional situations anymore, they are our new normals. We should design to fall.

## About Failures and Limits

The distributed nature of microservice systems is a double-edged sword. 
It does increase the chance of failure, but it decreases the change of outright failures. 
So it's not the all-or-nothing game anymore, you have got a middle state called **the partial failure**.

It's when some specific subset of your system experience high error rate, latency or any other failing conditions. 
The rest of the system may be less affected or fully functional.

This is the most plausible scenario. So this condition should be at the very center of our design considerations. 
What would we do if any of your dependencies go down, respond with errors or don't respond at all for a while?

When you start answering those questions, you will see that when your system is unbound, there are a ton of ways it can fail.
The failures are going to be unpredictable and slow to respond.

That's why the heart of resiliency engineering is
in applying [all sorts of limits](https://bravenewgeek.com/take-it-to-the-limit-considerations-for-building-reliable-systems/).
That will restrict your system to **fail in the way you expect it to fail**.

## Reliability Engineering

Sooo, what is Hyx? 

Hyx is your ready-to-use **resiliency engineering toolkit** that will help you to restrict your system to fail in the predictable way.
Hyx implements and provides primitives and components that are well-known in resiliency engineering and proven to be useful in production settings.

All components can be divided into two groups:

- **Reactive Components**. Don't prevent errors, but they are helpful to tolerate errors or reduce their blast radius when they occur.
- **Proactive Components**. Bound the system to force it to fail in the predicated way.

## Components

Here is a list of components that Hyx is currently providing:

#### Reactive Components

- [Retries](retry.md)
- [Circuit Breakers](circuit_breakers.md)
- [Timeouts](timeout.md)
- [Fallbacks](fallback.md)

#### Proactive Components

- [Bulkheads](bulkhead.md)
- [Rate Limiters](rate_limiter.md)