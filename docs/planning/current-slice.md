# Current Vertical Slice

## Slice 3 — Roll, Review and Adjudicate

**Status:** ACCEPTED  
**Accepted:** 2026-10-02  
**Owner:** Product Lead / Human Project Owner  
**Specification:** `docs/planning/slice-3-spec.md`

## Goal

Validate a bounded GM-authoritative D20 resolution workflow that explicitly separates:

1. immutable raw roll;
2. immutable mechanical result;
3. final GM adjudicated outcome;
4. later correction/supersession without rewriting mechanical evidence or pretending irreversible human disclosure can be undone.

## Accepted scenario

Slice 3 reuses the existing Slice-1 slicing scenario.

Kara Venn attempts to slice the Imperial Cargo Terminal to discover where a confiscated shipment was transferred.

The bounded workflow is:

```text
Intent + Risk + slicing mechanic + DC + pre-bound success effect
-> Roll
-> immutable RAW ROLL
-> immutable MECHANICAL RESULT
-> GM adjudication
-> Finalize
-> bounded consequence commit
-> optional later Correct outcome
-> superseding adjudication + append-only history
```

The success consequence remains:

> Kara becomes AWARE of the pre-bound KnowledgeFragment:
> "The confiscated shipment was transferred to Dock 47."

The failure path remains one concrete GM-authored failure adjudication string; the predeclared Risk may be used unchanged when it is already sufficient.

## Required Slice 3 contracts

- raw d20 is generated exactly once by the backend and is immutable through normal Product commands;
- resolved modifier, total, DC and mechanical result are immutable after Roll;
- mechanical result remains binary SUCCESS/FAILURE for this slice;
- final adjudicated outcome is separate from mechanical result;
- Override is the exceptional case where final outcome differs from mechanical result;
- Override is allowed in both binary directions;
- override reason is optional;
- common path uses one Finalize action after review;
- final SUCCESS applies only the existing pre-bound CharacterKnowledge effect;
- final FAILURE persists a concrete failure adjudication and does not apply the success effect;
- Risk may directly supply the failure adjudication when sufficient;
- Correct outcome creates a new adjudication that supersedes the prior one;
- correction reason is required;
- correction never rewrites raw/mechanical evidence;
- FAILURE -> SUCCESS correction may add the pre-bound knowledge disclosure;
- SUCCESS -> FAILURE after disclosure retains CharacterKnowledge = AWARE and preserves disclosure history;
- existing Slice-1-specific ActionResolution is evolved narrowly rather than replaced;
- current adjudication stays in PostgreSQL relational state;
- prior adjudications remain in append-only DomainEvent history;
- Player receives a bounded finalized-resolution projection containing raw d20, modifier, total, mechanical result, final outcome, overridden marker and corrected marker;
- Player does not receive DC, GM reasons, failure-adjudication text, GM-only Risk/stakes, gm_veracity, or full correction history;
- Finalize and Correct remain synchronous, row-locked and backend-authorized;
- campaign isolation remains strict.

## Required API direction

Keep:

```text
POST /campaigns/{campaign_id}/resolutions
POST /campaigns/{campaign_id}/resolutions/{resolution_id}/roll
GET  /campaigns/{campaign_id}/resolutions/{resolution_id}
GET  /campaigns/{campaign_id}/resolutions/latest
```

Introduce:

```text
POST /campaigns/{campaign_id}/resolutions/{resolution_id}/finalize
POST /campaigns/{campaign_id}/resolutions/{resolution_id}/correct
```

The old `/apply` and `/close-failure` terminal mutation semantics must not remain alternative paths around the accepted adjudication contract.

## Acceptance criteria

The normative acceptance criteria and test contract are defined in `docs/planning/slice-3-spec.md`.

At minimum, implementation must prove end-to-end:

- normal mechanical SUCCESS -> Finalize SUCCESS;
- mechanical FAILURE -> Override -> Finalize SUCCESS;
- mechanical SUCCESS -> Override -> Finalize FAILURE;
- finalized FAILURE -> Correct -> SUCCESS;
- finalized SUCCESS -> Correct -> FAILURE after disclosure while retaining CharacterKnowledge;
- immutable mechanical evidence across Finalize/Correct;
- append-only finalization/correction history;
- GM-only mutations;
- Player-safe finalized-resolution projection;
- reload persistence;
- idempotency/concurrency behavior;
- migration from legacy Slice-1 ActionResolution rows;
- Slice 2 Contact Reveal remains independent of ActionResolution.

## Explicit Slice 3 exclusions

- generic resolution engine;
- generic Resolution aggregate for hypothetical mechanics;
- generic Adjudication aggregate/table;
- generic workflow/state-machine framework;
- generic undo/change-set framework;
- arbitrary rollback;
- generic compensation framework;
- generic consequence/effect engine;
- Rule Effect DSL;
- event sourcing;
- combat/encounter system;
- Player-side rolling;
- collaborative/group actions;
- realtime/WebSockets/SSE;
- rerolls;
- crits;
- degrees of success;
- opposed rolls;
- advantage/disadvantage expansion;
- mechanical repair UI;
- full Player resolution-history browser;
- Player-visible DC;
- Player-visible GM reasons;
- generic Scene/Session;
- broker/worker;
- microservices;
- a second D20 mechanic introduced only for generality.

## Deferred questions

Only genuinely deferred questions remain in `docs/planning/open-questions.md`.

Deferred items are non-normative and must not be inferred as accepted Slice 3 requirements.
