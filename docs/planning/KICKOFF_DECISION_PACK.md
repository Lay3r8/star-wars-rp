# Star Wars RP — Kickoff Decision Pack

Status: CROSS-DOMAIN REVIEWS CONSOLIDATED — HUMAN ARBITRATION PENDING  
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
- **REVIEW CONSENSUS** — Product, Game Design, UX, and Architecture positions are compatible after review; human ratification may still be required for normative status.

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


## Cross-domain review consolidation

The Game Design, UX, and Architecture reviews of this PR have now been completed. Their blocking comments are compatible with one another and with the Accepted ADR baseline.

The following disposition applies to each substantive review remark:

| Review remark | Classification | Consolidated disposition |
|---|---|---|
| Game Design approval of K-04, K-05, K-06, K-07, K-08, K-09, K-12, K-17/K-18/K-19 and the Slice 1 scenario | ACCEPTABLE WITHOUT CHANGE | Retained; the affected sections are updated only where the same review requested clarifications. |
| Game Design: add a minimum when-to-roll rule | DOMAIN-SPECIFIC CHANGE | Incorporated. For Slice 1 a roll exists only when outcome is uncertain, meaningful risk/consequence exists, and success and failure are both fictionally possible. |
| Game Design: failure must change the situation and unchanged retries are forbidden | DOMAIN-SPECIFIC CHANGE with cross-domain implementation impact | Incorporated. Failure requires a concrete pre-roll risk, a short final GM adjudication, terminal closure/history, and a retry rule. |
| Game Design: Slice 1 needs exactly one epistemic state, `Aware` | DOMAIN-SPECIFIC CHANGE | Incorporated. Absence remains Unknown; Believed/Doubted/provenance remain deferred. |
| Game Design: exact success reveal must be bound before the roll | CROSS-DOMAIN DECISION | Incorporated because UX and Architecture independently require the same contract. |
| UX: pre-roll compact summary and Apply preview must show recipient plus exact player-visible claim | EDITORIAL / CLARIFICATION with security impact | Incorporated. No post-roll KnowledgeFragment picker is allowed in Slice 1. |
| UX: failed resolution needs explicit `record/confirm consequence -> Close` interaction | CROSS-DOMAIN DECISION | Incorporated; Game Design and Architecture independently require the same terminal failure path. |
| UX: avoid a resolution wizard; prefill uniquely determined actor/context/mechanic | DOMAIN-SPECIFIC CHANGE | Incorporated as a Slice 1 UX requirement. |
| UX: manual refresh is acceptable only as a Slice 1 concession | EDITORIAL / CLARIFICATION | Incorporated. It is not the target live-player MVP experience. |
| Architecture: `campaign_id` scoping is not authorization; use authenticated server-derived principals and validate every referenced object | DOMAIN-SPECIFIC CHANGE | Incorporated into K-22, Slice 1 permissions, security, and acceptance criteria. |
| Architecture: persist the bound success effect with the resolution before rolling | CROSS-DOMAIN DECISION | Incorporated; this matches Game Design and UX. |
| Architecture: define Roll/Resolve and Apply as explicit transaction boundaries; Apply must be idempotent/one-shot | DOMAIN-SPECIFIC CHANGE | Incorporated. Exact tables/status values remain implementation detail. |
| Architecture: direct in-process orchestration for immediate effect; DomainEvent must not be internal RPC | DOMAIN-SPECIFIC CHANGE | Incorporated into K-22. |
| Architecture: meaningful history is a projection/read model, not a second mutable source of truth | EDITORIAL / CLARIFICATION | Incorporated. Corrections create new authorized mutations/events; existing history is not rewritten. |
| Architecture: failed resolution must support terminal adjudication/close | CROSS-DOMAIN DECISION | Incorporated; Game Design and UX independently require it. |
| All three reviews: Session, Scene, realtime push, generic undo, generic consequence framework, full Rule DSL, combat breadth, generation breadth and advanced epistemics are unnecessary for Slice 1 | SAFE TO DEFER | Retained as explicit Slice 1 exclusions/deferred topics. |
| Product-level MVP breadth beyond Slice 1 | HUMAN DECISION REQUIRED, but not a Slice 1 blocker | May be deferred. If deferred, only the accepted Slice 1 and existing Accepted baseline become implementation commitments; broader MVP recommendations remain provisional. |

No specialist review introduced a contradiction with an existing ACCEPTED decision.

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

**STATUS:** REVIEW CONSENSUS — READY TO ACCEPT  
**DECISION OWNER:** Product Lead with Game Design and UX review  
**AFFECTED DOMAINS:** Product, Game Design, UX, Architecture  
**BLOCKING:** YES — resolved in this pack, pending Human acceptance of Slice 1

### CONTEXT

The implementation gate requires a defined core gameplay loop.

### EVIDENCE / CURRENT POSITIONS

Product, Game Design, and UX converge on a fiction-first loop. Game Design explicitly approved Option 2 and supplied the minimum when-to-roll rule. UX approved the same interaction model and requires that the live path remain compact rather than becoming a generic form workflow. Architecture can persist the required resolution trace without introducing a workflow engine.

### CONSOLIDATED LOOP

```text
Fictional positioning
-> player intent
-> GM determines whether a roll is warranted
-> concrete stakes: Intent + Risk
-> mechanic/DC and any deterministic success effect are fixed
-> roll
-> outcome
-> success: preview deterministic effect -> GM Apply -> committed mutation
-> failure: GM records/confirms concrete adjudication -> Close
-> meaningful history / disclosure
-> new fictional situation
```

### MINIMUM WHEN-TO-ROLL RULE

For Slice 1, a roll should normally occur only when all three are true:

1. the outcome is uncertain;
2. there is a meaningful consequence or risk;
3. both success and failure are fictionally possible.

If one of those conditions is false, the GM should normally resolve the action without a roll.

### MINIMUM RETRY RULE

After failure, the same approach under materially unchanged fictional circumstances cannot simply be rerolled.

A new attempt requires a meaningful change such as:

- a changed approach or circumstance;
- new assistance or equipment;
- additional time;
- acceptance of a new or increased cost/risk.

### PRODUCT IMPACT

This establishes the core assisted-play value while keeping the D20 subordinate to fiction.

### GAME DESIGN IMPACT

Game Design owns these semantics and has approved them for Slice 1. They do not freeze the eventual full Custom D20 rules.

### UX IMPACT

The live path must remain one compact surface; persisted fields do not imply a multi-step wizard.

### ARCHITECTURE IMPACT

Resolution, outcome, terminal adjudication/effect, and history need durable correlation, not a generic workflow engine.

### SECURITY IMPACT

Any disclosure or state mutation resulting from the loop remains backend-authorized.

### RECOMMENDATION

**Adopt the consolidated fiction-first loop and minimum when-to-roll/retry rules for Slice 1.**

---

## K-05 — GM authority

**STATUS:** CROSS-DOMAIN CONSENSUS — HUMAN FORMALIZATION REQUIRED  
**DECISION OWNER:** Product Lead / Game Design / Human Project Owner  
**AFFECTED DOMAINS:** All  
**BLOCKING:** YES

### CONTEXT

The decision log records "GM retains final narrative authority" as To formalize. The three specialist reviews are now compatible on the meaning required for Slice 1.

### EVIDENCE / CURRENT POSITIONS

Game Design explicitly approves GM final authority over interpretive and authoritative narrative/canonical changes.

UX approves one explicit GM Apply action for the deterministic reveal and explicit GM closure of the failure adjudication.

Architecture supports bounded deterministic automation while requiring authorized, transactional commit.

### OPTIONS

1. System may automatically commit any rule-derived narrative/canonical consequence.
2. GM retains final authority over interpretive and authoritative narrative/canonical changes; bounded deterministic effects may be mechanically derived and committed under an accepted policy.
3. Every state change, including trivial deterministic arithmetic, always requires bespoke GM interpretation.

### TRADE-OFFS

Option 1 undermines the project's GM-authority direction.  
Option 2 preserves useful automation without transferring narrative authority to the system.  
Option 3 adds unnecessary friction and prevents useful deterministic assistance.

### PRODUCT IMPACT

Option 2 defines the application as a GM assistant rather than an autonomous GM.

### GAME DESIGN IMPACT

Approved by Game Design.

### UX IMPACT

Supports explicit confirmation where disclosure or important mutation is cognitively/narratively significant.

### ARCHITECTURE IMPACT

Supports direct, authorized, transactional state mutation for accepted effects.

### SECURITY IMPACT

Only authorized server-derived GM principals may adjudicate/commit GM operations.

### RECOMMENDATION

**Product recommends Option 2 and formalizing D-004 as ACCEPTED. This now requires Human Project Owner ratification rather than further specialist design.**

---

## K-06 — Action resolution / stakes

**STATUS:** REVIEW CONSENSUS — READY TO ACCEPT AS A CAPABILITY CONTRACT  
**DECISION OWNER:** Game Design for semantics; Product for capability; Architecture for representation  
**AFFECTED DOMAINS:** All  
**BLOCKING:** YES — resolved at capability level

### CONTEXT

Dice rolls without intent, risk, and consequence context cannot support meaningful assisted mutation/history.

### EVIDENCE / CURRENT POSITIONS

Product, Game Design, UX, and Architecture now converge on a bounded persistent resolution trace.

Game Design approves **Intent + Risk** as the minimum stakes contract for Slice 1 and does not require a structured Approach field.

UX requires the live interaction to remain compact.

Architecture requires a persistent trace sufficient to reconstruct what the roll meant after reload, but does not require a generic workflow/consequence aggregate.

### CONSOLIDATED MINIMUM CONTRACT

Slice 1 needs a persistent resolution trace capable of correlating:

- actor;
- current context/target when relevant;
- Intent;
- concrete Risk;
- selected/supported mechanic;
- DC fixed before roll;
- exact deterministic success-effect binding fixed before roll;
- roll inputs/result;
- success/failure outcome;
- success Apply or final failure adjudication;
- terminal/closed state;
- meaningful history correlation.

Approach remains semantically meaningful in play but does not need to be a persisted Slice 1 field.

### PRODUCT IMPACT

This enables assisted consequences and meaningful history without creating a workflow engine.

### GAME DESIGN IMPACT

Intent + Risk and the failure/retry semantics are Game Design-approved for Slice 1.

### UX IMPACT

Persisted structure must not surface as a wizard; uniquely determined values should be prefilled.

### ARCHITECTURE IMPACT

Architecture retains ownership of exact tables, aggregates, DTOs, endpoints, and status representation.

### SECURITY IMPACT

GM-only resolution/adjudication fields and player-visible output must remain separately authorized/projected.

### RECOMMENDATION

**Adopt this as the Slice 1 capability contract, not as a prescribed persistence schema.**

---

## K-07 — Minimum D20 contract for Slice 1

**STATUS:** GAME DESIGN APPROVED FOR SLICE 1  
**DECISION OWNER:** Game Design  
**AFFECTED DOMAINS:** Game Design, UX, Architecture, Product  
**BLOCKING:** YES — resolved for Slice 1

### CONTEXT

Slice 1 needs one real Custom D20 resolution mechanic without freezing the full system.

### EVIDENCE / CURRENT POSITIONS

Game Design has explicitly approved the following slice-level contract:

```text
natural d20 + resolved precomputed modifier >= GM-selected DC
=> success
else
=> failure
```

The DC is fixed before rolling.

Slice 1 persists:

- natural d20 result;
- resolved modifier;
- total;
- DC;
- binary success/failure outcome.

The precomputed modifier is sufficient for this slice.

### SAFE TO DEFER

- global difficulty ladder;
- critical rules;
- degrees of success;
- opposed checks;
- final advantage/disadvantage rules;
- secondary narrative result;
- modifier-budget design.

### PRODUCT IMPACT

This is sufficient to validate the integration seam and does not define the final breadth of Custom D20.

### GAME DESIGN IMPACT

Approved by the Game Design owner for Slice 1 only.

### UX IMPACT

One simple check is enough; actor/context/mechanic should be prefilled when uniquely determined.

### ARCHITECTURE IMPACT

Persistence must retain the explanatory roll inputs/result without treating this binary contract as the only future resolution shape.

### SECURITY IMPACT

Only an authorized GM may initiate/adjudicate the Slice 1 resolution operation.

### RECOMMENDATION

**Adopt this exact minimum contract for Slice 1. Do not infer final Custom D20 crit/degree/opposed/advantage rules from it.**

---

## K-08 — Deterministic versus interpretive consequences

**STATUS:** GAME DESIGN APPROVED — REVIEW CONSENSUS  
**DECISION OWNER:** Game Design with Product/UX review  
**AFFECTED DOMAINS:** All  
**BLOCKING:** YES — resolved conceptually

### CONTEXT

The system needs predictable semantics for what can be mechanically derived and what remains GM judgment.

### CONSOLIDATED CLASSIFICATION

1. **Deterministic effects** — mechanically complete once the pre-roll contract is fixed; for example the Slice 1 bound reveal of one exact claim to one exact character.
2. **Bounded interpretive consequences** — the rules establish that a consequence is warranted, but the GM selects/confirms/edits its concrete fictional meaning.
3. **Authoritative narrative/canonical changes** — major narrative/canonical decisions remain GM-authored/adjudicated.

### EVIDENCE / CURRENT POSITIONS

Game Design explicitly approved this three-way distinction. UX does not want the GM manually classifying consequence type during play; supported behavior should already determine the class. Architecture supports typed/direct Slice 1 handling rather than generic scripting.

### PRODUCT IMPACT

Provides predictable assistance without hiding narrative authority.

### GAME DESIGN IMPACT

Classification semantics are owned and approved by Game Design.

### UX IMPACT

The UI may present deterministic previews differently from interpretive adjudication without exposing internal classification controls.

### ARCHITECTURE IMPACT

Slice 1 needs only its direct typed reveal effect, not a generic effect language.

### SECURITY IMPACT

Only authorized actors may commit campaign-changing effects.

### RECOMMENDATION

**Adopt the three-class model as the kickoff direction. Slice 1 implements only the bounded behavior it actually needs.**

---

## K-09 — Confirmation / commit boundary

**STATUS:** REVIEW CONSENSUS — READY TO ACCEPT FOR SLICE 1  
**DECISION OWNER:** Cross-domain  
**AFFECTED DOMAINS:** Product, Game Design, UX, Architecture  
**BLOCKING:** YES — resolved for Slice 1

### CONTEXT

The team needs a clear point where a calculated outcome becomes canonical mutable state.

### CONSOLIDATED SLICE 1 CONTRACT

**Before Roll**

The exact deterministic success reveal is already bound to:

- one recipient character;
- one exact KnowledgeFragment/player-visible claim.

The compact pre-roll summary shows actor/context, Intent, concrete Risk, mechanic/DC, and the exact success effect.

**Success**

```text
successful roll
-> derived preview from persisted bound effect
-> GM verifies recipient + exact player-visible claim
-> Apply
-> atomic canonical mutation + resolution state + DomainEvent
```

Apply is one-shot/idempotent: retry, double-click, or network retry must not duplicate CharacterKnowledge or history.

**Failure**

```text
failed roll
-> GM records/confirms short concrete adjudication of the pre-declared Risk
-> Close
-> terminal resolution + meaningful history
```

This does not require a generic consequence editor or structured failure-world-state engine in Slice 1.

### PRODUCT IMPACT

This validates automation conservatively while giving both outcomes a complete playable terminal path.

### GAME DESIGN IMPACT

The success effect is deterministic because its recipient and claim are fixed before rolling. Failure must change the situation.

### UX IMPACT

Success uses compact preview + Apply. Failure uses one small record/confirm + Close interaction.

### ARCHITECTURE IMPACT

Roll/Resolve and Apply/Close are explicit application-level transaction boundaries. Exact persistence statuses remain implementation detail.

### SECURITY IMPACT

The backend re-authorizes the GM at Apply/Close and verifies all referenced objects belong to the same authorized campaign.

### RECOMMENDATION

**Adopt this boundary for Slice 1. Selective auto-apply may be reconsidered only after playtesting.**

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

**STATUS:** REVIEW CONSENSUS — SLICE 1 SEMANTICS DEFINED  
**DECISION OWNER:** Product for scope; Game Design for epistemic semantics; Architecture for projection  
**AFFECTED DOMAINS:** All  
**BLOCKING:** YES — resolved for Slice 1

### CONTEXT

Knowledge is both a product differentiator and an Accepted architecture boundary. Slice 1 should validate it without importing the full belief/provenance system.

### EVIDENCE / CURRENT POSITIONS

ADR-002 and ADR-003 are Accepted.

Game Design approves exactly one Slice 1 epistemic state:

**Aware** — the character has been exposed to the claim and can act on that information. `Aware` does not assert objective truth and does not assert full belief.

Absence of `CharacterKnowledge` continues to mean Unknown.

UX approves a targeted reveal but requires the Apply preview to show the exact recipient and exact player-visible disclosure.

Architecture can support `Aware` without designing later epistemic states.

### SLICE 1 CONTRACT

- one GM-only `KnowledgeFragment`;
- no `CharacterKnowledge` initially;
- exact fragment and recipient bound to the resolution before roll;
- successful GM Apply creates/updates `CharacterKnowledge` to `Aware`;
- player projection gains only the player-visible claim;
- GM veracity/internal metadata remains absent from the player response.

### SAFE TO DEFER

- Believed/Doubted states;
- provenance;
- misinformation workflow;
- sharing semantics;
- infohazards;
- broader epistemic-state taxonomy.

### PRODUCT IMPACT

Validates an important product differentiator early.

### GAME DESIGN IMPACT

The minimum state is now defined by Game Design.

### UX IMPACT

Disclosure is explicit and previewed because it is cognitively irreversible once seen by a player.

### ARCHITECTURE IMPACT

Uses the Accepted KnowledgeFragment/CharacterKnowledge and projection boundaries without over-designing later states.

### SECURITY IMPACT

The hidden claim must be absent before Apply, and only the intended authorized projection may receive it afterward.

### RECOMMENDATION

**Adopt `Unknown by absence -> Aware` as the complete epistemic scope of Slice 1.**

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

**STATUS:** ARCHITECTURE APPROVED WITH CONSOLIDATED CONTRACTS  
**DECISION OWNER:** Architecture  
**AFFECTED DOMAINS:** Architecture, Security, Product, UX, Game Design  
**BLOCKING:** YES — resolved at kickoff-contract level

### CONTEXT

Architecture has approved the minimum-contract approach and the concrete stack for Slice 1/MVP. The review requested stronger authorization, transaction, idempotency, orchestration, and history contracts.

### ACCEPTED BY ARCHITECTURE FOR SLICE 1 / MVP DIRECTION

- React + FastAPI modular monolith + PostgreSQL.
- Docker Compose for local orchestration.
- PostgreSQL as the single source of truth for mutable campaign state.
- No Kubernetes, broker, worker fleet, or distributed infrastructure justified by Slice 1.
- Explicit player-facing projections.
- Persistent resolution trace/correlation, not raw dice only.
- Immediate accepted effects execute synchronously in the same PostgreSQL transaction as canonical state mutation and significant `DomainEvent`.
- No outbox worker in Slice 1.
- No generic Rule Effect DSL; the knowledge reveal is represented directly/typed.
- No persistent Session or Scene in Slice 1.
- No generated-candidate persistence in Slice 1.
- Manual re-fetch is technically acceptable for Slice 1; realtime remains deferred.

### AUTHORIZATION CONTRACT

`campaign_id` is an isolation invariant, **not** sufficient authorization.

Slice 1 requires two distinct authenticated principals:

- one GM;
- one Player.

The backend derives the acting principal from authentication and never trusts caller-supplied role, campaign membership, or character ownership.

For every relevant read/mutation it validates authorization and same-campaign consistency for every referenced object, including:

- campaign;
- acting character;
- player assignment;
- context/target;
- bound KnowledgeFragment;
- reveal recipient.

A syntactically valid identifier plus a caller-supplied matching `campaign_id` is never sufficient authorization.

Authentication provider/technology is not selected by this kickoff pack.

### PERSISTED SUCCESS-EFFECT CONTRACT

The exact KnowledgeFragment and recipient character are retained by the persisted resolution **before the roll**.

After reload the backend can reconstruct exactly what success meant without client-only state or a post-roll picker.

The preview is derived/transient; a separate generic `ConsequenceProposal` aggregate is not required.

### TRANSACTION CONTRACT

**Roll/Resolve commit**

Persist the resolution contract and roll result, including the pre-bound success effect.

**Apply success commit**

In one transaction:

1. derive/re-authorize the GM principal;
2. verify the resolution is successful and not already applied/closed;
3. verify all referenced objects remain in the authorized campaign;
4. create/update the recipient `CharacterKnowledge` to `Aware`;
5. mark/correlate the resolution as applied/closed;
6. append the significant `DomainEvent`.

Apply is idempotent/one-shot.

**Close failure commit**

Persist the GM's concrete final adjudication of the declared Risk, close the resolution, and commit the correlated meaningful history consistently.

No generic failure-consequence engine is required.

### ORCHESTRATION CONTRACT

The immediate knowledge mutation occurs through a direct in-process application/domain call in the same unit of work.

Do **not** implement:

```text
Resolution DomainEvent -> internal event subscriber -> Knowledge mutation
```

`DomainEvent` is append-only history/audit output for the committed change, not internal RPC. Future outbox publication remains separate.

### HISTORY CONTRACT

Slice 1 does not need a second editable history store.

Human-readable GM activity/history is a projection/read model derived from resolution/current state/events.

Corrections create new authorized mutations/events. Existing append-only history is not rewritten.

### SECURITY / TESTABILITY CONTRACT

Integration tests must prove at least:

1. hidden knowledge is absent from the player projection before Apply and present after Apply;
2. GM/Player authorization is enforced server-side using authenticated principals;
3. the Player cannot invoke GM resolution, adjudication, Apply, or Close operations;
4. player-to-character assignment is server-authoritative;
5. cross-campaign reads, references, and mutations fail, including embedded cross-campaign object references;
6. successful Apply is atomic and safe to retry/double-submit;
7. rollback cannot leave `CharacterKnowledge`, resolution state, and history inconsistent;
8. failed resolution can be concretely adjudicated and closed;
9. reload reconstructs the persisted resolution and bound success effect without transient client state.

If a tunnel such as ngrok or Cloudflare Tunnel is used, it is transport/exposure only and is never the authentication/authorization boundary.

### SHOULD NOT BE BUILT YET

- generic `ConsequenceProposal` / `AppliedChangeSet` framework merely for Slice 1;
- event-driven internal command routing;
- generic workflow/state-machine engine for ActionResolution;
- generic scripting/expression language;
- nullable Session/Scene/generator fields for future-proofing;
- broker/async worker/distributed services;
- plugin runtime/marketplace;
- Elasticsearch/OpenSearch;
- Kubernetes for Slice 1.

### RECOMMENDATION

**Adopt these as the minimum Architecture contracts for Slice 1. Exact tables, endpoints, classes, and status values remain implementation decisions.**

---

## K-23 — First playable vertical slice

**STATUS:** CROSS-DOMAIN REVIEW CONSENSUS — HUMAN ACCEPTANCE REQUIRED  
**DECISION OWNER:** Product Lead / Human Project Owner  
**AFFECTED DOMAINS:** All  
**BLOCKING:** YES

### CONTEXT

All three specialist reviews support the terminal-slicing scenario after the clarifications incorporated in this pack.

### EVIDENCE / CURRENT POSITIONS

Game Design approves a non-combat terminal-slicing slice and the minimum D20/stakes semantics.

UX approves the scenario provided both success and failure have clear terminal interactions and the live path remains compact.

Architecture approves the scenario and its minimal persistence/security/transaction footprint.

### OPTIONS

1. CRUD-only campaign/character/world slice.
2. Consolidated non-combat "slice a terminal and reveal a secret" loop.
3. Broader first encounter including combat, generation, Session/Scene, or other deferred systems.

### TRADE-OFFS

Option 1 does not test the gameplay loop.  
Option 2 exercises a real end-to-end GM/player loop with bounded mechanics and strong security/persistence tests.  
Option 3 imports multiple unresolved systems and weakens delivery focus.

### PRODUCT IMPACT

Option 2 validates the core assisted-play hypothesis.

### GAME DESIGN IMPACT

The required minimum semantics are now approved.

### UX IMPACT

The success and failure live paths are now complete and compact.

### ARCHITECTURE IMPACT

The minimum contracts are now defined without horizontal platform work.

### SECURITY IMPACT

The slice directly tests principal-based authorization, cross-campaign reference rejection, and pre/post-reveal disclosure.

### RECOMMENDATION

**Product recommends Option 2. The consolidated detailed specification is in Phase 3.**

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

# Phase 3 — Consolidated First Vertical Slice

## Slice 1 — "Slice the terminal, reveal the secret"

**Status:** CROSS-DOMAIN REVIEW CONSENSUS — HUMAN ACCEPTANCE PENDING

### Product goal

Prove that one GM and one Player can use the application end-to-end to move from persistent campaign context to a fiction-first D20 action, complete either success or failure cleanly, persist the result, safely reveal previously hidden information on success, and reconstruct the state after reload.

This slice is intentionally **not** a combat, generation, search, Session, Scene, realtime, or AI slice.

## Actors and authentication

Slice 1 uses **two distinct authenticated principals**:

### GM

- is authorized as GM for the campaign;
- creates the minimal campaign content;
- sees canonical/hidden information;
- initiates and adjudicates the resolution;
- commits the success reveal or closes the failed resolution.

### Player

- is authorized as Player for the campaign;
- is server-assigned to one Player Character;
- can read only the allowed player projection;
- cannot access GM-only knowledge;
- cannot invoke GM resolution/adjudication/Apply/Close operations.

The backend derives principal identity and authorization from authentication. Caller-supplied role, membership, assignment, ownership, or `campaign_id` is never trusted as authorization.

The authentication provider/technology itself is out of scope for the kickoff decision.

## Initial state

Through application UI/API rather than direct database editing, establish:

- one Campaign;
- one authenticated GM membership;
- one authenticated Player membership;
- one server-authoritative player-to-character assignment;
- one Player Character with the precomputed modifier required by the approved Slice 1 D20 contract;
- one Location/current context;
- optionally one target/world object only if implementation/UX needs it; the Location may be sufficient context;
- one hidden `KnowledgeFragment` with GM-side veracity metadata and player-visible claim text;
- no `CharacterKnowledge` for that fragment.

No procedural generator is used.

## Fiction and when-to-roll

The player declares at the table that the character wants to slice an Imperial cargo terminal to discover where a confiscated shipment was transferred.

A dedicated player-to-GM intent messaging feature is out of scope.

The GM requests a roll only because all three conditions are true:

1. the outcome is uncertain;
2. there is a meaningful consequence/risk;
3. both success and failure are fictionally possible.

If those conditions are not true, the action should normally resolve without a roll.

## Pre-roll resolution contract

Before the D20 is rolled, the resolution binds:

- actor: the assigned Player Character;
- current context/target;
- **Intent:** discover where the confiscated shipment was transferred;
- **Risk:** on failure, the intrusion is noticed by Imperial security;
- supported mechanic/skill;
- GM-selected DC;
- **deterministic success effect:** reveal this exact predefined `KnowledgeFragment` to this exact acting/recipient character.

The exact recipient and exact fragment are fixed before rolling.

There is no post-roll fragment picker.

### Live UX requirement

The normal live path is one compact surface.

Where uniquely determined by Slice 1 context:

- actor is prefilled;
- current context is prefilled;
- the single supported mechanic is prefilled.

The GM primarily enters/edits Intent, Risk, and DC and verifies the pre-bound success effect.

The pre-roll summary shows the exact success contract without exposing internal persistence terminology.

## Game mechanic

The Game Design-approved Slice 1 contract is:

```text
natural d20 + resolved precomputed character modifier >= GM-selected DC
=> success
else
=> failure
```

The DC is fixed before Roll.

Persist:

- natural d20 result;
- resolved modifier;
- total;
- DC;
- binary outcome.

Slice 1 does not decide the final Custom D20 rules for crits, degrees, opposed checks, advantage/disadvantage, difficulty ladder, or secondary narrative result.

## Roll / Resolve transaction

The Roll/Resolve operation persists enough state to reconstruct after reload:

- actor/context;
- Intent;
- concrete Risk;
- mechanic;
- DC;
- pre-bound recipient + success KnowledgeFragment reference;
- roll inputs/result;
- outcome.

Persisting several fields does not imply a multi-step UX wizard.

## Success path

On success:

1. the application derives a preview from the already persisted success-effect binding;
2. the preview shows the **recipient character** and the **exact player-visible claim text**;
3. the GM chooses **Apply**;
4. the backend re-authorizes the GM principal;
5. the backend verifies the resolution is successful and not already applied/closed;
6. the backend validates campaign consistency of all referenced objects;
7. in one PostgreSQL transaction:
   - create/update the recipient `CharacterKnowledge` to **Aware**;
   - mark/correlate the resolution as applied/closed;
   - append the significant `DomainEvent`;
8. the player projection can now include the revealed claim.

Apply is one-shot/idempotent. A retry, double-click, or network retry cannot duplicate the effect or history.

The immediate Knowledge mutation uses direct in-process application/domain orchestration. `DomainEvent` is not used as internal RPC.

## Failure path

On failure:

1. the failed roll is persisted;
2. the GM is shown the concrete pre-declared Risk;
3. the GM records/confirms one short concrete adjudication of how the risk manifests;
4. the GM chooses **Close**;
5. the final adjudication and terminal resolution/history are committed consistently.

Example adjudication:

> Imperial security logs the intrusion and the terminal enters an alerted state in the fiction.

Slice 1 does not require a generic structured world mutation or generic consequence engine for this failure.

### Retry rule

The same approach under materially unchanged fictional circumstances cannot simply be rerolled.

A new attempt requires a meaningful change, such as:

- changed approach/circumstance;
- new assistance/equipment;
- additional time;
- new/increased cost or risk.

## Knowledge semantics

Slice 1 uses exactly one explicit `CharacterKnowledge` state:

**Aware** — the character has been exposed to the claim and can act on it.

`Aware` does not imply that the claim is objectively true or fully believed.

Absence of `CharacterKnowledge` means Unknown.

Believed, Doubted, provenance, misinformation workflow, sharing semantics, and infohazards remain deferred.

## Hidden and revealed information

### Before Apply

- GM can see the `KnowledgeFragment` and GM-side metadata.
- Player projection contains neither the hidden claim nor GM veracity/internal metadata.

### Apply preview

The GM sees:

- exact recipient;
- exact player-visible claim.

### After Apply

- recipient `CharacterKnowledge` is `Aware`;
- the authorized player projection contains the player-visible claim;
- GM veracity/internal metadata remains absent.

Frontend hiding is never an authorization mechanism.

## History

`DomainEvent` remains append-only audit/history output.

A GM-facing readable activity feed/history may be a projection/read model derived from resolution/current state/events.

There is no separate editable history source of truth.

Corrections create new authorized mutations/events; existing history is not rewritten.

## Player flow

1. Authenticate as the Player principal.
2. Open the assigned character projection.
3. Verify that the hidden claim is absent.
4. Declare the fictional action at the table.
5. After successful GM Apply, re-fetch the player projection.
6. See the newly revealed claim.

Manual refresh/simple re-fetch is acceptable as a **Slice 1 concession only**. It is not the target live-player MVP experience; polling or push can be introduced later when justified.

## Data persisted

Minimum product-level persistence requirements:

- Campaign;
- campaign memberships/roles;
- player-to-character assignment;
- Character;
- Location/current context reference;
- `KnowledgeFragment`;
- `CharacterKnowledge` = `Aware` after successful Apply;
- resolution trace sufficient to reconstruct pre-roll contract, bound success effect, roll, outcome, Apply/Close and final adjudication;
- current mutable state;
- append-only significant `DomainEvent` history.

Architecture owns exact schema/API/class/status representation.

## Authorization invariants

Every relevant read/write is both campaign-scoped and principal-authorized.

The backend validates that campaign, acting character, assignment, context/target, bound fragment, and reveal recipient belong to the same authorized campaign.

A valid identifier with a matching caller-supplied `campaign_id` is never sufficient.

Cross-campaign embedded references must be rejected.

## Expected result

The project proves end-to-end:

```text
persistent campaign context
-> fictional player intent
-> when-to-roll decision
-> Intent + concrete Risk + bound success effect
-> minimal Custom D20
-> success OR failure
-> explicit terminal GM action
-> atomic/correlated persistence
-> safe player disclosure when applicable
-> meaningful history
-> reload with state intact
```

## Acceptance criteria

1. The GM and Player operate as two distinct authenticated principals.
2. The GM can create/open the minimum campaign content without direct DB editing.
3. The backend owns campaign membership, GM/Player role, and player-to-character assignment.
4. Before Apply, the player-facing API/view does not expose the hidden claim or GM-only veracity/internal metadata.
5. The Player cannot invoke GM resolution, adjudication, Apply, or Close operations.
6. The GM can establish the resolution on one compact live surface; uniquely determined actor/context/mechanic are prefilled rather than redundantly selected.
7. Before Roll, Intent, concrete Risk, DC, exact recipient, and exact success KnowledgeFragment are fixed and persisted/correlated.
8. The system applies the approved minimum D20 contract and persists natural roll, modifier, total, DC, and binary outcome.
9. DC is fixed before the roll.
10. On success, the Apply preview shows the exact recipient and exact player-visible claim.
11. Successful Apply is authorized, atomic, idempotent/one-shot, and cannot duplicate `CharacterKnowledge` or history.
12. Successful Apply creates/updates the recipient `CharacterKnowledge` to `Aware`, closes/correlates the resolution, and appends the significant `DomainEvent` in one transaction.
13. After successful Apply, only the authorized player projection receives the player-visible claim; GM-only metadata remains absent.
14. On failure, the GM can record/confirm a concrete adjudication of the pre-declared Risk and Close the resolution without a generic consequence editor.
15. A failed resolution has an unambiguous terminal/closed state and meaningful retained history.
16. The same approach under materially unchanged fiction cannot simply be rerolled; the UI/rules do not present failure as retry-until-success.
17. Cross-campaign reads, mutations, assignments, or embedded object references are rejected.
18. Transaction rollback cannot leave `CharacterKnowledge`, resolution state, and history mutually inconsistent.
19. A full reload reconstructs the persisted resolution, its pre-bound success effect, final outcome, and disclosure state without transient client state.
20. Immediate success mutation uses direct in-process orchestration; `DomainEvent` is not internal command/RPC routing.
21. Human-readable history does not become a second mutable source of truth.
22. Slice 1 correctness does not depend on an outbox worker, broker, WebSocket service, generic Rule Effect DSL, generic workflow engine, or generic undo system.

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
- inventory/resource economy unless the approved single modifier cannot be represented without it;
- secondary narrative result die;
- criticals and degree-of-success rules;
- opposed checks;
- final advantage/disadvantage rules;
- global difficulty ladder;
- tactical maps/tokens;
- vehicles/space combat;
- progression;
- Force mechanics;
- Dark Side mechanics;
- advanced knowledge states;
- knowledge provenance;
- misinformation workflows;
- information hazards;
- story-thread management;
- faction clocks/campaign pulse;
- contextual generation;
- realtime push/WebSockets;
- private messaging;
- generic undo;
- archive/delete implementation;
- generic consequence editor/framework;
- generic Rule Effect DSL;
- outbox worker/broker;
- extension/package lifecycle;
- pack-author tooling;
- Kubernetes/distributed production orchestration for this slice.

---

# Post-review disposition

## Game Design

**Disposition after consolidation:** no remaining specialist blocker identified in the submitted review, provided the four requested clarifications are incorporated.

Incorporated:

- minimum when-to-roll rule;
- concrete failure + retry semantics;
- `Aware` as the only Slice 1 epistemic state;
- exact success reveal bound before Roll.

## UX

**Disposition after consolidation:** no remaining specialist blocker identified in the submitted review, provided failure Close and the pre-roll/Apply disclosure contract are incorporated.

Incorporated:

- explicit terminal failure interaction;
- exact pre-roll success binding and exact disclosure preview;
- compact non-wizard live flow with prefilling;
- manual refresh marked as Slice 1 concession only.

## Architecture

**Disposition after consolidation:** no remaining specialist blocker identified in the submitted review, provided the requested contract clarifications are incorporated.

Incorporated:

- server-derived authenticated principals;
- authorization stronger than `campaign_id`;
- cross-campaign reference validation;
- persisted pre-roll success binding;
- explicit Roll/Resolve and Apply/Close transaction boundaries;
- idempotent Apply;
- direct in-process orchestration rather than DomainEvent RPC;
- history as projection, not mutable duplicate truth;
- failure terminal close;
- expanded integration-test/security contract.

---

# Human Arbitration Pack

Only the following decisions still require Human Project Owner action **before Slice 1 implementation**.

Broader MVP breadth can reasonably be deferred until after Slice 1; if deferred, it remains a Product recommendation rather than an implementation commitment.

## K-05 — Formalize GM final narrative authority

### QUESTION

Should D-004 be formalized as:

> The GM retains final authority over interpretive and authoritative narrative/canonical changes; bounded deterministic effects may be mechanically derived and committed under an accepted policy.

### WHY NOW

The Slice 1 success/failure commit semantics depend on a stable authority boundary. D-004 is currently only "To formalize".

### OPTION A — Formalize the consolidated rule

**Description:** adopt the wording above.

**Advantages:**

- matches Product, Game Design, UX, and Architecture;
- preserves deterministic assistance;
- prevents mechanical outcome from silently becoming narrative truth;
- gives future automation a clear boundary.

**Inconvénients:**

- later automation must continue respecting the deterministic/interpretive distinction.

### OPTION B — Keep D-004 unresolved

**Description:** do not formalize GM authority yet.

**Advantages:**

- preserves theoretical flexibility.

**Inconvénients:**

- leaves consequence authority ambiguous;
- keeps a kickoff implementation gate open;
- invites inconsistent future automation behavior.

### PRODUCT VIEW

Option A.

### GAME DESIGN VIEW

Option A is explicitly approved.

### UX VIEW

Consistent with explicit Apply/Close and prevention of irreversible accidental disclosure.

### ARCHITECTURE VIEW

Consistent with bounded authorized transactional mutations and the distinction between derived effects and GM adjudication.

### BLOCKING SLICE 1

**YES**

### DEFAULT IF DEFERRED

Slice 1 remains blocked at the kickoff gate; no implementation should assume a narrative-authority policy that is not formally accepted.

---

## K-23 — Accept the consolidated first vertical slice

### QUESTION

Should Slice 1 be the consolidated non-combat **"Slice the terminal, reveal the secret"** scenario defined above?

### WHY NOW

The implementation gate requires the first vertical slice to be accepted before implementation planning begins.

### OPTION A — Accept the consolidated terminal-slicing slice

**Description:** implement the bounded end-to-end scenario defined in Phase 3.

**Advantages:**

- unanimously supported in direction by all three specialist reviews;
- tests real GM/player play rather than CRUD only;
- exercises D20, stakes, success/failure completion, permissions, persistence, knowledge, disclosure, transactions, history, and reload;
- avoids combat, generation, Session/Scene, realtime, and generic infrastructure.

**Inconvénients:**

- deliberately does not test combat or procedural generation;
- includes enough authentication/security work to validate two real principals.

### OPTION B — Reduce to CRUD/persistence only

**Description:** remove the D20/consequence/disclosure loop from Slice 1.

**Advantages:**

- smaller implementation.

**Inconvénients:**

- does not validate the fundamental gameplay-assistance loop;
- does not exercise the most important projection/disclosure boundary;
- all three specialist reviews preferred the gameplay slice.

### OPTION C — Expand Slice 1 with combat or generation

**Description:** add another major subsystem now.

**Advantages:**

- tests more headline features immediately.

**Inconvénients:**

- imports unresolved Game Design/UX/Architecture questions;
- materially increases scope and slows first end-to-end validation;
- no specialist review recommends it.

### PRODUCT VIEW

Option A.

### GAME DESIGN VIEW

Approves the terminal-slicing scenario after the incorporated rules for when-to-roll, failure/retry, `Aware`, and pre-bound success effect.

### UX VIEW

Approves the scenario after explicit failure Close, compact prefilling, and exact pre-roll/Apply disclosure preview.

### ARCHITECTURE VIEW

Approves the scenario after principal-based authorization, persisted effect binding, atomic/idempotent Apply, terminal failure closure, and history/testability clarifications.

### BLOCKING SLICE 1

**YES**

### DEFAULT IF DEFERRED

No first slice is accepted, so implementation remains blocked by `docs/planning/PROJECT_KICKOFF.md`.

---

## Product decisions not requiring immediate Human arbitration

The following remain important but **do not block Slice 1** and can be decided after the first slice if desired:

- exact broader MVP boundary in K-03;
- procedural generation as MVP vs post-MVP in K-16;
- personal-scale combat later-MVP vs post-MVP in K-17;
- final post-MVP status of tactical maps in K-18;
- vehicle/space combat timing in K-19;
- final explicit MVP exclusions in K-24.

**Default if deferred:** none of these capabilities become an implementation commitment merely because they are recommended in this pack. The Accepted baseline plus the accepted Slice 1 remain the only immediate commitments.

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

The specialist-review portion of the kickoff is complete.

The kickoff is ready to transition to implementation planning when:

1. the Human Project Owner formalizes K-05 GM authority;
2. the Human Project Owner accepts K-23 Slice 1;
3. the resulting accepted decisions are transferred from this review artifact into the appropriate authoritative domain/planning documents;
4. `docs/planning/current-slice.md` is updated to the accepted Slice 1;
5. remaining non-blocking MVP recommendations are either explicitly accepted or retained as deferred/proposed without delaying Slice 1.

Until then, this document remains a review artifact and does not authorize implementation.
