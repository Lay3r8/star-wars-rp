# Product Directions from Slice 2 Manual Testing

**Status:** PROPOSED — HUMAN-VALIDATED FUTURE DIRECTIONS — CROSS-DOMAIN CONTRACTS DEFERRED  
**Owner:** Product Lead  
**Source:** Human Project Owner manual testing during Slice 2 implementation  
**Current-slice impact:** NONE

## Purpose

Capture durable future Product directions observed while testing the Slice 2 implementation.

The Human Project Owner validated these directions as future Product intent on 2026-10-01; they remain non-normative until selected and accepted through a future cross-domain slice/decision.

This validation means the directions should be preserved for future slice selection. It does **not** pre-accept the Game Design, UX, Architecture or Security contracts needed to implement them.

These points are **not**:

- requirements for the accepted Slice 2;
- blockers for PR #12 by themselves;
- instructions to polish temporary/prototype UI;
- automatically accepted architecture or Game Design decisions.

They are inputs for future vertical-slice selection and cross-domain review.

---

# 1. Player knowledge should evolve into a searchable knowledge library

## Product direction

The Player-facing "Known information" area should eventually become more than a flat list of claims.

A future Player knowledge experience should be able to show useful acquisition context such as:

- where the information was learned;
- how it was learned;
- the fictional source/origin category, for example:
  - NPC;
  - another Player Character;
  - object/document;
  - puzzle;
  - terminal/system;
  - direct observation;
  - other;
- relevant roll information when a roll contributed to acquisition, for example:
  - raw die;
  - applicable modifiers;
  - displayed without necessarily exposing the system's success/failure adjudication;
- quest/thread association when a future accepted quest/thread model exists.

The Player should eventually be able to:

- search known information;
- browse/filter it efficiently;
- group or sort it by quest/thread when that domain exists.

## Character/NPC knowledge should be 0..N, not a single field

The Slice 2 field **"Information this Contact knows"** is a deliberately narrow proof surface.

It must not become the long-term Character/NPC knowledge model.

A Character, Contact or NPC should eventually be able to have:

```text
0..N CharacterKnowledge entries
```

This means:

- a newly created NPC may know nothing explicitly modeled;
- another NPC may know one prepared claim;
- an important recurring NPC may accumulate many claims over time;
- Player Characters and NPCs should ultimately use the same epistemic model where appropriate.

A Contact is therefore not defined by "having one information field".

The prepared information field in Slice 2 is only one authoring shortcut for one vertical slice.

### Acquisition metadata should be optional and attached to knowledge acquisition

A CharacterKnowledge relationship may eventually carry or reference optional acquisition metadata such as:

- where the Character learned the information;
- when it was learned;
- source/origin type;
- source entity when known;
- acquisition method;
- related resolution or roll;
- degree of confidence / epistemic state when Game Design defines it.

Conceptually:

```text
KnowledgeFragment
  claim / proposition
  GM veracity

CharacterKnowledge
  character
  fragment
  epistemic state
  optional acquisition/provenance metadata
```

The exact data model remains Architecture-owned.

### Provenance must be optional

Not every known fact needs an explainable parent/source chain.

A GM must be able to author:

> "This NPC knows X."

without explaining why.

That is especially important for manually authored campaign content, where forcing provenance would create bookkeeping with little gameplay value.

Therefore a future provenance model should support knowledge with no recorded source as a valid first-class case.

### Procedurally generated characters may benefit from richer provenance chains

For procedurally generated content, provenance can create meaningful internal coherence.

Example:

```text
Imperial manifest
-> dock clerk reads manifest
-> dock clerk tells smuggler
-> smuggler tells Player Character
```

Such a chain could later support:

- source credibility;
- contradictory rumours;
- traceable misinformation;
- procedural investigation hooks;
- questions such as "who could plausibly know this?".

This should remain optional structure, not a requirement that every generated fact form a complete causal graph.

### Product principle

The durable direction is:

> Knowledge can be richly sourced when that creates gameplay value, but unexplained GM-authored knowledge remains valid.

Do not force provenance merely because the architecture can represent it.

## GAME DESIGN IMPACT

Game Design must eventually define:

- whether provenance affects belief/confidence;
- whether confidence is an epistemic state, metadata, or both;
- how contradictory sources affect CharacterKnowledge;
- whether procedurally generated provenance has mechanical effects.

## UX IMPACT

Authoring must support both:

- fast path: "NPC knows this";
- richer path: add source/location/time/acquisition metadata when useful.

The fast path should remain the default unless the selected workflow benefits from provenance.

## ARCHITECTURE IMPACT

The accepted ADR already supports 0..N knowledge naturally through CharacterKnowledge.

Future work should avoid:

- a single `known_information` string on Character/Contact;
- mandatory provenance foreign keys;
- copying source metadata into KnowledgeFragment truth data.

If provenance becomes necessary, prefer optional acquisition/provenance structures associated with CharacterKnowledge or an acquisition event.

## SECURITY IMPACT

Provenance itself may contain hidden information.

Player projections must independently authorize:

- the claim;
- the source;
- the Location;
- acquisition metadata.

Disclosure of a claim does not automatically authorize disclosure of its full provenance.

---
## Important semantic distinction

Acquisition metadata is **not** the same thing as truth.

For example:

```text
Claim: "The governor is secretly financing the rebels."
Truth: GM-only veracity
Character state: AWARE / later epistemic state
Acquisition context:
  source = NPC
  source entity = Nira Voss
  learned at = Dock 47
  acquisition = conversation
  related resolution = ...
```

The source/location/roll context must not accidentally become proof that the claim is true.

## GAME DESIGN IMPACT

A future review must decide:

- whether source provenance affects belief/trust mechanics;
- which epistemic states beyond AWARE are actually useful;
- whether roll context has gameplay meaning after acquisition;
- how quest/thread grouping should interact with knowledge.

## UX IMPACT

Requires a Player-facing knowledge information architecture, including:

- search;
- filters/grouping;
- concise metadata presentation;
- distinction between claim, certainty/belief, source and acquisition context.

## ARCHITECTURE IMPACT

Likely requires a future acquisition/provenance concept linked to CharacterKnowledge rather than overloading KnowledgeFragment truth data.

Do not add quest foreign keys before an accepted quest/thread model exists.

## SECURITY IMPACT

Player-visible acquisition metadata must itself be disclosure-safe.

A source identity, Location, resolution or quest association may be hidden information.

## Status

**PROPOSED / FUTURE SLICE CANDIDATE**

Related existing deferred question:

- Q-001 Player-visible knowledge source provenance.

---

# 2. Campaign entity database for GM and discovered-world database for Players

## Product direction

The long-term application should expose the campaign as a navigable persistent world database.

The **Campaign** is the root context.

The GM should eventually be able to navigate major first-party entity categories such as:

- Locations;
- Characters / Contacts / NPCs;
- Objects / Items;
- later additional accepted entity categories.

A future GM information architecture may use tabs or another equivalent category-oriented navigation.

The exact visual navigation pattern remains UX-owned.

## Global campaign search

The GM should eventually have a general campaign search entry point able to find individual authorized entities without traversing the relationship tree manually.

This is broader than Slice 2 Contact search and deliberately reopens deferred Q-003 only when selected as a future slice.

## Player discovered-world database

Players should eventually have a related but strictly projected/read-only experience.

A Player should see only entities and fields that have actually been disclosed to that Player/Character.

The Player experience may eventually show:

- known Characters;
- known Locations;
- known Items;
- other discovered entity types;
- knowledge/certainty state where Game Design defines it.

This is **not** permission to serialize GM canonical entities and hide fields in React.

Player views remain explicit backend projections.

## GM catalogue / publication workflow

A future GM workflow should support selecting one or more campaign entities and publishing a bounded catalogue/projection to one or more Players.

Examples:

### Weapons catalogue

A Player reads a weapons catalogue.

The GM can disclose selected weapon entries with safe fields such as:

- name;
- description;
- price.

Associated secrets/internal GM fields remain hidden unless explicitly selected through a disclosure rule.

### Celebrity magazine

The GM may disclose selected Character public profiles without exposing:

- hidden allegiances;
- secrets;
- GM notes;
- undiscovered relationships.

### Atlas

The GM may disclose selected Locations with public/base fields while retaining hidden content.

## Product principle

This should be modeled as **controlled disclosure of entity projections**, not copying canonical GM records into a Player-owned database.

## PRODUCT IMPACT

Potentially a major long-term product differentiator:

> persistent world knowledge becomes a Player-accessible in-universe database.

## GAME DESIGN IMPACT

Game Design must eventually define:

- what it means for a Character to "know" an entity;
- whether entity knowledge has certainty levels;
- relationship between entity discovery and claim-based KnowledgeFragment semantics.

## UX IMPACT

Requires:

- GM entity navigation;
- global campaign search;
- Player read-only discovered-world navigation;
- multi-select publication/disclosure workflow;
- clear indication of what fields will be sent.

## ARCHITECTURE IMPACT

Likely requires entity-specific Player projections and explicit disclosure grants/knowledge relationships.

Do not create one generic "serialize any entity with arbitrary selected fields" mechanism without architecture/security review.

## SECURITY IMPACT

High.

Field-level projection must be server-authoritative.

Bulk disclosure must prevent accidental leakage of:

- GM notes;
- secrets;
- undiscovered relationships;
- internal truth metadata;
- other campaign data.

## Status

**PROPOSED / FUTURE PRODUCT CAPABILITY**

Related existing deferred question:

- Q-003 Multi-entity/global campaign search.

---

# 3. GM should eventually manage the lifecycle of campaign entities

## Product direction

For first-party mutable campaign entities, the GM should eventually be able to manage their lifecycle through normal application workflows.

At Product level this means:

- create;
- read;
- update;
- remove from active use.

"CRUD" should **not** automatically imply unrestricted hard delete.

Persistent campaigns have:

- references;
- history;
- revealed knowledge;
- prior resolutions;
- audit/event history.

Therefore the normal destructive workflow may eventually be:

```text
Edit
Archive / Deactivate
Restore
Hard-delete only when safe/explicitly allowed
```

The exact lifecycle remains domain-specific.

## UX IMPACT

Destructive actions should:

- distinguish Archive from permanent Delete;
- show reference/impact information where needed;
- prevent accidental destructive operations.

## ARCHITECTURE IMPACT

Deletion semantics must preserve referential integrity and accepted history contracts.

## Status

**PROPOSED PRODUCT PRINCIPLE**

Related existing deferred question:

- Q-006 Contact authoring history and lifecycle.

---

# 4. GM authority should eventually extend to explicit resolution adjudication / correction

## Human Product direction

The Human Project Owner wants the GM to retain explicit control over the **final adjudicated outcome** of a roll.

Desired future behavior:

- a resolution should not become irreversibly closed solely because the mechanical roll was computed;
- the GM should explicitly approve/finalize the outcome;
- the GM should be able to override/correct the outcome when necessary;
- a roll/resolution should support correction/reopening rather than forcing database repair.

## Important: this intentionally reopens part of the current resolution contract

Current accepted behavior proved in Slice 1 is narrower.

This future direction therefore requires a deliberate cross-domain decision before implementation.

## Product recommendation for future design

Do **not** destroy or rewrite the raw roll.

Prefer separating:

```text
Mechanical result
  raw d20
  modifiers
  total
  DC
  mechanically derived result

from

GM adjudication
  accepted outcome
  overridden outcome if any
  final consequences
  finalized by GM
```

A "rollback" should likely mean:

- reopen/correct;
- apply a compensating/corrective mutation where necessary;
- preserve prior audit/history.

It should not normally mean deleting the original roll as though it never happened.

## GAME DESIGN IMPACT

Requires explicit decisions on:

- whether GM may override mechanical success/failure;
- what "outcome" means relative to raw mechanical result;
- whether override requires a reason;
- interaction with crits/degrees when those exist;
- what Players may see.

## UX IMPACT

Potential flow:

```text
Roll
-> mechanical result
-> GM adjudication/preview
-> Approve / Override
-> commit consequences
-> Close
```

Also needs:

- Reopen/Correct flow;
- clear distinction between "rolled" and "finalized".

## ARCHITECTURE IMPACT

Likely requires explicit immutable roll data plus mutable/final adjudication state.

Corrections should remain auditable.

## SECURITY IMPACT

Only an authorized GM may override/finalize/reopen GM-adjudicated resolutions.

## Status

**PROPOSED — CROSS-DOMAIN DECISION REQUIRED**

This is not a Slice 2 change.

---

# 5. Future collaborative actions and Player-side rolling

## Product direction

Several Players should eventually be able to participate in one action/resolution.

A future collaborative-resolution workflow should support scenarios such as:

- two or more Characters jointly performing an action;
- several Players rolling;
- one Player leading while others assist;
- several independent rolls contributing to one shared outcome.

The exact rule is Game Design-owned.

## Future Player-side rolling

The Human Project Owner wants Players eventually to roll from their own interface.

Candidate experience:

```text
GM creates/request resolution
-> participating Players receive the request
-> Players can see the authorized stakes/conditions
-> Player roll UI becomes available
-> Players submit rolls
-> GM sees incoming results
-> GM adjudicates/finalizes
```

## Stakes visibility

Players should be able to see the stakes that are fictionally known/relevant to them.

This does not imply that every GM-side hidden consequence or secret risk must be disclosed.

The Player-safe stakes contract needs Game Design + UX review.

## GAME DESIGN IMPACT

Must define:

- group-check semantics;
- lead + assist versus everyone rolls;
- aggregation of multiple results;
- partial success/failure;
- how modifiers/skills are selected;
- whether players can decline participation;
- when results become final.

## UX IMPACT

Requires coordinated GM and Player resolution states.

The Player UI should clearly show:

- what action is requested;
- their Character;
- applicable mechanic;
- visible stakes;
- roll availability/status;
- submitted result.

GM needs:

- participant status;
- submitted results;
- final adjudication controls.

## ARCHITECTURE IMPACT

A live update mechanism will likely become useful.

**Do not pre-decide WebSockets.**

The Product requirement is:

> resolution requests and state changes should arrive promptly enough for live table play.

Possible architectures may include:

- HTTP commands + polling;
- HTTP commands + SSE;
- WebSockets;
- another bounded push mechanism.

Architecture should choose based on actual bidirectional requirements, operational cost and solo-developer constraints.

Player roll submission itself can remain an authenticated command even if server-to-client notification uses a separate mechanism.

## SECURITY IMPACT

High.

The server must derive:

- acting Player;
- assigned Character;
- allowed resolution;
- allowed mechanic;
- whether the Player is a participant.

Players must not be able to:

- submit for another Character;
- change GM-authored stakes;
- change hidden conditions;
- submit arbitrary roll results unless the accepted dice contract explicitly allows client-generated randomness.

## Important dice-integrity question

If Player-side rolling is digital, a future Architecture/Game Design review must decide whether:

- the backend generates/verifies randomness;
- the client requests the backend roll;
- cryptographic/verifiable dice matter;
- physical/manual dice entry is allowed.

Do not assume the browser should be trusted to generate authoritative results.

## Status

**PROPOSED — FUTURE VERTICAL SLICE CANDIDATE**

Related existing deferred question:

- Q-005 Realtime Player disclosure updates, but collaborative resolution is broader than disclosure freshness.

---

# 6. Manual test observation: both resolution terminal paths remain usable

During manual testing around Glabur le Vicieux, the Human Project Owner exercised both:

- a failed resolution;
- a successful resolution.

This is useful evidence that the existing prototype can traverse both terminal resolution paths.

It does **not** by itself change the accepted Slice 1/2 contracts.

No immediate implementation action is required from this observation.

---

# 7. Suggested future slice decomposition

The points above should **not** be implemented as one large roadmap item.

Plausible future vertical slices include:

## Player Knowledge Library

```text
discover information
-> retain acquisition metadata
-> search/filter Player knowledge
-> group by an accepted quest/thread
-> remain disclosure-safe
```

## Campaign Database & Publication

```text
GM finds/selects entities
-> chooses Players
-> previews safe fields
-> publishes catalogue
-> Players browse read-only discovered entities
```

## GM-Adjudicated Resolution

```text
roll
-> mechanical result
-> GM approve/override
-> commit
-> reopen/correct with audit trail
```

## Collaborative Player Roll

```text
GM creates group action
-> Players receive stakes
-> participants roll
-> GM receives results
-> final adjudication
```

These are candidates only.

They must compete with already deferred areas such as:

- personal-scale combat;
- procedural generation;
- richer knowledge/investigation;
- broader campaign search.

---

# 8. Non-actions now

These observations do **not** authorize:

- changing the current Slice 2 acceptance contract;
- blocking PR #12 solely because these future capabilities are absent;
- adding WebSockets immediately;
- building a generic global entity browser now;
- adding quest entities merely for knowledge grouping;
- adding full source provenance now;
- adding a generic resolution engine now;
- allowing client-trusted arbitrary dice rolls;
- implementing full CRUD/hard delete for every entity;
- redesigning the entire frontend now.

They are future Product inputs and should be considered during the next slice-selection cycle.
