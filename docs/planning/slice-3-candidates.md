# Slice 3 Candidate Shortlist

**Status:** PROPOSED — CROSS-DOMAIN REVIEW REQUIRED  
**Owner:** Product Lead  
**Purpose:** Cross-domain review artifact for selecting the next vertical slice  
**Source of truth:** current `main` after Slice 2 implementation and future-directions merge

This document does **not** select Slice 3.

---

# 1. Baseline after Slice 2

## FACT — capabilities now proven

The project has now proven end-to-end:

- authenticated GM and Player principals;
- campaign membership and backend authorization;
- Player-to-Character assignment;
- Character and Location persistence;
- Contact persistence using Character identity + narrow Contact state;
- Contact create/edit;
- GM-only campaign-scoped Contact search;
- compact live Contact retrieval;
- KnowledgeFragment / CharacterKnowledge;
- explicit Player projections;
- safe hidden-information disclosure;
- one bounded D20 ActionResolution flow;
- Intent + Risk;
- backend-generated D20 resolution against DC;
- explicit Apply/Close terminal paths;
- synchronous transactional canonical mutation;
- DomainEvent history for meaningful changes;
- idempotent commands;
- reload/persistence;
- integration and E2E test infrastructure.

## FACT — important implementation constraints

### ActionResolution

The current persisted ActionResolution is still Slice-1-specific:

- mechanic fixed to slicing;
- success effect fixed to one KnowledgeFragment;
- actor = success recipient;
- state machine optimized for the Slice 1 disclosure scenario.

Future slices may reuse:

- D20 calculation;
- authorization patterns;
- transactional/idempotent commands;
- GM/Player separation;
- history;
- test infrastructure;

without generalizing the existing ActionResolution model by default.

### Knowledge

The accepted architecture already supports:

```text
KnowledgeFragment = claim/proposition + GM veracity
CharacterKnowledge = one Character's epistemic relationship to a claim
absence = unknown
```

Slice 2 deliberately exposed only one prepared claim per Contact as a narrow authoring shortcut.

Future Product direction explicitly expects Characters/NPCs to support 0..N knowledge entries and optional provenance when useful.

### Search

Slice 2 proves a small PostgreSQL Contact search only.

It does not establish:

- multi-entity global search;
- Player search;
- external search infrastructure;
- full campaign information architecture.

---

# 2. Evaluation principles

A credible Slice 3 candidate should:

1. deliver a concrete GM/Player outcome;
2. add meaningful new Product learning;
3. remain small enough for one developer;
4. reuse Slice 1/2 where useful;
5. avoid horizontal platform work;
6. traverse UX + domain rules + API + persistence + permissions + tests where applicable;
7. expose a real playtestable hypothesis;
8. defer adjacent systems aggressively.

The candidates below are deliberately **not ranked**.

---

# Candidate A — GM-Adjudicated Resolution

## NAME

**Roll, Review and Adjudicate**

## USER VALUE

The GM can create a normal D20 action, see the mechanical result, then explicitly decide the final adjudicated outcome before the resolution becomes canonical.

The GM can also correct/reopen a finalized resolution without deleting the historical roll.

This directly addresses the Human Product direction that the GM must retain control over the final result rather than having the mechanical roll automatically settle the fiction.

## WHY NOW

The project already has a working D20 path and history/audit foundation.

Manual testing exposed a meaningful limitation:

- raw mechanical result and final GM adjudication are currently effectively coupled;
- closed outcomes cannot be corrected cleanly;
- future combat and collaborative Player rolling would both benefit from a clearer resolution authority model.

This candidate can therefore harden a foundational gameplay contract **before** more systems depend on it.

## WHAT WE LEARN

- whether separating mechanical result from final adjudication improves GM trust/control;
- whether explicit GM approval adds acceptable friction;
- whether override/correction is understandable during live play;
- what history Players/GMs should see after correction;
- whether this contract is a better foundation for later combat and Player-side rolling.

## REUSE FROM SLICE 1/2

Very high reuse:

- D20 calculation;
- ActionResolution concepts;
- GM authorization;
- Character/Location context;
- transaction/idempotency patterns;
- DomainEvent history;
- E2E harness;
- Player projection boundaries.

## PRODUCT QUESTIONS

- Must every roll require explicit final GM approval?
- Is GM override of mechanical success/failure allowed?
- Is override limited to exceptional cases or normal authority?
- Should the GM provide a reason for override/correction?
- What does "rollback" mean in Product terms:
  - reopen;
  - supersede;
  - corrective mutation;
  - true deletion?
- What does the Player see:
  - raw roll only;
  - mechanical result;
  - final outcome;
  - correction history?

## GAME DESIGN REQUIRED

Substantial but bounded.

Game Design must define:

- mechanical result versus adjudicated outcome;
- whether the GM may override binary success/failure;
- whether an override changes only narrative outcome or also mechanical effects;
- when consequences are committed;
- correction/reopen semantics;
- relationship to future crits/degrees;
- whether a reason/fictional justification is required.

The candidate should not define the whole future resolution engine.

## UX REQUIRED

A compact live flow such as:

```text
create resolution
-> roll
-> mechanical result
-> GM Approve / Override
-> consequence preview
-> Finalize
```

And a bounded correction flow:

```text
closed resolution
-> Correct / Reopen
-> new adjudication
-> commit correction
```

UX must keep the distinction between:

- raw roll;
- mechanical result;
- final adjudication;

clear without turning every action into a wizard.

## ARCHITECTURE REQUIRED

Likely changes:

- separate immutable/raw roll data from final adjudication state;
- new transition(s) between rolled and finalized;
- auditable correction/supersession;
- compensating/corrective mutation where prior canonical effects changed;
- history projection showing current/final state without rewriting append-only events.

Architecture must decide whether to evolve the existing Slice-1-specific ActionResolution or introduce a cleaner first-party resolution model while preserving migration simplicity.

## SECURITY IMPACT

Moderate.

Only authorized GM may:

- approve;
- override;
- reopen/correct;
- finalize consequences.

Player must not be able to alter:

- DC;
- raw roll;
- modifiers;
- GM adjudication;
- hidden stakes.

## NEW COMPLEXITY

Moderate:

- richer resolution lifecycle;
- correction semantics;
- historical/current-state distinction;
- possible compensation of previously applied effects.

No new infrastructure service is required.

## RISKS

- over-generalizing ActionResolution too early;
- adding too much confirmation friction;
- confusing "mechanical success" with "fictional success";
- difficult correction semantics if canonical side effects already happened;
- temptation to build a generic undo/change-set engine.

## EXPLICIT EXCLUSIONS

- Player-side rolling;
- group actions;
- realtime/push;
- combat;
- generic Rule Effect DSL;
- generic workflow engine;
- global undo;
- full event sourcing;
- critical/degrees system;
- opposed rolls;
- arbitrary consequence framework.

## BLOCKERS

Game Design is the main blocker.

Before implementation:

- define mechanical result vs adjudicated outcome;
- define override authority;
- define bounded correction semantics;
- define whether already-applied deterministic effects can be corrected in this slice.

---

# Candidate B — Player Knowledge Library

## NAME

**Remember Where You Learned It**

## USER VALUE

The Player gets a useful searchable knowledge view rather than a flat list of claims.

A newly learned claim can carry safe acquisition context such as:

- where it was learned;
- source type;
- source entity if disclosed;
- timestamp;
- associated roll/result details when relevant.

The Player can search known information and understand **how/where they learned it** without seeing GM truth.

## WHY NOW

Slice 1/2 already proved safe disclosure but exposed the Player knowledge UX as deliberately minimal.

Manual testing specifically identified the need for:

- acquisition metadata;
- source/context;
- search;
- multiple claims over time;
- better understanding of contradictory/updated information.

This candidate can validate whether persistent knowledge is a real Player-facing differentiator rather than only a backend security construct.

## WHAT WE LEARN

- whether Players actually use/search a persistent knowledge library;
- which acquisition metadata is useful;
- whether source/location context improves comprehension;
- how much provenance is helpful before it becomes bookkeeping;
- whether contradictions/new versions are understandable without full belief mechanics;
- whether one shared epistemic model can serve PCs and NPCs.

## REUSE FROM SLICE 1/2

Very high:

- KnowledgeFragment;
- CharacterKnowledge;
- disclosure;
- Contact source context;
- Location;
- DomainEvent/history;
- Player projection;
- existing knowledge list UI;
- PostgreSQL search patterns.

## PRODUCT QUESTIONS

- What metadata belongs in the first usable acquisition record?
- Is source entity optional?
- Should timestamp be system-generated?
- Should roll detail show:
  - raw die;
  - modifier;
  - total;
  - DC;
  - without success/failure?
- What happens when two claims conflict?
- Is search enough, or are filters also required?
- Quest/thread grouping should be deferred unless a Quest model exists.

## GAME DESIGN REQUIRED

Moderate.

Game Design must decide:

- whether source provenance affects belief/confidence now or remains descriptive;
- whether AWARE remains sufficient for this slice;
- how contradictory claims are presented semantically;
- whether a Character can know multiple conflicting claims simultaneously;
- whether acquisition roll metadata has gameplay meaning or is informational only.

A full Believed/Doubted system is not automatically required.

## UX REQUIRED

Player-facing knowledge library:

- search;
- readable claim cards/list;
- compact acquisition metadata;
- safe handling of unknown source;
- optional source/location labels;
- clear distinction between:
  - claim;
  - source;
  - confidence/certainty if any;
  - truth, which remains hidden.

GM authoring must support a fast path with no provenance.

## ARCHITECTURE REQUIRED

Likely:

- optional knowledge acquisition/provenance record associated with CharacterKnowledge or acquisition event;
- source type;
- optional source entity;
- optional Location;
- acquired_at;
- optional related resolution/roll reference;
- Player-safe knowledge projection;
- Player knowledge search.

Architecture must avoid:

- putting provenance into KnowledgeFragment truth fields;
- mandatory source foreign keys;
- generic graph/provenance engine.

## SECURITY IMPACT

High.

Each metadata field may itself be hidden.

Player projection must independently authorize:

- claim;
- source identity;
- Location;
- roll context.

Knowing a claim must not automatically reveal a secret source.

## NEW COMPLEXITY

Moderate:

- provenance/acquisition data;
- Player search/read model;
- contradiction presentation;
- richer disclosure projection.

## RISKS

- deepening Knowledge again after two knowledge-heavy slices;
- over-modeling epistemology;
- confusing truth, belief and source;
- accidental source disclosure;
- adding quest/thread structure prematurely.

## EXPLICIT EXCLUSIONS

- Quest/thread model;
- Believed/Doubted unless Game Design proves necessary;
- provenance graph;
- automatic source-chain inference;
- misinformation propagation engine;
- AI summarization;
- shared Player notes;
- knowledge publication between Players;
- global entity database;
- semantic search.

## BLOCKERS

Game Design + UX:

- minimum acquisition metadata;
- contradiction semantics;
- source visibility.

Architecture review required for safe optional provenance modeling.

---

# Candidate C — Campaign Catalogue Publication

## NAME

**Publish an Intel Catalogue to a Player**

## USER VALUE

The GM selects a small set of already-existing campaign entities and publishes a safe read-only catalogue to one Player.

Example scenario:

The Player reads an Imperial dock manifest or local atlas.

The GM publishes selected:

- Contacts/Characters;
- Locations;

with only safe/public fields.

The Player then gets a small read-only discovered-world catalogue.

## WHY NOW

Slice 2 proved:

- Contact persistence;
- Contact search;
- Player-safe claim disclosure;
- explicit backend projections.

Manual feedback now asks for:

- campaign entity navigation;
- Player read-only discovered entities;
- GM-controlled bulk/catalogue publication.

A bounded publication slice can test that vision without building the full campaign database.

## WHAT WE LEARN

- whether entity-level disclosure is useful beyond claim-level disclosure;
- what "Player knows this entity" should mean;
- which base fields are safe/useful;
- whether bulk publication is manageable for the GM;
- whether Players benefit from a discovered-world database;
- whether entity projection can remain explicit and maintainable across types.

## REUSE FROM SLICE 1/2

High:

- Entity registry;
- Character/Contact;
- Location;
- GM campaign search concepts;
- Player projection boundary;
- authorization;
- disclosure/history patterns;
- frontend read-only Player surface.

## PRODUCT QUESTIONS

- What exactly is published:
  - selected entities;
  - selected safe field profiles;
  - a named catalogue/document?
- Does publication persist as a Player discovery grant?
- Which two entity types are enough for this slice?
- Is one Player recipient sufficient?
- Should publishing again update the Player view automatically?
- Does entity discovery imply anything about KnowledgeFragments attached to that entity? Default should be no.

## GAME DESIGN REQUIRED

Moderate.

Game Design must define minimal semantics for:

- what it means for a Character to know/discover a Character/Location entity;
- whether discovery has certainty;
- relationship between entity discovery and claim knowledge.

No relationship/reputation system should be required.

## UX REQUIRED

GM:

```text
find/select entities
-> preview safe Player fields
-> choose Player
-> Publish
```

Player:

```text
open discovered-world catalogue
-> browse published Contacts/Locations
-> read safe fields
```

UX must clearly distinguish:

- canonical GM entity;
- published Player projection;
- hidden fields not sent.

## ARCHITECTURE REQUIRED

Likely:

- explicit entity discovery/publication grants;
- explicit Player projections for only two types:
  - Contact/Character;
  - Location;
- publication command;
- bulk validation/transaction;
- read-only Player catalogue endpoint;
- optional small multi-entity GM selection query.

Architecture must not create:

- generic arbitrary field-selection engine;
- universal entity serializer;
- graph database;
- external search.

## SECURITY IMPACT

Very high.

The central test is preventing leakage of:

- GM notes;
- Contact prepared claims;
- gm_veracity;
- hidden relationships;
- unpublished entities;
- other-campaign data.

Bulk publication must be backend-authorized.

## NEW COMPLEXITY

Moderate to high:

- first entity-level Player disclosure model;
- two entity projections;
- publication grant semantics;
- bulk selection;
- read-only Player catalogue UX.

## RISKS

- expanding into full Campaign Database too early;
- generic projection abstraction;
- field-level leakage;
- unclear semantics between "knows entity" and "knows claims about entity";
- broad navigation redesign.

## EXPLICIT EXCLUSIONS

- Items/weapons in first slice unless one is already a stable typed entity;
- all entity types;
- global GM database redesign;
- full multi-entity search platform;
- editable Player entities;
- Player notes;
- relationship graph;
- secrets auto-published with entity;
- arbitrary field picker;
- catalogue templating;
- realtime delivery;
- quest/thread system.

## BLOCKERS

Product + Game Design:

- define entity-discovery semantics.

UX + Security:

- safe preview/publication workflow.

Architecture:

- bounded grant/projection model for exactly selected entity types.

---

# Candidate D — Cinematic Personal Combat Encounter

## NAME

**Escape the Imperial Patrol**

## USER VALUE

The GM and Player can run one short personal-scale combat encounter with a clear objective, hostile opposition and persistent consequences.

This would be the first slice where the product feels directly like a combat-capable RPG rather than a campaign/knowledge assistant.

## WHY NOW

Combat remains one of the largest completely unproven MVP areas.

The project now has:

- Character identity;
- D20;
- GM/Player auth;
- persistence;
- Contact/NPC identity foundations;
- live workflow experience;
- history/tests.

This is enough platform foundation to test combat without simultaneously inventing the whole application.

## WHAT WE LEARN

- whether abstract cinematic combat works without tactical maps;
- whether repeated actions remain usable live;
- whether a bounded encounter context is required;
- minimum health/damage model;
- minimum hostile representation;
- Player vs GM command boundary;
- whether combat should reuse or replace current resolution concepts.

## REUSE FROM SLICE 1/2

Strong infrastructure reuse:

- auth/authz;
- Character identity;
- D20 seam;
- Location;
- transactions;
- DomainEvents;
- Player projection;
- test harness.

Contact identity may support one named NPC antagonist, but combat state would be new.

## PRODUCT QUESTIONS

- Is combat GM-mediated or does Player submit actions?
- One PC + one hostile group or multiple units?
- Objective-based end condition versus defeat-all?
- What combat state must Player see?
- How much automation should occur after a hit?

## GAME DESIGN REQUIRED

Largest rules requirement among candidates.

Minimum contract:

- turn order;
- action economy;
- attack procedure;
- defence/DC;
- damage;
- short-term health;
- incapacitation;
- hostile group/minion semantics;
- encounter end condition;
- minimal range/position if required.

Must explicitly defer most broader combat design.

## UX REQUIRED

Compact repeated live interaction:

- current actor;
- objective;
- target;
- action;
- roll/result;
- damage/state change;
- advance turn;
- encounter end.

Must avoid using long freeform Intent/Risk forms for every routine attack.

## ARCHITECTURE REQUIRED

Likely:

- bounded Encounter/combat context;
- combatants;
- health/damage state;
- turn state;
- hostile representation;
- combat-visible Player projections;
- deterministic combat mutations.

Architecture must decide whether Encounter is a narrow combat aggregate rather than a generic Scene subsystem.

## SECURITY IMPACT

Moderate to high depending on Player-active commands.

If Player submits actions:

- actor assignment server-derived;
- target same-campaign/encounter validated;
- action legality server-authoritative.

## NEW COMPLEXITY

High:

- several new rules at once;
- repeated shared state;
- combat lifecycle;
- new UI;
- new persistence;
- likely first important expansion of Character mechanical state.

## RISKS

- scope explosion;
- premature health/initiative/range decisions;
- bookkeeping-heavy UX;
- generic encounter/rule engine temptation;
- longer slice for one developer.

## EXPLICIT EXCLUSIONS

- tactical grid/maps;
- exact movement;
- reactions;
- detailed armour;
- critical injury system;
- large equipment catalogue;
- Force powers;
- talents;
- progression;
- vehicle/space combat;
- NPC AI;
- encounter builder;
- generic Scene/Session.

## BLOCKERS

Game Design is the primary blocker.

UX must validate the repeated-action flow before implementation.

Architecture follows after the combat micro-contract is accepted.

---

# Candidate E — Generated Playable Situation

## NAME

**Generate, Review and Play One Situation**

## USER VALUE

The GM can generate one small playable situation, review/edit it, explicitly accept it into the campaign, then immediately use one generated element during play.

Example package:

- one Location;
- one Contact;
- one pressure/threat;
- one secret/claim;
- one hook/affordance.

## WHY NOW

Procedural generation remains a major intended differentiator and is still completely unproven.

Slice 2 now provides real campaign state that generated content could target:

- Location;
- Character/Contact;
- KnowledgeFragment;
- disclosure.

That makes generation more meaningful now than it would have been before Slice 2.

## WHAT WE LEARN

- whether generation actually saves GM preparation time;
- what minimum generated structure is useful;
- whether generated content feels playable rather than descriptive;
- how much review/editing is needed;
- whether accepted generated content can become ordinary campaign state;
- whether optional knowledge provenance is valuable for generated coherence.

## REUSE FROM SLICE 1/2

High on canonicalization:

- Location;
- Character/Contact;
- KnowledgeFragment;
- GM authorization;
- disclosure;
- existing authoring patterns;
- persistence.

## PRODUCT QUESTIONS

- Exact generated package?
- Whole-package acceptance or per-element acceptance?
- Candidate survives refresh/relogin or remains transient?
- What counts as "played"?
- Is a real external AI/model provider required, or can generation logic be deterministic/mock-backed for the slice?
- How much editability before acceptance?

## GAME DESIGN REQUIRED

Moderate.

Define a minimum playable situation:

- pressure/threat;
- opportunity;
- hook;
- secret/rumour;
- relationships between at least some generated elements.

Must define what makes generated output actually playable.

## UX REQUIRED

```text
Generate
-> review structured candidate
-> edit
-> Accept / Reject
-> canonical campaign state
-> retrieve/use in play
```

UX must make candidate vs canonical state unambiguous.

## ARCHITECTURE REQUIRED

Potentially:

- generator application boundary;
- external provider integration if selected;
- candidate/staging representation only if persistence is required;
- canonicalization into existing typed tables;
- validation;
- provider configuration/secrets.

No worker/broker should be added without a real long-running requirement.

## SECURITY IMPACT

Potentially high if external model/provider is used:

- campaign data leaving system;
- prompt/data minimization;
- API key handling;
- output validation;
- malicious/unexpected generated references.

## NEW COMPLEXITY

Medium to high:

- provider/generation logic;
- candidate lifecycle;
- review UI;
- structured output validation;
- potentially asynchronous latency/failure.

## RISKS

- impressive demo but poor GM value;
- review fatigue;
- provider overengineering;
- generic generation framework too early;
- accidental canonicalization;
- data leakage to provider;
- generated lore with no gameplay utility.

## EXPLICIT EXCLUSIONS

- planet/galaxy generation;
- campaign plot generation;
- AI GM;
- faction simulation;
- background world simulation;
- generic generator plugin framework;
- image generation;
- all entity types;
- automatic accepted writes without GM review;
- queue/worker unless concretely required.

## BLOCKERS

Product + Game Design:

- exact generated package;
- "playable" acceptance criterion.

UX:

- candidate review/accept workflow.

Architecture/Security:

- provider mode;
- candidate persistence;
- external-data boundary.

---

# 3. Candidates explicitly not shortlisted

## Collaborative Player Roll

**Not shortlisted as Slice 3.**

It is valuable, but currently depends on several unresolved contracts simultaneously:

- final GM adjudication semantics;
- group-action Game Design;
- Player-visible stakes;
- digital dice integrity;
- live delivery/push choice;
- multi-participant resolution persistence.

A smaller foundation slice such as Candidate A may make this substantially safer later.

This is **deferred, not rejected**.

## Realtime / WebSockets

Rejected as a standalone slice.

Realtime is a delivery mechanism, not user value by itself.

It should be selected only when a concrete live workflow proves manual refresh/polling insufficient.

## Full campaign database

Rejected as too broad.

Candidate C narrows it to a publication workflow for a very small set of existing entity types.

## Generic CRUD / lifecycle framework

Rejected as horizontal.

Entity lifecycle should expand only when a selected scenario requires archive/deactivate/restore semantics.

## Full NPC system

Rejected as too broad.

Future slices may add inventory, mechanics or other Character capabilities incrementally.

## Generic global search platform

Rejected as horizontal.

Search should continue expanding only with concrete entity workflows.

## Quest/thread subsystem

Rejected as premature.

Knowledge grouping by quest is desirable, but no accepted Quest model exists yet.

## Generic knowledge/provenance graph

Rejected as over-modeling.

Candidate B keeps provenance optional and bounded.

---

# 4. Cross-candidate review dimensions

Reviewers should assess each candidate on:

1. concrete user value;
2. novelty of Product learning;
3. cross-domain readiness;
4. reuse of Slice 1/2;
5. implementation size for one developer;
6. risk of horizontal infrastructure;
7. risk of premature domain decisions;
8. security/disclosure risk;
9. playtestability;
10. leverage for later slices.

No final weighting or ranking is set in this document.

---

# 5. Exact Game Design review questions

## Candidate A — GM-Adjudicated Resolution

1. Distinguish precisely mechanical result from final adjudicated outcome.
2. May the GM override mechanical success/failure?
3. What exactly can an override change?
4. When are canonical consequences committed?
5. What does reopen/correct mean after a finalized resolution?
6. Does correction require a reason/fictional explanation?
7. Can this contract be defined without deciding crits/degrees/opposed checks?
8. Would this materially improve the foundation for combat and Player-side rolling?

## Candidate B — Player Knowledge Library

1. Is AWARE sufficient for the slice?
2. Can contradictory claims coexist without Believed/Doubted?
3. Which acquisition metadata has actual gameplay meaning?
4. Should source confidence/provenance affect epistemic state now or later?
5. Is roll context merely descriptive?
6. How should unknown/no-source knowledge be represented conceptually?
7. Can quest/thread grouping remain excluded?

## Candidate C — Campaign Catalogue Publication

1. What does it mean mechanically/fictionally for a Character to "know" an entity?
2. Does entity discovery need certainty?
3. How does entity discovery differ from knowing claims about the entity?
4. Are Contact/Character + Location enough entity types for one slice?
5. Does publishing base entity identity imply any attached KnowledgeFragment? Proposed answer: no.
6. Can catalogue publication remain independent of relationships/reputation?

## Candidate D — Combat

1. Minimum turn order?
2. Minimum action economy?
3. Attack/defence contract?
4. Damage/health/incapacitation?
5. Minimum hostile/minion representation?
6. Need for range/position?
7. Objective-driven combat termination?
8. GM-mediated versus Player-active action semantics?
9. Which combat concepts can safely remain deferred?

## Candidate E — Generation

1. What minimum generated package is actually playable?
2. Must generated elements relate to each other?
3. Is Contact + Location + pressure + secret + hook sufficient?
4. Does generated provenance add gameplay value now?
5. What counts as "used in play"?
6. Which generator ambitions should remain explicitly deferred?

---

# 6. Exact UX review questions

## Candidate A

1. Can explicit GM adjudication fit live play without excessive confirmation friction?
2. How should raw roll, mechanical result and final outcome be distinguished visually?
3. What is the smallest correction/reopen flow?
4. What should Players see after override/correction?

## Candidate B

1. What is the minimum useful Player knowledge-library IA?
2. Which metadata can be shown without overwhelming the claim itself?
3. How should unknown source be represented?
4. How should conflicting claims be presented?
5. Is simple search sufficient for the first slice?
6. How do we prevent truth/source/confidence confusion?

## Candidate C

1. What is the smallest GM publication workflow?
2. Can a bounded catalogue live inside existing campaign UI without a full IA redesign?
3. What Player read-only presentation is sufficient?
4. How should GM preview exactly what fields will be disclosed?
5. How should already-published entities be indicated?
6. How do we keep bulk disclosure safe but fast?

## Candidate D

1. Can repeated combat actions remain compact?
2. What shared state must stay visible at all times?
3. What is the minimum encounter UI?
4. Can we avoid a tactical map?
5. What interaction burden arises if the GM mediates every action?
6. What changes if Players submit their own combat actions?

## Candidate E

1. How should candidate vs canonical content be visually separated?
2. What review volume is acceptable?
3. Whole-package or partial acceptance?
4. What is the smallest useful editing surface?
5. How should provider latency/failure appear?
6. How do we avoid generation review becoming more work than manual prep?

---

# 7. Exact Architecture review questions

## Candidate A

1. Can existing ActionResolution be evolved safely, or should a cleaner resolution model be introduced?
2. How should immutable roll data and mutable/final adjudication be separated?
3. What is the minimum correction/supersession model?
4. How are already-applied effects corrected without generic undo?
5. What DomainEvents/read models are needed?
6. Can this remain fully synchronous in the modular monolith?

## Candidate B

1. Where should optional acquisition/provenance metadata live?
2. Should it attach to CharacterKnowledge or a separate acquisition record?
3. How do we model optional source/location/resolution references without forcing them?
4. How do we make Player knowledge searchable in PostgreSQL?
5. How do projection rules independently authorize provenance fields?
6. How do we avoid building a knowledge graph?

## Candidate C

1. What is the minimum entity-discovery/publication grant model?
2. Can explicit projections for Contact/Character + Location stay simple?
3. How should bulk publication be transactional/idempotent?
4. How do we prevent arbitrary field-selection architecture?
5. Does a small multi-entity selection query require any search abstraction beyond PostgreSQL?
6. What tests prove no field leakage?

## Candidate D

1. What is the smallest combat/Encounter persistence model?
2. Can Encounter remain combat-specific rather than a generic Scene?
3. How should repeated deterministic effects be applied?
4. What Character mechanical state must be added?
5. How do we avoid a generic rules/effects framework?
6. What changes if Player-active commands are selected?

## Candidate E

1. Can generation be implemented with a narrow provider boundary?
2. Must unaccepted candidates persist?
3. If persisted, what is the smallest staging representation?
4. How should generated output validate into existing typed models?
5. Is synchronous HTTP sufficient?
6. What campaign data may be sent externally?
7. What secrets/configuration handling is required?
8. How do we avoid a generic generator/plugin architecture?

---

# 8. Selection gate

No candidate is selected by this PR.

After Game Design, UX and Architecture reviews:

1. Product consolidates the three expert positions.
2. Candidates that require disproportionate prerequisite work are removed or reduced.
3. Human arbitration is requested only for materially different remaining Product priorities.
4. The selected option is converted into an exact Slice 3 specification.
5. `docs/planning/current-slice.md` remains unchanged until that specification is accepted.
6. Implementation remains unauthorized until the accepted Slice 3 contract is in `main`.
