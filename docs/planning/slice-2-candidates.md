# Slice 2 Candidate Shortlist

**Status:** PROPOSED  
**Owner:** Product Lead  
**Purpose:** Cross-domain review artifact for selecting the next vertical slice  
**Source of truth:** `main` as of 2026-10-01

## Important repository note

Slice 1 implementation and the UX interaction guidance are present in `main`.

The previously prepared Product closeout document from PR #8 is **not currently present in `main`**; PR #8 remains open/draft. Its observations are therefore treated here only as non-normative Product input, while `main` remains authoritative.

This document does **not** select Slice 2.

---

# 1. Baseline after Slice 1

## Accepted and proven

Slice 1 has proven an end-to-end path across:

- authenticated GM and Player principals;
- campaign membership and server-authoritative role checks;
- Player-to-Character assignment;
- campaign-scoped authorization;
- Character and Location persistence;
- `KnowledgeFragment` and `CharacterKnowledge`;
- explicit player projections;
- one bounded `ActionResolution`;
- fiction-first Intent + Risk;
- pre-bound success effect;
- D20 resolution using a precomputed modifier against DC;
- explicit GM Apply on success;
- explicit GM adjudication + Close on failure;
- atomic canonical mutation;
- append-only `DomainEvent` history;
- reload/persistence;
- idempotent success application;
- backend-enforced disclosure.

## Technical capability now available

The implementation now provides reusable foundations for later slices:

- React application shell;
- FastAPI modular monolith;
- PostgreSQL + Alembic;
- Docker Compose;
- local authentication sufficient for prototype slices;
- campaign membership/authorization services;
- Entity identity registry;
- typed Character and Location tables;
- Custom D20 character profile;
- Knowledge models;
- ActionResolution lifecycle;
- player-safe read projection;
- history events/read view;
- backend integration tests;
- Playwright E2E verification.

## Still materially unproven

The following major product/gameplay areas remain essentially unvalidated:

- personal-scale combat;
- initiative/action economy;
- health/damage/wounds;
- equipment/weapons;
- NPC/minion-group handling;
- abstract range/position;
- procedural generation;
- generated-content review/acceptance;
- rich world authoring;
- NPC/faction/item/objective authoring;
- global/live-session search;
- persistent Session;
- persistent Scene/current-context model;
- multi-actor live context;
- realtime/push disclosure;
- richer player actions;
- knowledge belief/provenance/sharing/misinformation;
- progression;
- Force/Dark Side;
- faction/world clocks;
- campaign pulse.

## UX constraints learned from Slice 1

Future surfaces should preserve the interaction guidance already recorded under `docs/ux/**`, especially:

- mutation feedback;
- double-submit protection;
- readable errors;
- visible validation constraints;
- correct campaign-scoped GM/Player mental model;
- context-appropriate selection controls;
- compact live-session interaction;
- explicit confirmation before irreversible disclosure;
- no leakage of persistence/implementation concepts into normal UX.

The temporary Slice 1 bootstrap workspace should not be extended by inertia.

---

# 2. Candidate shortlist

The following four candidates are deliberately **not ranked**.

Each is a bounded end-to-end scenario rather than a horizontal subsystem.

---

# Candidate A — Cinematic Personal Combat Encounter

## NAME

**Escape the Imperial Patrol**

## USER VALUE

The GM can run a short personal-scale Star Wars combat encounter in which a Player Character and one small hostile group contest a concrete objective, such as escaping a checkpoint or reaching a shuttle.

The player gains a recognizably RPG-like combat experience rather than only isolated skill resolution.

This directly addresses one of the largest still-unproven parts of the intended product.

## WHY NOW

Slice 1 already proved:

- actor selection;
- Intent/Risk;
- D20 resolution;
- consequence commit;
- persistence;
- GM authority;
- history;
- player projection.

Combat is therefore a natural stress test of whether those primitives can support **repeated consequential actions in a shared encounter** without becoming cumbersome.

The Human Project Owner also explicitly noted during Slice 1 arbitration that the absence of combat was disappointing, while accepting its deferral.

## PRODUCT QUESTIONS ANSWERED

- Does the product feel like a usable tabletop RPG assistant during actual conflict?
- Can repeated ActionResolution interactions remain fast enough in live play?
- Is abstract personal combat sufficient without tactical maps?
- Does combat need a first-class encounter/context concept?
- How much combat state should the system automate versus leave to GM adjudication?
- Can one-player / one-hostile-group combat produce enough value before broader party support?

## GAME DESIGN REQUIRED

This candidate requires Game Design to define the **minimum combat contract**, not the whole combat system.

At minimum:

- initiative or another turn-order approach;
- minimum action economy;
- attack/check procedure;
- defence or target difficulty;
- damage model;
- minimum health model;
- defeat/incapacitation semantics;
- one bounded condition if needed;
- abstract range/position vocabulary if range matters;
- minimum enemy/minion-group representation;
- whether the objective can end combat before all enemies are defeated.

Major open proposals such as Vitality + Wounds must not be adopted automatically merely because they were previously discussed.

## UX REQUIRED

UX must design a compact live encounter flow for:

- current actor/turn;
- current objective;
- target selection;
- range/context if relevant;
- attack/action resolution;
- damage/effect preview;
- GM confirmation where interpretive consequences exist;
- readable encounter state;
- end-of-encounter closure.

The UX must avoid converting combat into repeated long-form resolution forms.

## ARCHITECTURE REQUIRED

Likely additions include:

- one minimal NPC/enemy representation;
- possibly a grouped anonymous-enemy representation;
- combat-relevant Character/NPC state;
- health/resource persistence;
- damage/effect mutation;
- encounter ordering/context if required by Game Design;
- player projection additions for combat-visible state;
- history for meaningful combat changes;
- authorization for any player-side combat actions if introduced.

Architecture must determine whether combat needs a first-class Encounter/Scene concept or whether a bounded encounter context can remain an application construct.

## REUSE FROM SLICE 1

Strong reuse:

- authenticated principals;
- campaign authorization;
- Character;
- Location;
- ActionResolution;
- D20 calculation seam;
- pre-bound effects;
- Apply/Close semantics;
- DomainEvent/history;
- player projection;
- transaction/idempotency patterns;
- E2E harness.

## NEW COMPLEXITY

Substantial new complexity:

- repeated actions rather than one isolated check;
- shared encounter state;
- hostile actors;
- mechanical damage/health;
- ordering/turn semantics;
- possible range/position;
- combat termination conditions;
- potentially more frequent deterministic mutations.

## RISKS

### Product

Combat may absorb multiple slices if the first candidate is not aggressively bounded.

### Game Design

The combat system is currently one of the least mature rule areas.

Prematurely fixing initiative, health, armour, weapons, reactions, range and conditions simultaneously could lock in weak mechanics.

### UX

High risk of bookkeeping and live-session click burden.

### Architecture

Risk of introducing a generic encounter engine or over-generalized rules/effects framework too early.

### Security

If Players can directly submit combat actions, authorization boundaries become broader than Slice 1.

## EXPLICIT EXCLUSIONS

This candidate must not automatically include:

- tactical grid/maps;
- exact metre/square movement;
- vehicle combat;
- space combat;
- full weapon catalogue;
- full armour catalogue;
- progression;
- talents;
- Force powers;
- advanced conditions;
- NPC AI;
- automated GM decisions;
- generic Rule Effect DSL;
- large encounter builder;
- multi-session Scene framework unless demonstrably necessary.

## DEPENDENCIES / BLOCKERS

**Game Design blocker:** a small accepted combat contract.

**UX blocker:** a compact live encounter workflow.

**Architecture review required:** minimal encounter/combat persistence and effect boundaries.

---

# Candidate B — Procedurally Generated Playable Location

## NAME

**Generate, Review and Enter a Playable Location**

## USER VALUE

The GM can request a generated Star Wars location/situation, inspect and edit the result, accept it into the campaign, then use at least one generated element in actual play.

The value is not "generate prose"; it is reducing preparation effort while producing campaign state that immediately supports gameplay.

## WHY NOW

Procedural generation is repeatedly identified in Product and Game Design material as a major intended differentiator, but **none of it has been technically or experientially validated**.

Slice 1 already established:

- persistent Location;
- hidden KnowledgeFragment;
- ActionResolution;
- GM-authoritative commit boundaries.

Those foundations make it possible to test the critical Product hypothesis:

> generated content can become normal editable campaign state without becoming an autonomous source of truth.

## PRODUCT QUESTIONS ANSWERED

- Is procedural generation actually valuable to the GM during preparation?
- What minimum generated package is useful enough to save prep time?
- Does the GM prefer generate -> inspect/edit -> accept?
- Should generated content remain staged before acceptance?
- How much structure is required before generated content feels playable rather than encyclopedic?
- Can accepted generated content become indistinguishable from manually authored campaign state?
- Does generation need to produce interconnected hooks rather than isolated descriptions?

## GAME DESIGN REQUIRED

Game Design must define a **minimum generated situation contract**.

For example, one generated location may require a bounded subset of:

- one notable NPC;
- one threat/pressure;
- one opportunity;
- one secret/rumour;
- one concrete player-facing hook.

Game Design must review:

- which categories are mandatory;
- whether generated hooks need active/latent states;
- what relationships between generated elements are meaningful;
- what makes the generated result playable.

This slice should not define a universal world-generation grammar.

## UX REQUIRED

A new preparation workflow is required:

```text
Generate
-> inspect structured candidate
-> edit
-> accept / reject
-> accepted content appears as ordinary campaign content
-> use one accepted element in play
```

UX must answer:

- how the GM distinguishes candidate content from canonical content;
- what can be edited before acceptance;
- whether partial acceptance is allowed;
- how much generated detail is shown at once;
- how to prevent accidental canonicalization.

Mutation feedback and explicit commit principles from the Slice 1 UX guidance apply strongly here.

## ARCHITECTURE REQUIRED

Potential new architecture:

- generation application service;
- candidate representation;
- persistence semantics for unaccepted generated content, or explicit decision to keep candidates transient;
- accepted transformation into normal typed campaign data;
- additional typed domain models if NPC/hook/threat structures are accepted;
- generator version/input metadata only if required by reproducibility needs;
- authorization for GM-only generation;
- possibly external model/provider integration if AI-based generation is chosen.

If an external generation provider is used, this may create the first real asynchronous/long-running use case, but an outbox/worker must not be introduced unless actually required.

## REUSE FROM SLICE 1

Reuse includes:

- Campaign;
- Location;
- KnowledgeFragment;
- Character where an NPC can reuse or extend the identity model;
- Entity registry;
- GM authorization;
- hidden/player-visible separation;
- persistence patterns;
- history;
- manual authoring concepts.

## NEW COMPLEXITY

- generation engine/provider;
- structured generated content;
- candidate versus accepted lifecycle;
- edit/review UI;
- potentially new NPC/hook/threat domain concepts;
- deterministic/reproducibility questions;
- failure/latency/error handling around generation.

## RISKS

### Product

A generator can appear impressive while saving little actual prep time.

There is also risk of validating generation quality instead of validating the campaign product.

### Game Design

Generated output may be descriptive but mechanically unusable.

### UX

Large generated payloads can create review fatigue and hidden bookkeeping.

### Architecture

High temptation to build generic schemas, pack engines, generator pipelines, queues, or provider abstractions prematurely.

### Security

External AI/provider usage may introduce data exposure, secrets/configuration, abuse and content-boundary concerns depending on implementation.

## EXPLICIT EXCLUSIONS

Do not expand this candidate into:

- whole-planet generation;
- galaxy generation;
- full NPC generator;
- full faction simulation;
- campaign plot generation;
- autonomous story progression;
- AI GM;
- background simulation;
- generic generator plugin framework;
- marketplace/pack system;
- arbitrary JSON world model;
- bulk generation of every entity type;
- image generation unless separately justified.

## DEPENDENCIES / BLOCKERS

**Product blocker:** define the minimum useful generated package.

**Game Design blocker:** define what makes generated output playable.

**UX blocker:** candidate review/edit/accept workflow.

**Architecture review required:** candidate lifecycle and provider boundary.

---

# Candidate C — Prepare, Find and Use Campaign Content Live

## NAME

**Prep a Contact, Find Them Instantly, Use Them in Play**

## USER VALUE

The GM can prepare a small piece of campaign content before the session — for example a Location, an NPC/contact and one secret — and later retrieve that content quickly during live play, use it in an action, and reveal/update relevant information.

This tests whether the application can evolve from a Slice 1 demo setup into a genuinely useful GM workspace.

## WHY NOW

Manual Slice 1 testing showed that the bootstrap setup screens should **not** become the future authoring product.

At the same time, Product and UX work repeatedly identify:

- preparation;
- live-session speed;
- authoring;
- search/retrieval;

as core product value.

This candidate tests those assumptions while reusing almost every proven Slice 1 backend primitive.

It also gives global/live search a real user outcome instead of making search a horizontal infrastructure project.

## PRODUCT QUESTIONS ANSWERED

- Can the product materially reduce GM friction between preparation and live play?
- What is the minimum authoring structure a GM actually needs?
- Is global campaign search important once content volume grows beyond the Slice 1 toy dataset?
- Should preparation and live play be distinct workflows or merely distinct presentations?
- Which entity types are genuinely necessary next?
- Is an NPC/contact model more valuable than adding broader world objects first?
- Can one prepared secret/contact/location be retrieved and used in seconds during a live scene?

## GAME DESIGN REQUIRED

Limited Game Design is required compared with combat or investigation.

Potentially needed:

- minimal NPC/contact semantics;
- whether NPC disposition/tag data is required;
- whether one objective/thread needs representation;
- what information is mechanically relevant versus pure campaign content.

No full social system should be designed unless the scenario proves it necessary.

## UX REQUIRED

This candidate is UX-heavy.

UX must define:

- preparation workspace;
- create/edit flow for the minimum accepted content;
- reusable mutation feedback patterns;
- campaign navigation;
- fast search/command palette/combobox behavior;
- result grouping and disclosure-safe search;
- transition from prep to live use;
- compact entity summary;
- quick reveal/action from retrieved content;
- empty states and duplicate-submit protection.

The existing interaction guidance should become visible in a real replacement surface.

## ARCHITECTURE REQUIRED

Likely architecture additions:

- minimal NPC/contact typed model;
- edit/update APIs for selected entity types;
- possibly archive/deactivate if needed by the workflow;
- PostgreSQL-backed campaign search;
- explicit GM search projection;
- player-safe search only if the candidate requires player search;
- indexing appropriate for the small expected dataset;
- richer read models for entity summary/live retrieval.

A dedicated search engine is not justified for this candidate.

## REUSE FROM SLICE 1

Very high reuse:

- campaign/auth;
- Entity registry;
- Character;
- Location;
- KnowledgeFragment;
- ActionResolution;
- disclosure;
- player projection;
- history;
- React/FastAPI/PostgreSQL stack;
- tests.

## NEW COMPLEXITY

- real authoring/edit UX;
- at least one new content type, probably NPC/contact;
- update/edit lifecycle;
- cross-entity navigation;
- search/retrieval;
- larger campaign read models.

## RISKS

### Product

Could become "build the admin UI" rather than a vertical slice.

The scenario must stay anchored in prepare -> retrieve -> use during play.

### Game Design

Risk of prematurely defining social/relation mechanics just because an NPC exists.

### UX

High design cost. This is where temporary prototype patterns must be replaced rather than polished.

### Architecture

Search can trigger premature search-service abstraction; authoring can trigger generic CRUD frameworks.

### Security

Any future player search must preserve explicit disclosure projections. For the initial candidate, GM-only search may be enough.

## EXPLICIT EXCLUSIONS

Do not turn this candidate into:

- complete campaign CMS;
- every entity type;
- generic entity editor;
- global Principal directory;
- Elasticsearch/OpenSearch;
- graph database;
- full relationship system;
- faction management;
- procedural generation;
- Scene/Session persistence unless directly proven necessary;
- full journal/wiki;
- collaborative rich-text editor.

## DEPENDENCIES / BLOCKERS

**UX is the primary blocker**: the scenario requires an actual replacement workflow rather than extension of the Slice 1 cards.

**Product decision required:** exact minimum content types.

**Architecture review required:** bounded search and edit contracts.

Game Design review is needed only for any NPC/contact fields with mechanical meaning.

---

# Candidate D — Investigation, Rumour and Conflicting Knowledge

## NAME

**Follow a Rumour, Discover a Conflicting Claim**

## USER VALUE

Players can engage with information as gameplay rather than receiving a single binary secret reveal.

A character may learn a rumour, investigate it, discover a conflicting or corroborating claim, and see their personal knowledge state update without exposing GM truth.

This starts exercising one of the project's more distinctive persistent-campaign concepts.

## WHY NOW

Slice 1 already proved the hard security/architecture seam:

- hidden KnowledgeFragment;
- CharacterKnowledge;
- absence = Unknown;
- player projection;
- GM-side veracity hidden from Player;
- explicit disclosure.

The next logical knowledge slice could test whether this model creates **interesting gameplay**, rather than only secure disclosure plumbing.

This candidate also reuses ActionResolution without requiring combat or generation.

## PRODUCT QUESTIONS ANSWERED

- Is character-specific knowledge a meaningful product differentiator?
- Do players value a personal record of rumours/discoveries?
- Does the GM benefit from tracking conflicting claims separately from canonical truth?
- How much epistemic complexity is useful before bookkeeping becomes burdensome?
- Is information provenance important in actual play?
- Should Players be able to share information through the product, or is GM-mediated disclosure enough initially?
- Can knowledge gameplay support investigation without creating a full journal system?

## GAME DESIGN REQUIRED

This candidate requires substantial Game Design ownership.

Game Design must decide a **small epistemic contract**, potentially including some subset of:

- Aware;
- Believed;
- Doubted;
- source/provenance;
- contradiction handling;
- character-to-character sharing;
- GM adjudication of belief changes.

The candidate should not automatically accept all previously discussed states.

It also needs one investigation procedure:

- what fictional action produces a new claim;
- whether an ActionResolution is used;
- how failure changes the situation;
- whether a source can be unreliable without exposing truth.

## UX REQUIRED

UX must design:

- player knowledge view;
- clear distinction between "my character knows this" and "this is true";
- source/provenance display if selected;
- presentation of conflicting claims;
- GM reveal/adjudication controls;
- optional player sharing workflow if included;
- prevention of accidental GM-truth leakage.

This is a major mental-model challenge.

## ARCHITECTURE REQUIRED

Potential additions:

- expanded CharacterKnowledge state if accepted;
- provenance/source data if accepted;
- relationships between claims or contradiction metadata only if truly required;
- player projection updates;
- sharing mutation/authorization if included;
- history of knowledge acquisition/change;
- potentially support for revealing to multiple recipients.

Architecture must preserve:

- KnowledgeFragment as claim;
- gm_veracity as GM-only truth metadata;
- absence of CharacterKnowledge = Unknown.

## REUSE FROM SLICE 1

Excellent reuse:

- KnowledgeFragment;
- CharacterKnowledge;
- player projection;
- GM-only veracity;
- ActionResolution;
- pre-bound disclosure;
- Apply semantics;
- campaign authorization;
- history.

## NEW COMPLEXITY

- epistemic states beyond Aware;
- provenance;
- multiple claims about the same subject;
- possibly player-to-player sharing;
- richer player knowledge UX;
- potentially more nuanced GM adjudication.

## RISKS

### Product

Could become a sophisticated feature before basic campaign/combat/generation breadth exists.

### Game Design

Risk of over-modeling belief and creating bookkeeping rather than play.

### UX

Very high risk of confusing "truth", "claim", "aware", "believed", "source" and "player-visible" concepts.

### Architecture

Potential for overly generic graph/claim/provenance modeling.

### Security

Highest disclosure sensitivity among candidates. Projection mistakes can reveal GM truth or other characters' private information.

## EXPLICIT EXCLUSIONS

Do not automatically add:

- full journal/wiki;
- semantic knowledge graph;
- truth inference engine;
- automatic belief propagation;
- information hazards;
- AI summarization;
- faction-wide knowledge;
- universal provenance graph;
- collaborative note-taking;
- search across GM-hidden knowledge for Players.

## DEPENDENCIES / BLOCKERS

**Game Design is the primary blocker:** minimum epistemic semantics.

**UX blocker:** understandable player/GM mental model.

**Architecture review required:** provenance/state representation and projection security.

---

# 3. Candidate areas examined but not shortlisted as standalone slices

## Global / live-session search

**Not shortlisted alone.**

Search is valuable, but "implement search" is horizontal and does not prove a complete user outcome.

It is incorporated into Candidate C, where success is measured by whether the GM can prepare content and retrieve/use it rapidly in play.

## Stronger campaign preparation / authoring workflow

**Not shortlisted as a generic authoring project.**

A broad authoring redesign risks becoming a CMS build.

It is represented by Candidate C as one bounded prepare -> find -> use workflow.

## Live-session context / Scene or equivalent

**Not shortlisted alone.**

Creating a persistent `Scene` merely because it sounds useful would be domain-first design.

Candidate A may demonstrate that combat requires encounter context.

Candidate C may demonstrate that live navigation benefits from contextual state.

A persistent Scene should be introduced only when a selected user workflow proves the need.

## Player-facing realtime / disclosure improvements

**Not shortlisted alone.**

Replacing manual refresh with polling, SSE or WebSockets is primarily a delivery mechanism.

It should be introduced when a future slice demonstrates that delayed/manual disclosure materially harms the selected user experience.

Realtime infrastructure must not become the goal of a slice.

## Generic "improve the frontend"

**Rejected as a slice.**

The Slice 1 UX guidance is important, but implementing generic error normalization, mutation state infrastructure and new component libraries without a selected workflow would be horizontal work.

A later slice should consume those principles while delivering new user value.

## Session persistence

**Not shortlisted alone.**

A Session record should not be created before a concrete workflow needs session-level grouping, notes, participants or resume semantics.

## Full procedural world generation

**Rejected as too broad.**

Candidate B deliberately limits generation to one playable location/situation.

## Full combat system

**Rejected as too broad.**

Candidate A deliberately limits combat to one short personal-scale objective encounter.

---

# 4. Cross-candidate comparison dimensions for reviewers

Reviewers should not rank candidates by personal preference alone.

For each candidate, assess:

1. **User-value strength** — does it materially improve an actual campaign/session?
2. **Learning value** — does it answer an important unvalidated Product hypothesis?
3. **Vertical completeness** — does it cross UX, rules, API, persistence, permissions and tests where relevant?
4. **Reuse** — does it compound the Slice 1 investment?
5. **Novelty risk** — how many completely new systems must be designed at once?
6. **Solo-developer size** — can the candidate be bounded to a short implementation cycle?
7. **Future leverage** — does it establish primitives that several later slices can reuse?
8. **Scope containment** — can obvious domino features be explicitly excluded?
9. **Playtestability** — can success be evaluated with a real GM/player scenario rather than technical checks only?
10. **Decision maturity** — how many unresolved domain decisions must be made before implementation?

No weighting is fixed in this document.

---

# 5. Review requests

## Game Design review requested

Game Design should focus on:

### Candidate A — Combat
- minimum viable combat procedure;
- initiative/turn-order need;
- minimum health/damage semantics;
- range/position need;
- minion-group viability;
- objective-driven encounter closure;
- which combat questions can safely remain deferred.

### Candidate B — Generation
- minimum generated situation contract;
- mandatory versus optional hook categories;
- what makes generated content playable;
- whether latent/active generated hooks are necessary immediately.

### Candidate C — Prep/Search
- minimum mechanically meaningful NPC/contact data;
- whether any relation/disposition mechanic is actually required.

### Candidate D — Knowledge
- minimum epistemic vocabulary;
- provenance need;
- contradiction semantics;
- sharing semantics;
- minimum investigation procedure.

Game Design should also identify any candidate that secretly requires much more rules work than Product has estimated.

## UX review requested

UX should focus on:

### Candidate A
- live combat interaction cost;
- readable shared encounter state;
- whether repeated resolution remains compact.

### Candidate B
- generate/review/edit/accept workflow;
- canonical-versus-candidate mental model;
- review fatigue.

### Candidate C
- preparation/live workflow;
- replacement of temporary bootstrap UI;
- campaign navigation/search;
- fast retrieval and use during session.

### Candidate D
- player knowledge mental model;
- conflicting claims and source display;
- disclosure/sharing controls.

UX should also identify which candidate best exercises the durable interaction principles now in `docs/ux/interaction-principles.md`.

## Architecture review requested

Architecture should focus on incremental cost and whether each candidate can remain bounded.

### Candidate A
- encounter/combat persistence;
- NPC/minion representation;
- repeated deterministic effects;
- whether Scene/Encounter becomes necessary.

### Candidate B
- candidate generation lifecycle;
- external-provider boundary;
- persistence-before-acceptance;
- whether asynchronous infrastructure is actually necessary.

### Candidate C
- edit/update lifecycle;
- PostgreSQL search;
- read models;
- NPC/contact model;
- avoiding generic CRUD/search architecture.

### Candidate D
- knowledge-state extension;
- provenance;
- projection security;
- avoiding graph over-modeling.

Architecture should explicitly call out any candidate likely to trigger horizontal infrastructure disproportionate to user value.

---

# 6. Human/Product questions after specialist review

The Product Lead should only ask the Human Project Owner to arbitrate questions that remain materially different after specialist review.

Likely eventual arbitration dimensions include:

- whether the next learning priority is **core RPG breadth** (combat), **product differentiation** (generation or knowledge), or **GM workflow maturity** (prep/search);
- how much Game Design uncertainty is acceptable before implementation;
- whether near-term value should target live play or GM preparation;
- whether a higher-novelty slice is worth slower delivery for a solo developer.

No such choice is made in this PR.

---

# 7. Selection gate

A Slice 2 candidate should be accepted only after:

1. Game Design review identifies required mechanics and blockers;
2. UX review confirms a bounded usable workflow;
3. Architecture review confirms the slice can remain incremental;
4. Product consolidates the reviews;
5. the Human Project Owner arbitrates any remaining material trade-off;
6. the selected slice is written into `docs/planning/current-slice.md`;
7. implementation begins only after that acceptance.

Until then, all four candidates remain **PROPOSED**.
