# Current Vertical Slice

## Slice 1 — Slice the terminal, reveal the secret

**Status:** ACCEPTED  
**Accepted:** 2026-10-01  
**Owner:** Product Lead / Human Project Owner  
**Specification:** `docs/planning/KICKOFF_DECISION_PACK.md`, Phase 3

## Goal

Validate one real end-to-end GM/player gameplay loop:

```text
persistent campaign context
-> fictional player intent
-> when-to-roll decision
-> Intent + concrete Risk + pre-bound success effect
-> minimal Custom D20 check
-> success OR failure
-> explicit terminal GM action
-> atomic/correlated persistence
-> safe player disclosure when applicable
-> meaningful history
-> reload with state intact
```

## Required Slice 1 contracts

- two distinct authenticated principals: GM and Player;
- backend-derived authorization, membership, role, assignment, and campaign checks;
- one Player Character with a precomputed D20 modifier;
- one Location/current context;
- one hidden `KnowledgeFragment`;
- absence of `CharacterKnowledge` means Unknown;
- the only explicit Slice 1 epistemic state is `Aware`;
- minimum stakes are Intent + concrete Risk;
- roll only when the outcome is uncertain, meaningful risk exists, and success/failure are both fictionally possible;
- minimum roll contract: `1d20 + resolved precomputed modifier >= DC`;
- DC and exact success reveal recipient/fragment are fixed before Roll;
- success uses preview -> GM Apply;
- Apply is authorized, atomic, one-shot/idempotent, and creates/updates `CharacterKnowledge = Aware`;
- failure uses concrete adjudication -> GM Close;
- unchanged retry-until-success is not allowed;
- `DomainEvent` is append-only history/audit output, not internal RPC;
- PostgreSQL is authoritative mutable state;
- explicit player projections protect hidden/GM-only information.

## Explicit Slice 1 exclusions

- combat and initiative;
- tactical maps;
- procedural generation;
- AI assistance;
- global search;
- persistent Session/Scene;
- realtime/WebSockets;
- progression;
- Force/Dark Side mechanics;
- vehicles/space combat;
- advanced epistemic states/provenance/infohazards;
- generic consequence framework;
- generic Rule Effect DSL;
- generic undo;
- outbox worker/broker;
- plugin runtime;
- Kubernetes/distributed infrastructure.

Combat is intentionally deferred from Slice 1 and may be introduced in a later vertical slice/MVP stage.
