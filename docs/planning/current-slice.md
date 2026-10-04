# Current Vertical Slice

## Slice 5 — Escape the Imperial Patrol / Personal-Scale Combat Encounter

**Status:** ACCEPTED  
**Accepted:** 2026-10-04  
**Owner:** Product Lead / Human Project Owner  
**Specification:** `docs/planning/slice-5-spec.md`

## Goal

Validate one complete, objective-driven personal-scale combat encounter without building the full combat system, VTT, generic Scene system, or generic combat engine.

## Accepted scenario

```text
GM starts encounter
-> Round 1 / Globox turn
-> Player chooses Attack or Escape
-> deterministic combat state updates
-> if still active: GM Resolve Patrol Attack
-> next round
-> repeat
-> ESCAPED / PATROL_NEUTRALIZED / INCAPACITATED
```

## Accepted combat micro-contract

- one PC: Globox;
- one abstract hostile group: Imperial Patrol;
- deterministic Player-first alternating turns;
- exactly one action per side per turn;
- Player actions: Attack or Escape;
- Patrol action: Attack Globox;
- GM explicitly triggers Resolve Patrol Attack;
- backend-authoritative d20 + Attack Modifier >= static Defence;
- natural 1/20 have no special behavior;
- fixed damage = 2;
- encounter-scoped Combat Vitality / Group Strength;
- Escape Progress 0 -> 3;
- no grid, range, movement, cover or line of sight;
- deterministic routine combat effects commit immediately;
- no Slice-3 Finalize/Override/Correct on routine combat actions.

## Slice 5 tuning

```text
Globox
  Attack Modifier +3
  Defence 12
  Combat Vitality 4
  Damage 2

Imperial Patrol
  Attack Modifier +2
  Defence 12
  Group Strength 4
  Damage 2

Escape Target 3
```

These values are acceptance-scenario tuning only, not final Custom D20 combat balance.

## End conditions

```text
Escape Progress >= 3 -> ESCAPED
Patrol Group Strength <= 0 -> PATROL_NEUTRALIZED
Globox Combat Vitality <= 0 -> INCAPACITATED
```

Terminal state ends the encounter immediately.

## Architecture direction

Use one combat-specific persisted `CombatEncounter`.

Do not route combat through the Slicing-specific `ActionResolution`.

The database must atomically enforce at most one ACTIVE encounter per campaign + Player Character with a narrow partial unique index.

Reuse existing:

- Character identity;
- PlayerCharacterAssignment;
- backend D20 rule shape;
- PostgreSQL row-locking patterns;
- explicit Player projections;
- DomainEvent append-only history;
- bounded polling.

Do not introduce generic Scene, Combatant, encounter-builder, workflow/state-machine, combat-engine, Rule Effect DSL or realtime-push infrastructure.

## Authorization

Player Attack/Escape authorization is backend-derived from:

```text
authenticated principal
-> PLAYER CampaignMembership
-> PlayerCharacterAssignment
-> same campaign
-> assigned Character matches encounter Character
-> ACTIVE
-> current actor = PLAYER
-> expected round matches
```

Patrol Attack and encounter creation are GM-only.

Clients cannot provide authoritative die, modifier, Defence, damage, health, progress, target, turn transition, status or scenario tuning.

## Player-safe projection

Player combat state uses an explicit read model, never canonical `CombatEncounter` serialization.

`last_action` exposes only the explicitly approved combat-feedback fields and must not return raw DomainEvent payloads wholesale.

## Freshness

Use immediate re-fetch plus bounded HTTP polling while waiting, targeting approximately one second during active combat.

No WebSockets/SSE.

## Testing

Required:

- targeted backend combat rules/invariants/security tests;
- necessary integration/concurrency tests;
- frontend typecheck/build;
- normal Alembic upgrade-to-head;
- dedicated migration tests only if implementation introduces real transformation risk;
- normally one useful combat E2E.

Human functional testing is mandatory before implementation merge.

The final Product acceptance before that Human test must provide the concrete functional test plan.

## Explicit exclusions

The complete exclusion list is normative in `docs/planning/slice-5-spec.md`.

It includes full combat-system expansion, VTT/grid, movement/range/cover, permanent health, weapons/armour systems, crits/reactions, multiple hostile groups, NPC AI, generic combat abstractions, combat through ActionResolution, universal Target/Subject, and push realtime infrastructure.

## Deferred questions

Only genuinely deferred cross-domain questions remain in `docs/planning/open-questions.md`.

Deferred items must not be inferred as accepted Slice 5 requirements.
