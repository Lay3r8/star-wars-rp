# Architecture Pre-Kickoff Sync

Status: CONSOLIDATED
Owner: Principal Software Architect
Branch: `ai/architecture/pre-kickoff-sync`

## Purpose

This document consolidates architecture conclusions already established before kickoff. It does not introduce a redesign and does not supersede Product, Game Design, or UX decisions.

## Accepted architecture decisions already present in main

- Custom D20 is first-party for the MVP.
- PostgreSQL is the source of truth for mutable campaign state.
- Campaign isolation is enforced using `campaign_id`.

## Accepted architecture decisions consolidated by this sync

- `Entity` is an identity registry for domain objects, not a generic property bag.
- Stable first-party concepts use typed relational tables.
- Dynamic extension-owned entity data uses `EntityExtensionData` with `namespace`, `schema_id`, `schema_version`, and a JSONB payload.
- `KnowledgeFragment` represents a proposition/claim and carries GM-side veracity.
- `CharacterKnowledge` represents a character's epistemic state for a fragment; absence means unknown.
- Player endpoints use explicit player-facing projections/read models rather than serializing canonical GM/domain models directly.
- `DomainEvent` is append-only audit/history data.
- A transactional outbox is the intended integration mechanism when durable asynchronous publication is required; this is not full event sourcing.
- Platform Core contains only cross-cutting concepts.
- Species, Class, Skills, Talents, and Force mechanics belong to the first-party Custom D20 system.
- Setting Packs are primarily data-oriented and reference mechanics supported by the game system.
- Backend services remain authoritative for authentication, authorization, campaign scoping, validation, and state mutation.

## Proposed, not yet accepted

The following remain proposals and must not be treated as normative before kickoff review:

- React + FastAPI modular monolith + PostgreSQL as the concrete initial application stack.
- Docker Compose as the initial local/runtime orchestration mechanism.
- A declarative Rule Effect model/DSL implemented as a deliberately small closed set of typed triggers, conditions, and effects.
- Exact package pinning using package id, version, and checksum.
- Exact generator reproducibility contract including generator version, inputs, and context fingerprint.
- Detailed module dependency direction between World, Characters, Knowledge, Rules, Dice, Generators, and AI Bridge.

## Open architecture questions

1. What is the first accepted vertical slice, and which domains must it cross?
2. Which GM/player workflow must the first slice support?
3. Which Custom D20 resolution semantics are required by that slice?
4. Which mutations must be synchronous in the same transaction, and which real MVP use case requires an outbox worker?
5. What minimum extension lifecycle is required for MVP: load-only, enable/disable, or upgrade?
6. What exact authorization roles and ownership rules are required for GM and player endpoints?
7. What persistence guarantees are required for generated candidates before GM acceptance?

## Cross-domain dependencies

### PRODUCT IMPACT

Architecture cannot finalize slice boundaries, persistence behavior for drafts/candidates, or package lifecycle without the MVP scope and first vertical slice.

### GAME DESIGN IMPACT

Architecture depends on Game Design for the exact D20 result contract, knowledge semantics visible in play, progression data, Force mechanics, and rule-effect requirements. Architecture owns persistence and execution boundaries, not the rules themselves.

### UX IMPACT

Player projections and GM mutation APIs depend on the approved GM/player workflows and on which information can be revealed, edited, staged, accepted, or rejected.

### SECURITY IMPACT

Every query and mutation must be scoped by campaign and actor authorization. Frontend visibility is never an authorization control. Player APIs must expose explicit projections rather than canonical GM objects.

## Contradictions resolved by existing decisions

- Platform Core must not own Species/Class/Skills/Talents/Force merely because they are common in the current game; they belong to Custom D20.
- `KnowledgeFragment` must not use "unknown to character" as a truth state; unknown is represented by absence of `CharacterKnowledge`.
- Dynamic extension data must not turn `Entity` into an unbounded JSONB property bag.

## Implementation gate

This sync does not authorize implementation. The kickoff gate in `docs/planning/PROJECT_KICKOFF.md` remains authoritative.
