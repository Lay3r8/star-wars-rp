# Slice 2 Specification — Prepare, Find and Use a Contact in Play

**Status:** PROPOSED — CROSS-DOMAIN REVIEW REQUIRED  
**Owner:** Product Lead  
**Selected direction:** Option C from `docs/planning/slice-2-candidates.md`  
**Implementation authorization:** NOT GRANTED

## Purpose

Transform the Human-selected Slice 2 direction into a small, concrete, end-to-end and testable slice contract.

This specification is intentionally narrow.

It must validate:

```text
prepare Contact
-> edit if needed
-> find quickly during live play
-> open compact summary
-> use the Contact in play through one explicit reveal
```

It must **not** become:

- a generic CMS;
- a full NPC system;
- a relationship/reputation engine;
- a global search platform;
- a complete frontend redesign;
- a Scene or Session subsystem.

The current Slice 1 bootstrap UI and Slice-1-specific `ActionResolution` persistence are implementation artifacts, not templates that this slice must extend.

---

# 1. Exact user scenario

## Scenario

Before a session, the GM prepares a recurring contact:

**Name:** Nira Voss  
**Role:** Imperial dock clerk and discreet informant  
**Location:** Dock 47  
**Information she knows:** "A customs audit is scheduled for Dock 47 tomorrow at 06:00."

The information is represented as campaign knowledge that is initially hidden from the Player Character.

During live play, the Player Character asks the GM who at Dock 47 might know about upcoming Imperial activity.

The GM:

1. opens the campaign-content search entry point;
2. types a few characters such as `Nira` or `dock clerk`;
3. finds Nira Voss;
4. opens a compact Contact summary without leaving the live workflow;
5. sees the Contact's role, associated Location, and GM-only prepared information;
6. chooses the exact prepared information to reveal to the assigned Player Character;
7. sees an explicit disclosure preview showing:
   - recipient Character;
   - exact player-visible claim;
8. confirms the reveal;
9. the Player Character's projection now includes the information.

No roll is required in this scenario because the slice does not introduce a social-resolution mechanic and the GM has already established that Nira is willing/able to provide the information in the fiction.

If, during actual play, the GM considers the outcome uncertain and risky, the accepted when-to-roll rule still applies, but that branch is **outside the required Slice 2 acceptance path**.

## Product rationale

This scenario validates the selected Product hypothesis:

> A GM can prepare useful campaign content, retrieve it in seconds during live play, and act on it without dropping out of the session flow.

It also exercises a durable replacement workflow instead of polishing the Slice 1 bootstrap cards.

---

# 2. Actors

## GM — required

The GM:

- creates the Contact;
- edits the Contact;
- associates the Contact with a campaign Location;
- associates one prepared KnowledgeFragment that the Contact can reveal;
- searches campaign Contacts during live play;
- opens the compact Contact summary;
- explicitly reveals the prepared information.

## Player — required for this scenario

A Player is included because the selected "use in play" action is an actual information disclosure.

The Player:

- is an authenticated campaign member;
- is assigned to one Player Character;
- cannot see the Contact's GM-only information before reveal;
- receives the exact claim after the GM commits the reveal.

The Player does **not** need:

- campaign-content search;
- Contact authoring;
- Contact browsing;
- a social-action UI;
- a Player-side Contact directory.

---

# 3. Minimum Contact data

## PRODUCT DECISION

Slice 2 requires only the information necessary for the scenario.

A Contact must expose the following Product-level fields/concepts:

1. **Name**
   - required;
   - human-readable display name.

2. **Role / short fictional function**
   - required;
   - short user-facing description such as "Imperial dock clerk and discreet informant".

3. **Associated Location**
   - required for this scenario;
   - references one existing campaign Location.

4. **GM note**
   - optional;
   - short private preparation note;
   - not Player-visible.

5. **Prepared information known by the Contact**
   - exactly one KnowledgeFragment is sufficient for Slice 2 acceptance;
   - the exact persistence representation is Architecture-owned;
   - this association does not mean the Contact owns canonical truth;
   - it means the GM has prepared this Contact as a fictional source for that claim.

## Explicitly not required

The Contact does not require:

- stats;
- class/species;
- combat profile;
- disposition score;
- trust/fear/reputation;
- relationship tags;
- faction membership;
- inventory;
- portrait;
- biography;
- objectives;
- schedules;
- voice/personality fields;
- procedural-generation metadata;
- social skill values.

## GAME DESIGN CONTRACT REQUIRED

Game Design must confirm that this scenario does **not** require a new social mechanic merely because a Contact exists.

The intended default is:

- if the GM establishes that the Contact gives the information, no roll is required;
- the existing when-to-roll rule remains authoritative for uncertain/risky fictional situations.

---

# 4. Preparation workflow

## PRODUCT DECISION

The GM must be able to complete the following preparation flow:

```text
Create Contact
-> enter minimum fields
-> Save
-> see clear success state
-> optionally Edit
-> Save changes
```

The Contact becomes normal durable campaign state immediately after successful Save.

There is no draft/candidate lifecycle in this slice.

## UX CONTRACT REQUIRED

UX must define a bounded durable authoring surface that:

- does not reuse the numbered Slice 1 bootstrap-card sequence as information architecture;
- uses domain language such as Contact, Role, Location and Information;
- follows UX-A01 mutation lifecycle guidance;
- prevents accidental duplicate submission while Save is pending;
- follows UX-A02 for actionable errors;
- exposes known constraints before submission per UX-A03;
- uses an authorized Location selector consistent with UX-A06;
- does not expose raw IDs or persistence concepts;
- makes Edit an ordinary modification of accepted campaign state.

UX should decide:

- whether create/edit are the same surface or separate modes;
- whether the Contact is edited in a page, panel, drawer or another bounded surface;
- the minimum visible success feedback after Save.

## ARCHITECTURE CONTRACT REQUIRED

Architecture must define:

- how Contact identity/persistence fits the accepted Entity + typed-table model;
- whether the current Character model can appropriately represent a non-player Contact or whether a dedicated typed Contact/NPC concept is required;
- authorized create/update commands;
- same-campaign validation for the Location reference and Knowledge association;
- history/event behavior for meaningful create/edit operations if required.

Product does **not** prescribe the table/schema.

## SECURITY IMPACT

Only an authorized GM may create or edit Contacts in Slice 2.

Client-supplied `campaign_id`, role, Contact ownership or Location membership cannot substitute for backend authorization.

GM-only note and prepared hidden information must not appear in Player projections.

---

# 5. Live retrieval workflow

## PRODUCT DECISION

The live workflow must be:

```text
Open campaign search
-> enter short query
-> see matching campaign Contacts
-> choose Contact
-> open compact summary
-> reveal prepared information
```

The search entry point is a GM-only **campaign-content search entry point** for this slice.

It is not Principal/account discovery.

## Interaction target

The UX goal is qualitative rather than a network SLA:

- the GM should not need to navigate through a deep hierarchy;
- after entering a useful query, the matching Contact should be reachable in roughly:
  - one result selection;
  - then one compact summary surface.

The normal target is:

```text
open search
-> type
-> select result
-> summary ready for action
```

No multi-step search wizard is acceptable.

## UX CONTRACT REQUIRED

UX must define:

- where the bounded search entry point lives in the campaign workflow;
- keyboard/mouse behavior;
- how results display type/context;
- how duplicate names are disambiguated;
- whether compact summary is inline, drawer, popover or another form;
- how the GM returns to the prior live context;
- how the Reveal action is exposed without clutter.

The compact summary must show, at minimum:

- Contact name;
- role;
- associated Location;
- GM-only note if present;
- prepared information available for reveal.

It must not expose database IDs, raw KnowledgeFragment terminology or internal storage state.

---

# 6. Search semantics

## PRODUCT DECISION

Slice 2 search is intentionally small.

### Search scope

- current campaign only;
- GM-only;
- Contacts only for the acceptance path.

Architecture may structure the query so later entity types can be added, but Product does not require a generic global search abstraction now.

### Search input

One free-text query string.

### Searchable fields

For Slice 2 acceptance:

- Contact name;
- Contact role / short fictional function.

Location name may be included **only if Architecture/UX conclude it is trivial and useful**, but it is not required for Product acceptance.

GM note and hidden KnowledgeFragment content are **not required** search fields and should not be indexed merely to expand search scope.

### Matching

Minimum Product requirement:

- case-insensitive matching;
- partial textual match sufficient for queries such as:
  - `Nira`;
  - `dock`;
  - `clerk`.

Product does not require fuzzy spelling correction, semantic search or ranking models.

### Ordering

Minimum deterministic ordering:

1. name matches before role-only matches;
2. within the same match class, alphabetical by Contact name.

Architecture may implement an equivalent deterministic behavior if PostgreSQL query semantics make another small rule simpler, provided UX can explain/predict the result ordering.

### Empty results

The UI must provide a meaningful empty state.

No automatic creation of a new Contact from a no-result state is required.

## ARCHITECTURE CONTRACT REQUIRED

Architecture decides:

- SQL/search implementation;
- indexes;
- whether `ILIKE`, `pg_trgm`, full-text or another PostgreSQL-native mechanism is appropriate;
- search DTO/read model;
- pagination/limit if needed.

No Elasticsearch/OpenSearch or external search service is permitted for this slice unless Architecture identifies a concrete blocker and raises it for cross-domain review.

## SECURITY IMPACT

The query must be campaign-scoped server-side.

The search API must not:

- search Principals;
- reveal Contacts from another campaign;
- expose hidden Player-inaccessible canonical data through a Player endpoint;
- rely on frontend filtering for campaign isolation.

---

# 7. Exact "use in play" action

## PRODUCT DECISION

The exact Slice 2 live action is:

> **Reveal one prepared piece of information from the Contact to the assigned Player Character.**

The Contact functions as the fictional source/context for the disclosure.

## Flow

```text
Contact summary
-> choose prepared information
-> preview recipient + exact claim
-> GM Reveal
-> CharacterKnowledge updated
-> Player projection contains the claim
```

## Reuse from Slice 1

The disclosure must preserve the accepted Slice 1 principle:

- hidden information requires an explicit commit boundary;
- GM sees recipient and exact claim before commit;
- backend authorization/projection remains authoritative;
- GM-side veracity remains hidden from Player.

## UX CONTRACT REQUIRED

UX must define the Reveal affordance and preview.

The preview must communicate in domain language:

- which Character receives the information;
- the exact information they will see;
- optionally that Nira Voss is the fictional source if source presentation is part of this slice.

UX must not display:

- `CharacterKnowledge`;
- `KnowledgeFragment`;
- `gm_veracity`;
- persistence statuses.

## GAME DESIGN CONTRACT REQUIRED

Game Design must confirm:

- the Contact-as-fictional-source use case does not require provenance mechanics in `CharacterKnowledge` for Slice 2 acceptance;
- no social check is mandatory in the proposed scenario;
- if source provenance would materially alter gameplay semantics, Game Design must explicitly request it rather than letting Architecture infer it.

## ARCHITECTURE CONTRACT REQUIRED

Architecture must determine the narrowest way to represent:

- the prepared association between Contact and KnowledgeFragment;
- the disclosure command;
- the resulting CharacterKnowledge mutation;
- meaningful history if retained.

Product prefers reuse of existing knowledge/disclosure concepts over creating a generic "Contact action" engine.

## SECURITY IMPACT

Before reveal:

- the Player must not receive the hidden claim;
- the Player must not receive the GM note;
- the Player must not receive GM veracity;
- the Player need not receive the Contact object at all unless the selected projection explicitly requires it.

After reveal:

- only the authorized recipient Character's projection gains the exact claim.

---

# 8. Edit and persistence boundaries

## PRODUCT DECISION

### Durable immediately after Save

The following are durable accepted campaign state:

- Contact identity;
- name;
- role;
- Location association;
- GM note;
- prepared Knowledge association.

### Editable by GM

The GM may edit, before or during a session:

- name;
- role;
- Location association;
- GM note;
- prepared Knowledge association.

The slice does not require a draft mode.

### Search consistency

After a successful edit:

- subsequent search/retrieval must reflect the new canonical values;
- reload must preserve the update.

Product does not require instantaneous push-refresh of an already-open summary on another client.

### Knowledge disclosure

Changing the Contact's prepared information association does **not** retract knowledge already revealed to a Player Character.

A Player cannot "unsee" a previous disclosure.

The slice does not require generic undo or knowledge retraction.

## UX CONTRACT REQUIRED

UX must ensure that:

- mutation state is observable;
- an edit success is understandable;
- stale saved values are not presented as if the Save failed;
- the user can distinguish editing the Contact from revealing information.

## ARCHITECTURE CONTRACT REQUIRED

Architecture owns:

- update concurrency behavior appropriate to this slice;
- transaction boundaries;
- history/event recording;
- query/read-model freshness after Save.

No event sourcing or draft-copy architecture is required.

---

# 9. Player effect

## PRODUCT DECISION

The Player-visible effect is intentionally minimal.

Before Reveal:

- Player sees no newly prepared Contact information.

After Reveal:

- the assigned Player Character's existing knowledge projection contains the exact claim.

The Player does not need a Contact detail screen in Slice 2.

The Player does not need to search for the Contact.

The Player does not need to see the GM note, Contact role metadata, Location association or source relationship unless UX/Game Design explicitly justify a player-visible source label during review.

## CROSS-DOMAIN DECISION

Whether the Player should see **"Source: Nira Voss"** together with the claim is **not decided by Product**.

- GAME DESIGN must say whether source provenance is mechanically/narratively required in this slice.
- UX must say whether it improves or confuses the Player mental model.
- ARCHITECTURE must assess whether it requires new knowledge provenance persistence or can remain contextual/presentational.
- SECURITY must ensure that source information itself is authorized to disclose.

Default if deferred:

- reveal only the claim, exactly as Slice 1;
- the Contact remains the GM-side fictional context.

---

# 10. Acceptance criteria

The final reviewed Slice 2 must satisfy all of the following.

## Preparation

1. An authenticated GM can create a Contact in an authorized campaign.
2. Contact creation requires only the accepted minimum fields.
3. The GM can associate the Contact with an existing same-campaign Location.
4. The GM can associate one same-campaign KnowledgeFragment as prepared information for the Contact.
5. Save has an observable pending/completed/failed lifecycle.
6. Accidental repeated Save while pending does not create duplicate unintended state.
7. A successful reload preserves the Contact and its associations.
8. The GM can edit the accepted Contact and save the changes.
9. Reload/search after edit shows the canonical updated values.

## Search / retrieval

10. The GM has a campaign-content search entry point suitable for live use.
11. The Slice 2 acceptance path searches Contacts in the current campaign only.
12. Search matches Contact name and role case-insensitively using partial textual input.
13. Search never returns Contacts from another campaign.
14. Name matches are ordered before role-only matches, with deterministic name ordering within the same class, or a reviewed equivalent deterministic ordering.
15. Duplicate Contact names are allowed and disambiguated through context rather than rejected as invalid.
16. Selecting a result opens a compact summary without forcing navigation through a deep administration hierarchy.
17. The compact summary shows name, role, Location and prepared GM information in user/domain language.

## Use in play

18. From the compact summary, the GM can initiate Reveal of the prepared information.
19. Before commit, the GM sees the exact recipient Character and exact player-visible claim.
20. The Player cannot commit the Reveal.
21. Before Reveal, the hidden claim is absent from the Player Character projection.
22. Reveal is backend-authorized and same-campaign validated.
23. Reveal commits the CharacterKnowledge mutation consistently with the existing accepted Knowledge model.
24. After Reveal, the authorized Player Character projection contains the exact claim.
25. GM note and `gm_veracity` remain absent from the Player projection.
26. Reload preserves both Contact state and the already-revealed CharacterKnowledge state.

## Security

27. Client-supplied campaign IDs, roles or Contact references do not bypass backend authorization.
28. Cross-campaign Location, Contact, KnowledgeFragment or recipient references are rejected.
29. The GM search path is not usable as a global Principal/account directory.
30. No Player endpoint serializes canonical GM Contact data and relies on frontend hiding.

## Scope / architecture

31. Search works using the existing application/PostgreSQL topology.
32. The implementation does not introduce Elasticsearch/OpenSearch, a broker, worker, WebSockets, microservices or distributed infrastructure merely for this slice.
33. No generic CMS/entity-editor framework is required.
34. No generic social/relationship engine is required.
35. No Scene/Session subsystem is required.
36. The existing Slice-1-specific ActionResolution persistence is not generalized merely to support this Contact workflow.

## End-to-end acceptance scenario

A Product acceptance test can demonstrate:

```text
GM prepares Nira Voss
-> saves
-> edits role/note if desired
-> reloads
-> enters live workflow
-> searches "Nira" or "dock"
-> opens Nira compact summary
-> previews disclosure
-> reveals prepared claim
-> Player projection receives claim
-> reload preserves state
```

---

# 11. Explicit exclusions

Slice 2 must not pull in the following unless a reviewer demonstrates that one is unavoidable for the accepted scenario.

## Product / UX exclusions

- complete campaign CMS;
- generic entity editor;
- complete global information architecture redesign;
- generic dashboard redesign;
- full NPC/contact profile;
- Player Contact directory;
- Player global campaign search;
- Principal/account search;
- invitation/onboarding redesign;
- realtime update system;
- generic notification system;
- i18n implementation;
- generic duplicate-content detection;
- generic undo.

## Game Design exclusions

- relationship/disposition system;
- faction reputation;
- social combat;
- contact favour/debt currencies;
- social skill subsystem;
- NPC combat stats;
- progression;
- Force mechanics;
- combat;
- encounter rules.

## Architecture exclusions

- Scene;
- Session;
- Elasticsearch/OpenSearch;
- search abstraction for hypothetical backends;
- graph database;
- event-driven indexing;
- generic CRUD/meta-form framework;
- generic ActionResolution engine;
- Rule Effect DSL;
- outbox worker;
- broker/queue;
- cache platform;
- WebSockets/SSE solely for this slice;
- microservices;
- plugin runtime.

## Content exclusions

- procedural generation;
- automatic Contact generation;
- faction authoring;
- full relationship graph;
- objectives/threads subsystem;
- items/vehicles authoring;
- portraits/image generation;
- rich text/wiki/journal system.

---

# 12. Cross-domain review matrix

## 12.1 Contact concept and minimum fields

**PRODUCT DECISION**

Required Product concepts:

- name;
- short role;
- Location;
- optional GM note;
- one prepared KnowledgeFragment.

**UX CONTRACT REQUIRED**

Confirm field presentation/order and create/edit interaction.

**GAME DESIGN CONTRACT REQUIRED**

Confirm no additional mechanical/social fields are required.

**ARCHITECTURE CONTRACT REQUIRED**

Choose typed persistence/domain placement and reference model.

**SECURITY IMPACT**

GM-only fields and campaign references must be server-authorized.

---

## 12.2 Search workflow

**PRODUCT DECISION**

GM-only, current campaign, Contact name + role, partial case-insensitive matching.

**UX CONTRACT REQUIRED**

Entry point, keyboard interaction, result presentation, compact summary, duplicate-name disambiguation.

**GAME DESIGN CONTRACT REQUIRED**

None expected.

**ARCHITECTURE CONTRACT REQUIRED**

PostgreSQL query/index/read-model shape.

**SECURITY IMPACT**

Campaign-scoped query; no Principal discovery; no reuse of GM DTO for Player search.

---

## 12.3 Contact use in play

**PRODUCT DECISION**

Exact action = reveal one prepared piece of information to the assigned Player Character.

**UX CONTRACT REQUIRED**

Reveal affordance and disclosure preview.

**GAME DESIGN CONTRACT REQUIRED**

Confirm no mandatory roll/social subsystem and decide whether source provenance matters.

**ARCHITECTURE CONTRACT REQUIRED**

Contact-to-Knowledge association and disclosure transaction.

**SECURITY IMPACT**

Hidden claim and GM metadata remain server-protected until authorized reveal.

---

## 12.4 Edit behavior

**PRODUCT DECISION**

Accepted Contact state is directly editable; no draft mode.

**UX CONTRACT REQUIRED**

Save feedback, validation and distinction between Edit and Reveal.

**GAME DESIGN CONTRACT REQUIRED**

None expected.

**ARCHITECTURE CONTRACT REQUIRED**

Update command, transaction/history/read consistency.

**SECURITY IMPACT**

Only authorized GM may edit.

---

## 12.5 Player source label

**PRODUCT DECISION**

Not required by default.

**UX CONTRACT REQUIRED**

Assess whether a source label is understandable/useful.

**GAME DESIGN CONTRACT REQUIRED**

Decide whether source provenance is part of the Slice 2 gameplay semantics.

**ARCHITECTURE CONTRACT REQUIRED**

Only if source persistence/projection is required.

**SECURITY IMPACT**

Source identity itself may be hidden information and requires explicit projection rules.

---

# 13. Exact questions for specialist review

## UX review questions

1. What is the smallest durable create/edit Contact workflow that replaces, rather than extends, the Slice 1 bootstrap cards?
2. Where should the bounded campaign search entry point live without freezing the entire future navigation architecture?
3. What interaction pattern should provide:
   - query input;
   - keyboard-friendly result selection;
   - compact summary;
   - return to live context?
4. How should duplicate Contact names be disambiguated using role/Location/context?
5. Is the proposed interaction target `open search -> type -> select -> summary` sufficiently precise and usable?
6. What should success/error/pending feedback look like for create/edit in this workflow?
7. How should the prepared hidden information appear in the GM compact summary without exposing persistence terminology?
8. What is the minimum disclosure preview before Reveal?
9. Should the Player-visible claim include a source label such as "Source: Nira Voss", or should source remain purely fictional/GM-side in Slice 2?
10. Does any part of this scenario force a broader information-architecture decision that cannot safely be deferred?

## Game Design review questions

1. Can a Contact in this slice remain a purely fictional campaign entity with no disposition/reputation/social-stat mechanics?
2. Is it valid for the proposed scenario to require no roll because the GM establishes that the Contact provides the information?
3. Does the existing when-to-roll rule remain sufficient for any optional uncertain variant?
4. Does associating one KnowledgeFragment with a Contact as "prepared information the Contact can reveal" introduce any semantic contradiction with the accepted Knowledge model?
5. Is source provenance mechanically/narratively required for Slice 2, or can it remain deferred?
6. If source provenance is required, what is the absolute minimum semantic contract?
7. Are any additional Contact fields mechanically necessary for this exact scenario?
8. Does the exact "Reveal prepared information" action provide sufficient actual-play value to count as use in play?

## Architecture review questions

1. Should Contact be represented by extending/reusing the existing Character identity/typed model, or by introducing a narrow Contact/NPC typed concept?
2. What is the narrowest persistent representation for:
   - role;
   - Location association;
   - optional GM note;
   - Contact-to-KnowledgeFragment prepared-information association?
3. What create/update API and transaction boundaries are appropriate?
4. What PostgreSQL-native search approach best satisfies:
   - campaign-only;
   - name + role;
   - case-insensitive partial match;
   - deterministic ordering?
5. Is a dedicated GM Contact search read model/API preferable to a generic campaign-search abstraction for this slice?
6. What index is actually justified at expected scale?
7. How should cross-campaign Location/Knowledge associations be rejected?
8. Can existing Knowledge disclosure application logic be reused directly without dragging in the Slice-1-specific ActionResolution persistence?
9. If source provenance is selected, what is the narrowest safe representation without broadening CharacterKnowledge unnecessarily?
10. What DomainEvents/history entries, if any, should Contact create/edit/reveal produce?
11. Are any new ADRs necessary, or can the implementation remain within existing Accepted architecture?
12. What integration/E2E tests are required to prove search isolation, edit persistence and safe disclosure?

---

# 14. Potential Human arbitration

At Product specification time, no Human arbitration is required beyond the already completed selection of Option C.

However, Human arbitration may become necessary after specialist review if any of the following remain materially contested:

1. **Player-visible source provenance**
   - claim only;
   - claim + "Source: Nira Voss".

2. **Contact domain identity**
   - only if Game Design/Product meaning and Architecture implementation create a cross-domain disagreement over whether Contact is a Character subtype/role or a separate typed domain concept.

3. **Search scope**
   - only if UX/Product find Contacts-only search too narrow for the selected user value while Architecture warns that multi-entity search materially expands the slice.

4. **Use-in-play sufficiency**
   - only if Game Design concludes that a direct reveal is not enough to count as meaningful actual play and proposes a bounded resolution interaction instead.

These should not be escalated unless specialist reviews produce a real disagreement.

---

# 15. Review and acceptance gate

This document remains:

**PROPOSED — CROSS-DOMAIN REVIEW REQUIRED**

The next steps are:

1. Game Design reviews only the questions above.
2. UX reviews only the questions above.
3. Architecture reviews only the questions above.
4. Product consolidates the three reviews.
5. Any genuine cross-domain disagreements are presented to the Human Project Owner.
6. Only after the exact contract is accepted:
   - record the Slice 2 decision;
   - update `docs/planning/current-slice.md`;
   - authorize implementation.

No implementation should begin from this proposal alone.
