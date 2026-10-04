# Slice 4 Product Closeout and Slice 5 Candidate Shortlist

**Status:** HUMAN OPTION SELECTED — SLICE SPECIFICATION REQUIRED  
**Owner:** Product Lead  
**Source of truth:** current `main` after PR #18 and PR #19 merge

This document closes Product work on the implemented Slice 4 and proposes the first more-substantial candidate set for Slice 5.

It does **not** select Slice 5.

---

# 1. Slice 4 Product closeout

## Durable validated learnings

Human functional testing validated the complete accepted workflow:

```text
GM creates PLAYER-authority request
-> Player sees request without global Refresh
-> Player triggers Roll
-> backend generates authoritative d20
-> GM sees mechanical result without global Refresh
-> GM Finalizes / Overrides
-> Player sees final outcome without global Refresh
```

Slice 4 therefore proves that the existing resolution/adjudication foundation can support a meaningful two-principal live workflow while preserving:

- backend-authoritative randomness;
- exactly-one-roll semantics;
- immutable mechanical evidence;
- explicit GM final adjudication;
- Player-safe projections;
- server-derived Player assignment/authorization;
- bounded polling rather than realtime infrastructure.

## Positive Product learning

The project no longer needs to treat Player participation, polling freshness or GM/Player authority separation as unproven foundations.

These are now reusable constraints for larger playable capabilities.

## Testing-process learning

The implementation cycle also showed that exhaustive browser-harness hardening can become disproportionate to Product risk.

The accepted post-Slice-4 Product direction now governs future slices:

- targeted backend rule/invariant/security coverage;
- useful integration coverage;
- build/typecheck;
- migration tests when risk justifies them;
- normally one valuable happy-path E2E;
- mandatory Human functional test before implementation merge;
- Product supplies the concrete functional test plan at the final pre-human-test acceptance.

## Action-context learning

The repeated Slices 1-4 resolution workflow makes Q-009 materially important.

A fictional Subject can be ephemeral and need no persisted Entity.

Example:

```text
Actor: Globox
Mechanic: Athletics
Context: Coruscant rooftops
Subject: the opposite rooftop
Intent: jump across the gap
```

This closeout does not resolve Q-009.

It only confirms that Slice 5 selection must explicitly consider richer action context.

---

# 2. Slice 5 selection principles

From Slice 5 onward, prefer a genuinely playable end-to-end capability over another foundational micro-slice.

A candidate may introduce several coherent changes when they all support one user scenario.

Do not split a selected capability into one slice per:

- field;
- endpoint;
- read model;
- local UI interaction;
- small persistence refinement.

A Slice 5 candidate must cross:

```text
playable user scenario
-> Game Design/domain semantics
-> GM and/or Player UX
-> API
-> persistence
-> authorization/security
-> targeted automated tests
-> Human functional test
```

The candidates below are deliberately **not ranked**.

---

# CANDIDATE A — Escape the Senate Archive: Multi-Action Resolution

## NAME

**General Action Resolution / Multi-Skill Challenge**

## END-TO-END USER SCENARIO

One coherent infiltration/escape sequence proves several real action types without building a generic RPG engine.

Example sequence:

```text
1. Slice archive terminal
   Subject: archive security terminal
   Intent: obtain Senator Traitrus's restricted records

2. Force open a sealed maintenance door
   Mechanic/Skill: physical-force skill
   Subject: sealed maintenance door
   Intent: reach the service corridor

3. Jump to the opposite rooftop
   Mechanic/Skill: Athletics
   Subject: opposite rooftop
   Intent: escape the pursuing guards

4. Bluff or persuade one guard if the fiction reaches that branch
   Mechanic/Skill: one bounded social skill
   Subject: checkpoint guard
   Intent: pass without raising the alarm
```

The exact accepted sequence may use fewer actions if Game Design judges that three mechanics are sufficient.

For every action, the live contract should consider:

```text
Actor
Mechanic / Skill
Context
Subject
Intent
Risk
DC
Roll authority
Risk visibility
```

Subject must support human-readable ephemeral fiction.

An optional Entity enrichment may be considered later, but an Entity must not be required.

## USER VALUE

This is the first candidate that turns the resolution foundation into an actual general-purpose session tool rather than a Slicing demonstrator.

A GM could resolve several common Star Wars actions in one continuous playable sequence while Players retain direct roll participation.

## WHY NOW

Slices 1-4 already prove:

- D20 vs DC;
- immutable mechanical evidence;
- GM adjudication;
- correction/supersession;
- GM/Player roll authority;
- safe Player request/result projections;
- polling freshness;
- campaign/security boundaries.

The major unresolved question is now whether those proven concepts can support multiple real mechanics without encoding false generality.

## WHAT WE LEARN

- which parts of current ActionResolution are genuinely cross-mechanic;
- which parts are Slicing-specific accidental coupling;
- whether a shared action-resolution core is justified;
- how Subject differs from mechanical target/effect recipient/context;
- how Character skills/modifiers should be represented beyond `slicing_modifier`;
- whether success/failure consequences can remain mostly narrative while selected mechanics keep bounded automatic effects;
- whether one live UX can handle multiple skills without becoming form-heavy.

## WHAT IS ALREADY PROVEN

- backend d20 generation;
- D20 + modifier vs DC;
- roll authority;
- Risk visibility;
- immutable result;
- Finalize/Override/Correct;
- Player-safe live workflow;
- KnowledgeFragment disclosure as one bounded success effect.

## WHAT IS ACTUALLY NEW

- at least two non-Slicing mechanics;
- a real first-party Skill vocabulary/lookup;
- per-action Subject semantics;
- removal or isolation of hardcoded `mechanic = slicing`;
- decoupling the common resolution lifecycle from mandatory KnowledgeFragment success;
- one coherent multi-action sequence;
- possibly one bounded challenge-level progress/pressure concept if Game Design determines the scenario needs it.

This candidate must **not** begin by declaring a universal generic ActionResolution engine.

The preferred learning path is:

> implement several concrete first-party mechanics, then extract only the common concepts demonstrated by those mechanics.

## GAME DESIGN REQUIRED

Game Design must define:

- exact mechanics/skills used in the selected scenario;
- how modifier lookup works;
- whether the same D20 procedure applies to all selected skills;
- when a roll is warranted;
- minimum stakes contract;
- mechanical target vs fictional Subject vs effect recipient vs contextual entity;
- whether Subject has any mechanical semantics or is descriptive for this slice;
- what success/failure means for each action;
- whether any selected action has a deterministic committed effect;
- whether social checks need special authority limits;
- whether a challenge-level progress/failure model is needed or whether sequential independent checks are enough.

## UX REQUIRED

UX must define a fast multi-mechanic authoring/resolution surface.

It must answer:

- what the GM must explicitly enter;
- what can be derived from actor/mechanic/context;
- how Subject is captured without forcing Entity selection;
- whether Subject is one lightweight text field, mechanic-specific label, or another bounded interaction;
- how skill/mechanic selection works;
- how Player-safe context is previewed;
- how repeated actions avoid form fatigue;
- whether the sequence needs one "challenge" surface or ordinary resolutions are sufficient.

## ARCHITECTURE REQUIRED

Architecture must challenge current Slicing coupling:

- `mechanic = 'slicing'` DB constraint;
- `CustomD20CharacterProfile.slicing_modifier`;
- mandatory `success_recipient_character_id = actor`;
- mandatory `success_fragment_id`;
- Slicing-specific serialization/effect logic.

Architecture must determine the narrowest safe evolution after Game Design/UX contracts.

Possible direction to evaluate, not pre-decide:

- shared resolution evidence/adjudication fields;
- mechanic-specific rule lookup;
- optional/typed bounded consequence specialization;
- free-text Subject plus no Entity requirement.

Do not build:

- dynamically pluggable game-system runtime;
- generic arbitrary effect DSL;
- polymorphic universal target graph;
- generic workflow engine.

## SECURITY IMPACT

High.

Player projections must not leak:

- hidden Risk;
- hidden DC if still policy;
- hidden mechanic-specific consequence data;
- undisclosed Entity enrichment if later added.

Player mutation remains limited to authorized Roll trigger where accepted.

## TESTING STRATEGY

Required:

- targeted backend tests for each selected mechanic's modifier/rule resolution;
- authorization tests for GM/Player roll authority;
- Subject validation/security behavior;
- mechanical-evidence invariants;
- regression of Finalize/Override/Correct;
- integration tests proving mechanic-specific consequence behavior;
- frontend build/typecheck.

Migration test only if converting existing Slicing rows/model presents real data risk.

E2E:

- one useful happy-path sequence containing at least two different action types.

Human functional test:

- run the full selected infiltration/escape sequence and assess whether the workflow feels like one usable RPG tool rather than multiple demo forms.

## SCOPE

Substantial but bounded:

- 2-4 concrete first-party skills/mechanics;
- one Character capability representation sufficient for them;
- Subject support for ephemeral text;
- existing GM/Player roll workflow;
- existing adjudication/correction;
- only consequence behaviors required by the selected scenario.

## EXPLICIT EXCLUSIONS

- complete skill catalogue;
- attributes/character creation redesign;
- opposed rolls unless one chosen mechanic truly requires them;
- advantage/disadvantage unless required;
- crits/degrees;
- universal Rule Effect DSL;
- universal target/entity relation model;
- arbitrary effect scripting;
- generic Scene engine;
- combat subsystem;
- Force subsystem;
- vehicle chase subsystem;
- generalized social-influence system.

## RISKS

- disguising premature framework work as "general resolution";
- forcing all mechanics into identical consequence semantics;
- Subject becoming an over-modeled target system;
- Character sheet scope explosion;
- too many skills in one slice;
- accidentally weakening Slicing's proven knowledge effect.

## BLOCKERS

Game Design must define a concrete 2-4 mechanic contract before Architecture generalizes anything.

UX must establish the minimal repeated-action workflow.

---

# CANDIDATE B — Escape the Imperial Patrol

## NAME

**Personal-Scale Combat Encounter**

## END-TO-END USER SCENARIO

Run one objective-driven personal combat from start to finish.

Example:

```text
Imperial patrol corners Globox in a docking bay
-> encounter starts with objective: reach the exit
-> initiative/current actor established
-> Player chooses one bounded action
-> attack or manoeuvre resolves
-> vitality/state changes
-> stormtroopers act as one bounded hostile group
-> position/range changes if required
-> encounter ends when Globox escapes or is incapacitated
```

## USER VALUE

This introduces the first complete high-frequency RPG conflict loop and makes the product materially more playable as a game rather than primarily an information/resolution tool.

## WHY NOW

The foundational roll and live Player/GM authority model is stable enough that combat no longer needs to solve those problems simultaneously.

## WHAT WE LEARN

- viability of cinematic objective-driven combat;
- repeated-action interaction cost;
- minimum initiative/action economy;
- minimum health/damage model;
- abstract range/position value;
- grouped anonymous-enemy handling;
- whether Player-side action initiation should expand beyond Roll.

## WHAT IS ALREADY PROVEN

- Character identity;
- backend rolls;
- adjudication authority;
- Player authentication/projections;
- polling;
- transactional state mutation;
- DomainEvent history.

## WHAT IS ACTUALLY NEW

- encounter lifecycle;
- turn order;
- combat action legality;
- attack/defence;
- damage;
- short-term health;
- hostile group;
- encounter objective/end state;
- repeated actions.

## GAME DESIGN REQUIRED

Must freeze a combat micro-contract:

- deterministic or rolled initiative;
- action economy;
- attack procedure;
- defence/DC;
- damage;
- Vitality or another bounded short-term health model;
- incapacitation;
- hostile/minion group rules;
- range/position only if needed;
- cover if needed;
- encounter objective and end condition;
- GM adjudication boundary for combat results.

## UX REQUIRED

Must produce a fast repeated loop:

```text
objective/current actor/status
-> choose action/target
-> resolve
-> show state change
-> next turn
```

UX must prevent:

- repeated long Intent/Risk authoring for routine attacks;
- excessive confirmations;
- tactical-map creep unless proven necessary.

## ARCHITECTURE REQUIRED

Likely a combat-specific Encounter aggregate with:

- encounter id/campaign;
- combatants;
- turn/order;
- objective/status;
- encounter-scoped combat state.

Architecture must decide whether health is initially encounter-scoped or Character-persistent.

Do not force current Slicing ActionResolution to become the combat engine merely for reuse.

Reuse pure D20 and authorization concepts where appropriate.

## SECURITY IMPACT

High if Player initiates combat actions.

Server must enforce:

- current actor/turn;
- valid combatant;
- valid target;
- campaign isolation;
- hidden hostile stats;
- GM-only controls.

## TESTING STRATEGY

Required:

- backend rule tests for initiative/action legality/attack/damage/end conditions;
- authorization tests;
- integration tests for encounter state transitions;
- build/typecheck;
- migration test only if persistent Character state changes introduce meaningful migration risk.

E2E:

- one complete escape encounter happy path.

Human functional test:

- play the encounter and assess pace, bookkeeping and readability.

## SCOPE

One PC, one hostile group, one Location, one objective, one minimal action set.

## EXPLICIT EXCLUSIONS

- tactical grid;
- exact movement distances;
- reactions;
- full weapons catalogue;
- full armour system;
- critical injury subsystem;
- Force powers;
- talents/progression;
- vehicle/space combat;
- NPC AI;
- generic encounter builder;
- full persistent injury model unless indispensable.

## RISKS

- highest Game Design scope;
- health model becoming prematurely permanent;
- UI repetition;
- hidden tactical-map requirements;
- rules engine/effect DSL creep.

## BLOCKERS

Game Design combat contract is mandatory.

---

# CANDIDATE C — Generate a Playable Complication and Run It

## NAME

**Procedural Playable Situation — Generate -> Review -> Accept -> Play**

## END-TO-END USER SCENARIO

GM asks the system for one bounded playable situation for the current campaign.

Example output:

- one Location/context;
- one Contact/Character;
- one pressure/threat;
- one secret/claim;
- one actionable opportunity/hook;
- a small number of explicit relationships tying them together.

Flow:

```text
Generate
-> structured candidate
-> GM reviews/edits
-> Accept
-> canonical Location/Character/Knowledge state created
-> GM immediately uses one accepted element in play
-> Player performs/reviews one existing supported interaction against it
```

"Play" must be observable, not merely "saved to database".

## USER VALUE

This directly tests one of the product's intended differentiators: reducing GM prep while producing content that enters actual play rather than encyclopedic filler.

## WHY NOW

The project now has canonical primitives and working live workflows into which generated content can be accepted.

## WHAT WE LEARN

- whether generation materially reduces prep effort;
- minimum structure for generated content to be playable;
- candidate review burden;
- candidate vs canonical persistence needs;
- whether generated relationships/Subject context improve immediate usability;
- whether external AI generation is worth the operational/security cost.

## WHAT IS ALREADY PROVEN

- Location;
- Character/Contact;
- KnowledgeFragment;
- Contact authoring;
- campaign auth;
- live roll/adjudication;
- Player disclosure;
- typed canonical services.

## WHAT IS ACTUALLY NEW

- generator input/output contract;
- structured candidate lifecycle;
- review/edit/accept;
- canonicalization;
- possibly provider boundary;
- explicit "use in play" acceptance.

## GAME DESIGN REQUIRED

Define a minimum playable package:

- pressure;
- opportunity;
- actionable choice;
- claim/secret;
- actor or force that wants something;
- meaningful relationships between elements;
- what counts as immediately playable.

Game Design must avoid requiring a full procedural-world ontology.

## UX REQUIRED

```text
Generate
-> inspect compact structured package
-> edit only what matters
-> Accept / Reject
-> jump directly to use
```

UX must determine:

- whole-package vs partial acceptance;
- candidate durability across refresh;
- review workload;
- how to show generated relationships without a graph editor;
- failure/regenerate flow.

## ARCHITECTURE REQUIRED

Must decide:

- deterministic/local stub vs external model provider for first slice;
- whether candidates must persist before acceptance;
- if persistent, minimum staging representation;
- validation of untrusted generated output;
- canonicalization through existing typed services;
- outbound campaign-data boundary.

No generic provider plugin framework.

## SECURITY IMPACT

Potentially high with external generation:

- campaign data egress;
- secret/GM-only context leakage;
- API credentials;
- prompt injection/untrusted output;
- cross-campaign contamination.

## TESTING STRATEGY

Required:

- backend validation/canonicalization tests;
- authorization/campaign-isolation tests;
- provider adapter tests with deterministic fake if external provider exists;
- integration test Generate -> Accept -> canonical state;
- build/typecheck.

Migration test only if candidate persistence introduces nontrivial migration risk.

E2E:

- one Generate -> Review -> Accept -> Play happy path using deterministic test provider.

Human functional test:

- assess whether generated package is actually useful at the table and faster than manual prep.

## SCOPE

One bounded situation package and one actual subsequent use of accepted content.

## EXPLICIT EXCLUSIONS

- galaxy/planet generation;
- full campaign plot generation;
- AI GM;
- autonomous NPC simulation;
- faction simulation;
- image generation;
- generic provider marketplace;
- automatic acceptance;
- background worker unless proven necessary;
- complete NPC mechanical sheets;
- generated combat subsystem.

## RISKS

- technically successful generation with low gameplay value;
- review fatigue;
- premature schema based on generated vocabulary;
- external-provider complexity;
- hidden-data leakage.

## BLOCKERS

Game Design/Product must define the package and play criterion before Architecture chooses persistence/provider shape.

---

# CANDIDATE D — Investigate a Contradiction

## NAME

**Player Knowledge / Investigation Workflow**

## END-TO-END USER SCENARIO

Player acquires two claims about the same matter from different sources and uses a persistent investigation view to reason about them.

Example:

```text
Contact Nira Voss reveals:
"The senator met the smuggler at Dock 47."

Later, terminal slicing reveals:
"The senator's official itinerary places him at Senate Tower."

-> both claims appear in Player Knowledge
-> each may show safe acquisition context
-> Player can search/filter the investigation
-> contradictory claims coexist without the system declaring which is true
-> Player chooses the next lead/source to pursue
```

The slice should end with a meaningful next Player choice, not merely a prettier list.

## USER VALUE

Turns the accepted knowledge model into an actual investigation game surface supporting rumours, contradictions and source reasoning.

## WHY NOW

Knowledge has been central to Slices 1-3, but most Player value is still simple disclosure.

A substantial investigation workflow can finally test whether provenance is gameplay or bookkeeping.

## WHAT WE LEARN

- whether source/acquisition context changes Player decisions;
- which provenance fields are actually useful;
- whether contradictory claims can be presented clearly without belief mechanics;
- whether searchable knowledge creates a durable investigation loop;
- whether Player actions naturally emerge from the knowledge view.

## WHAT IS ALREADY PROVEN

- KnowledgeFragment;
- CharacterKnowledge AWARE;
- Contact reveal;
- Slicing disclosure;
- Player-safe projections;
- source entities and Locations;
- ActionResolution history.

## WHAT IS ACTUALLY NEW

- optional acquisition context;
- source/location/method representation;
- Player investigation/search UI;
- contradiction-aware presentation;
- possibly links back to known source entities where disclosure-safe.

## GAME DESIGN REQUIRED

Must define:

- whether AWARE remains sufficient;
- whether contradiction is simply coexistence of claims;
- whether provenance is descriptive only;
- whether source identity affects mechanics;
- whether confidence/belief remains deferred;
- what minimum next-choice gameplay the investigation view should enable.

## UX REQUIRED

Player UX must be claim-first and useful during play.

Must solve:

- search/filter;
- compact source/location/time presentation;
- unknown source;
- contradictory claims;
- avoiding truth implication;
- navigating to an actionable next lead.

GM UX must preserve fast path:

> Character knows X.

without mandatory provenance bookkeeping.

## ARCHITECTURE REQUIRED

Must choose the smallest optional acquisition model:

- fields on CharacterKnowledge;
- or narrow acquisition record/event reference.

Must independently authorize visibility of:

- claim;
- source;
- Location;
- related resolution.

No provenance graph.

## SECURITY IMPACT

Very high.

Revealed claim does not automatically authorize:

- source identity;
- source Location;
- related resolution;
- gm_veracity;
- hidden relationships.

## TESTING STRATEGY

Required:

- backend projection/security tests;
- optional provenance behavior;
- contradictory-claim coexistence;
- search integration tests;
- build/typecheck.

Migration test only if existing CharacterKnowledge transformation presents real risk.

E2E:

- one useful investigation path from two acquisitions to searchable contradictory claims.

Human functional test:

- determine whether provenance helps decide what to do next or merely adds clutter.

## SCOPE

Two sources, two potentially conflicting claims, optional safe acquisition metadata, one searchable investigation view.

## EXPLICIT EXCLUSIONS

- belief/confidence system unless Game Design proves indispensable;
- quest subsystem;
- knowledge graph;
- automated truth inference;
- AI summarization;
- automatic provenance chains;
- Player-to-Player sharing;
- misinformation mechanics beyond conflicting claims.

## RISKS

- building bookkeeping rather than gameplay;
- source leakage;
- over-modeling epistemology;
- contradiction UI implying truth or falsehood;
- low breadth after several knowledge-heavy slices.

## BLOCKERS

Game Design must establish the minimum gameplay meaning of provenance/contradiction.

---

# CANDIDATE E — Publish a Mission Dossier

## NAME

**Campaign Database / Controlled Publication Workflow**

## END-TO-END USER SCENARIO

GM prepares a small in-universe mission dossier from existing campaign entities and publishes it to one Player.

Example:

```text
GM searches/selects:
- Vic la Menace (Character/Contact)
- Imperial Cargo Terminal (Location)

-> GM previews exact Player-safe fields
-> publishes dossier
-> Player sees a persistent read-only "Known world" dossier
-> Player opens Vic and the terminal
-> Player sees only published base fields
-> claims/secrets remain separate knowledge disclosures
-> later GM uses one published entity as context for a live resolution
```

## USER VALUE

Creates the first true persistent Player-facing campaign database rather than isolated claim/result panels.

It can become a durable navigation surface for actual campaigns.

## WHY NOW

The application already has:

- Entity identity;
- Contact search;
- explicit Player projections;
- controlled claim disclosure;
- safe resolution projections.

The unanswered product question is entity-level discovery/publication.

## WHAT WE LEARN

- whether Players value persistent discovered-world navigation;
- what "knowing an entity" means;
- which fields are safe/useful;
- live-linked vs snapshot behavior;
- whether broader campaign search is required;
- separation between entity discovery and claim knowledge.

## WHAT IS ALREADY PROVEN

- Character/Contact;
- Location;
- GM search;
- campaign isolation;
- safe Player projections;
- disclosure preview principle;
- Player workspace.

## WHAT IS ACTUALLY NEW

- durable entity discovery/publication grant;
- exact safe projection for two entity types;
- GM multi-entity selection/preview/publish;
- Player known-world browse/search;
- publication lifecycle/update semantics.

## GAME DESIGN REQUIRED

Must define:

- what it means for a Character to know/discover an entity;
- whether discovery is binary;
- whether it has mechanical meaning;
- distinction from KnowledgeFragment claims;
- whether publishing an entity implies any claims (default proposal: no);
- whether updates should automatically change Player knowledge.

## UX REQUIRED

GM:

```text
find entities
-> select
-> exact safe preview
-> publish
```

Player:

```text
Known world
-> browse/search published Characters/Contacts + Locations
-> open safe profile
```

UX must keep this bounded and avoid redesigning the entire app navigation.

## ARCHITECTURE REQUIRED

Likely:

- explicit discovery/publication grant;
- explicit Character/Contact Player projection;
- explicit Location Player projection;
- idempotent publication transaction;
- bounded catalogue/search endpoint.

Architecture must decide live-link vs snapshot only after Product/Game Design semantics.

No arbitrary serializer/field picker.

## SECURITY IMPACT

Critical.

Must prevent leakage of:

- GM notes;
- prepared information;
- gm_veracity;
- hidden relationships;
- hidden fields;
- unpublished entities;
- cross-campaign entities.

## TESTING STRATEGY

Required:

- backend field-level projection/security tests;
- publication idempotency;
- campaign isolation;
- search/browse integration tests;
- build/typecheck.

Migration test only if grant persistence introduces real migration risk.

E2E:

- one GM publish -> Player browse happy path.

Human functional test:

- verify preview confidence, discoverability and whether Player navigation is genuinely useful.

## SCOPE

Exactly two entity types:

- Character/Contact;
- Location.

One Player recipient is enough.

## EXPLICIT EXCLUSIONS

- all entity types;
- generic CMS;
- arbitrary field publication;
- Player editing;
- Player notes;
- relationship graph;
- automatic claim publication;
- Items unless separately accepted;
- global search engine;
- external search service;
- realtime publication transport.

## RISKS

- campaign-CMS scope explosion;
- unsafe generic projection abstraction;
- ambiguous live/snapshot semantics;
- confusing entity discovery with knowledge claims;
- significant UX navigation expansion.

## BLOCKERS

Game Design/Product must define discovery semantics and live-vs-snapshot behavior.

---

# 3. Candidate comparison questions for parallel review

Game Design, UX and Architecture should review all five candidates in parallel.

A second review loop is needed only if one domain identifies a material dependency that changes another domain's contract.

---

# 4. Exact Game Design review questions

## Candidate A — Multi-Action Resolution

1. Which 2-4 concrete mechanics/skills should the scenario prove?
2. Does one D20 + modifier vs DC rule apply to all of them?
3. What Character capability/skill vocabulary is minimally required?
4. Exactly when should each action require a roll?
5. Is Intent + Risk still the minimum stakes contract?
6. Distinguish mechanical target, fictional Subject, effect recipient and contextual entity for each selected action.
7. Is Subject descriptive only or mechanically relevant anywhere in this slice?
8. What success/failure consequence contract is shared, if any?
9. Which selected mechanics need deterministic committed effects?
10. Can Slicing keep its KnowledgeFragment effect as a specialization while non-Slicing actions remain narrative?
11. Is a challenge-level progress/failure track actually needed?
12. Which apparent "general" concepts should explicitly remain mechanic-specific?

## Candidate B — Combat

1. Minimum initiative rule?
2. Minimum action economy?
3. Attack vs defence procedure?
4. Damage model?
5. Minimum short-term health model?
6. Incapacitation?
7. Hostile/minion group semantics?
8. Range/position needed?
9. Cover needed?
10. Exact encounter objective/end condition?
11. Which combat results are deterministic vs GM-adjudicated?
12. Which combat mechanics must remain deferred?

## Candidate C — Procedural Situation

1. Exact minimum playable package?
2. Which generated relationships are required?
3. What meaningful Player choice must the package create?
4. What makes the situation immediately usable rather than descriptive?
5. What qualifies as "Play" for slice acceptance?
6. Which generated categories can remain absent?
7. Does generated content require provenance/causal chains in this slice?

## Candidate D — Investigation

1. Is AWARE sufficient for both conflicting claims?
2. Can contradictory claims simply coexist?
3. Is provenance descriptive only?
4. Can knowledge have no source?
5. Which acquisition metadata has actual gameplay value?
6. Does source identity influence mechanics now or later?
7. Can belief/confidence remain fully deferred?
8. What Player decision should the investigation view enable?

## Candidate E — Publication

1. What does "knowing/discovering an entity" mean?
2. Is discovery binary?
3. Is it mechanically meaningful?
4. How is entity discovery distinct from claim knowledge?
5. Does publication imply any attached claim? Proposed answer: no.
6. Should later GM edits automatically alter the Player-visible entity?
7. Are Character/Contact and Location sufficient for first publication semantics?

---

# 5. Exact UX review questions

## Candidate A

1. What is the minimum reusable roll form across multiple mechanics?
2. How should mechanic/skill selection work?
3. How should ephemeral Subject be captured with minimal friction?
4. Which fields can be derived rather than entered?
5. How do repeated actions avoid form fatigue?
6. Should the selected multi-action scenario have one challenge workspace or ordinary resolution cards?
7. What exact Player-safe preview is needed for each action?
8. How should mechanic-specific consequences appear without fragmenting the UX?

## Candidate B

1. What combat information must stay continuously visible?
2. Maximum acceptable interactions for a routine action?
3. Can combat remain understandable without a grid?
4. How should hostile groups be shown?
5. How does Player choose action/target?
6. How are damage/state changes communicated?
7. How is objective progress kept more prominent than bookkeeping?

## Candidate C

1. Whole-package or partial acceptance?
2. Must generated candidate survive refresh?
3. Minimum editing surface?
4. Maximum acceptable review burden?
5. How should relationships be shown without graph-editor complexity?
6. How does GM move directly from Accept to Play?
7. What is the regeneration/error flow?

## Candidate D

1. Minimum investigation IA?
2. Claim-first vs source-first?
3. How to show unknown source?
4. How to show contradictions without indicating truth?
5. Which filters/search are actually useful live?
6. How should the UI expose an actionable next lead?
7. How does GM retain a zero-bookkeeping "Character knows X" path?

## Candidate E

1. Minimum GM find/select/preview/publish flow?
2. What exact fields need preview?
3. How is already-published state shown?
4. Minimum Player Known World navigation?
5. Is search needed immediately?
6. How are later GM edits represented?
7. How do we prevent this from becoming a full campaign CMS redesign?

---

# 6. Exact Architecture review questions

## Candidate A

1. Which fields/lifecycle concepts of current ActionResolution are demonstrably cross-mechanic after Slices 1-4?
2. Which are Slicing-specific and should be extracted/optional/specialized?
3. How should mechanic/skill identity and modifier lookup be represented without a plugin framework?
4. How should ephemeral Subject be persisted, if it must be persisted at all?
5. Can optional Entity enrichment remain absent from Slice 5?
6. How should Slicing's KnowledgeFragment success effect coexist with non-Slicing narrative outcomes?
7. Is a narrow typed consequence strategy needed, or can non-Slicing success/failure remain adjudication text?
8. Would a challenge aggregate be justified or is it unnecessary?
9. What migration safely preserves existing Slicing rows?
10. How do we avoid "generic ActionResolution" becoming a false universal abstraction?

## Candidate B

1. Smallest combat-specific Encounter model?
2. Which state belongs to Encounter vs Character?
3. Can health be encounter-scoped initially?
4. How are hostile groups represented?
5. Which pure D20/adjudication concepts can be reused without using ActionResolution as the combat engine?
6. What concurrency is needed for Player actions?
7. How do we avoid Scene/Rule Effect/general workflow abstractions?

## Candidate C

1. External provider vs deterministic/local generator for first slice?
2. Does the candidate need persistence before acceptance?
3. If yes, smallest staging model?
4. How are generated outputs schema-validated?
5. How are accepted elements canonicalized through existing services?
6. What campaign context may leave the system?
7. Is synchronous HTTP sufficient?
8. How do we avoid generic provider/plugin abstractions?

## Candidate D

1. Acquisition metadata on CharacterKnowledge vs separate record?
2. How are optional source, Location and related resolution represented?
3. How are each of those independently disclosure-authorized?
4. What PostgreSQL search is sufficient?
5. How are contradictory claims represented without adding truth inference?
6. How do we avoid a provenance graph?

## Candidate E

1. Minimum entity-discovery/publication grant model?
2. Live-linked vs snapshot persistence implications?
3. Exact explicit projections for Character/Contact and Location?
4. Idempotent publication transaction?
5. How does bounded Player search work?
6. How do we avoid arbitrary serializer/field-selection architecture?
7. Which tests prove non-leakage?

---

# 7. Human selection

**Date:** 2026-10-04  
**Human Project Owner selection:** **Candidate B — Escape the Imperial Patrol / Personal-Scale Combat Encounter**

## Selection meaning

Candidate B is selected as the basis for Slice 5 specification.

This is **not yet an ACCEPTED Slice 5 contract**.

The selected Product direction is one complete, bounded, objective-driven personal-scale combat encounter:

```text
Imperial patrol corners Globox
-> encounter begins with a concrete escape objective
-> current actor / turn is established
-> Player performs bounded combat actions
-> attack / manoeuvre resolution changes encounter state
-> one hostile group acts
-> encounter ends through escape or incapacitation
```

The selected direction should be substantial enough to prove combat as a real playable capability, but it does not authorize implementation of the full combat system.

## Why this candidate now

Slices 1-4 already prove:

- persistence/auth/campaign isolation;
- backend-authoritative d20;
- GM adjudication and correction;
- Player-triggered Roll;
- safe Player projections;
- bounded live freshness.

Slice 5 can therefore spend its complexity budget on the actual combat loop rather than re-solving those foundations.

## Contracts still requiring cross-domain review

### Game Design

Must define the combat micro-contract before implementation:

- initiative / turn-order rule;
- action economy;
- attack vs defence procedure;
- damage;
- minimum short-term health model;
- incapacitation;
- hostile/minion group semantics;
- whether range/position is required;
- whether cover is required;
- encounter objective and exact end condition;
- which outcomes are deterministic and which remain GM-adjudicated;
- which combat mechanics are explicitly deferred.

### UX

Must define the repeated live-session loop:

- information that remains continuously visible;
- action/target selection;
- number of interactions for a routine combat action;
- hostile-group presentation;
- feedback for damage/state changes;
- objective progress;
- whether gridless combat is sufficiently understandable;
- avoidance of long per-action Intent/Risk forms.

### Architecture

Must define the narrowest combat-specific persistence/API model:

- smallest Encounter aggregate;
- Encounter state vs Character-persistent state;
- whether health can remain encounter-scoped initially;
- hostile-group representation;
- reuse of pure D20 / authorization / polling concepts without making current Slicing ActionResolution the combat engine;
- concurrency for Player-active actions;
- explicit avoidance of generic Scene, Rule Effect DSL, workflow engine or tactical-map infrastructure.

## Explicitly not selected

This selection does not pre-accept:

- tactical grid;
- exact movement distances;
- full weapon/armour catalogue;
- critical injury subsystem;
- Force powers;
- talents/progression;
- vehicle/space combat;
- NPC AI;
- generic encounter builder;
- permanent universal health model;
- generic combat engine abstraction.

---

# 8. Selection gate

After the parallel Game Design, UX and Architecture reviews of Candidate B:

1. Product consolidates only the contracts needed for the bounded personal-scale combat encounter.
2. A second review loop occurs only if one domain raises a material dependency changing another domain contract.
3. Product writes the exact Slice 5 specification.
4. Human acceptance is required before Slice 5 becomes ACCEPTED.
5. `docs/planning/current-slice.md` remains on Slice 4 until that acceptance.
6. No implementation begins before the accepted Slice 5 contract is merged to `main`.

---

# 9. Consolidated Slice 5 combat contract

**Consolidation status:** READY FOR EXACT SPECIFICATION  
**Selection status remains:** HUMAN OPTION SELECTED — SLICE SPECIFICATION REQUIRED

This section consolidates only the contracts necessary to write the exact Slice 5 specification.

It does not mark Slice 5 ACCEPTED and does not authorize implementation.

## PRODUCT SCENARIO

One Player Character, Globox, is cornered by one abstract Imperial Patrol group in one bounded encounter.

Primary objective:

> **Escape the Imperial Patrol.**

The playable loop is:

```text
Encounter starts
-> Round 1 / Globox turn
-> Player chooses Attack or Escape
-> deterministic combat state updates
-> if encounter remains active: GM resolves Patrol Attack
-> next round / Globox turn
-> repeat
-> encounter ends by escape, patrol neutralization, or Globox incapacitation
```

This slice proves one objective-driven personal-scale combat encounter.

It does not define the permanent Custom D20 combat system or final balance.

The exact scenario tuning accepted as the basis for specification is:

```text
Globox
  Attack Modifier: +3
  Defence: 12
  Combat Vitality: 4
  Attack Damage: 2

Imperial Patrol
  Attack Modifier: +2
  Defence: 12
  Group Strength: 4
  Attack Damage: 2

Escape Progress
  starts at 0
  target = 3
```

These values are Slice 5 encounter tuning only.

## GAME DESIGN MICRO-CONTRACT

Slice 5 contains exactly:

- deterministic Player-first alternating turns;
- one action per acting side per turn;
- Player actions: Attack or Escape;
- hostile action: Attack Globox;
- backend-authoritative d20 attacks;
- static Defence threshold;
- fixed damage;
- encounter-scoped Combat Vitality / Group Strength;
- deterministic Escape Progress;
- automatic terminal-state detection.

No natural-1/natural-20 special rule.

No crit, fumble, opposed roll, defence roll, degree of success, advantage/disadvantage or rolled damage.

## PLAYER LOOP

Always-visible state:

- objective;
- round;
- current actor;
- Globox current/initial Combat Vitality;
- Patrol current/initial Group Strength;
- Escape Progress / target;
- latest safe action result;
- terminal status when ended.

On the Player turn, exactly two primary actions are available:

### Attack

One interaction:

```text
Attack
-> backend authoritative d20
-> d20 + 3 vs Patrol Defence 12
-> HIT or MISS
-> HIT applies 2 damage immediately
-> if Patrol Strength reaches 0, encounter ends
-> otherwise turn becomes Patrol
```

No target selector because the Patrol group is the only valid target.

No Intent, Risk, confirmation, GM Finalize or damage confirmation.

### Escape

One interaction:

```text
Escape
-> Escape Progress +1
-> if Progress reaches 3, encounter ends ESCAPED
-> otherwise turn becomes Patrol
```

No roll and no confirmation.

After a committed Player action, Player controls become read-only until the next Player turn.

## GM LOOP

The GM supervises rather than approves routine deterministic combat effects.

Flow:

```text
Start Encounter
-> observe Player action/result
-> when Patrol turn: Resolve Patrol Attack
-> observe result/state change
-> repeat
-> intervene only for fiction/edge cases outside the bounded controls
```

Product resolves the hostile-turn interaction as:

> **GM presses one compact `Resolve Patrol Attack` command.**

The hostile action is not automatic in Slice 5.

Rationale:

- preserves GM pacing;
- keeps actor attribution clear;
- avoids a System principal;
- keeps Player and hostile mutations independently observable;
- introduces no NPC decision tree or AI.

No GM Finalize/Override is required for routine Attack, Escape, damage or threshold transitions.

## ENCOUNTER OBJECTIVE

Primary objective:

> Escape the Imperial Patrol.

Victory:

```text
Escape Progress >= 3
OR
Patrol Group Strength <= 0
```

Defeat:

```text
Globox Combat Vitality <= 0
```

Neutralizing the Patrol is an alternative means of securing escape, not a mandatory kill-all objective.

Terminal thresholds end the encounter immediately. No extra End Encounter confirmation.

## TURN MODEL

Exact order:

```text
Round 1:
  Globox
  Imperial Patrol

Round N:
  Globox
  Imperial Patrol
```

Start:

- round = 1;
- current actor = PLAYER.

After a non-terminal Player action:

- current actor = PATROL;
- round unchanged.

After a non-terminal Patrol action:

- round += 1;
- current actor = PLAYER.

Terminal state:

- current actor becomes null;
- encounter ends immediately.

No initiative roll, initiative score, phases or End Turn action.

## ACTION ECONOMY

Exactly one action per side per turn.

Player:

- Attack;
- Escape.

Patrol:

- Attack Globox.

The action itself consumes the turn.

No reactions, opportunity attacks, bonus actions, free actions, movement action or multiple attacks.

## ATTACK / DEFENCE

Attack procedure:

```text
backend d20 + Attack Modifier >= static Defence
=> HIT
else
=> MISS
```

Player:

```text
d20 + 3 vs 12
```

Patrol:

```text
d20 + 2 vs 12
```

Defence is a Slice 5 static combat threshold, not a universal future Defence formula.

Attack modifiers are scenario-scoped precomputed combat values.

Slice 5 does not define Skills/Attributes/weapon-proficiency formulas.

## DAMAGE

Fixed deterministic damage:

```text
HIT -> 2
MISS -> 0
```

Damage commits in the same combat-action transaction.

No weapon catalogue and no damage roll.

## HEALTH / INCAPACITATION

Health is encounter-scoped only.

Globox:

```text
Combat Vitality: 4 -> minimum 0
```

Patrol:

```text
Group Strength: 4 -> minimum 0
```

When Globox reaches 0:

- status = INCAPACITATED;
- encounter ends;
- no death/wound/recovery semantics are implied.

When Patrol reaches 0:

- status = PATROL_NEUTRALIZED;
- encounter ends in Player victory.

Combat Vitality and Group Strength are not accepted as the permanent Character health model.

## HOSTILE GROUP

The entire Imperial Patrol is one abstract encounter-scoped hostile unit.

It has:

- display name;
- Attack Modifier;
- Defence;
- fixed Damage;
- Group Strength;
- one turn.

No individual stormtrooper Character rows.

No per-minion HP.

No degradation of attack capability at intermediate Group Strength.

No NPC AI.

When the Patrol turn is active, its only legal action is Attack Globox.

## RANGE / POSITION

No range or positional subsystem is required.

The encounter fiction establishes that:

- both sides can attack;
- Globox can attempt Escape;
- exact distance is irrelevant to available choices.

Escape Progress is sufficient spatial abstraction for the selected objective.

Do not introduce grid, coordinates, range bands, movement or cover.

## DETERMINISTIC VS GM-ADJUDICATED EFFECTS

### Deterministic

- d20 generation;
- attack total;
- HIT/MISS;
- fixed damage;
- Vitality/Strength reduction;
- Escape Progress +1;
- round/current actor transition;
- threshold detection;
- terminal encounter status.

These commit synchronously without Slice-3-style Finalize/Override.

### GM-adjudicated

- unusual fictional actions outside Attack/Escape;
- narrative description of results;
- interpretation of what incapacitation means after combat;
- consequences outside the bounded encounter state;
- edge cases not represented by accepted commands.

This remains consistent with D-004.

## ARCHITECTURE MODEL

Use one combat-specific persisted aggregate.

Suggested ownership:

```text
combat module
  -> CombatEncounter current state and legal transitions
  -> combat-specific commands
  -> combat-safe projections

custom_d20
  -> reuse pure d20 + modifier >= threshold rule shape

campaigns
  -> membership / PlayerCharacterAssignment

characters
  -> existing Player Character identity

history
  -> append-only combat action history
```

Do not route combat through Slicing-specific ActionResolution.

### CombatEncounter minimum persisted state

- id;
- campaign_id;
- location_id;
- player_character_id;
- objective;
- status = ACTIVE | ESCAPED | PATROL_NEUTRALIZED | INCAPACITATED;
- round;
- current_actor = PLAYER | PATROL | null when terminal;
- Player attack modifier / Defence / fixed Damage;
- initial/current Player Vitality;
- Patrol display name;
- Patrol attack modifier / Defence / fixed Damage;
- initial/current Patrol Strength;
- Escape Progress / target;
- created_by_principal_id;
- created_at;
- ended_at.

Scenario tuning is initialized server-side.

The client does not submit combat tuning.

No generic Combatant table, Scene, generic Encounter builder, action-command model, workflow engine, Rule Effect DSL or combat engine abstraction.

## AUTHORIZATION

### Start Encounter

GM-only.

Backend validates:

- GM campaign membership;
- same-campaign Player Character;
- same-campaign Location;
- Character is assigned to a PLAYER member;
- no conflicting ACTIVE encounter for that Character.

### Player Attack / Escape

Server derives:

```text
authenticated principal
-> PLAYER CampaignMembership
-> PlayerCharacterAssignment
-> encounter Character matches assignment
-> same campaign
-> ACTIVE
-> current actor = PLAYER
-> expected round matches
```

Player cannot supply authoritative:

- target;
- die;
- modifier;
- Defence;
- damage;
- Vitality;
- Group Strength;
- Escape Progress;
- turn transition;
- encounter status.

### Patrol Attack

GM-only.

Backend requires ACTIVE + PATROL turn + expected round.

## PLAYER PROJECTION

Do not serialize CombatEncounter directly.

Minimum Player-safe projection:

- encounter id;
- objective;
- status;
- round;
- current actor;
- Player Character id/name;
- current/initial Vitality;
- Patrol display name;
- current/initial Group Strength;
- Patrol status;
- Escape Progress/target;
- derived `can_attack`;
- derived `can_escape`;
- compact safe `last_action`.

For Attack feedback, `last_action` may expose:

- raw roll;
- applicable modifier;
- total;
- Defence threshold;
- HIT/MISS;
- damage;
- before/after bounded health state.

This exposure is accepted only for the selected combat feedback, not as a generic hostile-stat projection rule.

## LIVE UPDATE STRATEGY

Existing bounded polling remains sufficient.

Use:

- immediate re-fetch after own mutation;
- immediate re-fetch after stale/conflict response;
- polling while waiting for the other side;
- approximately 1 second during an active combat wait if the existing 2-second cadence feels sluggish;
- stop polling when terminal.

No WebSockets or SSE.

The exact interval is an implementation tuning value, not a new transport contract.

## CONCURRENCY / STALE COMMANDS

Use PostgreSQL row locking.

Player/GM combat commands carry `expected_round`.

Mutation requires:

- ACTIVE;
- expected current actor;
- expected round.

This prevents a delayed Round-1 Player command from becoming valid again when Round 2 returns to PLAYER.

At-most-once state mutation is required.

No generic idempotency-key platform.

## HISTORY

Current state remains relational on CombatEncounter.

DomainEvent remains append-only history only.

Sufficient bounded event types:

- `combat.player_attack_resolved`;
- `combat.escape_advanced`;
- `combat.patrol_attack_resolved`.

No CombatAction table is required for this slice.

No event sourcing.

## TESTING STRATEGY

Follow the accepted post-Slice-4 testing direction.

### Required backend rules/invariants

- d20 + modifier vs Defence;
- natural 1/20 ordinary;
- HIT fixed damage 2;
- MISS zero damage;
- health/strength clamp at 0;
- Escape +1 with no roll;
- deterministic starting turn;
- Player -> Patrol transition;
- Patrol -> next-round Player transition;
- each terminal threshold;
- no actions after terminal.

### Required security

- non-member denied;
- wrong Player denied;
- assigned Character only;
- Player only on Player turn;
- Patrol command GM-only;
- cross-campaign access rejected;
- no injection of authoritative combat values;
- Player projection does not leak non-approved fields.

### Required integration/concurrency

- duplicate/concurrent Attack applies at most once;
- duplicate/concurrent Escape applies at most once;
- duplicate Patrol attack applies at most once;
- stale expected_round rejected;
- full multi-turn service sequence;
- reload uses PostgreSQL current state;
- current-state mutation and history append are atomic.

### Frontend

- typecheck;
- production build.

### Migration

One additive CombatEncounter migration is expected.

Dedicated populated-data migration test is **not required by default** because existing tables need not be transformed.

Normal Alembic upgrade-to-head verification remains required.

### E2E

One complete useful combat loop.

Do not duplicate HIT/MISS/terminal/security matrices in Playwright.

### HUMAN TESTING

Mandatory before implementation merge.

The final Product acceptance before Human testing must provide a concrete functional test plan.

## EXPLICIT EXCLUSIONS

No:

- initiative roll/stat;
- tactical map/grid;
- coordinates;
- exact movement;
- range bands;
- cover;
- reactions;
- opportunity attacks;
- bonus/free actions;
- multiple attacks;
- multiple independent hostile groups;
- Player target selection;
- individual stormtrooper entities;
- per-minion HP;
- armour system;
- weapon catalogue;
- weapon-specific/rolled damage;
- crits/fumbles;
- degrees of success;
- permanent Character health;
- wounds/injuries/death/recovery;
- advanced conditions;
- Force;
- talents/progression;
- NPC AI;
- morale/surrender;
- generic combat correction/Undo;
- encounter builder;
- generic Scene;
- generic Combatant abstraction;
- generic combat/rules engine;
- generic action-command model;
- workflow/state-machine engine;
- Rule Effect DSL;
- combat through ActionResolution;
- universal Target/Subject model;
- WebSockets/SSE;
- broker/worker;
- microservices.

# 10. Review disagreements and Product dispositions

## Hostile turn: automatic vs GM-triggered

**FACT**

Game Design defines exactly one Patrol behavior and leaves execution pacing to Product/UX. UX recommends one GM `Resolve Patrol Attack` interaction. Architecture independently recommends the same approach.

**DOMAIN OWNER POSITION**

- Game Design: either execution shape is compatible with the combat rules.
- UX: GM-triggered is preferred for pacing and awareness.
- Architecture: GM-triggered is preferred for authorization/audit simplicity and to avoid a System principal or chained automatic mutation.

**PRODUCT IMPACT**

Slice 5 uses one GM `Resolve Patrol Attack` command.

No tactical decision is presented.

**HUMAN DECISION REQUIRED: NO**

## Health persistence

**FACT**

Game Design proposes Combat Vitality / Group Strength solely for this encounter. Architecture can keep both entirely on CombatEncounter. UX does not need a permanent Character-health representation.

**DOMAIN OWNER POSITION**

All three domains support encounter-scoped health for Slice 5.

**PRODUCT IMPACT**

No Character or CustomD20CharacterProfile permanent health field is introduced.

**HUMAN DECISION REQUIRED: NO**

## Range / position / cover

**FACT**

The accepted Attack-vs-Escape decision does not depend on spatial distance.

**DOMAIN OWNER POSITION**

Game Design: defer range and cover.
UX: no spatial UI is justified.
Architecture: no positional persistence is needed.

**PRODUCT IMPACT**

All spatial subsystems remain excluded.

**HUMAN DECISION REQUIRED: NO**

## Routine GM adjudication

**FACT**

The combat micro-contract gives deterministic meaning to Attack, Escape, damage and terminal thresholds.

**DOMAIN OWNER POSITION**

Game Design and UX explicitly recommend immediate deterministic commit rather than Slice-3 Finalize/Override for routine actions. Architecture supports synchronous state mutation.

**PRODUCT IMPACT**

Combat does not reuse the ActionResolution adjudication lifecycle for routine actions.

D-004 remains intact for unusual fiction and consequences beyond the accepted combat state.

**HUMAN DECISION REQUIRED: NO**

## Combat-state correction / Undo

**FACT**

UX identifies a bounded GM correction flow as possible but safe to defer. Architecture recommends no correction command by default.

**DOMAIN OWNER POSITION**

No domain requires combat correction to validate the selected encounter.

**PRODUCT IMPACT**

Correction/Undo is excluded from Slice 5.

A deterministic product defect found during testing must still be fixed; manual acceptance can restart the bounded test encounter if an operator misclick needs recovery.

**HUMAN DECISION REQUIRED: NO**

## Polling cadence

**FACT**

Slice 4 proved bounded polling. Combat has more frequent state transitions.

**DOMAIN OWNER POSITION**

UX suggests approximately 1 second if 2 seconds feels sluggish. Architecture agrees this is implementation tuning and does not require push transport.

**PRODUCT IMPACT**

Bounded polling remains the contract. Implement around 1 second for active combat waiting unless implementation/testing shows a better bounded value.

No WebSocket/SSE.

**HUMAN DECISION REQUIRED: NO**

## Numeric encounter tuning

**FACT**

Game Design supplied exact values to make the acceptance scenario deterministic enough to balance and test.

**DOMAIN OWNER POSITION**

Game Design explicitly states these values are Slice-5 tuning, not global Custom D20 balance. Architecture persists them as encounter-scoped snapshots. UX consumes them through combat state.

**PRODUCT IMPACT**

Product accepts the reviewed values for the Slice 5 scenario only.

They must not be documented as permanent Character progression/combat balance.

**HUMAN DECISION REQUIRED: NO**

# 11. Consolidation result

## BLOCKERS

None.

Game Design: READY FOR SPEC.  
UX: READY FOR SPEC.  
Architecture: READY FOR SPEC.

No material cross-domain disagreement requires a second review loop.

## HUMAN ARBITRATION

**NO MATERIAL HUMAN ARBITRATION REMAINS AT THIS STAGE.**

The next Product step after this PR merges is to write the exact Slice 5 specification from this consolidated contract.

Slice 5 remains unaccepted until the Human Project Owner explicitly accepts that specification.

