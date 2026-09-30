# UX Pre-Kickoff Sync

Status: CONSOLIDATED
Owner: Senior Product / UX Designer
Branch: `ai/ux/pre-kickoff-sync`

## Purpose

This document consolidates UX conclusions already discussed before kickoff and compares them with the current state of `main`.

It does not authorize implementation, redefine game rules, or silently change Product or Architecture decisions. Cross-domain concepts listed below remain proposals until reviewed by the responsible owners.

## What is already normative from main

The following repository decisions directly constrain UX and must be treated as accepted:

- PostgreSQL is the source of truth for mutable campaign state.
- Campaign isolation is enforced using `campaign_id`.
- `Entity` is an identity registry, not a generic property bag.
- Stable first-party domain concepts use typed relational tables.
- Dynamic extension data uses `EntityExtensionData` with `namespace`, `schema_id`, `schema_version`, and JSONB payload.
- `KnowledgeFragment` represents a proposition/claim with GM-side veracity metadata.
- `CharacterKnowledge` represents a character's epistemic state; absence means unknown.
- Player-facing endpoints use explicit player projections/read models and never rely on frontend-only redaction.
- `DomainEvent` is append-only history/audit data; current state is not reconstructed through event sourcing.
- Custom D20 is first-party for the MVP.
- Platform Core is restricted to cross-cutting concepts; Species, Class, Skills, Talents, progression, and Force mechanics belong to Custom D20.
- Backend services remain authoritative for authentication, authorization, campaign scoping, validation, and state mutation.
- The GM retains final narrative authority, although this still requires formalization in the cross-domain decision log.

## UX conclusions from the pre-kickoff review

These conclusions are UX recommendations from the existing working session. They are not cross-domain decisions unless explicitly accepted elsewhere.

### 1. The UI must not mirror the persistence model

Users should work with domain language such as NPCs, locations, factions, secrets, actions, consequences, and discoveries.

Technical concepts such as `EntityExtensionData`, raw relationship records, JSONB schemas, rule DSL internals, and `DomainEvent` types should remain implementation details except in administration/debugging contexts.

### 2. The product should distinguish three usage contexts

A practical UX separation is recommended between:

- preparation;
- live session;
- world administration.

Preparation may expose richer editing and exploration.
Live session must prioritize speed, context, search, recent activity, and low-friction mutation.
World administration may expose lower-frequency technical/configuration functions.

This is an information-architecture recommendation, not yet a Product decision.

### 3. Contextual creation should be preferred over generic forms

When the GM creates or generates content from a location, faction, scene context, or entity page, obvious relationships should be inferred automatically.

Example: creating an NPC while viewing a cantina should not require manually selecting that same cantina again.

### 4. Generated content should not silently become canonical

Procedural or AI-assisted generation should support a staged interaction such as:

- generate;
- inspect;
- edit if needed;
- accept/use;
- reject/regenerate.

The persistence semantics for draft candidates are not yet accepted and require Architecture/Product review.

### 5. Player disclosure must be projection-driven

The player client must receive only information the player/character is authorized to access.

Hidden GM information must not be sent to the browser and merely concealed in the UI.

This UX requirement is consistent with ADR-003.

### 6. Knowledge UX should hide epistemic bookkeeping by default

The GM needs to distinguish canonical reality from what individual characters know, but should not be forced to manually manage `KnowledgeFragment` and `CharacterKnowledge` for routine lore.

Knowledge fragments should be used where secrecy, misinformation, discovery, differing beliefs, or provenance matter in play.

A reveal interaction should make the target audience and exact player-visible content explicit before disclosure.

### 7. Search must be a primary live-session interaction

The GM should be able to retrieve relevant entities and campaign information without navigating deep taxonomies.

Global search is considered high priority for a playable MVP UX.

### 8. Destructive actions should favor archive over hard delete

For persistent campaign content, the normal UX should prefer reversible archival/deactivation where domain semantics allow it.

Permanent deletion should be exceptional and should expose dependency/impact information before confirmation.

This requires Architecture review for lifecycle semantics.

### 9. Autosave and explicit commit should be differentiated

Low-risk text editing can autosave with visible save/error feedback.

Narratively significant or destructive mutations, knowledge revelation, and consequence application should require explicit user action rather than silent autosave.

### 10. Domain history should be rendered as user-meaningful activity

The GM should not see a raw stream of technical events such as `EntityUpdated` or `CharacterKnowledgeCreated`.

The UX should project those into meaningful statements about what happened in the campaign, with links to relevant entities and actions.

## Proposed cross-domain concepts

The following concepts emerged as important during UX analysis but are not present as accepted decisions in `main`.

They must therefore remain PROPOSED until kickoff review.

### CROSS-DOMAIN DECISION — Session

A persistent `Session` concept may be needed to group:

- participants;
- start/end;
- live-session context;
- resolutions;
- discoveries;
- notes;
- history.

**PRODUCT IMPACT:** defines a primary user workflow boundary.  
**UX IMPACT:** enables preparation/live/post-session continuity.  
**ARCHITECTURE IMPACT:** requires persistence, API, and event correlation.  
**GAME DESIGN IMPACT:** low unless session-scoped rules exist.

### CROSS-DOMAIN DECISION — Scene or equivalent current context

A lightweight `Scene` or equivalent may be needed to represent current narrative context independently from a physical `Location`.

It could associate:

- current location;
- present characters/NPCs;
- active narrative threads;
- pinned session elements;
- optional encounter.

**PRODUCT IMPACT:** affects session workflow scope.  
**UX IMPACT:** provides the main live-session context model.  
**ARCHITECTURE IMPACT:** requires domain ownership and lifecycle definition.  
**GAME DESIGN IMPACT:** may interact with encounters and turn-based play.

### CROSS-DOMAIN DECISION — ActionResolution / Stakes

The existing UX review strongly recommends a structured concept between player intent, Dice, Rules, and world mutation.

Candidate flow:

```
Intent
  -> Stakes
  -> Check / Roll
  -> Outcome
  -> Consequence proposals
  -> GM validation
  -> Applied mutations
  -> History
```

This would let the UI represent:

- who acts;
- target/context;
- intended outcome;
- public/private stakes;
- requested check;
- result;
- proposed consequences;
- accepted/rejected consequences;
- final mutations.

**PRODUCT IMPACT:** central interaction model for assisted gameplay.  
**GAME DESIGN IMPACT:** owns resolution semantics, stakes, success/failure, and narrative result rules.  
**UX IMPACT:** avoids disconnected dice rolls and opaque mutations.  
**ARCHITECTURE IMPACT:** requires aggregate/transaction/API decisions.

### CROSS-DOMAIN DECISION — Consequence proposal and reversible change grouping

For significant mutations, the UX should be able to show the GM what will change before persistence and allow correction afterward.

Possible supporting concepts include `ConsequenceProposal` and an `AppliedChangeSet` or equivalent correlation mechanism.

The exact persistence model is Architecture-owned.

**PRODUCT IMPACT:** supports GM authority and confidence in automation.  
**GAME DESIGN IMPACT:** defines which consequences are deterministic vs interpretive.  
**UX IMPACT:** enables preview, accept/reject, and undo.  
**ARCHITECTURE IMPACT:** requires transaction and compensation semantics.

### CROSS-DOMAIN DECISION — NarrativeThread

A dedicated or typed concept may be useful for persistent campaign threads such as hooks, investigations, threats, unresolved consequences, and evolving plots.

The UX need is real, but whether this should be a dedicated domain model, a typed Entity, or another representation is not yet decided.

**PRODUCT IMPACT:** affects MVP scope for campaign management.  
**GAME DESIGN IMPACT:** may overlap with objectives and narrative progression.  
**UX IMPACT:** gives the GM a manageable view of ongoing story state.  
**ARCHITECTURE IMPACT:** model choice remains open.

## Assumptions not yet validated

The previous UX review assumed, but `main` does not yet establish, that:

- the MVP includes a distinct live-session mode;
- the GM should be able to generate additional playable content during a session;
- players use their own companion screen during live play;
- global search is part of the MVP rather than a later usability enhancement;
- combat/initiative is included in the first playable release;
- recent actions can be corrected through an explicit undo workflow;
- generated content is staged before becoming canonical;
- entity archival is preferable to deletion for routine world management;
- private GM-player actions/messages are part of the MVP;
- a minimal "playable now" generation mode is desirable to reduce perceived latency.

These assumptions require Product prioritization and, where relevant, Architecture/Game Design review.

## Contradictions found

No direct contradiction was found between the existing UX review and accepted ADRs.

The main discrepancy is status:

- the UX review treated several concepts as effectively necessary for a usable product;
- `main` currently treats those concepts as undocumented proposals or does not mention them.

This sync deliberately does not elevate them to ACCEPTED.

## Open UX questions for kickoff

1. What exact GM workflow defines the first vertical slice?
2. What exact player workflow must be supported in that slice?
3. Does the MVP have a distinct live-session mode?
4. Is a persistent `Session` concept required for the first slice?
5. Is a `Scene` domain concept required, or can current context initially remain a read/workflow concern?
6. Which actions must be possible in one or two interactions during live play?
7. What information must remain permanently visible to the GM while a session is live?
8. What is the minimum player companion scope for the MVP?
9. Which knowledge disclosures are manual, rules-driven, or both?
10. What preview is required before revealing knowledge to a player or party?
11. Which consequence types can be applied automatically without GM confirmation?
12. Which consequence types always require GM approval?
13. What undo/correction guarantee is required for the MVP?
14. Is world-content generation during a live session a MUST, SHOULD, or later feature?
15. What is the acceptable latency and minimum output for live generation?
16. Is combat/initiative part of the first vertical slice?
17. Does the MVP require `NarrativeThread`, or can initial story tracking use a simpler representation?
18. What lifecycle does editable campaign content need: active/archive/delete, or something else?
19. Which player-visible history and knowledge provenance are required in the MVP?
20. Which UX conclusions must become Product requirements before frontend implementation begins?

## Dependencies on other roles

### PRODUCT IMPACT

Product must decide MVP scope, first vertical slice, live-session requirements, player companion scope, generation priority, and whether search/combat/private actions belong to the MVP.

### GAME DESIGN IMPACT

Game Design must define the actual resolution contract, stakes semantics, D20 result interpretation, deterministic vs discretionary consequences, combat state, conditions/effects, and epistemic gameplay semantics.

### ARCHITECTURE IMPACT

Architecture must determine the persistence and API representation for sessions/scenes if accepted, action resolution, staged generation, reversible mutations, lifecycle/archive behavior, correlation of domain history, and safe player projections.

### SECURITY IMPACT

The UX requires server-side authorization and disclosure enforcement. Secret/canonical data must never be shipped to unauthorized player clients. Private actions and targeted reveals require explicit audience enforcement in backend projections/APIs.

## Recommended minimal UX documentation before kickoff

This document is sufficient as the UX pre-kickoff consolidation.

After kickoff decisions, the UX space should be expanded only as needed with:

- accepted GM workflow(s);
- accepted player workflow(s);
- primary information architecture;
- first-slice interaction specification;
- any UX-specific decision records that become normative.

## Implementation gate

This sync does not authorize frontend implementation.

The implementation gate defined in `docs/planning/PROJECT_KICKOFF.md` remains authoritative.
