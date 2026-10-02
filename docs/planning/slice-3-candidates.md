# Slice 3 Candidate Consolidation

**Status:** HUMAN OPTION SELECTED — SLICE SPECIFICATION REQUIRED  
**Owner:** Product Lead  
**Purpose:** Consolidated cross-domain review and Human arbitration artifact  
**Source of truth:** current `main` + completed Game Design, UX and Architecture reviews of PR #14

This document does **not** select Slice 3.

---

# 1. Consolidation result

The three specialist reviews agree that all five original candidates are technically viable **if kept within their explicit exclusions**.

They differ materially in readiness and Product learning value.

## Final Human-arbitration shortlist

1. **OPTION A — Roll, Review and Adjudicate**
2. **OPTION B — Escape the Imperial Patrol**
3. **OPTION C — Generate, Review and Play One Situation**

## Candidates deferred from immediate arbitration

### Remember Where You Learned It — Player Knowledge Library

**FACT**

This is the most cross-domain-ready candidate:

- Game Design: READY;
- UX: READY;
- Architecture: READY;
- migration/operational cost: low;
- reuse: very high.

**EXPERT POSITION**

The reviews agree it can remain small:

- `AWARE` is sufficient;
- contradictory claims may coexist;
- source/acquisition context remains optional/descriptive;
- no Believed/Doubted;
- no provenance graph;
- no Quest dependency;
- simple PostgreSQL search.

**PRODUCT RECOMMENDATION**

Defer it from immediate Slice 3 arbitration.

Reason:

- Slice 1 and Slice 2 already exercised KnowledgeFragment, CharacterKnowledge, disclosure and Player knowledge projection extensively;
- this candidate deepens a strong existing seam rather than testing a major still-unproven pillar;
- it is technically attractive precisely because it is incremental, but that also means lower breadth of Product learning than the three retained options.

This candidate is a strong later slice and may become attractive if Product priority shifts to Player-facing polish/utility.

### Publish an Intel Catalogue to a Player

**FACT**

This has credible GM + Player value and would advance the long-term campaign-database vision.

**EXPERT POSITION**

Game Design is READY, but UX and Architecture both require contract decisions first:

- safe base fields;
- already-published state;
- live grant vs publication snapshot;
- update/republish semantics;
- referenced-entity disclosure;
- exact projection-security boundary.

**PRODUCT RECOMMENDATION**

Defer from immediate Slice 3 arbitration.

Reason:

- it primarily extends disclosure/projection/search patterns already proven in Slice 2;
- its strongest new learning is entity-level publication security, not a new gameplay loop;
- the long-term campaign-database direction remains valid, but there is no need to establish it before at least one more foundational gameplay/differentiation pillar is tested.

---

# 2. OPTION A — Roll, Review and Adjudicate

## PRODUCT VALUE

### FACT

Current implementation already separates Roll from canonical success Apply, but the persisted model still couples mechanical outcome and final resolution semantics tightly.

Manual testing produced a validated future Product direction:

> the GM should retain explicit authority over the final adjudicated outcome and be able to correct a finalized adjudication without rewriting the original die.

### EXPERT POSITION

Game Design: high foundational value, but semantic contract must be fixed first.

UX: high GM trust/value, but common-path finalization must remain fast.

Architecture: high reuse and low operational cost; no new infrastructure required.

### PRODUCT RECOMMENDATION

Keep as a final option.

This is the strongest **foundation-first** candidate because it directly reduces ambiguity before future combat and Player-side rolling depend on resolution semantics.

## GAME DESIGN READINESS

**NEEDS SMALL GAME-DESIGN CONTRACT FIRST**

Required contract:

- immutable raw roll;
- immutable mechanical result;
- distinct final adjudicated outcome;
- override may change final adjudication, not raw evidence;
- no canonical consequence commits before GM finalization;
- correction supersedes prior adjudication while preserving history;
- no generic rollback.

Safe deferrals:

- crits;
- degrees;
- opposed rolls;
- Player rolling;
- group actions;
- generic consequences;
- generic undo.

## UX READINESS

**NEEDS SMALL UX CONTRACT FIRST**

Preferred common path:

```text
Create resolution
-> Roll
-> Mechanical result
-> Accept / Finalize
```

Exceptional path:

```text
Mechanical result
-> Override
-> Final outcome
-> Finalize
```

Correction:

```text
Finalized resolution
-> Correct outcome
-> preserve original roll/current history
-> commit replacement adjudication
```

UX explicitly warns against confirmation fatigue.

## ARCHITECTURE READINESS

**NEEDS CONTRACT DECISIONS FIRST, THEN LOW/MODERATE COST**

Strong reuse:

- D20 function;
- ActionResolution row/locking;
- authz;
- DomainEvent;
- integration/E2E harness.

Architecture can likely prove the concept by narrowly evolving the existing slicing resolution.

It must **not** become a generic resolution engine.

## SECURITY IMPACT

Moderate.

Only GM may:

- finalize;
- override;
- correct.

Raw roll, DC, modifier and mechanical result must remain non-rewritable by adjudication commands.

## REUSE

Highest among final options.

## NEW COMPLEXITY

Moderate:

- explicit adjudication state;
- finalization transition;
- correction/supersession;
- possible bounded corrective mutation;
- Player-visible history only if selected.

## WHAT WE LEARN

- whether explicit GM adjudication improves trust and usability;
- whether GM authority can coexist with immutable dice evidence;
- whether correction is understandable without generic undo;
- whether this becomes the right foundation for combat and collaborative Player rolling.

## WHAT WE DEFER

- generic resolution engine;
- collaborative rolls;
- Player dice;
- realtime;
- combat;
- crits/degrees;
- opposed rolls;
- arbitrary effect compensation;
- generic undo.

## RISKS

- over-generalizing ActionResolution;
- override harming Player agency if routine/invisible;
- excessive confirmation;
- ambiguity between mechanical and fictional outcome;
- impossible promises of rollback after irreversible human-visible effects.

## BLOCKERS

Before implementation:

1. define whether finalization is required for every persisted/consequential roll;
2. define exact override semantics;
3. define bounded correction semantics;
4. decide what, if anything, the Player sees of mechanical/final/correction history;
5. decide whether Slice 3 deliberately remains on the current slicing action or introduces one other bounded action shape.

## HUMAN DECISION

Choosing A means prioritizing **resolution correctness and future-system leverage** over introducing a large new gameplay/domain pillar immediately.

---

# 3. OPTION B — Escape the Imperial Patrol

## PRODUCT VALUE

### FACT

Personal-scale combat remains one of the largest completely unproven RPG capabilities.

### EXPERT POSITION

Game Design: high value but requires a combat micro-contract first.

UX: high live-play value; repeated interaction cost is the dominant constraint.

Architecture: viable in the existing monolith, but it is the largest new data/gameplay aggregate among the options.

### PRODUCT RECOMMENDATION

Keep as a final option.

This is the strongest **core-gameplay breadth** candidate.

## GAME DESIGN READINESS

**NEEDS GAME-DESIGN CONTRACT FIRST**

Minimum required:

- one objective and end condition;
- deterministic turn order;
- one action per unit/turn;
- one attack procedure;
- defence/DC rule;
- deterministic damage;
- short-term health;
- incapacitation;
- hostile group/minion semantics;
- minimum abstract range/position only if required.

Safe deferrals:

- tactical grid;
- exact movement;
- reactions;
- Vitality/Wounds;
- critical injury system;
- full weapon/armour catalogue;
- Force;
- talents;
- progression;
- vehicles/space combat;
- NPC AI.

## UX READINESS

**NEEDS UX CONTRACT AFTER GAME DESIGN**

Required live loop:

```text
objective/current turn
-> choose action/target
-> resolve
-> state change
-> advance
-> repeat
-> encounter ends
```

Routine combat must not reuse long free-text Intent/Risk entry for every attack.

Must choose:

- GM-mediated;
- Player-active commands.

No tactical map required.

## ARCHITECTURE READINESS

**NEEDS RULE CONTRACT FIRST**

Likely new state:

- combat-specific Encounter;
- combatants/hostile representation;
- turn/order;
- health/damage;
- objective/end state;
- minimal range if required.

Architecture explicitly warns:

- do not create generic Scene;
- do not use current ActionResolution as combat engine;
- do not introduce Rule Effect DSL;
- do not decide durable Character HP before Game Design does.

## SECURITY IMPACT

Moderate if GM-mediated.

High if Player-active:

- actor server-derived;
- current-turn validation;
- target/action legality server-side;
- authoritative randomness/mechanics.

## REUSE

Good infrastructure reuse:

- Character;
- D20;
- auth/authz;
- Location;
- transactions;
- projections;
- history;
- tests.

Less literal domain-model reuse than A.

## NEW COMPLEXITY

Highest of final options:

- new gameplay aggregate;
- repeated shared state;
- health/damage;
- hostile actors/groups;
- turn lifecycle;
- combat UX;
- concurrency/stale-action handling.

## WHAT WE LEARN

- whether the product works as an actual combat RPG assistant;
- whether cinematic non-grid combat is sufficient;
- whether repeated actions remain fast enough;
- whether CombatEncounter is needed;
- minimum health/damage/hostile model;
- whether Players should directly submit routine actions.

## WHAT WE DEFER

- complete combat system;
- tactical VTT;
- equipment catalogue;
- reactions;
- advanced conditions;
- crit injuries;
- Force/talents;
- vehicles;
- generic Scene;
- realtime until command/freshness needs prove it.

## RISKS

- longest likely slice;
- scope explosion;
- premature rules commitments;
- bookkeeping-heavy UX;
- over-generalized Encounter/rules engine;
- Player-active commands increasing auth/concurrency burden.

## BLOCKERS

Before implementation:

1. accept combat micro-contract;
2. choose GM-mediated vs Player-active;
3. define health persistence semantics;
4. define hostile group representation;
5. define minimum range/position;
6. UX validate repeated-action flow.

## HUMAN DECISION

Choosing B means prioritizing **core RPG gameplay validation now**, accepting the largest up-front Game Design and implementation cost.

---

# 4. OPTION C — Generate, Review and Play One Situation

## PRODUCT VALUE

### FACT

Procedural generation remains a major intended product differentiator and is completely unproven.

Slice 2 now provides typed campaign state — Location, Character/Contact, Knowledge — into which generated material can canonicalize.

### EXPERT POSITION

Game Design: potentially high value, but generation must produce a playable situation rather than prose.

UX: potentially high prep value, but highest conditional throwaway-UI risk if lifecycle/package decisions are not fixed first.

Architecture: feasible in the monolith; no worker/realtime required by default.

### PRODUCT RECOMMENDATION

Keep as a final option.

This is the strongest **product-differentiation** candidate.

## GAME DESIGN READINESS

**NEEDS SMALL GAME-DESIGN CONTRACT FIRST**

Minimum playable situation:

- Location/context;
- pressure/threat;
- opportunity;
- secret/rumour/claim;
- concrete hook/affordance;
- at least one meaningful relationship between elements.

At least one accepted generated element must produce a meaningful Player choice or trigger an existing gameplay operation.

No universal procedural grammar required.

## UX READINESS

**NEEDS CONTRACT FIRST**

Preferred flow:

```text
Generate
-> review bounded structured candidate
-> minimal edit
-> Accept / Reject
-> canonical campaign state
-> use one accepted element in play
```

UX recommends whole-package acceptance for the first slice unless a concrete reason for partial acceptance emerges.

Must decide:

- package size;
- candidate durability;
- whole vs partial accept;
- review workload.

## ARCHITECTURE READINESS

**NEEDS CONTRACT DECISIONS FIRST**

If candidate is transient:

- no staging table required.

If candidate must survive refresh:

- one narrow validated/schema-versioned staging payload may be justified.

Accepted content must become ordinary typed campaign state.

Architecture explicitly rejects creating generic `Threat`, `Opportunity`, or `Hook` tables merely because those labels appear in generated output.

## SECURITY IMPACT

Low/moderate with local deterministic generator.

High with external provider:

- outbound data policy;
- API keys;
- data minimization;
- output validation;
- hidden campaign data;
- provider failures/timeouts.

Generated output is untrusted until accepted.

## REUSE

High after canonicalization:

- Location;
- Contact/Character;
- KnowledgeFragment;
- authoring services;
- GM auth;
- disclosure;
- persistence;
- tests.

## NEW COMPLEXITY

Medium/high:

- generator/provider boundary;
- structured candidate;
- review/edit/accept lifecycle;
- schema validation;
- optional staging;
- provider error handling.

## WHAT WE LEARN

- whether generation actually saves prep time;
- whether review effort cancels the value;
- minimum useful generated package;
- whether generated situations produce real Player decisions;
- whether generated content fits naturally into typed canonical state.

## WHAT WE DEFER

- world/planet/galaxy generation;
- AI GM;
- full plot generation;
- background simulation;
- faction simulation;
- provider/plugin framework;
- image generation;
- provenance graph;
- NPC stat generation;
- queue/worker unless actual durability need appears.

## RISKS

- impressive demo with weak actual GM value;
- review cost > manual authoring cost;
- premature generator/provider abstractions;
- accidental canonicalization;
- generated narrative labels driving domain schema;
- external data leakage;
- unstable review UI if lifecycle is not fixed first.

## BLOCKERS

Before implementation:

1. exact generated package;
2. exact observable "used in play" criterion;
3. whole vs partial acceptance;
4. candidate durability;
5. canonical representation of pressure/opportunity/hook if they must persist;
6. concrete provider mode;
7. outbound data policy if external provider.

## HUMAN DECISION

Choosing C means prioritizing **differentiation and GM prep automation**, accepting more lifecycle/provider uncertainty than A.

---

# 5. Cross-option comparison

## FACT

None of the three options requires:

- WebSockets/SSE;
- broker/worker;
- microservices;
- external search;
- graph DB;
- Kubernetes;
- generic workflow engine;
- generic Rule Effect DSL.

## FACT — readiness

### Option A

- Game Design: needs small contract;
- UX: needs small contract;
- Architecture: needs small contract, then low/moderate cost.

### Option B

- Game Design: needs substantial micro-contract;
- UX: follows after rules;
- Architecture: follows after rules;
- highest implementation complexity.

### Option C

- Game Design: needs small contract;
- UX: lifecycle contract required;
- Architecture: lifecycle/provider contract required;
- medium/high complexity.

## FACT — deferred candidates

### Player Knowledge Library

Technically easiest and most ready, but yields less breadth because Knowledge/disclosure have already been central to both completed slices.

### Campaign Catalogue Publication

Valuable long-term, but primarily extends already-proven search/projection/disclosure patterns and introduces a security-heavy publication contract before another major gameplay/differentiation pillar has been tested.

---

# 6. Human Arbitration Pack

## OPTION A — Roll, Review and Adjudicate

### SCOPE

One persisted D20 resolution:

```text
Roll
-> immutable mechanical result
-> GM Accept or Override
-> Finalize bounded consequence
-> optionally Correct final adjudication later
```

No generic resolution engine.

### PRIMARY USER VALUE

The GM retains explicit, auditable authority over what becomes the final fictional/canonical outcome.

### WHY NOW

Future combat and collaborative Player rolling will be safer if mechanical result and final GM adjudication are separated first.

### WHAT IT VALIDATES

- GM authority;
- Player trust in immutable roll evidence;
- finalization friction;
- correction semantics;
- durable resolution lifecycle.

### MAIN RISKS

- over-generalization;
- confirmation fatigue;
- arbitrary-feeling overrides;
- impossible "rollback" expectations.

### EXPLICIT EXCLUSIONS

- Player rolling;
- collaborative actions;
- combat;
- realtime;
- generic undo;
- generic consequence engine;
- crits/degrees/opposed rolls.

### WORK REQUIRED BEFORE IMPLEMENTATION

- small Game Design contract;
- small UX finalization/override/correction contract;
- Architecture decision on narrow evolution of current ActionResolution.

---

## OPTION B — Escape the Imperial Patrol

### SCOPE

One short objective-driven personal combat:

- one PC;
- one bounded hostile unit/group;
- one objective;
- deterministic turn rule;
- attack/defence;
- damage/health;
- incapacitation;
- encounter end.

No tactical map.

### PRIMARY USER VALUE

Run an actual Star Wars combat encounter inside the application.

### WHY NOW

Combat is one of the largest untouched pillars of the intended RPG.

### WHAT IT VALIDATES

- core combat loop;
- repeated live interaction;
- health/damage;
- hostile representation;
- encounter state;
- need for Player-active commands.

### MAIN RISKS

- scope explosion;
- longest likely implementation;
- premature combat design;
- bookkeeping UX;
- generic encounter/rule-engine creep.

### EXPLICIT EXCLUSIONS

- tactical grid;
- full initiative/action economy;
- reactions;
- armour system;
- critical injuries;
- full weapons;
- Force/talents;
- vehicles;
- NPC AI;
- generic Scene.

### WORK REQUIRED BEFORE IMPLEMENTATION

- combat Game Design micro-contract;
- Product decision on GM-mediated vs Player-active;
- UX repeated-action flow;
- Architecture encounter model after rules are fixed.

---

## OPTION C — Generate, Review and Play One Situation

### SCOPE

Generate one bounded structured situation, review/edit it, explicitly accept it, canonicalize it into ordinary campaign state, then use at least one generated element in play.

### PRIMARY USER VALUE

Reduce GM prep effort while producing playable material rather than only generated prose.

### WHY NOW

Generation is a major intended differentiator and Slice 2 now provides useful canonical entity/knowledge targets.

### WHAT IT VALIDATES

- generation value after review cost;
- candidate vs canonical lifecycle;
- minimum playable generated structure;
- generated-content integration with campaign state;
- provider boundary.

### MAIN RISKS

- demo value without prep value;
- review fatigue;
- lifecycle ambiguity;
- premature generation framework;
- provider/data-egress complexity.

### EXPLICIT EXCLUSIONS

- whole-world generation;
- AI GM;
- background simulation;
- faction simulation;
- provider/plugin framework;
- image generation;
- automatic canonical writes;
- queue/worker by default.

### WORK REQUIRED BEFORE IMPLEMENTATION

- exact playable package;
- whole/partial acceptance decision;
- candidate durability decision;
- canonical representation decision;
- provider mode;
- UX review/edit/accept contract;
- external data policy if provider is external.

---

# 7. Product recommendation

## PRODUCT RECOMMENDATION: OPTION A — Roll, Review and Adjudicate

This is the preferred next slice.

Reasoning:

1. It addresses a limitation directly observed during manual testing, not a hypothetical future feature.
2. It strengthens the core action-resolution contract before combat and collaborative rolling depend on it.
3. It has the highest literal reuse among the three retained options.
4. It remains a small vertical slice if deliberately kept on one bounded D20 action.
5. It reduces future migration risk by clarifying mechanical result vs final GM adjudication now.
6. It provides new gameplay-system learning without the implementation breadth of combat.
7. It preserves the Human Product direction that the GM retains final authority while keeping raw dice evidence immutable/auditable.

### Why not Option B as the default now

Combat offers more visible gameplay value, but it requires the largest number of new rules and the largest new persistent gameplay aggregate.

A cleaner adjudication contract first should reduce ambiguity in later combat resolution.

### Why not Option C as the default now

Generation remains strategically important, but its core lifecycle/package/provider contracts are less mature and it has the highest risk of throwaway Product/UX work if specified prematurely.

### Why not the technically easiest Player Knowledge Library

It is a good slice, but after two knowledge/disclosure-heavy slices, the marginal Product learning is lower than resolving the action-resolution authority boundary.

---

# 8. Human arbitration outcome

**Date:** 2026-10-02  
**Human Project Owner decision:** **OPTION A — Roll, Review and Adjudicate**

## Decision meaning

Option A is selected as the basis for Slice 3 specification.

This is **not yet an ACCEPTED implementation slice**.

Before implementation is authorized, the selected option must be converted into an exact cross-domain contract covering:

- exact user scenario;
- which persisted/consequential roll is used for the slice;
- immutable raw roll and mechanical result semantics;
- final GM adjudication semantics;
- override boundaries;
- finalization/commit boundary;
- correction/supersession semantics;
- behavior for already-applied or cognitively irreversible effects;
- Player-visible result/history, if any;
- UX common path vs exceptional override/correction path;
- architecture migration/evolution boundary for the existing Slice-1-specific ActionResolution;
- authorization/security;
- acceptance criteria and tests;
- explicit exclusions.

## Human-selected priority

The selected priority is:

> strengthen resolution authority/foundation before introducing combat or collaborative Player rolling.

## Deferred options

- **Combat — Escape the Imperial Patrol:** remains a credible later slice; still requires a combat micro-contract.
- **Generation — Generate, Review and Play One Situation:** remains a credible later slice; still requires package/lifecycle/provider contracts.
- **Player Knowledge Library:** remains deferred despite high readiness.
- **Campaign Catalogue Publication:** remains deferred; publication/security contracts are still required.
- **Collaborative Player Roll:** remains deferred and should benefit from the adjudication contract established here.

---

# 9. Slice 3 specification gate

The selected option becomes ACCEPTED only after:

1. Game Design finalizes the minimum mechanical-result vs adjudicated-outcome contract.
2. UX finalizes the minimum common-path finalization, exceptional override, and correction flows.
3. Architecture confirms the narrowest persistence/API evolution compatible with the accepted semantics.
4. Product consolidates those inputs into one exact end-to-end scenario and acceptance contract.
5. Any genuine material cross-domain disagreement is escalated to the Human Project Owner.
6. `docs/planning/current-slice.md` is updated only after the final Slice 3 specification is accepted.
7. Implementation begins only after that accepted contract is merged into `main`.

Until then, Option A is **SELECTED FOR SPECIFICATION**, not `ACCEPTED`.

PR #14 remains a selection artifact and must not be treated as implementation authorization.
