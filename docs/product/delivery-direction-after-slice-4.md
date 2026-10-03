# Product Delivery Direction After Slice 4

**Status:** ACCEPTED PRODUCT DIRECTION — FUTURE SELECTION INPUT — NOT AN IMPLEMENTATION CONTRACT  
**Owner:** Human Project Owner / Product Lead  
**Effective:** next slice-selection cycle after Slice 4 implementation merge  
**Implementation authorization:** NONE

This document records durable Product/Engineering direction established after Human manual validation of Slice 4.

It does not reopen Slice 4, amend the ACCEPTED Slice 4 contract, or add requirements to PR #18.

Nothing in this document is directly implementable merely because this Product direction is ACCEPTED. Subject semantics, persistence shapes, broader resolution generalization, and future playable capabilities must still be selected, reviewed, specified and explicitly accepted through the normal slice process before implementation.

---

# 1. Action context / fictional Subject

## Observation

Repeated use of ActionResolution across Slices 1-4 has made one limitation material:

> Actor + mechanic + Location context + free-text Intent/Risk may still be insufficient to express what the action is actually about.

Examples:

```text
Actor: Globox
Mechanic: Slicing
Context: Imperial Cargo Terminal
Subject: security terminal
Intent: obtain Senator Traitrus's records
```

and:

```text
Actor: Globox
Mechanic: Athletics
Context: rooftops of Coruscant
Subject: the opposite rooftop
Intent: jump across the gap
```

The Subject may therefore be a transient fictional object that has no persistent Entity identity.

## Product direction

The next slice-selection cycle must explicitly evaluate richer action context / fictional Subject as a material need.

Do **not** reduce the problem to `target_entity_id`.

An optional Entity reference may later enrich a Subject, but persistence must not assume that every Subject is an Entity.

## Required cross-domain analysis

### Game Design

Must distinguish at least:

- **mechanical target** — something directly participating in rules resolution;
- **fictional subject** — what the action is fictionally about or directed toward;
- **effect recipient** — who/what receives the committed consequence;
- **contextual entity** — a persistent campaign entity relevant to the action context.

These concepts may coincide in some mechanics and diverge in others.

### UX

Must determine the minimum information the GM actually needs to enter or select so that an action is understandable during live play.

The Product goal is richer context without turning every roll into a form-heavy workflow.

Possible contextual information may be derived, free text, selected from existing entities, or structured only for mechanics that need it.

### Architecture

Must not choose a persistence representation until the Game Design and UX contracts are concrete.

In particular, do not precommit to:

- one Entity FK;
- singular cardinality;
- universal applicability to all ActionResolution instances;
- a polymorphic participant table;
- a generic target framework.

## Status

This direction raises the priority of existing Q-009 as a future selection input.

It does not resolve Q-009, define a Subject model, or authorize any schema/API/UI implementation.

---

# 2. Larger vertical slices

## Product direction

This is a future slice-selection principle, not authorization to broaden the current implementation automatically.

Slices 1-4 intentionally de-risked narrow foundations.

From the next cycle onward, prefer larger vertical slices that represent a genuinely playable capability end-to-end, even when that requires several coherent domain/UI/API/persistence changes.

Avoid creating a separate vertical slice for each:

- field;
- endpoint;
- selector;
- read model;
- isolated interaction;
- small persistence refinement.

A larger slice is appropriate when its changes collectively support one coherent playable user capability.

## Selection expectation

Future shortlist candidates should be evaluated as complete capabilities crossing:

```text
user scenario
-> gameplay/domain semantics
-> GM and/or Player UX
-> API
-> persistence
-> authorization/security
-> targeted automated tests
-> mandatory Human functional test
```

The next shortlist must explicitly evaluate whether the project is ready to move beyond the slicing demonstrator toward a resolution system supporting multiple action types.

This evaluation must not silently generalize ActionResolution.

It should ask:

- which concepts have now been proven common across multiple action types;
- which concepts remain slicing-specific;
- whether at least one additional real mechanic is sufficient to justify extraction/generalization;
- how richer action Subject/context interacts with multiple mechanics;
- whether a substantial playable capability is a better next step than another foundational micro-slice.

---

# 3. Development-phase testing direction

## Principle

This testing direction applies when Product and Architecture define test scope for future implementation slices. It does not retroactively amend accepted slice contracts and does not by itself authorize removing existing tests or weakening required security/invariant coverage.

Automated tests remain required where they protect rules, invariants, authorization, security boundaries and meaningful integration behavior.

During this rapidly evolving product phase, avoid spending disproportionate effort on exhaustive browser matrices or test-harness hardening that duplicates lower-level coverage.

## REQUIRED

For implementation slices, require as appropriate:

- targeted backend tests for rules and domain invariants;
- targeted backend tests for authorization/security boundaries;
- migration tests when a migration presents real data or compatibility risk;
- frontend build and typecheck;
- integration tests necessary to prove the slice's important boundaries.

## E2E

Prefer:

- one happy-path E2E when it adds meaningful confidence in the end-to-end user workflow;
- additional E2E variants only when the behavior cannot be covered efficiently or reliably at a lower level.

E2E should validate cross-layer wiring and the user-critical path, not duplicate every backend invariant.

## DO NOT REQUIRE BY DEFAULT

Do not require by default:

- exhaustive Playwright matrices;
- E2E duplication of rules/security invariants already well covered in backend tests;
- extensive browser-harness hardening unrelated to product behavior;
- broad regression E2E expansion merely because a new slice touches a shared surface.

This does not justify ignoring deterministic product defects discovered by E2E.

## Human functional acceptance

This is a future process gate, not an implementation task by itself.

A Human functional test remains mandatory before merge of an implementation slice.

The final Product acceptance immediately before that Human test must provide a concrete functional test plan covering the accepted user workflow and the most material Product risks.

The Human test should focus on actual usability and workflow behavior rather than reproducing automated invariant matrices.

---

# 4. Process cadence

The accelerated process remains:

1. Product closes the completed slice and shortlists the next substantial slice, preferably in one PR when coherent.
2. Game Design, UX and Architecture review in parallel.
3. A second review loop occurs only for a material cross-domain dependency.
4. Human selects the next direction.
5. Product consolidates the exact slice specification.
6. Human explicitly accepts the specification.
7. Architecture implements only after the normative PR is merged.
8. Product performs targeted acceptance and supplies the functional test plan.
9. Human performs the mandatory functional test.
10. Product marks implementation READY TO MERGE if no blocker remains.

The repository remains the durable source of truth.
