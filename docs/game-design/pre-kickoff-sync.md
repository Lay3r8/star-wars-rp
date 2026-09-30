# Game Design Pre-Kickoff Sync

Status: CONSOLIDATED
Owner: Senior Game Designer / RPG Systems Designer
Branch: `ai/game-design/pre-kickoff-sync`

## Purpose

This document consolidates the game-design conclusions discussed before kickoff and compares them with the current state of `main`.

It is a synchronization artifact, not a redesign. It does not authorize implementation, change Product/UX/Architecture decisions, or promote unresolved game-design proposals to accepted status.

## What is already normative from main

The following repository decisions constrain Game Design and are already accepted unless explicitly noted otherwise:

- Custom D20 is first-party for the MVP.
- PostgreSQL is the source of truth for mutable campaign state.
- Campaign isolation is enforced using `campaign_id`.
- `Entity` is an identity registry, not a generic property bag.
- Stable first-party concepts use typed relational tables.
- Dynamic extension-owned data uses `EntityExtensionData` with `namespace`, `schema_id`, `schema_version`, and JSONB payload.
- `KnowledgeFragment` represents a proposition/claim and carries GM-side veracity metadata.
- `CharacterKnowledge` represents a character's epistemic state for a fragment; absence means unknown.
- Player-facing endpoints use explicit player projections/read models.
- `DomainEvent` is append-only history/audit data; current state is not reconstructed through event sourcing.
- A transactional outbox is the intended mechanism for future durable asynchronous publication when a concrete need exists.
- Platform Core is restricted to genuinely cross-cutting concepts.
- Species, Class, Skills, Talents, progression mechanics, and Force mechanics belong to Custom D20.
- Setting Packs are primarily data-oriented and reference mechanics explicitly supported by Custom D20.
- The GM retains final narrative authority, but this remains marked "To formalize" in the cross-domain decision log.

## Game-design conclusions already discussed

The following conclusions emerged from the game-design review and follow-up discussion. They are **PROPOSED** unless already covered by a normative repository decision.

### PROPOSED — Design principle: simple mechanics, broad fictional possibility

The game should deliberately keep its mechanical and technical primitives small while allowing a wide range of fictional situations, approaches, consequences, and combinations.

Examples of the intended direction:

- range bands rather than grid-distance arithmetic;
- a small number of relationship states/tags rather than large matrices of social statistics;
- clocks for escalating threats rather than continuous simulation;
- a bounded vocabulary of deterministic rule effects rather than a general scripting language;
- procedural generation that creates many possible situations without requiring mechanically distinct subsystems for each one.

This is a game-design principle, not yet an accepted cross-domain decision.

### PROPOSED — Core resolution loop

The proposed reference loop is:

```text
Fictional positioning
-> Player intent
-> Player approach
-> GM decides whether a roll is necessary
-> Stakes
-> Mechanic selection
-> Roll
-> Mechanical outcome
-> Optional narrative secondary outcome
-> Consequence interpretation
-> Proposed state changes
-> Deterministic effects and/or GM-confirmed narrative effects
-> Knowledge/visibility update
-> New fictional situation
-> Next player choice
```

The exact persistence/API representation remains Architecture-owned.

### PROPOSED — When to roll

A roll should normally exist only when all of the following are true:

1. the outcome is uncertain;
2. there is a meaningful consequence or cost;
3. both success and failure are fictionally possible.

If failure would not materially change the situation, the GM should normally not request a roll.

This also provides the main protection against "retry until success".

### PROPOSED — Intent and approach are distinct

The player's **intent** describes the desired outcome.

The player's **approach** describes how they try to obtain it.

The fiction determines which mechanic, skill, difficulty, advantage/disadvantage, or other rule is applicable.

### PROPOSED — Stakes contract

The minimum useful stakes declaration is currently proposed as:

- **Intent:** what the acting character is trying to obtain;
- **Risk:** the primary meaningful consequence if the attempt goes badly.

Additional detail may be added when useful, but the live-session workflow should not require the GM to author a complete branching outcome tree before each roll.

### PROPOSED — D20 primary outcome

The game should keep the primary resolution mechanic recognizable and bounded, using a D20 check against a difficulty or resistance.

Open numerical details include:

- final difficulty scale;
- modifier budgets;
- degree-of-success thresholds;
- opposed-roll rules;
- critical rules.

No final numbers are accepted yet.

### PROPOSED — Circumstantial advantage/disadvantage over modifier stacking

For ordinary fictional circumstances, advantage/disadvantage is preferred over accumulating many small +/- modifiers.

The exact roll procedure and cancellation/stacking rules remain to be accepted.

### PROPOSED — Optional narrative secondary outcome

A secondary narrative result was discussed as a way to produce outcomes such as:

- success with complication;
- success with opportunity;
- failure with complication;
- failure with opportunity.

A candidate model is an additional small die used only for explicitly dramatic checks, not every routine attack or skill check.

The existence, die size, frequency, and exact interpretation of this mechanic remain **OPEN**.

### PROPOSED — Failure changes the situation

After a failed roll, the exact same fictional situation plus the exact same approach should not normally permit an immediate identical reroll.

A new attempt should require a meaningful change such as:

- a different approach;
- different equipment;
- assistance;
- a changed position;
- additional time;
- acceptance of increased risk or cost.

### PROPOSED — Consequence classes

Three broad classes are proposed for design purposes.

#### A. Deterministic effects

Effects whose meaning is mechanically complete once the GM has accepted the action/stakes.

Examples:

- damage/resource change;
- consume item/charge;
- add/remove bounded condition;
- advance/retreat a clock;
- add/remove a mechanical tag.

These may be candidates for automatic application.

#### B. Bounded narrative consequences

The rules can determine that a consequence is warranted, but the GM must select, confirm, edit, or replace its concrete fictional meaning.

Examples:

- NPC attitude changes;
- faction suspicion increases;
- a location becomes compromised;
- a persistent injury is proposed;
- an opportunity is created or removed.

These should not silently mutate important campaign state.

#### C. Authoritative narrative changes

Major narrative/canonical changes remain GM decisions.

Examples:

- changing canonical truth;
- killing a major NPC;
- changing a major NPC motivation;
- transferring political control of a major location;
- creating or resolving major story elements.

### CROSS-DOMAIN DECISION — Proposed vs committed consequences

The existing UX and Architecture pre-kickoff work both point toward a structured boundary between mechanical outcome and committed campaign mutation.

Candidate conceptual flow:

```text
Roll outcome
-> Proposed consequence/effect
-> GM adjudication
-> Accepted effect(s)
-> Committed world-state change
-> History
```

**GAME DESIGN IMPACT:** defines which consequences are deterministic versus interpretive.  
**UX IMPACT:** requires an efficient accept/edit/replace/ignore workflow.  
**ARCHITECTURE IMPACT:** requires transaction, correlation, and persistence semantics.  
**PRODUCT IMPACT:** affects how much assistance the product provides during live play.

This is not yet accepted.

### PROPOSED — Range bands instead of tactical distance arithmetic

The preferred direction is abstract distance bands rather than measuring grid squares/metres for ordinary combat.

Candidate vocabulary:

- Engaged / very close;
- Near / close;
- Far;
- Distant / very far.

Weapons and actions can define effective and disadvantaged bands rather than exact geometry.

Whether the MVP includes a tactical map remains a Product/UX question.

### PROPOSED — Character build responsibilities

The existing character structure can remain healthy if each axis has a clear responsibility:

- **Species:** limited biological/physiological traits;
- **Origin:** social/background context, competencies, contacts;
- **Class:** primary mechanical role;
- **Specialization:** focused expression of that role;
- **Force Affinity:** sensitivity/potential;
- **Force Tradition:** learned framework and training;
- **Talents:** granular customization.

The main game-design risk is allowing every layer to become a large independent power package.

### PROPOSED — No multiclassing in the first playable slice/MVP

Because Class, Specialization, and out-of-class talents already provide hybridization space, full multiclassing is currently considered unnecessary complexity for the MVP.

This is not yet accepted.

### PROPOSED — Talent access categories

A candidate structure is:

- general talents;
- class-associated talents;
- signature talents.

The purpose is to allow customization while limiting unrestricted cherry-picking of dominant combinations.

Exact talent rules remain open.

### PROPOSED — Bounded progression

Progression should prefer increasing options, techniques, reactions, contacts, and meaningful capabilities over unrestricted numerical inflation.

The intent is to reduce power creep while preserving character growth.

No numerical progression curve is accepted yet.

### PROPOSED — Force structure

The Force should not be modeled as a generic mana system.

The current proposed separation is:

- **Force Affinity:** sensitivity/potential;
- **Training / Tradition:** what has been learned and through which framework;
- **Techniques:** concrete capabilities;
- **Strain or equivalent cost:** pressure from pushing beyond safe limits.

A character may be Force-sensitive without being trained or able to deliberately execute formal techniques.

The exact Dark Side / temptation model remains open.

### PROPOSED — Temptation should create choices, not only penalties

A promising direction is to make emotionally charged or Dark Side use an offer with power and consequences rather than a passive corruption tax.

A full universal corruption meter is not recommended for the first slice without playtesting.

### PROPOSED — Knowledge is a gameplay system, not only disclosure plumbing

The accepted `KnowledgeFragment` / `CharacterKnowledge` split should support gameplay involving:

- secrets;
- rumours;
- misinformation;
- partial information;
- contradictory claims;
- differing beliefs;
- provenance;
- sharing between characters;
- gradual discovery;
- information whose exposure itself creates consequences.

Exact epistemic states remain Game Design-owned and open.

A small initial vocabulary such as `Aware`, `Believed`, and `Doubted` was discussed, with absence meaning unknown, but this is **not accepted**.

### PROPOSED — Knowledge provenance matters

When information is shared, the receiving character should be able to know the claim through the sharing character without converting it into canonical truth.

Example conceptually:

```text
KnowledgeFragment X
-> Character A believes X
-> Character A tells Character B
-> Character B becomes aware of / believes X
   source = Character A
```

This supports rumours, deception, propaganda, and later source re-evaluation.

The exact data model is Architecture-owned.

### PROPOSED — Dangerous knowledge / infohazards are separate from veracity

Whether a claim is true and whether exposure to it creates consequences are separate concepts.

If dangerous knowledge is included in campaign content, exposure triggers and effects should not be encoded as truth/veracity states.

This remains a campaign/game-design feature proposal, not an architecture decision.

### PROPOSED — Relationships should remain low-bookkeeping

The preferred direction is:

- a short overall disposition scale;
- relationship tags for specific facts such as debts, suspicion, fear, respect, betrayal;
- clocks only when a relation-like state is progressing toward a concrete event.

Large matrices of trust/fear/loyalty/respect/suspicion/etc. for every pair of entities are explicitly discouraged.

### PROPOSED — Reputation is distinct from personal disposition

A personal NPC relationship and a faction-level reputation are different game concepts and should not be collapsed into one universal social score.

### PROPOSED — Combat should be cinematic and objective-driven

The preferred combat direction is:

- low action-economy complexity;
- abstract range/position;
- meaningful cover/positioning;
- objectives beyond "reduce all enemies to zero";
- grouped handling for anonymous enemies;
- persistent consequences only when they add later decisions.

Exact initiative, health, armour, weapon, reaction, and action rules remain open.

### PROPOSED — Vitality plus persistent wounds

A two-layer health concept was discussed:

- **Vitality:** short-term ability to stay in the fight;
- **Wounds:** rarer persistent consequences.

This is a candidate model only. It has not been accepted.

### PROPOSED — Minion / NPC groups

Anonymous enemies such as stormtrooper squads should be representable and resolved as groups rather than forcing the GM to maintain a full persistent character record for every combatant.

Exact group rules remain open.

### PROPOSED — Vehicles and space combat are post-MVP unless the first slice proves otherwise

The recommendation is to validate personal-scale conflict first and later reuse common primitives for vehicles/space combat rather than creating a separate complete rules engine immediately.

Product must confirm scope.

### PROPOSED — World activity uses selective simulation

The persistent world should feel alive without continuously simulating every NPC/faction/location.

A candidate relevance model is:

- **Active:** currently in scene/play;
- **Relevant:** may advance through clocks/events between scenes;
- **Background:** unchanged until reactivated or affected by a major event.

This is a game-design direction; exact lifecycle/persistence semantics remain Architecture/Product-owned.

### PROPOSED — Factions and threats advance through clocks/events

Faction plans, investigations, alerts, threats, travel pressure, and similar progressions are good candidates for clocks.

A "campaign pulse" after a session, time skip, or explicit GM action was discussed as a simpler alternative to permanent background simulation.

The exact workflow is not accepted.

### PROPOSED — Procedural generation creates situations, not only encyclopedic data

Generated content should create playable situations, not just descriptive world facts.

For relevant generated locations or contexts, the preferred direction is a bounded set of interconnected gameplay hooks such as:

- opportunities;
- secrets;
- threats;
- pressures;
- conflicts;
- notable NPCs;
- points of interest;
- resources;
- rumours.

The latest working direction is **1 to N elements per relevant category, with an upper bound around 5**, rather than exactly one element per category.

The generator should prefer connected elements that explain, escalate, reveal, threaten, or enable one another.

Example relationship:

```text
Pressure -> Conflict <- NPC
    |          |
 escalates   creates
    v          v
 Threat    Opportunity
       ^
       |
     Secret
```

The upper bound, minimum requirements, and category list are not yet accepted.

### PROPOSED — Generated elements may be latent

Generated opportunities, secrets, threats, and pressures do not all need to be active simultaneously.

Candidate states such as active/latent/dormant were discussed so the generator can produce depth without forcing the GM to manage every generated hook at once.

The exact state model is open.

### PROPOSED — Generated elements should answer gameplay questions

A generated element should normally contribute to at least one meaningful question:

- What can the players gain?
- What can the players lose?
- What can they discover?
- What is changing?
- Who wants something?
- What happens if nobody intervenes?

This is a design heuristic, not a persistence requirement.

### PROPOSED — Rule Effect DSL should remain deliberately small

Game Design supports the Architecture proposal to keep any Rule Effect DSL as a closed vocabulary of bounded mechanical effects.

Likely candidates include:

- resource add/remove;
- condition add/remove;
- clock advance/retreat;
- tag add/remove;
- modifier grant/remove;
- knowledge reveal where game semantics are explicit.

The DSL should not become a general scripting environment for arbitrary narrative interpretation, procedural generation, or NPC decision-making.

Exact effect vocabulary remains open and should be slice-driven.

## Contradictions found

No direct contradiction was found between the accepted ADRs/current `main` and the game-design conclusions above.

The main discrepancy is documentation maturity:

- Architecture and UX already reference a likely `ActionResolution / Stakes / consequence proposal` boundary;
- Game Design has not yet made the resolution semantics normative;
- `main` contains no accepted numerical D20 procedure, progression model, combat model, Force cost model, relationship model, or procedural-generation gameplay contract.

This sync deliberately leaves those as proposals/open questions.

## Assumptions not yet validated

The previous game-design review assumed or proposed the following without authoritative Product approval:

- combat belongs in the first playable MVP;
- a tactical map is not required for core resolution;
- range bands are sufficient for the intended experience;
- the MVP should include player-side live participation;
- a live-session context exists as a first-class workflow;
- knowledge provenance should be player-visible/useful in the first slice;
- generated locations are expected to provide multiple hooks per category;
- faction clocks or a campaign pulse belong in the MVP;
- out-of-class talents are part of the initial character build;
- a Strain-like resource is the correct first Force cost;
- Vitality + Wounds is the correct health structure;
- multiclassing can be deferred without harming the product promise;
- vehicle and space combat can be deferred.

These require kickoff arbitration where they affect scope or other disciplines.

## Major game-design risks before implementation

### CRITICAL — Resolution semantics are not accepted

The repository does not yet define precisely:

- when a roll is required;
- what minimum stakes must be established;
- how success/failure is interpreted;
- whether a narrative secondary result exists;
- when consequences become state mutations.

Implementing a generic rule engine before these are accepted would risk encoding unstable semantics.

### CRITICAL — Mechanical outcome must not silently become narrative truth

The project needs a clear boundary between a roll result, a consequence proposal, GM adjudication, and committed world state.

This is the most important cross-domain rule/UX/architecture dependency before implementing assisted resolution.

### HIGH — Character-build combinatorics

Species + Origin + Class + Specialization + Force Affinity + Force Tradition + Talents can become difficult to balance if every axis is a large independent power source.

### HIGH — Over-automation

Automating interpretive consequences would undermine the accepted principle of GM narrative authority.

### HIGH — Over-simulation

Persistent-world ambition can create disproportionate implementation and GM bookkeeping if it becomes continuous simulation rather than selective clocks/events.

### HIGH — Over-generalized DSL

A highly expressive rule DSL would become a second programming language and prematurely freeze unstable game semantics.

### MEDIUM — Knowledge reduced to access control

If knowledge is implemented only as hidden/visible content, the project loses much of the gameplay value enabled by the accepted canonical-claim/character-belief architecture.

### MEDIUM — Excess social bookkeeping

Too many numeric relationship dimensions would create maintenance burden without proportionate player choice.

## Open game-design questions for kickoff

1. What exact GM/player scenario defines the first vertical slice?
2. What is the accepted "when to roll" rule?
3. What is the minimum stakes contract?
4. What is the exact primary D20 resolution procedure required by the first slice?
5. Does the MVP include a secondary narrative result? If yes, when is it rolled?
6. What counts as a deterministic consequence versus a consequence requiring GM confirmation?
7. What correction/override behavior is required after a resolution has been applied?
8. Are abstract range bands accepted for the first slice?
9. Is tactical grid movement explicitly out of scope, optional UI, or required later?
10. Which character-build components are required by the first slice?
11. Is full multiclassing explicitly deferred?
12. Which talent access rules are needed initially?
13. What progression cadence and power-growth philosophy are accepted?
14. What minimum Force mechanics are required in the first slice?
15. Is Strain or an equivalent pressure resource accepted?
16. Does the first slice require Dark Side temptation/corruption mechanics?
17. Which epistemic states must `CharacterKnowledge` support?
18. Is knowledge provenance required in the first slice?
19. Do dangerous-information mechanics belong to the generic Custom D20 system, a campaign module, or later content?
20. What minimal relationship representation is required?
21. What minimal combat model belongs to the first slice?
22. Is Vitality + Wounds accepted or should health remain simpler initially?
23. Do grouped/minion NPC rules belong to the first slice?
24. Are vehicles/space combat explicitly post-MVP?
25. Which clocks are required by the first slice, if any?
26. Does the MVP require off-screen faction progression/campaign pulse?
27. What procedural-generation categories are required for the first slice?
28. Is the 1..N (max ~5) per relevant category generation model accepted?
29. Must generated hooks be explicitly linked to one another?
30. Can generated hooks exist in latent/dormant states before becoming active?
31. Which Rule Effect primitives are actually required by the first slice?

## Cross-domain dependencies

### PRODUCT IMPACT

Product must decide:

- first vertical slice and MVP scope;
- whether combat belongs to the first slice;
- whether tactical maps are part of the product promise;
- whether live world generation is required during sessions;
- whether faction/off-screen progression belongs to MVP;
- whether vehicles/space combat can be deferred;
- which player-facing knowledge/history capabilities matter in the first release.

### UX IMPACT

UX must make the accepted resolution model usable during live play without turning each roll into form filling.

Particularly sensitive workflows include:

- defining stakes;
- accepting/editing/replacing proposed consequences;
- range/position presentation;
- knowledge reveal and provenance;
- clock visibility;
- low-friction NPC/location creation;
- generated candidate review.

### ARCHITECTURE IMPACT

Architecture depends on Game Design for:

- the exact resolution contract;
- deterministic versus interpretive effects;
- required Rule Effect vocabulary;
- knowledge-state semantics;
- relationship primitives;
- combat-state requirements;
- progression and Force state;
- procedural-generation acceptance/state requirements.

Game Design does not prescribe persistence/API shapes beyond these semantic needs.

### SECURITY IMPACT

Rules involving secrets, private knowledge, individual character beliefs, or targeted reveals require backend-enforced disclosure boundaries.

Game Design should never rely on frontend hiding of canonical/GM information.

## Recommended minimal game-design documentation before kickoff

This document is sufficient as the pre-kickoff game-design consolidation.

After kickoff decisions, add only the documents needed by the accepted first slice, likely:

- accepted core resolution contract;
- accepted consequence/stakes semantics;
- first-slice character/combat rules if required;
- first-slice knowledge mechanics;
- procedural-generation gameplay contract if generation is in-scope;
- accepted Force rules only if required by the slice.

Do not pre-document large catalogs of classes, talents, powers, weapons, vehicles, or full simulation rules before the slice needs them.

## Implementation gate

This sync does not authorize implementation.

The implementation gate in `docs/planning/PROJECT_KICKOFF.md` remains authoritative.
