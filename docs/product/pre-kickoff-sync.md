# Product Pre-Kickoff Sync

Status: CONSOLIDATED
Owner: Product Lead / Project Lead
Branch: `ai/product/pre-kickoff-sync`

## Purpose

This document consolidates the current product state before kickoff.

It compares the conclusions already discussed in Product work with the current state of `main`, including the merged Architecture, UX, and Game Design pre-kickoff synchronization documents.

This is a synchronization artifact, not a product redesign. It does not authorize implementation, select the first vertical slice, or silently promote cross-domain proposals to accepted decisions.

## What is already normative from main

The following repository decisions constrain Product and are already accepted unless explicitly noted otherwise:

- Custom D20 is first-party for the MVP.
- PostgreSQL is the source of truth for mutable campaign state.
- Campaign isolation is enforced using `campaign_id`.
- `Entity` is an identity registry rather than a generic property bag.
- Stable first-party concepts use typed relational tables.
- Dynamic extension-owned entity data uses `EntityExtensionData` with `namespace`, `schema_id`, `schema_version`, and JSONB payload.
- `KnowledgeFragment` represents a proposition/claim and carries GM-side veracity metadata.
- `CharacterKnowledge` represents a character's epistemic state toward a fragment; absence means unknown.
- Player-facing endpoints use explicit projections/read models rather than direct serialization of canonical GM/domain models.
- `DomainEvent` is append-only history/audit data.
- PostgreSQL current state remains authoritative; the architecture does not use full event sourcing.
- A transactional outbox is the intended pattern when a concrete durable asynchronous publication need exists.
- Platform Core contains only genuinely cross-cutting concepts.
- Species, Class, Skills, Talents, progression, and Force mechanics belong to Custom D20.
- Setting Packs are primarily data-oriented and reference mechanics explicitly supported by Custom D20.
- Backend services remain authoritative for authorization, campaign scoping, validation, disclosure, and state mutation.

The cross-domain decision log currently also records:

- GM retains final narrative authority — status: **To formalize**.

Product therefore treats GM narrative authority as an existing direction that still requires explicit cross-domain formalization before it should be cited as fully accepted.

## Product conclusions already discussed

The following conclusions were produced during Product review before the repository became authoritative.

They are retained here as **PROPOSED** unless already covered by an accepted repository decision.

### PROPOSED — Product identity

Star Wars RP should be treated primarily as a persistent campaign platform for GM and players rather than as a general-purpose VTT.

The product value is expected to come from the combination of:

- persistent editable campaign state;
- efficient GM authoring and live-session workflows;
- explicit separation between canonical reality and character/player knowledge;
- assisted action resolution and consequence handling;
- procedural generation as authoring assistance;
- later AI assistance where it provides clear value.

This framing is not yet an accepted cross-domain decision.

### PROPOSED — Generated content becomes ordinary campaign state after acceptance

Procedural generation should propose or create campaign content, but once the GM accepts generated content it should be managed through the same campaign model and editing workflows as manually created content.

Candidate interaction:

```text
Generate
-> Inspect/Edit
-> Accept
-> Persist as normal campaign state
```

This direction is strongly aligned with the UX pre-kickoff sync but is not yet formally accepted.

### PROPOSED — Generation is authoring assistance, not an independent source of truth

The generator should not silently recompute or overwrite accepted campaign state.

The mutable campaign remains authoritative after generated content is accepted.

### PROPOSED — Preparation and live session are distinct workflows

Product work previously assumed a distinction between:

- preparation, optimized for deeper creation/editing;
- live session, optimized for speed, context, search, resolution, consequence handling, and disclosure.

UX further proposes a third low-frequency world-administration context.

Whether these are explicit application modes, navigation states, or merely workflow optimizations remains open.

### PROPOSED — ActionResolution is likely a first-class product capability

The existing Product, UX, and Game Design analyses converge on a need for a structured boundary between player intent, rules/dice, consequences, and committed mutations.

Candidate conceptual flow:

```text
Intent
-> Stakes / Risk
-> Check or Roll
-> Outcome
-> Proposed effects/consequences
-> GM adjudication when required
-> Applied campaign mutations
-> History / disclosure
```

The exact domain/persistence representation belongs to Architecture.

The exact resolution semantics belong to Game Design.

Whether this capability is required in the first vertical slice is a Product decision still to be made at kickoff.

### PROPOSED — Consequence handling should distinguish deterministic and interpretive changes

Product work previously used three useful classes:

1. deterministic mechanical changes;
2. explicit bounded world-state changes;
3. narrative/canonical consequences requiring GM judgment.

The Game Design sync expresses a compatible distinction between deterministic effects, bounded narrative consequences, and authoritative narrative changes.

The shared unresolved issue is not the broad classification but the exact commit/confirmation policy.

### PROPOSED — Significant mutations should have an explicit commit boundary

For narratively significant or potentially surprising changes, the product should prefer a clear transition from proposed change to committed campaign mutation rather than silent state changes.

Candidate workflow:

```text
Outcome
-> Proposed consequence/effect
-> GM accepts/edits/replaces when required
-> Commit
```

This is consistent with UX and Game Design proposals but is not yet accepted.

### PROPOSED — Player experience should remain deliberately narrower than GM experience

The player-facing product should focus on the information and actions relevant to play, such as character state, abilities, inventory/resources, known information, objectives, and rolls/actions.

Players should not be exposed to internal campaign-authoring or persistence concepts.

The security boundary for this principle is already accepted through explicit player projections.

### PROPOSED — Build the product through playable vertical slices

Product review previously recommended proving a complete small campaign loop before expanding generation, AI, advanced extensibility, or broad content catalogs.

The first slice should cross only the minimum domains needed to validate a real GM/player workflow.

The exact slice remains intentionally unselected in `main`.

## Product conclusions that are not yet documented as decisions

The following conclusions have been discussed but are still missing as accepted product requirements:

- the exact product vision and differentiation;
- the primary personas and player/GM scope;
- the definition of a playable MVP;
- whether a dedicated live-session workflow is MVP;
- whether global search is MVP;
- whether procedural world generation is MUST for MVP versus a later milestone;
- whether live contextual generation is MVP;
- whether `ActionResolution` is mandatory for the first slice;
- the expected GM confirmation boundary for deterministic versus interpretive consequences;
- whether a persistent `Session` concept is needed;
- whether a `Scene` or equivalent current-context concept is needed;
- whether story-thread/objective tracking needs a dedicated capability in MVP;
- the minimum player companion experience;
- correction/undo expectations;
- archive/delete lifecycle expectations;
- combat scope for MVP;
- tactical-map scope;
- vehicle/space-combat scope;
- which knowledge states and provenance capabilities matter to MVP.

These should not be treated as accepted merely because they appeared in prior Product discussion.

## Contradictions found

### No direct contradiction with accepted architecture decisions

The Product conclusions reviewed here are compatible with the currently accepted ADRs.

The main gap is **decision status**, not incompatible design.

### Tension — Product MVP ambitions versus unresolved Game Design

Product previously described a potentially broad MVP including campaign creation, world authoring, session play, action resolution, knowledge, generation, and multiple sessions.

Game Design still has unresolved fundamentals including:

- exact D20 procedure;
- stakes contract;
- secondary narrative result;
- combat model;
- knowledge states;
- Force requirements;
- deterministic consequence semantics.

Therefore Product must not freeze a detailed MVP before the kickoff narrows these dependencies.

### Tension — Fast live-session UX versus explicit consequence confirmation

UX favors low-friction live operation while Product/Game Design also favor an explicit boundary before important mutations become canonical.

The kickoff must decide where confirmation is mandatory and where deterministic changes may apply directly.

### Tension — Persistent-world ambition versus over-simulation

Product value depends on continuity and persistent state.

Game Design correctly identifies the risk that persistence turns into continuous autonomous world simulation and excessive bookkeeping.

The current product position should be selective persistence of meaningful state, not simulation for its own sake.

### Tension — Extensibility versus solo-development constraints

Architecture preserves extension boundaries while Product must prevent those boundaries from becoming an MVP plugin-platform commitment.

No generic ecosystem, marketplace, or arbitrary runtime extensibility should be inferred from the accepted architecture.

## Assumptions not yet validated

Previous Product analysis assumed several points that `main` does not currently validate:

- the MVP must support a complete multi-session campaign rather than a smaller playable milestone followed by MVP expansion;
- initial procedural generation is part of the MVP;
- a player companion UI is used live by every player;
- `ActionResolution` should be persisted as a first-class concept;
- consequences are normally previewed before commit;
- generation should always use an explicit candidate/acceptance lifecycle;
- preparation and session are explicit UI modes;
- search is mandatory for the first playable release;
- the first slice should include knowledge revelation;
- the first slice should persist a Session record;
- combat is required early;
- archive is the normal removal behavior for campaign content;
- undo can be deferred in favor of history/correction;
- world authoring initially needs dedicated Location, NPC/Character, Faction, and Item concepts.

These are useful candidates for kickoff decisions, not repository facts.

## Open product questions for kickoff

1. What exact outcome defines the first playable vertical slice?
2. Which single GM workflow is the primary workflow of that slice?
3. Which player workflow, if any, must be exercised in the same slice?
4. What is the minimum product definition of MVP beyond the first slice?
5. Is procedural generation part of MVP, or a post-first-slice capability?
6. Is live-session contextual generation required for MVP?
7. Is a distinct live-session workflow an accepted product requirement?
8. Is a persistent `Session` concept required by the first slice?
9. Is `Scene` or an equivalent current-context model required, or can it be deferred?
10. Is `ActionResolution` required in the first slice?
11. Which consequence classes may commit automatically?
12. Which consequence classes always require GM confirmation?
13. What minimum correction/reversal guarantee is required after an incorrect mutation?
14. Is global campaign search a MUST for the first playable release?
15. What is the minimum player companion scope?
16. Must the first slice demonstrate knowledge disclosure and player-safe projections?
17. Is combat included in the first slice, later in MVP, or post-MVP?
18. Are tactical maps explicitly outside MVP?
19. Are vehicle and space-combat mechanics explicitly outside MVP?
20. Does MVP require story-thread/objective tracking as a dedicated capability?
21. Which world-entity types are actually required in the first slice?
22. Is generated-content staging required before persistence?
23. What content lifecycle is required: edit/archive/delete?
24. Which Game Design questions are blocking versus safely deferrable?
25. Which architecture proposals need acceptance before implementation of the first slice?
26. Should GM narrative authority be promoted from "To formalize" to an explicit accepted cross-domain decision at kickoff?

## Cross-domain dependencies

### GAME DESIGN IMPACT

Product cannot finalize the resolution-related MVP scope until Game Design defines the minimum semantics required by the accepted slice, including:

- when a roll occurs;
- stakes/risk semantics;
- the primary D20 result contract;
- any secondary narrative result;
- deterministic versus discretionary consequences;
- minimum character/combat/knowledge mechanics.

### UX IMPACT

Product must choose which workflows are product requirements before UX can finalize:

- preparation versus live-session information architecture;
- session workspace;
- search priority;
- player companion scope;
- consequence confirmation;
- knowledge reveal;
- quick/contextual creation;
- generated-candidate review.

### ARCHITECTURE IMPACT

Product must define the slice and MVP requirements before Architecture should finalize:

- persistence for Session/Scene if accepted;
- ActionResolution representation;
- candidate-generation lifecycle;
- correction/compensation guarantees;
- lifecycle/archive behavior;
- minimum authorization roles;
- which asynchronous use cases actually justify outbox processing in MVP.

### SECURITY IMPACT

Product requirements involving players, targeted knowledge, private actions, and generated/revealed content must preserve the accepted server-side disclosure boundary.

Product must never specify a workflow that depends on hidden canonical data already being sent to unauthorized clients.

## Minimal documentation needed before kickoff

This file is the minimum Product synchronization artifact required before kickoff.

No exhaustive backlog, roadmap, or final MVP specification should be added before cross-domain kickoff decisions.

After kickoff, Product should create or update only the documents needed to make accepted decisions authoritative, likely:

- product vision and primary personas;
- MVP scope and explicit exclusions;
- accepted first vertical slice;
- accepted cross-domain decisions in `docs/planning/decision-log.md`;
- concrete blocking questions in `docs/planning/open-questions.md`.

## Recommended kickoff order

The Product Lead should coordinate decisions in this order:

1. define the exact first playable GM/player scenario;
2. identify the minimum Game Design semantics required by that scenario;
3. define the matching UX workflow;
4. confirm the minimum architecture contracts needed for that workflow;
5. resolve blocking cross-domain questions;
6. record accepted decisions in the repository;
7. select and document the first vertical slice;
8. only then decompose it into implementation-ready stories/tasks.

## Implementation gate

This synchronization does not authorize implementation.

`docs/planning/current-slice.md` correctly remains unset until kickoff.

The implementation gate in `docs/planning/PROJECT_KICKOFF.md` remains authoritative.
