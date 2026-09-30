# ADR-004 — Domain events, current state, and transactional outbox

## Status

ACCEPTED

## Context

The application needs an audit/history trail and may later require reliable asynchronous integrations, but the project does not need full event sourcing.

## Decision

PostgreSQL stores current mutable domain state as the authoritative application state.

`DomainEvent` records are append-only and capture significant domain changes/history.

The architecture does not use full event sourcing: current state is not reconstructed by replaying events.

When a durable asynchronous side effect is required, a transactional outbox is the intended pattern so state changes and publish intent can be committed atomically.

Canonical rule effects that must be immediately consistent with the triggering command must execute synchronously in the same application transaction rather than relying on asynchronous outbox processing.

## Consequences

- Reads use current relational state.
- Event history remains available for audit, summaries, integrations, and diagnostics.
- Asynchronous consumers must be idempotent when introduced.
- An outbox worker need not be implemented until a concrete MVP asynchronous requirement exists.

## Alternatives considered

- Full event sourcing: rejected as disproportionate for the project.
- Direct best-effort publish after commit: rejected for future durable integrations because of dual-write failure modes.
