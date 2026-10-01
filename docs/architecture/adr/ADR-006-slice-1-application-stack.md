# ADR-006 — Slice 1 application stack and topology

## Status

ACCEPTED

## Context

The accepted first vertical slice needs a concrete implementation stack and runtime topology. The project is primarily developed by one person and explicitly rejects distributed infrastructure for Slice 1.

The kickoff review accepted React, FastAPI, PostgreSQL, a modular monolith, Docker Compose, and a replaceable tunnel/exposure layer.

## Decision

Slice 1 uses:

- React for the browser application;
- FastAPI for the backend HTTP application;
- PostgreSQL as the authoritative mutable datastore;
- a modular-monolith backend deployed as one application process;
- Docker Compose for local orchestration;
- ngrok, Cloudflare Tunnel, or equivalent only as an external transport/exposure layer when needed.

The frontend and backend remain application-level security boundaries independent of the tunnel provider.

The backend owns authentication, authorization, campaign isolation, validation, resolution transitions, disclosure, and state mutation.

No broker, asynchronous worker, distributed cache, separate search service, Kubernetes, microservice split, or realtime service is part of Slice 1.

## Consequences

- domain boundaries are code/package boundaries inside one deployable backend;
- cross-domain Slice 1 orchestration can use direct in-process calls and one PostgreSQL transaction;
- operational setup remains small enough for solo development;
- the tunnel can be replaced without application redesign;
- later infrastructure must be justified by a concrete requirement rather than anticipated scale.

## Alternatives considered

### Microservices

Rejected for Slice 1 because they add deployment, networking, observability, authorization, and distributed-transaction complexity without a demonstrated need.

### Event-driven internal architecture

Rejected for immediate canonical mutations because it would weaken the accepted synchronous transaction contract and turn DomainEvent into RPC.

### Kubernetes

Rejected for Slice 1 because Docker Compose satisfies the local orchestration requirement and the project has no current distributed-runtime need.
