# Star Wars RP — Kickoff Decision Pack

Status: PROPOSED FOR CROSS-DOMAIN REVIEW  
Owner: Product Lead / Project Lead  
Branch: `ai/product/kickoff`  
Source of truth reviewed: `main`

## Purpose

This document is the common decision dossier for the Star Wars RP kickoff.

It consolidates the Product, Game Design, UX, Architecture, ADR, and planning material already present in `main`. It does **not** make unresolved cross-domain decisions authoritative by itself.

The intended workflow is:

1. Product prepares the decision pack.
2. Game Design, UX, and Architecture review the same PR contradictorily.
3. Open points are revised or explicitly retained.
4. The Human Project Owner arbitrates remaining decisions.
5. Accepted decisions are then written into the authoritative planning/product/game-design/UX/architecture documents.
6. Only after the implementation gate is satisfied is the first slice considered ready to implement.

## Status vocabulary used in this pack

- **ACCEPTED BASELINE** — already normative in `main`; not reopened here.
- **PROPOSED FOR KICKOFF** — recommendation requiring review/arbitration.
- **TO FORMALIZE** — direction already recorded in `main` but not yet formally Accepted.
- **DEFER CANDIDATE** — Product recommends explicitly postponing the decision or capability.
- **OPEN** — no recommendation can safely replace specialist review.

---

# Phase 1 — Repository analysis

## Accepted baseline

The following are already normative and are not reopened by this kickoff pack:

- Custom D20 is first-party for the MVP.
- PostgreSQL is the source of truth for mutable campaign state.
- Campaign isolation is enforced using `campaign_id`.
- `Entity` is an identity registry, not an untyped property bag.
- Stable first-party concepts use typed relational tables.
- Dynamic extension-owned data uses `EntityExtensionData` with `namespace`, `schema_id`, `schema_version`, and JSONB payload.
- `KnowledgeFragment` represents a campaign proposition/claim with GM-side veracity metadata.
- `CharacterKnowledge` represents one character's epistemic state toward a fragment; absence means unknown.
- Player endpoints use explicit player-facing projections/read models.
- Backend authorization and disclosure, not frontend hiding, protect GM-only information.
- `DomainEvent` is append-only history/audit data.
- Current state is not reconstructed through event sourcing.
- A transactional outbox is reserved for concrete durable asynchronous publication needs.
- Immediately consistent canonical rule effects execute synchronously with the triggering command.
- Platform Core is limited to genuinely cross-cutting concepts.
- Species, Class, Skills, Talents, progression, and Force mechanics belong to Custom D20.
- Setting Packs are primarily data-oriented and reference mechanics supported by Custom D20.
- The MVP does not require a dynamically interchangeable arbitrary game-system runtime.

## Strong cross-domain convergence

The four pre-kickoff syncs converge strongly, without yet making these points Accepted, on the following directions:

1. The product should optimize a persistent GM/player campaign workflow rather than become a general-purpose VTT.
2. Live play needs a short path from player intent to resolution, consequence, state mutation, and disclosure.
3. A structured Action Resolution / Stakes boundary is useful between fiction, Dice/Rules, consequences, and committed state.
4. Mechanical outcome must not silently become authoritative narrative truth.
5. Deterministic effects and interpretive/narrative consequences need different treatment.
6. Significant mutations need an explicit and understandable commit boundary.
7. Player disclosure must use backend projections.
8. Generated content should not silently become canonical.
9. Persistent-world ambition must not become continuous simulation and bookkeeping.
10. Any Rule Effect mechanism should remain bounded and slice-driven rather than become a general scripting language.
11. Tactical-map/grid complexity is not required to prove the core product.
12. Vehicle/space combat can reasonably be deferred while personal-scale play is validated.

## Primarily single-domain proposals

### Product-owned

- exact product positioning;
- persona priority;
- MVP scope and exclusions;
- first vertical slice;
- procedural-generation priority;
- combat/tactical-map/vehicle scope.

### Game Design-owned

- exact "when to roll" rule;
- minimum stakes contract;
- D20 numerical procedure;
- critical/degree/opposed rules;
- secondary narrative result;
- combat mechanics;
- exact knowledge epistemic states;
- progression and Force mechanics.

### UX-owned

- information architecture for preparation/live/world administration;
- one/two-interaction live-session targets;
- search presentation;
- consequence confirmation interaction;
- knowledge reveal interaction;
- generated-candidate review;
- meaningful history/activity presentation.

### Architecture-owned

- concrete application stack acceptance;
- persistence/API representation of ActionResolution;
- module dependency direction;
- transaction boundaries;
- authorization implementation;
- Session/Scene persistence if selected;
- extension lifecycle;
- generator candidate persistence if selected.

## Main tensions to resolve

### Speed versus explicit confirmation

Live UX must remain fast, but Product/Game Design/UX all resist silent mutation of meaningful campaign state.

### Persistent world versus over-simulation

Continuity is a product value. Continuous simulation of every NPC/faction/location is not.

### Rich knowledge model versus first-slice simplicity

The accepted architecture supports beliefs, misinformation, and provenance, but the first slice does not need to exercise the full epistemic design.

### Product differentiation versus first-slice scope

Procedural generation is likely part of the product promise, but putting generation into Slice 1 would couple the first implementation to unresolved candidate/persistence/gameplay semantics.

### Extensibility versus solo-development cost

Accepted extension boundaries must not be interpreted as a requirement to build an ecosystem, marketplace, generic plugin runtime, or large Rule DSL during MVP.

## Questions that genuinely block Slice 1

The following must be resolved or explicitly constrained before Slice 1 implementation:

- minimum GM/player roles and player-to-character assignment;
- core gameplay/resolution loop used by the slice;
- minimum stakes contract;
- minimum D20 check contract;
- deterministic versus interpretive consequence boundary;
- who confirms/commits effects;
- minimum ActionResolution trace/persistence contract;
- minimum knowledge state required for one targeted reveal;
- backend disclosure behavior for that reveal;
- minimum architecture stack/contracts required to implement the slice;
- acceptance of the exact Slice 1 scenario.

## Questions safe to defer beyond Slice 1

- secondary narrative die;
- crit and degree-of-success systems;
- opposed-roll rules;
- full combat;
- range bands;
- initiative;
- Vitality/Wounds;
- minion-group rules;
- progression;
- multiclassing;
- Force mechanics;
- Dark Side mechanics;
- persistent Session entity;
- persistent Scene entity;
- global search;
- procedural generation;
- generation reproducibility;
- generated-hook categories;
- off-screen faction simulation;
- tactical maps;
- vehicle/space combat;
- generic undo engine;
- full archive/delete lifecycle;
- knowledge provenance;
- dangerous-information mechanics;
- full Rule Effect DSL;
- extension enable/disable/upgrade lifecycle;
- outbox worker.

---

# Phase 2 — Kickoff decisions

## K-01 — Product vision

**STATUS:** PROPOSED FOR KICKOFF  
**DECISION OWNER:** Product Lead  
**AFFECTED DOMAINS:** Product, UX, Game Design, Architecture  
**BLOCKING:** NO

### CONTEXT

The project needs a stable product identity to prevent scope creep and to judge future features against a coherent value proposition.

### EVIDENCE / CURRENT POSITIONS

Product proposes a persistent campaign platform centered on editable campaign state, assisted resolution, knowledge/disclosure, authoring, and later generation/AI.

UX emphasizes GM efficiency during preparation and live play.

Game Design emphasizes simple mechanics with broad fictional possibility and selective simulation.

Architecture supports persistent campaign state and explicit GM/player disclosure boundaries.

### OPTIONS

1. General-purpose VTT with campaign-management features.
2. Worldbuilding database with optional play tools.
3. Persistent GM/player campaign platform with assisted authoring/resolution, without replacing a full VTT.
4. AI-first autonomous campaign/game-master system.

### TRADE-OFFS

Option 1 creates major map/token/realtime scope.  
Option 2 under-serves live play.  
Option 3 fits the existing design and solo-development constraint.  
Option 4 conflicts with GM authority and creates large AI/reliability scope.

### PRODUCT IMPACT

Defines feature prioritization around playable campaign continuity.

### GAME DESIGN IMPACT

Rules should support live campaign decisions rather than simulate every possibility.

### UX IMPACT

GM live workflow becomes a primary design concern.

### ARCHITECTURE IMPACT

No new architecture beyond the accepted persistent campaign model.

### SECURITY IMPACT

Player/GM separation remains a first-class product requirement.

### RECOMMENDATION

**Product recommends Option 3.** Star Wars RP should be a persistent campaign platform for GM and players, with authoring, resolution, knowledge, and generation assistance, not a general VTT or autonomous GM.

---

## K-02 — Primary personas

**STATUS:** PROPOSED FOR KICKOFF  
**DECISION OWNER:** Product Lead  
**AFFECTED DOMAINS:** Product, UX, Architecture  
**BLOCKING:** YES

### CONTEXT

Slice 1 needs explicit actors so authorization, workflows, and acceptance criteria are testable.

### EVIDENCE / CURRENT POSITIONS

Product previously identified GM as primary and Player as secondary. UX explicitly designs separate GM/player experiences. Architecture requires character ownership/membership rules for player projections.

### OPTIONS

1. GM only initially.
2. GM primary + Player secondary.
3. GM + Player + pack/content author as equal MVP personas.

### TRADE-OFFS

Option 1 avoids auth complexity but fails to validate player projections.  
Option 2 validates the central GM/player boundary with limited scope.  
Option 3 adds authoring/ecosystem concerns unrelated to the first playable loop.

### PRODUCT IMPACT

Determines whose workflow must be satisfied first.

### GAME DESIGN IMPACT

Requires only player-facing semantics relevant to the first slice.

### UX IMPACT

Requires a minimal player companion view.

### ARCHITECTURE IMPACT

Requires GM/Player role semantics and player-to-character assignment.

### SECURITY IMPACT

Requires backend-enforced membership and disclosure.

### RECOMMENDATION

**Product recommends Option 2:** GM is primary; Player is secondary. Content/pack author is post-MVP as a distinct persona.

---

## K-03 — MVP definition

**STATUS:** PROPOSED FOR KICKOFF  
**DECISION OWNER:** Product Lead / Human Project Owner  
**AFFECTED DOMAINS:** All  
**BLOCKING:** NO

### CONTEXT

The MVP must be narrow enough for one developer but rich enough to validate the product in a real campaign.

### EVIDENCE / CURRENT POSITIONS

Product previously proposed a multi-session playable campaign. UX prioritizes preparation/live workflows, search, and player-safe disclosure. Game Design still has many unresolved advanced systems. Architecture explicitly favors incremental, slice-driven scope.

### OPTIONS

1. Technical prototype proving persistence and security only.
2. Playable MVP supporting a small multi-session campaign with manual authoring, Custom D20 resolution, knowledge, personal-scale combat, search, persistence, and bounded initial procedural generation.
3. Broad campaign platform including tactical maps, vehicles, AI assistance, progression, full generation, and advanced extensibility.

### TRADE-OFFS

Option 1 does not validate the product promise.  
Option 2 is substantial but can be built incrementally through slices.  
Option 3 is incompatible with solo-development scope.

### PRODUCT IMPACT

Defines the release boundary and roadmap.

### GAME DESIGN IMPACT

Requires only game systems needed for real personal-scale campaign play.

### UX IMPACT

Requires usable GM and player workflows, not every administration feature.

### ARCHITECTURE IMPACT

Allows architecture to remain modular-monolith and slice-driven.

### SECURITY IMPACT

Player-safe disclosure and campaign isolation are MVP requirements.

### RECOMMENDATION

**Product recommends Option 2.** Initial procedural generation and personal-scale combat belong to the MVP, but neither belongs to Slice 1. Advanced AI, tactical maps, vehicles/space combat, and generic extensibility do not.

---

## K-04 — Core gameplay loop

**STATUS:** PROPOSED FOR KICKOFF  
**DECISION OWNER:** Product Lead with Game Design and UX review  
**AFFECTED DOMAINS:** Product, Game Design, UX, Architecture  
**BLOCKING:** YES

### CONTEXT

The implementation gate requires a defined core gameplay loop.

### EVIDENCE / CURRENT POSITIONS

Product proposes prepare -> situation -> player action -> resolution -> consequences -> world/knowledge update -> continue -> save/resume.

Game Design proposes fictional positioning -> intent -> approach -> GM roll decision -> stakes -> mechanic -> roll -> outcome -> consequences -> state/disclosure -> new fiction.

UX proposes a live workflow centered on context, search, resolution, consequences, disclosure, and recent activity.

### OPTIONS

1. Dice-centric loop: choose mechanic -> roll -> update sheet.
2. Fiction-first loop with explicit intent/stakes and consequence boundary.
3. Fully freeform narrative with optional disconnected dice utilities.

### TRADE-OFFS

Option 1 loses the connection between fiction and persistent consequences.  
Option 2 matches all three disciplines but needs a compact live UX.  
Option 3 weakens the product's assisted-resolution value.

### PRODUCT IMPACT

Option 2 establishes the central assisted-play value.

### GAME DESIGN IMPACT

Requires a minimal "when to roll" and stakes contract.

### UX IMPACT

Must avoid turning each check into long form filling.

### ARCHITECTURE IMPACT

Requires correlation between resolution, effects, and history.

### SECURITY IMPACT

Any disclosure resulting from the loop must respect player projections.

### RECOMMENDATION

**Product recommends Option 2**, subject to Game Design confirming the resolution semantics and UX confirming the live interaction cost.

---

## K-05 — GM authority

**STATUS:** TO FORMALIZE  
**DECISION OWNER:** Product Lead / Game Design  
**AFFECTED DOMAINS:** All  
**BLOCKING:** YES

### CONTEXT

The decision log already records "GM retains final narrative authority" as To formalize. Consequence automation cannot be specified safely until this is explicit.

### EVIDENCE / CURRENT POSITIONS

Product, Game Design, UX, and Architecture all assume that significant narrative/canonical changes are not imposed silently.

### OPTIONS

1. System may automatically commit any rule-derived consequence.
2. GM retains final authority over interpretive and authoritative narrative/canonical changes; bounded deterministic effects may be automated under an accepted commit policy.
3. Every change, including HP/resource arithmetic, always requires bespoke GM adjudication.

### TRADE-OFFS

Option 1 undermines GM authority.  
Option 2 preserves assistance while retaining narrative control.  
Option 3 adds unnecessary friction.

### PRODUCT IMPACT

Defines the product as an assistant to the GM, not a replacement.

### GAME DESIGN IMPACT

Requires classification of deterministic versus interpretive consequences.

### UX IMPACT

Requires a clear confirmation model for meaningful changes.

### ARCHITECTURE IMPACT

Requires separation between proposed and committed effects where relevant.

### SECURITY IMPACT

No special change beyond GM-only authorization for adjudication.

### RECOMMENDATION

**Product recommends Option 2 and formalizing D-004 as ACCEPTED after Game Design review and Human approval.**

---

## K-06 — Action resolution / stakes

**STATUS:** PROPOSED FOR KICKOFF  
**DECISION OWNER:** Game Design for semantics; Product for capability; Architecture for representation  
**AFFECTED DOMAINS:** All  
**BLOCKING:** YES

### CONTEXT

Dice rolls without intent, risk, and consequence context cannot support meaningful assisted mutation/history.

### EVIDENCE / CURRENT POSITIONS

Product, Game Design, and UX independently converge on an ActionResolution/Stakes concept. Architecture has not accepted a persistence shape.

Game Design proposes minimum stakes of Intent + Risk and distinguishes intent from approach.

### OPTIONS

1. Persist only raw dice rolls.
2. Minimal structured resolution: actor, optional target/context, intent, risk, selected mechanic, difficulty, roll/result, proposed effects, applied effects/history correlation.
3. General workflow engine modeling all branches before rolling.

### TRADE-OFFS

Option 1 loses the meaningful link between action and state change.  
Option 2 captures enough semantics for the product while remaining bounded.  
Option 3 over-models narrative play.

### PRODUCT IMPACT

Option 2 enables assisted consequences and meaningful history.

### GAME DESIGN IMPACT

Game Design must approve the minimum semantic contract.

### UX IMPACT

The live form must stay compact; intent/risk should not become a branching editor.

### ARCHITECTURE IMPACT

Architecture must decide whether this is one aggregate/table, several records, or another representation.

### SECURITY IMPACT

GM-only fields and player-visible result information may require different projections.

### RECOMMENDATION

**Product recommends Option 2 as a capability requirement, not as a prescribed schema. Game Design and Architecture review are required.**

---

## K-07 — Minimum D20 contract for Slice 1

**STATUS:** OPEN — GAME DESIGN REVIEW REQUIRED  
**DECISION OWNER:** Game Design  
**AFFECTED DOMAINS:** Game Design, UX, Architecture, Product  
**BLOCKING:** YES

### CONTEXT

Slice 1 needs one real resolution mechanic but should not freeze the whole Custom D20 system.

### EVIDENCE / CURRENT POSITIONS

Game Design supports a recognizable D20 check against difficulty/resistance but has not accepted difficulty scale, crits, degree thresholds, opposed rolls, modifier budget, or secondary narrative die.

### OPTIONS

1. Slice 1 waits for the complete Custom D20 design.
2. Accept a deliberately minimal slice contract: `1d20 + resolved modifier >= DC`; persist natural roll, modifier, total, DC, and binary outcome; defer crits, degrees, opposed rolls, advantage/disadvantage details, and secondary die.
3. Use a temporary mechanic unrelated to intended Custom D20.

### TRADE-OFFS

Option 1 blocks implementation on unrelated game-design breadth.  
Option 2 validates the integration seam without prematurely freezing advanced rules.  
Option 3 creates throwaway behavior and migration risk.

### PRODUCT IMPACT

Option 2 is sufficient to test the core loop.

### GAME DESIGN IMPACT

Game Design must approve or replace the exact minimal formula and determine how a resolved modifier is obtained.

### UX IMPACT

Only one simple check needs to be presented in Slice 1.

### ARCHITECTURE IMPACT

Persistence should record inputs/results without assuming future advanced fields are impossible.

### SECURITY IMPACT

Roll creation/adjudication permissions must be explicit.

### RECOMMENDATION

**Product requests Game Design review of Option 2.** Product does not claim authority to accept the D20 formula.

---

## K-08 — Deterministic versus interpretive consequences

**STATUS:** PROPOSED FOR KICKOFF  
**DECISION OWNER:** Game Design with Product/UX review  
**AFFECTED DOMAINS:** All  
**BLOCKING:** YES

### CONTEXT

The system needs a bounded rule for what may be calculated/applied automatically and what remains adjudication.

### EVIDENCE / CURRENT POSITIONS

Product and Game Design converge on three broad classes:

- deterministic mechanical/explicit effects;
- bounded interpretive narrative consequences;
- authoritative narrative/canonical changes.

### OPTIONS

1. Binary split: automatic versus manual.
2. Three classes as above.
3. Per-rule freeform configuration with no global semantics.

### TRADE-OFFS

Option 1 is simpler but collapses useful distinctions.  
Option 2 matches current convergence and supports future automation policy.  
Option 3 creates inconsistent behavior and configuration burden.

### PRODUCT IMPACT

Option 2 gives users predictable automation.

### GAME DESIGN IMPACT

Game Design owns classification semantics.

### UX IMPACT

UI can present deterministic effects differently from interpretive suggestions.

### ARCHITECTURE IMPACT

Effect types can remain bounded rather than generic scripts.

### SECURITY IMPACT

Only authorized actors may commit campaign-changing effects.

### RECOMMENDATION

**Product recommends Option 2, subject to Game Design approval.**

---

## K-09 — Confirmation / commit boundary

**STATUS:** PROPOSED FOR KICKOFF  
**DECISION OWNER:** Cross-domain  
**AFFECTED DOMAINS:** Product, Game Design, UX, Architecture  
**BLOCKING:** YES

### CONTEXT

The team must choose how a calculated effect becomes canonical mutable state.

### EVIDENCE / CURRENT POSITIONS

UX wants explicit action for significant mutations. Game Design warns against mechanical outcomes silently becoming narrative truth. Product favors a proposed -> accepted -> committed boundary. Architecture requires immediately consistent effects to execute synchronously when committed.

### OPTIONS

1. Auto-commit every deterministic effect immediately after the roll.
2. For Slice 1, calculate deterministic effects and require one GM **Apply** action; interpretive consequences always require GM selection/edit/acceptance. Revisit selective auto-apply after playtesting.
3. Require per-effect confirmation forever.

### TRADE-OFFS

Option 1 maximizes speed but increases surprise/correction requirements.  
Option 2 is safe, simple, and provides a future migration path to auto-apply.  
Option 3 may create excessive click cost.

### PRODUCT IMPACT

Option 2 validates automation without overcommitting.

### GAME DESIGN IMPACT

Effects must be deterministic before they can appear as precomputed proposals.

### UX IMPACT

Needs a compact preview + Apply interaction.

### ARCHITECTURE IMPACT

Commit must be transactional with state mutation and history event.

### SECURITY IMPACT

Only an authorized GM commits the effect in Slice 1.

### RECOMMENDATION

**Product recommends Option 2 for Slice 1.**

---

## K-10 — Preparation versus live-session workflow

**STATUS:** PROPOSED FOR KICKOFF  
**DECISION OWNER:** Product Lead; UX owns interaction design  
**AFFECTED DOMAINS:** Product, UX, Architecture  
**BLOCKING:** NO

### CONTEXT

Preparation favors depth; live play favors speed. The question is whether this becomes a product requirement now.

### EVIDENCE / CURRENT POSITIONS

Product proposes preparation/live separation. UX proposes preparation/live/world-administration contexts. No persistent Session or Scene is required by that recommendation.

### OPTIONS

1. One undifferentiated UI.
2. Distinct preparation and live-play workflows over the same domain state; world administration may remain a lower-priority context.
3. Separate preparation and live applications/data models.

### TRADE-OFFS

Option 1 risks poor live ergonomics.  
Option 2 preserves one model while optimizing workflows.  
Option 3 duplicates state and implementation.

### PRODUCT IMPACT

Option 2 supports the core value without architectural duplication.

### GAME DESIGN IMPACT

No rules change.

### UX IMPACT

UX must define the minimal live surface after kickoff.

### ARCHITECTURE IMPACT

No duplicate domain models should be inferred.

### SECURITY IMPACT

Same authorization rules apply across contexts.

### RECOMMENDATION

**Product recommends Option 2.** Slice 1 may implement only the minimal live workflow necessary to prove the loop.

---

## K-11 — Minimum player experience

**STATUS:** PROPOSED FOR KICKOFF  
**DECISION OWNER:** Product Lead with UX review  
**AFFECTED DOMAINS:** Product, UX, Architecture, Security  
**BLOCKING:** YES

### CONTEXT

Slice 1 must exercise the accepted player-projection boundary without building a full player application.

### EVIDENCE / CURRENT POSITIONS

Product proposes a deliberately narrower player experience. UX asks for character, resources, knowledge, objectives, and actions but acknowledges scope requires prioritization. ADR-003 mandates explicit player projections.

### OPTIONS

1. No player UI in Slice 1.
2. Minimal companion: authenticate/join campaign, view assigned character summary, view currently disclosed knowledge, observe newly revealed knowledge after GM action.
3. Full player sheet, inventory, rolls, journal, messaging, combat, objectives, history.

### TRADE-OFFS

Option 1 fails to validate the primary security/projection boundary.  
Option 2 validates it cheaply.  
Option 3 is too broad for Slice 1.

### PRODUCT IMPACT

Option 2 proves a real GM/player loop.

### GAME DESIGN IMPACT

Only minimal character and knowledge semantics are required.

### UX IMPACT

Requires a simple read-oriented player surface.

### ARCHITECTURE IMPACT

Requires membership, character assignment, and projection endpoints.

### SECURITY IMPACT

This is a primary Slice 1 security test: hidden knowledge must not reach the player before reveal.

### RECOMMENDATION

**Product recommends Option 2.**

---

## K-12 — Knowledge / disclosure required for MVP

**STATUS:** PROPOSED FOR KICKOFF  
**DECISION OWNER:** Product for scope; Game Design for epistemic semantics; Architecture for projection  
**AFFECTED DOMAINS:** All  
**BLOCKING:** YES

### CONTEXT

Knowledge is both a differentiator and an already accepted architecture boundary. Slice 1 should validate it without requiring the full misinformation/provenance system.

### EVIDENCE / CURRENT POSITIONS

ADR-002 and ADR-003 are Accepted. Game Design considers knowledge a gameplay system and keeps exact states open. UX wants targeted reveal and explicit preview.

### OPTIONS

1. Defer knowledge from Slice 1.
2. Slice 1 supports one GM-only `KnowledgeFragment` and targeted reveal to one character; nuanced states/provenance are deferred.
3. Implement full aware/believed/doubted/provenance/misinformation mechanics immediately.

### TRADE-OFFS

Option 1 leaves accepted disclosure architecture untested.  
Option 2 tests the critical boundary with minimal semantics.  
Option 3 over-scopes Game Design and UI.

### PRODUCT IMPACT

Option 2 validates an important differentiator early.

### GAME DESIGN IMPACT

Game Design must approve the minimum meaning of the first visible state; nuanced epistemic states remain open.

### UX IMPACT

Needs a clear reveal action and player-visible result.

### ARCHITECTURE IMPACT

Uses accepted KnowledgeFragment/CharacterKnowledge and projection boundaries.

### SECURITY IMPACT

The secret must be absent from unauthorized player responses before reveal.

### RECOMMENDATION

**Product recommends Option 2.**

---

## K-13 — Persistent Session concept

**STATUS:** DEFER CANDIDATE  
**DECISION OWNER:** Product for need; Architecture for model; UX for workflow  
**AFFECTED DOMAINS:** Product, UX, Architecture  
**BLOCKING:** NO

### CONTEXT

UX proposes a persistent Session to group participants, resolutions, discoveries, notes, and history. Product previously assumed sessions but has not proven a persistence requirement.

### EVIDENCE / CURRENT POSITIONS

No Accepted decision requires Session. The first playable loop can be correlated by campaign, timestamp, actor, and resolution without a Session entity.

### OPTIONS

1. Require Session entity in Slice 1.
2. Use a live workflow without persistent Session in Slice 1; revisit for later MVP when grouping/notes/resume needs are concrete.
3. Reject Session permanently.

### TRADE-OFFS

Option 1 adds lifecycle and API scope early.  
Option 2 keeps the door open with less initial complexity.  
Option 3 is premature because later campaign continuity may benefit from it.

### PRODUCT IMPACT

Option 2 keeps Slice 1 small.

### GAME DESIGN IMPACT

No immediate effect.

### UX IMPACT

Live UI must not depend on persistent Session identity initially.

### ARCHITECTURE IMPACT

Avoids an unproven aggregate.

### SECURITY IMPACT

No additional scope.

### RECOMMENDATION

**Product recommends Option 2.**

---

## K-14 — Scene / current context

**STATUS:** DEFER CANDIDATE  
**DECISION OWNER:** Product for need; UX for workflow; Architecture for model  
**AFFECTED DOMAINS:** Product, UX, Architecture, Game Design  
**BLOCKING:** NO

### CONTEXT

UX proposes Scene or equivalent context linking current location, present actors, threads, and encounter state.

### EVIDENCE / CURRENT POSITIONS

No Accepted decision requires Scene. Slice 1 uses one known location and does not need a generalized context aggregate.

### OPTIONS

1. Persist Scene in Slice 1.
2. Use current location/context as workflow/read-state only and revisit a persistent Scene when multiple live-context requirements exist.
3. Reject Scene permanently.

### TRADE-OFFS

Option 1 adds lifecycle and relationship semantics.  
Option 2 avoids premature domain modeling.  
Option 3 may block later session ergonomics.

### PRODUCT IMPACT

Option 2 supports incremental design.

### GAME DESIGN IMPACT

Encounter/turn semantics can later inform Scene requirements.

### UX IMPACT

UX can design context without assuming persistence.

### ARCHITECTURE IMPACT

No Scene schema/API required yet.

### SECURITY IMPACT

No additional scope.

### RECOMMENDATION

**Product recommends Option 2.**

---

## K-15 — Search priority

**STATUS:** PROPOSED FOR KICKOFF  
**DECISION OWNER:** Product Lead with UX review  
**AFFECTED DOMAINS:** Product, UX, Architecture  
**BLOCKING:** NO

### CONTEXT

UX considers global campaign search high priority for live play, but Slice 1 operates on a deliberately tiny dataset.

### EVIDENCE / CURRENT POSITIONS

UX strongly favors search as a primary live interaction. Product previously considered it likely MVP. Architecture has no blocker.

### OPTIONS

1. Search in Slice 1.
2. Search is MUST for MVP but not Slice 1.
3. Search post-MVP.

### TRADE-OFFS

Option 1 spends effort before enough entities exist to validate relevance.  
Option 2 preserves UX value while protecting the first slice.  
Option 3 risks unusable live navigation once world size grows.

### PRODUCT IMPACT

Option 2 aligns scope with actual need.

### GAME DESIGN IMPACT

None.

### UX IMPACT

Search should be designed before the world grows substantially.

### ARCHITECTURE IMPACT

Can begin with PostgreSQL-backed search; no separate search platform should be assumed.

### SECURITY IMPACT

Search results must obey campaign and player disclosure rules.

### RECOMMENDATION

**Product recommends Option 2.**

---

## K-16 — Procedural generation priority

**STATUS:** PROPOSED FOR KICKOFF  
**DECISION OWNER:** Product Lead / Human Project Owner  
**AFFECTED DOMAINS:** Product, Game Design, UX, Architecture  
**BLOCKING:** NO

### CONTEXT

Procedural generation is part of the intended product value but introduces unresolved candidate, review, reproducibility, and gameplay-content questions.

### EVIDENCE / CURRENT POSITIONS

Product sees generation as authoring assistance. UX requires generated content not silently becoming canonical. Game Design wants generated situations, not only encyclopedic data. Architecture keeps candidate persistence/reproducibility open.

### OPTIONS

1. Include generation in Slice 1.
2. Generation is MUST for MVP but introduced after manual authoring/resolution/disclosure foundations are validated.
3. Generation post-MVP.

### TRADE-OFFS

Option 1 couples the first slice to multiple unresolved domains.  
Option 2 protects Slice 1 while retaining the differentiating promise.  
Option 3 weakens the intended product positioning.

### PRODUCT IMPACT

Option 2 preserves differentiation without destabilizing foundations.

### GAME DESIGN IMPACT

Later generation must produce playable situations using accepted rules/content semantics.

### UX IMPACT

Later flow should support generate -> inspect/edit -> accept/reject.

### ARCHITECTURE IMPACT

Candidate persistence/reproducibility can be designed when the generation slice is selected.

### SECURITY IMPACT

Generated GM-only content must respect disclosure rules after acceptance.

### RECOMMENDATION

**Product recommends Option 2.**

---

## K-17 — Combat priority

**STATUS:** PROPOSED FOR KICKOFF  
**DECISION OWNER:** Product for scope; Game Design for mechanics  
**AFFECTED DOMAINS:** Product, Game Design, UX, Architecture  
**BLOCKING:** NO

### CONTEXT

A Star Wars RPG MVP should eventually validate personal-scale conflict, but combat mechanics are among the least mature Game Design areas.

### EVIDENCE / CURRENT POSITIONS

Game Design proposes cinematic, objective-driven combat with abstract position but has not accepted initiative, health, armour, weapons, actions, or reactions.

### OPTIONS

1. Combat in Slice 1.
2. Personal-scale combat later in MVP after the generic action-resolution loop is proven.
3. Combat post-MVP.

### TRADE-OFFS

Option 1 forces many unresolved rules into the first slice.  
Option 2 allows the resolution foundation to be reused and validates a real RPG before MVP completion.  
Option 3 may make the MVP insufficiently representative of Star Wars play.

### PRODUCT IMPACT

Option 2 balances product completeness with sequencing.

### GAME DESIGN IMPACT

Game Design gets time to specify a bounded combat contract.

### UX IMPACT

No initiative/encounter UI in Slice 1.

### ARCHITECTURE IMPACT

Avoids premature combat aggregates.

### SECURITY IMPACT

No Slice 1 impact.

### RECOMMENDATION

**Product recommends Option 2.**

---

## K-18 — Tactical maps

**STATUS:** DEFER CANDIDATE  
**DECISION OWNER:** Product Lead with UX/Game Design review  
**AFFECTED DOMAINS:** Product, Game Design, UX, Architecture  
**BLOCKING:** NO

### CONTEXT

Tactical maps create a large VTT-like surface area.

### EVIDENCE / CURRENT POSITIONS

Game Design prefers abstract range bands over grid arithmetic. Product is not positioned as a general VTT.

### OPTIONS

1. Tactical map required for MVP.
2. Tactical maps explicitly post-MVP; personal-scale combat uses abstract positioning first.
3. Tactical map never supported.

### TRADE-OFFS

Option 1 adds maps, tokens, measurement, spatial synchronization, and UX complexity.  
Option 2 tests combat without becoming a VTT.  
Option 3 unnecessarily forecloses a future enhancement.

### PRODUCT IMPACT

Option 2 keeps MVP focused.

### GAME DESIGN IMPACT

Requires combat to work without grid geometry.

### UX IMPACT

No map editor/token UX initially.

### ARCHITECTURE IMPACT

No spatial engine/realtime map state required.

### SECURITY IMPACT

No special impact.

### RECOMMENDATION

**Product recommends Option 2.**

---

## K-19 — Vehicle and space combat

**STATUS:** DEFER CANDIDATE  
**DECISION OWNER:** Product Lead with Game Design review  
**AFFECTED DOMAINS:** Product, Game Design, UX, Architecture  
**BLOCKING:** NO

### CONTEXT

Vehicle and space combat are important Star Wars fantasies but introduce additional movement, scale, damage, crew, and encounter semantics.

### EVIDENCE / CURRENT POSITIONS

Game Design explicitly recommends post-MVP unless the first slice proves otherwise.

### OPTIONS

1. Include in first slice.
2. Include in MVP.
3. Explicitly post-MVP after personal-scale combat is validated.

### TRADE-OFFS

Options 1 and 2 materially expand Game Design and UI before core play is validated.  
Option 3 preserves future reuse of proven primitives.

### PRODUCT IMPACT

Option 3 is the strongest scope-control choice.

### GAME DESIGN IMPACT

Allows later reuse rather than parallel rules design.

### UX IMPACT

No cockpit/vehicle/space encounter UI in MVP.

### ARCHITECTURE IMPACT

No vehicle-combat subsystem now.

### SECURITY IMPACT

No impact.

### RECOMMENDATION

**Product recommends Option 3.**

---

## K-20 — Correction / undo requirements

**STATUS:** PROPOSED FOR KICKOFF  
**DECISION OWNER:** Product for requirement; UX for interaction; Architecture for semantics  
**AFFECTED DOMAINS:** Product, UX, Architecture, Game Design  
**BLOCKING:** NO

### CONTEXT

Automation creates the possibility of wrong or unintended mutations. A generic undo engine is costly, especially without event sourcing.

### EVIDENCE / CURRENT POSITIONS

UX wants correction after significant mutations. Product previously recommended targeted correction over global undo. Architecture uses current state + append-only history, not event sourcing.

### OPTIONS

1. Generic one-click undo for all mutations.
2. MVP requires explicit corrective edits/commands plus meaningful history; targeted undo may be added only for specific operations.
3. No correction support; manual database repair if mistakes occur.

### TRADE-OFFS

Option 1 creates substantial compensation/dependency complexity.  
Option 2 provides operational safety without an undo framework.  
Option 3 is unacceptable for a GM-facing tool.

### PRODUCT IMPACT

Option 2 is sufficient for MVP confidence.

### GAME DESIGN IMPACT

Corrections must not accidentally trigger unrelated rule effects.

### UX IMPACT

History should make the previous change understandable; correction path must be discoverable.

### ARCHITECTURE IMPACT

Requires normal mutation commands and history; no inverse-event infrastructure.

### SECURITY IMPACT

Corrections remain authorized mutations.

### RECOMMENDATION

**Product recommends Option 2. Slice 1 does not require generic undo.**

---

## K-21 — Edit / archive / delete lifecycle

**STATUS:** PROPOSED FOR KICKOFF  
**DECISION OWNER:** Product for lifecycle requirement; UX/Architecture review  
**AFFECTED DOMAINS:** Product, UX, Architecture  
**BLOCKING:** NO

### CONTEXT

Persistent campaign content accumulates references, history, and secrets. Hard deletion can break continuity.

### EVIDENCE / CURRENT POSITIONS

UX recommends archive/deactivate as the routine destructive action. Product previously considered archive preferable but unaccepted.

### OPTIONS

1. Full hard-delete CRUD.
2. Edit is required; archive/deactivate becomes normal removal in MVP; hard delete is restricted to safe/unreferenced or administrative cases and can be deferred.
3. Never permit deletion.

### TRADE-OFFS

Option 1 risks referential/history damage.  
Option 2 preserves continuity with manageable semantics.  
Option 3 may create unnecessary clutter and operational constraints.

### PRODUCT IMPACT

Option 2 supports persistent campaigns.

### GAME DESIGN IMPACT

Archived entities can remain historically referenced without being active.

### UX IMPACT

Archive should be reversible and distinct from permanent deletion.

### ARCHITECTURE IMPACT

Architecture must define lifecycle flags/constraints when the capability is implemented.

### SECURITY IMPACT

Destructive actions require GM authorization.

### RECOMMENDATION

**Product recommends Option 2 for MVP, but archive/delete is not required in Slice 1.**

---

## K-22 — Minimum architecture contracts

**STATUS:** OPEN — ARCHITECTURE REVIEW REQUIRED  
**DECISION OWNER:** Architecture  
**AFFECTED DOMAINS:** Architecture, Security, Product, UX, Game Design  
**BLOCKING:** YES

### CONTEXT

Architecture has accepted the domain/data boundaries but still lists the concrete application stack and detailed module direction as proposals.

### EVIDENCE / CURRENT POSITIONS

The Architecture sync proposes React + FastAPI modular monolith + PostgreSQL and Docker Compose. Accepted ADRs already define Entity, Knowledge, projections, events/outbox, and Custom D20 boundaries.

### OPTIONS

1. Finalize a broad architecture before Slice 1.
2. Accept only the minimum contracts required by Slice 1 and keep broader module/generator/extension design deferred.
3. Implement without explicit architecture contracts.

### TRADE-OFFS

Option 1 risks horizontal over-design.  
Option 2 fits vertical-slice and solo-development constraints.  
Option 3 risks incompatible implementation decisions.

### PRODUCT IMPACT

Option 2 provides enough stability to start implementation after kickoff.

### GAME DESIGN IMPACT

Architecture must not freeze unresolved rule semantics.

### UX IMPACT

API shape must support the selected GM/player workflow and disclosure boundary.

### ARCHITECTURE IMPACT

Product proposes that Architecture review at least these Slice 1 contracts:

- concrete stack: React + FastAPI modular monolith + PostgreSQL;
- Docker Compose for local orchestration if still appropriate;
- GM and Player campaign membership/authorization;
- player-to-character assignment;
- strict `campaign_id` scoping;
- one explicit player read projection;
- persistent trace of the check/resolution sufficient to correlate intent, risk, roll, outcome, applied consequence, and history;
- synchronous transaction for an accepted immediate effect + current-state mutation + `DomainEvent`;
- no outbox worker unless Slice 1 produces a real asynchronous durability requirement;
- no generic Rule Effect DSL in Slice 1: at most the single typed effect needed by the scenario;
- no Session/Scene persistence in Slice 1;
- no generated-candidate persistence in Slice 1.

The exact tables, aggregates, endpoints, and module boundaries remain Architecture-owned.

### SECURITY IMPACT

Authorization, campaign isolation, character assignment, and projection correctness are non-negotiable acceptance criteria.

### RECOMMENDATION

**Product recommends Option 2 and requests Architecture to approve, amend, or reject the listed minimum contracts.**

---

## K-23 — First playable vertical slice

**STATUS:** PROPOSED FOR KICKOFF  
**DECISION OWNER:** Product Lead / Human Project Owner with cross-domain review  
**AFFECTED DOMAINS:** All  
**BLOCKING:** YES

### CONTEXT

The first slice must validate a real GM/player loop without importing combat, generation, Session/Scene, search, advanced knowledge states, or a generic rules engine.

### EVIDENCE / CURRENT POSITIONS

All disciplines need a concrete scenario before they can close their blocking questions. The accepted knowledge/projection architecture is valuable to exercise early. Game Design's unresolved combat breadth makes a non-combat check a safer first resolution.

### OPTIONS

1. CRUD-only campaign/character/world slice.
2. Non-combat "slice a terminal and reveal a secret" loop using one Custom D20 check, one consequence application, and one player-safe knowledge reveal.
3. Full encounter including combat, initiative, generation, and session tracking.

### TRADE-OFFS

Option 1 does not test the gameplay loop.  
Option 2 crosses Product, Game Design, UX, Architecture, persistence, permissions, and disclosure with bounded mechanics.  
Option 3 forces too many open systems into the first implementation.

### PRODUCT IMPACT

Option 2 validates the core assisted-play hypothesis.

### GAME DESIGN IMPACT

Requires only a minimal check/stakes contract.

### UX IMPACT

Requires minimal GM authoring, live resolution, Apply, reveal, and player read surfaces.

### ARCHITECTURE IMPACT

Exercises campaign isolation, entities, character, knowledge, projection, resolution trace, transaction, and DomainEvent.

### SECURITY IMPACT

Directly tests that the player cannot access the secret before reveal.

### RECOMMENDATION

**Product recommends Option 2. Detailed Slice 1 specification is in Phase 3 below.**

---

## K-24 — Explicit MVP exclusions

**STATUS:** PROPOSED FOR KICKOFF  
**DECISION OWNER:** Product Lead / Human Project Owner  
**AFFECTED DOMAINS:** All  
**BLOCKING:** NO

### CONTEXT

Scope control requires explicit non-goals so future design discussions do not silently expand MVP.

### EVIDENCE / CURRENT POSITIONS

All pre-kickoff syncs warn against over-generalization, over-simulation, and premature feature breadth.

### OPTIONS

1. Keep exclusions implicit.
2. Explicitly list MVP exclusions and reopen them only through a deliberate Product decision.

### TRADE-OFFS

Option 1 encourages scope creep.  
Option 2 provides a stable planning boundary while allowing later reconsideration.

### PRODUCT IMPACT

Improves prioritization and solo-development feasibility.

### GAME DESIGN IMPACT

Avoids designing complete systems that are not needed yet.

### UX IMPACT

Avoids VTT-like and administration-heavy surfaces before validated need.

### ARCHITECTURE IMPACT

Avoids infrastructure for hypothetical future features.

### SECURITY IMPACT

Reduces unnecessary attack surface.

### RECOMMENDATION

**Product recommends Option 2. Proposed MVP exclusions:**

- tactical maps/grid/token engine;
- vehicle and space combat;
- generic hot-swappable game-system runtime;
- plugin marketplace/ecosystem;
- arbitrary user scripting;
- generic Rule Effect programming language;
- full event sourcing;
- generic global undo engine;
- continuous autonomous world/faction/NPC simulation;
- advanced AI/autonomous GM;
- voice/video/chat platform;
- advanced knowledge provenance/infohazard mechanics unless a later accepted slice requires them;
- full progression/Force/Dark Side breadth beyond what accepted MVP gameplay slices require;
- advanced multi-GM permission models;
- elaborate pack-author tooling.

---

# Phase 3 — Proposed First Vertical Slice

## Slice 1 — "Slice the terminal, reveal the secret"

**Status:** PROPOSED FOR CROSS-DOMAIN REVIEW

### Product goal

Prove that one GM and one player can use the application to move from persistent campaign context to a real D20 action, commit one consequence, safely reveal previously hidden information, and reload the resulting state.

This slice is intentionally **not** a combat, generation, search, Session, Scene, or AI slice.

## User scenario

During a Star Wars session, a player character wants to slice an Imperial cargo terminal to discover where a confiscated shipment was transferred.

The GM has already authored a campaign, one player character, one location, and one hidden knowledge fragment.

The player cannot see the fragment before the action.

The player declares the intended action at the table. In Slice 1 this declaration does not need a dedicated player-to-GM messaging feature.

The GM creates a resolution with:

- actor: the assigned player character;
- context/target: the Imperial cargo terminal or current location reference;
- intent: discover where the confiscated shipment was transferred;
- risk: the intrusion may be noticed;
- mechanic/skill: the single Custom D20 skill/check supported by the slice;
- difficulty: a GM-selected DC supported by the minimum Game Design contract.

The system rolls/resolves the check.

On success, the system proposes one deterministic consequence:

- reveal a predefined `KnowledgeFragment` to the acting character.

The GM sees exactly what will change and chooses **Apply**.

The application creates/updates the required `CharacterKnowledge`, writes meaningful history, and the player's projection now includes the discovered information.

If the check fails, the slice only needs to persist the failed resolution and show the declared risk to the GM for narrative adjudication. The slice does **not** need a generic persistent consequence engine for the failure risk.

## Actors

### GM

- owns/manages the campaign;
- creates the minimal campaign content;
- sees canonical/hidden information;
- initiates and adjudicates the resolution;
- commits the deterministic reveal effect.

### Player

- is a member of the campaign;
- is assigned to one player character;
- can read the allowed projection of that character;
- cannot access GM-only knowledge;
- can observe the newly revealed knowledge after the GM applies the result.

## Initial state

The UI must allow the GM to establish, at minimum:

- one Campaign;
- one GM membership;
- one Player membership;
- one player-to-character assignment;
- one Player Character with the precomputed skill/modifier required by the accepted minimal D20 contract;
- one Location;
- optionally one target/world object only if Architecture/UX judge it necessary; otherwise the location can provide resolution context;
- one hidden `KnowledgeFragment` whose GM-side veracity is defined;
- no `CharacterKnowledge` for that fragment at the start.

No procedural generator is used.

## GM actions

1. Create/open campaign.
2. Create or select the player character.
3. Create/select the location.
4. Create the hidden knowledge fragment.
5. Verify that the player does not currently know it.
6. Start the live resolution workflow; no persistent `Session` entity is required.
7. Select actor.
8. Enter/select intent and risk.
9. Select the minimal supported skill/mechanic.
10. Set/select DC.
11. Roll/resolve.
12. Inspect outcome and proposed reveal effect.
13. Click **Apply** on success.
14. See meaningful confirmation/history.

## Player actions

1. Authenticate/access the campaign.
2. Open the assigned character view.
3. Verify that the hidden fragment is absent before reveal.
4. Declare the fictional action at the table; dedicated in-app intent submission is out of scope.
5. After the GM applies the successful consequence, refresh or otherwise retrieve the updated player projection.
6. See the newly revealed knowledge.

Realtime push is not required; manual refresh or simple re-fetch is acceptable for Slice 1.

## Game mechanic used

Only one minimal Custom D20 check.

Candidate contract requiring Game Design approval:

```text
natural d20 + resolved character modifier >= GM-selected DC
=> success
else
=> failure
```

The persisted result should retain enough information to explain the roll:

- natural d20 result;
- resolved modifier;
- total;
- DC;
- success/failure.

The slice does not require:

- critical rules;
- degree-of-success bands;
- opposed checks;
- final advantage/disadvantage rules;
- secondary narrative die;
- combat actions;
- initiative.

The stakes contract should require at least:

- Intent;
- Risk.

## Data persisted

Minimum product-level persistence requirements:

- Campaign;
- campaign memberships/roles;
- player-to-character assignment;
- Character;
- Location;
- KnowledgeFragment;
- CharacterKnowledge after reveal;
- resolution/check trace sufficient to recover actor, intent, risk, mechanic, DC, roll, outcome, and consequence correlation;
- current mutable state resulting from the reveal;
- append-only DomainEvent/history for significant mutations.

Architecture decides exact tables, aggregates, DTOs, and event names.

## Permissions

### GM

May:

- view canonical campaign content;
- author the fragment;
- create/adjudicate the resolution;
- commit the reveal.

### Player

May:

- access only campaigns they belong to;
- view only the assigned/authorized character projection;
- receive only knowledge allowed by the accepted projection/disclosure rules;
- not create or commit GM consequences in Slice 1.

Every relevant read/write remains scoped by `campaign_id`.

## Hidden and revealed information

Before Apply:

- GM can see the KnowledgeFragment.
- Player API/projection must not contain the hidden fragment.

After Apply:

- the appropriate CharacterKnowledge state exists;
- the player projection includes the player-visible content of the fragment;
- unrelated GM-only metadata/veracity/internal fields remain absent.

Frontend hiding is not an acceptable implementation.

## Expected result

The project has proven, end-to-end, that:

```text
persistent campaign context
-> player intent
-> GM stakes
-> Custom D20 check
-> outcome
-> proposed deterministic consequence
-> explicit GM commit
-> persistent knowledge mutation
-> safe player disclosure
-> history
-> reload with state intact
```

This is the minimum useful validation of the product architecture and gameplay-assistance concept.

## Acceptance criteria

1. The GM can create/open the campaign from the application without direct DB editing.
2. The GM can establish one player membership and one player-to-character assignment.
3. The GM can create the minimum character, location, and hidden KnowledgeFragment required by the scenario.
4. Before reveal, the player-facing API/view does not expose the hidden fragment or GM-only canonical metadata.
5. The GM can create the minimal resolution with actor, intent, risk, mechanic, and DC.
6. The system records a D20 result using the Game Design-approved minimum contract.
7. The outcome is persisted and correlated with the resolution.
8. On success, the system presents the predefined knowledge-reveal effect before commit.
9. The player cannot commit that effect.
10. The GM can commit it with one explicit Apply action.
11. The reveal mutation and its significant DomainEvent/history record are committed consistently.
12. After commit, the player-facing projection exposes the newly revealed knowledge and still excludes GM-only data.
13. A full application reload preserves the campaign, resolution result, reveal state, and player-visible knowledge.
14. Cross-campaign access attempts cannot expose or mutate the slice data.
15. The slice does not require an outbox worker to remain correct.
16. No generic Rule Effect DSL is required merely to implement the single reveal effect.
17. A failed check can be recorded without forcing the system to invent or silently persist an interpretive narrative consequence.

## Explicitly out of scope for Slice 1

- procedural generation;
- AI assistance;
- global search;
- persistent Session model;
- persistent Scene model;
- NPC relationship system;
- combat and initiative;
- range bands;
- health/wounds;
- conditions beyond any strictly necessary technical test fixture;
- inventory/resource economy unless Game Design proves the selected skill cannot exist without it;
- secondary narrative result die;
- criticals and degree-of-success rules;
- opposed checks;
- tactical maps/tokens;
- vehicles/space combat;
- progression;
- Force mechanics;
- Dark Side mechanics;
- knowledge provenance;
- misinformation workflow beyond the accepted data model;
- information hazards;
- story-thread management;
- faction clocks/campaign pulse;
- contextual generation;
- live realtime push/WebSockets;
- private messaging;
- generic undo;
- archive/delete lifecycle;
- generic Rule Effect DSL;
- outbox worker;
- extension/package lifecycle;
- pack-author tooling.

---

# Review assignments

## Game Design review required

Game Design should review or amend:

- K-04 Core gameplay loop;
- K-05 GM authority;
- K-06 Action resolution / stakes;
- K-07 Minimum D20 contract;
- K-08 Consequence classes;
- K-09 Confirmation boundary;
- K-12 minimum knowledge semantics;
- K-17 combat sequencing;
- K-18 tactical-map assumption;
- K-19 vehicle/space-combat deferral;
- the Slice 1 check, stakes, success/failure semantics, and whether the knowledge reveal is a valid deterministic effect.

## UX review required

UX should review or amend:

- K-04 core gameplay loop interaction cost;
- K-09 preview/Apply flow;
- K-10 preparation/live workflow;
- K-11 minimum player experience;
- K-12 knowledge reveal;
- K-13 Session deferral;
- K-14 Scene deferral;
- K-15 search sequencing;
- K-20 correction requirement;
- K-21 archive/delete lifecycle;
- Slice 1 GM steps, player read flow, and whether manual refresh is acceptable.

## Architecture review required

Architecture should review or amend:

- K-06 ActionResolution representation boundary;
- K-09 transactional commit behavior;
- K-11 membership/character assignment/projection contracts;
- K-12 knowledge reveal persistence and projection;
- K-13 Session deferral;
- K-14 Scene deferral;
- K-15 search sequencing assumptions;
- K-20 correction/history semantics;
- K-21 lifecycle semantics;
- K-22 minimum architecture contracts;
- Slice 1 persistence, transaction, API, DomainEvent, and authorization design.

## Human Project Owner arbitration expected

The Human Project Owner should ultimately accept/reject:

- K-01 Product vision;
- K-03 MVP definition;
- K-05 formalization of GM authority after specialist review;
- K-16 procedural generation as MVP but post-Slice-1;
- K-17 personal-scale combat as later MVP;
- K-18 tactical maps post-MVP;
- K-19 vehicle/space combat post-MVP;
- K-23 exact first vertical slice;
- K-24 explicit MVP exclusions;
- any cross-domain point where specialist reviews remain materially incompatible.

---

# Deferred kickoff topics

The following do not need resolution to implement Slice 1 and should not block the kickoff unless a specialist identifies a concrete dependency:

- secondary narrative die;
- final difficulty scale beyond what Slice 1 needs;
- criticals;
- degree of success;
- opposed checks;
- advantage/disadvantage stacking/cancellation;
- combat action economy;
- initiative;
- Vitality/Wounds;
- minion groups;
- range-band vocabulary;
- progression;
- multiclassing;
- talent categories;
- Force Strain;
- Dark Side temptation/corruption;
- knowledge provenance;
- infohazards;
- relationship/reputation systems;
- faction clocks;
- campaign pulse;
- generation hook counts/categories;
- latent generated content;
- generator reproducibility;
- exact extension package lifecycle;
- exact module dependency graph beyond Slice 1;
- full Rule Effect DSL;
- realtime synchronization technology.

---

# Kickoff exit criteria

This kickoff is ready to transition to implementation planning when:

1. the Human Project Owner has accepted the first vertical slice;
2. Game Design has accepted the minimum resolution/stakes/D20 semantics required by that slice;
3. the consequence classification and commit boundary are accepted;
4. UX has accepted the minimum GM/player workflow for that slice;
5. Architecture has accepted the minimum stack, authorization, persistence, transaction, and projection contracts required by that slice;
6. GM narrative authority is formally resolved;
7. any remaining Slice 1 blockers are either accepted or explicitly removed from scope;
8. accepted decisions are transferred from this decision pack into the appropriate authoritative domain/planning documents;
9. `docs/planning/current-slice.md` is updated only after the slice is accepted.

Until then, this document remains a review artifact and does not authorize implementation.
