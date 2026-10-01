# Slice 2 Candidate Consolidation

**Status:** PROPOSED  
**Owner:** Product Lead  
**Purpose:** Consolidated cross-domain review and Human arbitration artifact  
**Source of truth:** current `main` plus completed Game Design, UX, and Architecture reviews of PR #10

This document does **not** select or accept Slice 2.

---

# 1. Repository baseline

## FACT

The following are now in `main` and authoritative for this selection:

- Slice 1 implementation;
- accepted Slice 1 planning/decision records;
- Slice 1 Product closeout;
- Slice 1 UX interaction guidance;
- Accepted ADRs and architecture decisions.

The stale note from the original PR #10 draft saying that the Product closeout was not in `main` is no longer true and is removed by this consolidation.

## FACT — what Slice 1 actually proved

The project has proven:

- authenticated GM and Player principals;
- campaign membership and backend authorization;
- Character assignment;
- Character and Location persistence;
- KnowledgeFragment / CharacterKnowledge disclosure;
- explicit Player projections;
- one bounded D20 resolution;
- Intent + Risk;
- explicit success Apply and failure Close;
- atomic canonical mutation;
- append-only DomainEvent history;
- reload/persistence;
- idempotent commands;
- E2E and integration-test harnesses.

## FACT — important implementation constraint

The existing persisted `ActionResolution` model is **Slice-1-specific**.

It is currently shaped around:

- `mechanic = slicing`;
- a pre-bound KnowledgeFragment;
- success recipient = acting Character;
- Apply/Close lifecycle for that disclosure flow.

Future slices may reuse:

- the pure D20 seam;
- authorization patterns;
- transactional/idempotent command patterns;
- orchestration boundaries;
- player projections;
- history patterns;

without reusing the current `ActionResolution` table unchanged.

**PRODUCT CONSEQUENCE:** no candidate may justify prematurely turning the Slice 1 resolution persistence into a generic workflow engine.

---

# 2. Shortlist reduction

The original shortlist contained four candidates.

After specialist review, three remain in the Human arbitration pack:

1. **A — Escape the Imperial Patrol**: bounded personal-scale combat.
2. **B — Generate, Review and Enter a Playable Location**: bounded procedural generation used in play.
3. **C — Prep a Contact, Find Them Instantly, Use Them in Play**: preparation/authoring + live retrieval/search.

## Candidate removed from immediate arbitration

### D — Follow a Rumour, Discover a Conflicting Claim

**FACT**

The candidate is technically viable and strongly reuses the accepted Knowledge architecture.

**EXPERT POSITION**

Game Design, UX, and Architecture all agree it can be bounded without introducing Believed/Doubted, a knowledge graph, sharing, or truth inference.

It still requires:

- source/provenance semantics;
- a Player mental model for sourced claims;
- a decision on implicit versus explicit conflict;
- unusually strict disclosure/security tests.

**PRODUCT RECOMMENDATION**

Defer this candidate from the immediate Slice 2 arbitration.

Reason:

- Slice 1 already exercised the Knowledge/disclosure seam;
- this candidate mainly deepens an already-proven domain rather than broadening the product;
- it begins defining durable Player knowledge information architecture;
- the security/mental-model complexity is disproportionate to the breadth of new product learning compared with A, B, or C.

This is a **defer**, not a rejection.

---

# 3. Candidate A — Escape the Imperial Patrol

## PRODUCT VALUE

**FACT**

This would be the first real personal-scale combat flow and the first repeated high-frequency live loop.

**EXPERT POSITION**

Game Design: high gameplay value and a strong test of whether the resolution seam survives repeated consequential actions.

UX: high live-play value; repeated interaction cost is the central issue.

Architecture: feasible inside the current monolith/PostgreSQL topology with no new infrastructure service.

**PRODUCT RECOMMENDATION**

Keep as a final option.

The candidate should remain:

> one short objective-driven encounter

not:

> implement the combat system.

## GAME DESIGN READINESS

**EXPERT POSITION — NEEDS GAME-DESIGN WORK FIRST**

A small combat micro-contract must be accepted before implementation:

- one encounter objective;
- one encounter-end condition;
- one deterministic turn-order rule;
- one action per unit/turn;
- one attack procedure;
- one defence/DC rule;
- one deterministic damage rule;
- one short-term health track;
- one incapacitation threshold;
- one hostile group representation;
- minimal range/position only if the chosen scenario requires it.

Safe deferrals include:

- rolled initiative;
- reactions;
- Vitality + Wounds;
- armour;
- critical injuries;
- advanced conditions;
- weapon catalogue/traits;
- Force;
- talents;
- progression;
- vehicles/space combat.

## UX READINESS

**EXPERT POSITION — NEEDS UX DECISIONS FIRST**

Before UI work:

1. choose the Player command boundary:
   - GM-mediated;
   - Player-active.
2. define routine deterministic damage commit behavior;
3. define current-turn state and encounter progression.

Routine combat must **not** require retyping Slice 1 freeform Intent/Risk for every attack.

The desired live flow is approximately:

```text
start bounded encounter
-> see objective/current actor
-> choose/resolve action
-> see result/state change
-> advance
-> end when objective resolved
```

## ARCHITECTURE READINESS

**EXPERT POSITION — NEEDS CONTRACT DECISIONS FIRST**

Architecture can remain incremental.

Likely persisted additions:

- bounded encounter state if required for reload;
- hostile group/unit;
- short-term health/damage;
- turn/order state if system-managed;
- minimal range/position only if rules need it.

A generic Scene is not required.

A narrowly scoped encounter concept is acceptable if the selected workflow requires resumable shared state.

## SECURITY IMPACT

Moderate if GM-driven.

Higher if Player-active combat is selected.

Player-active combat requires:

- server-derived acting Character;
- campaign membership enforcement;
- target references constrained to the same campaign/encounter;
- explicit Player projections for enemy-visible state;
- no caller-trusted actor identity.

## REUSE FROM SLICE 1

Strong reuse of:

- auth/authz;
- Character/Location identity;
- D20 calculation;
- transaction/idempotency pattern;
- DomainEvent/history;
- projections;
- integration/E2E test harness.

**FACT:** current ActionResolution persistence should not be reused literally as a generic combat resolution model.

## NEW COMPLEXITY

High:

- repeated actions;
- hostile actors;
- shared encounter state;
- turn order;
- health/damage;
- encounter termination;
- possibly range/position;
- potentially Player-side commands.

## WHAT WE LEARN

- whether the product feels like an RPG assistant during actual conflict;
- whether compact live interaction survives repeated use;
- whether abstract combat works without tactical maps;
- whether combat needs a persisted encounter concept;
- how much deterministic combat automation is comfortable;
- whether Player-active commands are desirable.

## WHAT WE DEFER

- complete combat system;
- tactical maps;
- detailed equipment;
- armour;
- advanced conditions;
- injuries/wounds;
- reactions;
- Force combat;
- NPC AI;
- encounter builder;
- vehicle/space combat.

## RISKS

- largest Game Design uncertainty of the final options;
- scope explosion into full combat;
- high-frequency UX bookkeeping;
- premature generic encounter/rules abstractions;
- Player-active security boundary expansion.

## BLOCKERS

Before implementation:

- accepted combat micro-contract;
- GM-mediated versus Player-active choice;
- routine deterministic damage commit policy;
- bounded encounter persistence decision.

## HUMAN DECISION

Selecting A means deliberately accepting more cross-domain design work before implementation in exchange for testing **core RPG breadth and live gameplay** next.

---

# 4. Candidate B — Generate, Review and Enter a Playable Location

## PRODUCT VALUE

**FACT**

Procedural generation is a major intended product differentiator but remains entirely unproven.

The useful product hypothesis is not "can we generate text?"

It is:

> can generation reduce GM preparation effort while producing editable campaign state that becomes genuinely playable?

**PRODUCT RECOMMENDATION**

Keep as a final option, but only in a deliberately reduced form.

The selected slice must test:

```text
Generate
-> Review/Edit
-> Accept or Reject
-> accepted content becomes normal campaign state
-> use at least one accepted element in play
```

## GAME DESIGN READINESS

**EXPERT POSITION — NEEDS SMALL GAME-DESIGN CONTRACT FIRST**

A minimal playable generated package must be accepted.

Game Design proposes something approximately like:

- one Location premise;
- one pressure or threat;
- one opportunity;
- one secret or rumour;
- one concrete Player-facing hook/affordance;
- at least two elements explicitly related.

A notable NPC is optional unless the chosen scenario needs one.

A generated element must then be used in a meaningful Player choice / ActionResolution / disclosure so the test measures playability rather than prose quality.

## UX READINESS

**EXPERT POSITION — NEEDS UX DECISIONS FIRST**

UX can support the slice, but several Product/UX contracts must be fixed before implementation:

- exact generated package;
- whole-package versus partial acceptance;
- candidate durability:
  - transient;
  - survives refresh/relogin;
- review volume;
- what counts as "used in play".

The candidate/canonical distinction must be obvious.

Generation must not silently overwrite accepted state.

## ARCHITECTURE READINESS

**EXPERT POSITION — NEEDS CONTRACT DECISIONS FIRST**

Architecture is feasible and potentially modest if the candidate stays bounded.

Key rule:

> accepted generated content becomes ordinary campaign state; the generator is not a second source of truth.

Unaccepted candidate persistence is **not automatically required**.

If candidate survival across refresh/relogin is not required, it may remain transient.

If persistence is required, use a bounded staging representation rather than a generic world schema.

An external provider boundary is needed only if a concrete provider is selected.

No worker/broker is justified merely because an external HTTP call exists.

## SECURITY IMPACT

Potentially the most novel security boundary of the final options if an external provider is used.

Need to define:

- what campaign data may leave the application;
- API key handling;
- output validation;
- generated-reference validation;
- GM-only generation;
- normal Knowledge projection/disclosure after canonicalization.

## REUSE FROM SLICE 1

Good reuse on the canonical side:

- Campaign;
- GM authorization;
- Entity;
- Location;
- KnowledgeFragment;
- Character if needed;
- persistence transactions;
- disclosure rules;
- history.

## NEW COMPLEXITY

Medium to high:

- generator/provider;
- candidate/canonical lifecycle;
- review/edit/accept UI;
- structured generated package;
- provider latency/errors;
- possibly new typed supporting state.

## WHAT WE LEARN

- whether procedural generation actually saves GM preparation time;
- how much generated structure is useful;
- whether review cost cancels generation value;
- whether staged acceptance is necessary;
- whether accepted generated content fits naturally into ordinary campaign state;
- whether generation can create playable situations rather than lore dumps.

## WHAT WE DEFER

- galaxy/planet generation;
- full NPC/faction/item generation;
- active/latent/dormant systems;
- generator plugin framework;
- background simulation;
- AI GM;
- image generation;
- generic orchestration/jobs;
- reproducibility framework unless a concrete need emerges.

## RISKS

- highest throwaway-UI risk if lifecycle decisions are not fixed first;
- impressive demo but weak actual prep value;
- provider/infrastructure overengineering;
- generated prose with poor gameplay affordance;
- accidental canonicalization;
- external data leakage.

## BLOCKERS

Before implementation:

- exact minimum generated package;
- "used in play" acceptance criterion;
- whole versus partial acceptance;
- candidate durability requirement;
- concrete generator/provider mode;
- external-data disclosure boundary if applicable.

## HUMAN DECISION

Selecting B means prioritizing **product differentiation and GM preparation automation** next, while accepting more Product/UX lifecycle decisions before implementation.

---

# 5. Candidate C — Prep a Contact, Find Them Instantly, Use Them in Play

## PRODUCT VALUE

**FACT**

Slice 1 proved the backend core but manual testing showed that its bootstrap/admin surfaces are not the desired GM product.

This candidate directly tests:

> can the GM prepare something earlier, retrieve it in seconds during play, and act on it without dropping out of the session flow?

**PRODUCT RECOMMENDATION**

Keep as a final option and treat it as the most implementation-ready candidate.

The slice must remain:

```text
prepare Contact
-> edit if needed
-> find rapidly in campaign search
-> open compact summary
-> use/reveal/resolve something from it in play
```

not:

> build the campaign CMS.

## GAME DESIGN READINESS

**EXPERT POSITION — GAME-DESIGN READY**

Very little new Game Design is required.

Minimum contact semantics may be:

- name/identity;
- short fictional role;
- relevant location/association;
- motivation/immediate want only if the scenario needs it;
- relevant information/secret only if used.

No relationship/disposition/reputation/social-combat subsystem is required.

If an uncertain action occurs, existing when-to-roll semantics can be reused conceptually.

## UX READINESS

**EXPERT POSITION — UX READY FOR A SLICE**

UX can bound the workflow without a full product information architecture.

Minimum durable surfaces:

Preparation:
```text
create Contact in context
-> save
-> edit later if necessary
```

Live:
```text
open campaign search
-> type/select
-> compact summary
-> direct relevant action/reveal/use
```

The search should remain campaign-content search, not Principal discovery.

This is the strongest candidate for applying the accepted UX guidance in a real replacement surface instead of extending the Slice 1 bootstrap cards.

## ARCHITECTURE READINESS

**EXPERT POSITION — ARCHITECTURALLY READY**

No new platform capability is required.

Bounded additions:

- minimal contact-specific fields if Character is insufficient;
- edit/update commands;
- GM campaign-search query/read model;
- compact entity summary projection;
- ordinary PostgreSQL indexes/search.

No Elasticsearch/OpenSearch, search service abstraction, Scene, Session, async pipeline, cache, broker, or realtime transport is required.

## SECURITY IMPACT

Low to moderate.

- GM campaign-content search must be campaign-scoped.
- It must not become identity/Principal search.
- GM-only notes/secrets remain GM-only.
- Player search is not required.
- If a Contact triggers Player disclosure, existing explicit projection rules apply.

## REUSE FROM SLICE 1

Highest literal reuse of the final options:

- current monolith;
- PostgreSQL;
- campaign/auth/authz;
- Entity;
- Character;
- Location;
- KnowledgeFragment;
- disclosure;
- history;
- D20 seam if needed;
- integration/E2E infrastructure.

## NEW COMPLEXITY

Moderate:

- first real durable authoring/edit workflow;
- Contact/NPC data;
- bounded campaign search;
- compact live summary/drawer;
- cross-entity retrieval.

## WHAT WE LEARN

- whether the application can become genuinely useful to a GM outside a proof/demo;
- whether prep and live play need distinct surfaces;
- what minimum NPC/contact structure is actually useful;
- whether campaign search has high live-session value;
- what retrieval interaction is fast enough at the table;
- whether the accepted UX guidance works in a durable surface.

## WHAT WE DEFER

- full NPC schema;
- relationship mechanics;
- reputation/factions;
- social combat;
- Principal discovery;
- Player-wide search;
- generic CMS/entity editor;
- full application IA;
- Scene/Session;
- Elasticsearch;
- procedural generation.

## RISKS

- lowest technical risk, but also less new game-system learning;
- danger of turning into generic CRUD/admin work;
- search may be low-value until campaign content volume grows;
- possible premature freezing of navigation/entity taxonomy.

## BLOCKERS

No major specialist blocker.

Before implementation Product still needs to fix:

- exact scenario;
- minimum Contact fields;
- exact "use in play" action;
- search semantics sufficient for the scenario.

These are bounded slice-definition decisions, not prerequisite platform work.

## HUMAN DECISION

Selecting C means prioritizing **GM workflow maturity, durable UX, and fast delivery** over introducing a major new game mechanic or differentiating generator in the next slice.

---

# 6. Cross-domain comparison

## FACT

No final candidate requires:

- WebSockets/SSE as a prerequisite;
- broker/outbox worker;
- microservices;
- search infrastructure outside PostgreSQL;
- generic Rule Effect DSL;
- generic workflow engine;
- generic Scene/Session platform;
- generic plugin/provider framework.

## FACT

Candidate readiness differs materially:

### A — Combat

- Game Design: not ready until micro-contract accepted.
- UX: not ready until repeated-action/Player-command/commit policy accepted.
- Architecture: incremental but dependent on those contracts.

### B — Generation

- Game Design: small playable-situation contract required.
- UX: lifecycle/durability/acceptance decisions required.
- Architecture: feasible after those Product/UX contracts.

### C — Prep/Search

- Game Design: ready.
- UX: ready for a bounded slice.
- Architecture: ready.
- Remaining decisions are normal Product slice-definition work.

## PRODUCT RECOMMENDATION

**Recommend Option C as the default next slice.**

Reasoning:

1. It directly addresses the biggest weakness exposed by the Slice 1 manual test: the application works, but does not yet feel like a durable GM product.
2. It has the highest reuse and lowest throwaway risk.
3. It exercises the accepted UX guidance in a real replacement surface.
4. It builds durable authoring/search/read-model primitives that can support later combat and generation workflows.
5. It has no major prerequisite Game Design or infrastructure decision.
6. It is best aligned with solo-developer delivery constraints.

This recommendation is **not** equivalent to saying C has the highest long-term product differentiation.

### Product view of A

A has the strongest **core RPG/gameplay learning value** and would be a valid choice if the Human Project Owner wants to prioritize making the application feel more like a game immediately.

The cost is a real Game Design/UX design phase before implementation.

### Product view of B

B has the strongest **differentiation learning value**.

The cost is greater Product/UX lifecycle uncertainty and the highest risk of designing throwaway review surfaces or premature generation infrastructure.

---

# 7. Human Arbitration Pack

No candidate is accepted by this document.

The Human Project Owner should choose the next learning priority from the three options below.

---

## OPTION A — Escape the Imperial Patrol

### SCOPE

One short objective-driven personal combat encounter:

- one Player Character;
- one hostile group/unit;
- one encounter objective;
- one bounded turn rule;
- one attack/defence procedure;
- one damage/health model;
- explicit encounter termination;
- no tactical map.

### PRIMARY USER VALUE

Run an actual Star Wars personal combat scene with minimal bookkeeping.

### WHY NOW

Slice 1 proved isolated resolution. This tests repeated live gameplay under pressure and begins validating the RPG system itself.

### WHAT IT VALIDATES

- combat viability without VTT/grid;
- repeated resolution UX;
- health/damage/turn semantics;
- objective-driven combat;
- Player versus GM command responsibility;
- need for a persisted encounter concept.

### MAIN RISKS

- largest rules-design burden;
- repeated-click UX;
- scope expansion into full combat;
- premature generic encounter/resolution abstractions.

### WHAT IT DOES NOT INCLUDE

- tactical maps;
- full initiative subsystem;
- reactions;
- Vitality/Wounds;
- armour;
- weapon catalogue;
- advanced conditions;
- Force/talents;
- vehicle/space combat.

### EXPECTED CROSS-DOMAIN WORK BEFORE IMPLEMENTATION

Game Design:
- accept combat micro-contract.

Product + UX + Game Design:
- GM-mediated vs Player-active;
- routine deterministic damage commit policy.

UX:
- compact encounter interaction.

Architecture:
- bounded encounter persistence after those contracts are fixed.

---

## OPTION B — Generate, Review and Enter a Playable Location

### SCOPE

Generate one bounded playable location/situation, review/edit it, explicitly accept/reject it, convert accepted output into ordinary campaign state, then use one generated element in play.

### PRIMARY USER VALUE

Reduce GM preparation effort while producing immediately playable campaign material.

### WHY NOW

Procedural generation is a major intended differentiator and remains completely unvalidated.

### WHAT IT VALIDATES

- actual generation value after review cost;
- candidate versus canonical lifecycle;
- minimum useful generated structure;
- generated-content playability;
- how generation integrates with normal persistent campaign state.

### MAIN RISKS

- generation demo with little real prep value;
- review fatigue;
- lifecycle ambiguity;
- provider/data-security concerns;
- premature queues/provider frameworks/world schemas.

### WHAT IT DOES NOT INCLUDE

- full world/planet/galaxy generation;
- autonomous story generation;
- background simulation;
- AI GM;
- generic provider/plugin framework;
- image generation;
- full NPC/faction/item generation.

### EXPECTED CROSS-DOMAIN WORK BEFORE IMPLEMENTATION

Product + Game Design:
- exact generated package;
- "used in play" criterion.

Product + UX:
- whole versus partial acceptance;
- candidate durability.

Architecture + Security:
- concrete provider boundary;
- what campaign data may leave the application;
- staging only if durability requires it.

---

## OPTION C — Prep a Contact, Find Them Instantly, Use Them in Play

### SCOPE

Prepare one Contact/NPC with only scenario-relevant information, edit it, find it quickly through campaign-content search during live play, open a compact summary, then use/reveal/resolve something from it.

### PRIMARY USER VALUE

Turn the application from a working prototype into a more credible GM preparation + live-session tool.

### WHY NOW

Slice 1 proved the core backend and exposed that the temporary setup UI is not a durable product workflow.

This candidate has the strongest cross-domain readiness and highest literal reuse.

### WHAT IT VALIDATES

- real GM preparation workflow;
- durable authoring/edit interaction;
- live search/retrieval value;
- minimum useful Contact/NPC shape;
- prep versus live UX;
- whether the Slice 1 UX principles work in a real replacement surface.

### MAIN RISKS

- becoming generic CRUD/CMS work;
- low game-system learning compared with combat;
- search usefulness may be limited in very small campaigns;
- premature information-architecture decisions.

### WHAT IT DOES NOT INCLUDE

- complete NPC schema;
- relationships/reputation;
- factions;
- social combat;
- Principal directory/search;
- Player global search;
- generic entity editor;
- full navigation redesign;
- Scene/Session;
- procedural generation.

### EXPECTED CROSS-DOMAIN WORK BEFORE IMPLEMENTATION

Product:
- exact scenario;
- minimum Contact fields;
- exact "use in play" outcome.

UX:
- bounded prep/search/live-detail workflow.

Architecture:
- PostgreSQL-backed GM search and small edit/read-model contracts.

Game Design:
- only review fields with actual mechanical meaning.

---

# 8. Product recommendation

**PRODUCT RECOMMENDATION: OPTION C — Prep a Contact, Find Them Instantly, Use Them in Play.**

This is the best default next step for a solo developer because it combines:

- high practical GM value;
- strong Slice 1 reuse;
- low architecture risk;
- low Game Design prerequisite cost;
- direct application of the Slice 1 UX learnings;
- likely durable product surfaces;
- short path to another end-to-end playtest.

If the Human Project Owner instead wants the next slice to maximize **gameplay-system learning**, choose **Option A**.

If the priority is to maximize **differentiation learning**, choose **Option B**.

---

# 9. Selection gate

No Slice 2 is ACCEPTED yet.

After Human arbitration:

1. record the selected option as a Product decision;
2. have the relevant specialists finalize only the blocking contracts identified above;
3. write the exact accepted Slice 2 scenario and acceptance criteria;
4. update `docs/planning/current-slice.md`;
5. only then authorize implementation.

PR #10 must remain unmerged until the Human Project Owner arbitrates.
