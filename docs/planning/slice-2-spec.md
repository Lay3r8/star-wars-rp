# Slice 2 Specification — Prepare, Find and Use a Contact in Play

**Status:** PROPOSED — REVIEWS CONSOLIDATED — READY FOR ACCEPTANCE  
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

# Cross-domain review consolidation

The UX, Game Design, and Architecture reviews are complete.

## Comment disposition

| Review comment | Classification | Resolution |
|---|---|---|
| UX: Contact preparation must author the one prepared information item inside the Contact workflow | CROSS-DOMAIN DECISION | Accepted. Inline authoring is now mandatory for the acceptance path. No separate Knowledge administration step is required. |
| Architecture: inline authoring must provide the required `gm_veracity` value | CROSS-DOMAIN DECISION | Accepted. The preparation flow includes a bounded GM-facing **Truth status** field with `TRUE / FALSE / UNKNOWN`. No silent default. |
| UX: do not make the GM select the only prepared information | CLARIFICATION | Accepted. Exactly one item exists; compact summary exposes a direct Reveal action. |
| UX: define 0/1/many search behavior | DOMAIN CHANGE | Accepted into the UX contract. |
| UX: campaign search entry point must not freeze global IA | ACCEPT WITHOUT CHANGE / CLARIFICATION | Retained and clarified. |
| UX: compact summary should prioritize name/role/Location/information; GM note secondary | DOMAIN CHANGE | Accepted. |
| UX: Location prerequisite must be explicit; do not add Location authoring | CLARIFICATION | Accepted. Slice 2 assumes a pre-existing Location. |
| UX + Game Design: Player-visible source provenance can be deferred | SAFE TO DEFER | Accepted. Player receives claim only; no persisted provenance/source label in Slice 2. |
| Game Design: Contact needs no social/disposition/reputation/stat subsystem | ACCEPT WITHOUT CHANGE | Confirmed. |
| Game Design: no mandatory roll in the acceptance path | ACCEPT WITHOUT CHANGE | Confirmed. |
| Game Design: direct Reveal is sufficient "use in play" | ACCEPT WITHOUT CHANGE | Confirmed. |
| Architecture: reuse Character identity plus a narrow Contact typed profile/table | DOMAIN CHANGE | Accepted as the minimum Architecture contract for this slice. |
| Architecture: replacing prepared information creates a new KnowledgeFragment; already revealed knowledge remains unchanged | DOMAIN CHANGE | Accepted. |
| Architecture: Reveal bypasses ActionResolution and uses direct synchronous application orchestration | ACCEPT WITHOUT CHANGE / CLARIFICATION | Confirmed. |
| Architecture: PostgreSQL `ILIKE` search with small cap, no trigram/full-text yet | DOMAIN CHANGE | Accepted. |
| Architecture: Contact create/edit need no DomainEvent by default; Reveal does | SAFE TO DEFER / DOMAIN CHANGE | Accepted. Authoring history is deferred; disclosure history remains meaningful. |
| Architecture: integration/E2E test matrix | DOMAIN CHANGE | Accepted into the final test contract. |

No review introduces a contradiction with an ACCEPTED decision.

No material Human arbitration remains after these changes.

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
6. uses the direct **Reveal…** action for the Contact's single prepared information item;
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
   - exactly one information item is required for Slice 2 acceptance;
   - the GM authors its player-visible claim text **inside the Contact preparation flow**;
   - the GM also supplies a bounded **Truth status** in domain language:
     - `TRUE`;
     - `FALSE`;
     - `UNKNOWN`;
   - persistence uses the existing Knowledge model, but the UX must not require the GM to pre-create or select a technical `KnowledgeFragment`;
   - the Contact-to-information association does not mean the Contact owns canonical truth;
   - it means the GM has prepared this Contact as a fictional source for that claim.
   - reuse of an existing claim may be added later or opportunistically, but is not required for the acceptance path.

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
-> enter name / role / existing Location / optional GM note
-> author one information item + Truth status
-> Save
-> see clear success state
-> optionally Edit
-> Save changes
```

The Contact and its one prepared information item become normal durable campaign state immediately after successful Save.

**Scenario precondition:** at least one Location already exists in the campaign; Dock 47 is test/setup state. Slice 2 does not add Location authoring merely to satisfy this prerequisite.

There is no draft/candidate lifecycle in this slice.

## UX CONTRACT REQUIRED

UX must define a bounded durable authoring surface that:

- does not reuse the numbered Slice 1 bootstrap-card sequence as information architecture;
- uses domain language such as Contact, Role, Location and Information;
- follows UX-A01 mutation lifecycle guidance;
- prevents accidental duplicate submission while Save is pending;
- follows UX-A02 for actionable errors;
- exposes known constraints before submission per UX-A03;
- uses an authorized Location selector consistent with UX-A06 and a clear empty state when no Location exists;
- authors the single prepared information item inline, including player-visible claim text and GM-facing Truth status;
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
- same-campaign validation for the Location reference and prepared information;
- one atomic Create Contact transaction that creates:
  1. Entity/Character identity;
  2. Contact typed state;
  3. the new KnowledgeFragment with explicit `gm_veracity`;
  4. the Contact -> KnowledgeFragment association;
- edit semantics for replacing prepared information without rewriting already revealed knowledge;
- history/event behavior where materially useful.

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

### Minimum 0 / 1 / many behavior

- **0 results:** retain the query and show a clear `No Contacts found` state; do not auto-create.
- **1 result:** show one normal selectable row; Enter/click opens it; do not auto-open.
- **many results:** each row shows **name + role + Location** for disambiguation.
- duplicate names are valid.
- minimum keyboard behavior:
  - Arrow Up/Down changes highlighted result;
  - Enter opens the highlighted result;
  - Escape closes search/summary and returns to the prior live context.

A keyboard shortcut to focus/open search is useful but not required for acceptance.

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

**Primary / immediately visible**
- Contact name;
- role;
- associated Location;
- the single prepared information item;
- direct **Reveal…** affordance.

**Secondary**
- GM-only note if present; it may be collapsed/de-emphasized and must not consume unnecessary live-session space.

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
2. lower-cased Contact name;
3. stable Contact identifier as tie-breaker.

A small hard result cap (for example 20 or 50) is sufficient. Pagination is not required for Slice 2.

### Empty results

The UI must provide a meaningful empty state.

No automatic creation of a new Contact from a no-result state is required.

## ARCHITECTURE CONTRACT REQUIRED

Architecture contract:

- PostgreSQL only;
- campaign-scoped `ILIKE '%q%'` matching on Character/Contact name and Contact role;
- ordinary campaign/reference indexes only for Slice 2;
- no `pg_trgm` or full-text index until measured need justifies it;
- narrow GM search-result read model:
  - Contact id;
  - name;
  - role;
  - Location name;
- narrow GM compact-summary read model;
- small hard result cap;
- no pagination requirement for Slice 2.

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
-> direct Reveal…
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
- prepared information.

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

### Prepared information replacement

When the GM changes the prepared information:

- do not mutate the old KnowledgeFragment in place if it may already have been revealed;
- create a new KnowledgeFragment and repoint the Contact's prepared-information association;
- any existing CharacterKnowledge continues to reference the previously revealed fragment.

A Player cannot "unsee" or silently have historical knowledge rewritten.

Cleanup of obsolete unreferenced fragments is safe to defer.

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

## CONSOLIDATED DECISION — source provenance deferred

UX and Game Design agree that persisted/player-visible source provenance is unnecessary for Slice 2.

Therefore:

- reveal **only the claim** to the Player;
- do not persist or project `Source: Nira Voss`;
- the Contact remains the GM-side fictional source/context;
- revisit provenance in a later knowledge/investigation slice where remembering the source materially changes play.

---

# 10. Acceptance criteria

The final reviewed Slice 2 must satisfy all of the following.

## Preparation

1. An authenticated GM can create a Contact in an authorized campaign.
2. Contact creation requires only the accepted minimum fields.
3. The GM can associate the Contact with an existing same-campaign Location.
4. The GM can author the Contact's one prepared information item inline in the Contact preparation flow, including claim text and explicit Truth status (`TRUE` / `FALSE` / `UNKNOWN`), without pre-creating a KnowledgeFragment elsewhere.
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
17. The compact summary shows name, role, Location and the single prepared information item in user/domain language; GM note is secondary.

## Use in play

18. From the compact summary, the GM can use a direct Reveal action for the single prepared information item; no information selector is required.
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

# 15. Test expectations

## PostgreSQL integration tests

Minimum required coverage:

1. GM creates Contact + inline KnowledgeFragment atomically.
2. Failed creation leaves neither partial Contact nor partial prepared knowledge.
3. Cross-campaign Location is rejected.
4. Cross-campaign Contact/Knowledge/recipient references are rejected.
5. Player cannot create/update/search/read GM Contact summary/reveal.
6. Edit persists after reload.
7. Replacing prepared information does not alter/retract already revealed CharacterKnowledge.
8. Search is strictly campaign-scoped.
9. Partial case-insensitive name matching.
10. Partial case-insensitive role matching.
11. Name-match precedence + deterministic ordering, including duplicate names.
12. Search results do not expose GM note or hidden claim.
13. Before Reveal, claim is absent from Player projection.
14. Reveal creates/maintains `CharacterKnowledge = AWARE` atomically.
15. Repeated Reveal is idempotent and does not duplicate disclosure history.
16. After Reveal, exact claim appears in the authorized Player projection.
17. `gm_veracity` and GM note never appear in Player JSON.
18. Reveal does not create or require an ActionResolution row.

## E2E

One full Playwright acceptance path is sufficient:

```text
pre-existing Location + GM/Player/assigned Character
-> GM creates Nira with information + Truth status inline
-> Save feedback
-> edit role/note
-> reload
-> search "Nira" or "dock"
-> select result
-> compact summary
-> preview recipient + exact claim
-> Reveal
-> Player refresh/re-fetch
-> exact claim visible
-> reload preserves state
```

Location may be fixture/precondition.

Duplicate-name ordering/disambiguation and cross-campaign isolation may remain integration tests.

---

# 16. Explicit exclusions

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

# 17. Cross-domain review matrix

# 12. Final architecture / data / API contract

## Contact identity

Architecture review establishes the following minimum implementation direction:

- a Contact is person-like and reuses the existing `Character` identity;
- Contact-specific state lives in a narrow typed relational profile/table;
- do not create a second independent NPC identity model;
- do not add nullable Contact-only columns to every Character;
- do not introduce generic JSONB NPC documents.

Conceptually:

```text
Contact
- campaign_id
- character_id PK/FK -> Character
- role
- location_id FK -> Location
- gm_note nullable
- prepared_fragment_id FK -> KnowledgeFragment
```

`Character.name` remains the name source.

Campaign-scoped composite references/constraints should be used where applicable.

## Minimum GM API/commands

No generic CRUD framework is required.

Minimum bounded commands/endpoints are conceptually:

```text
CreateContact
UpdateContact
SearchContacts
GetContactSummary
RevealPreparedInformation
```

Equivalent HTTP surfaces may be:

```text
POST /campaigns/{campaign_id}/contacts
PATCH or PUT /campaigns/{campaign_id}/contacts/{contact_id}
GET /campaigns/{campaign_id}/contacts/{contact_id}
GET /campaigns/{campaign_id}/contacts/search?q=...
POST /campaigns/{campaign_id}/contacts/{contact_id}/reveal
```

Exact route naming remains implementation detail.

## Create transaction

Acceptance-path input contains domain data:

- name;
- role;
- location id;
- optional GM note;
- prepared claim text;
- Truth status / `gm_veracity`.

One transaction creates identity, Contact state, KnowledgeFragment and association.

Failure leaves no partial Contact or orphaned acceptance-path knowledge.

## Update transaction

- validates same-campaign references;
- updates name/role/Location/note atomically;
- replacing prepared information creates a new KnowledgeFragment and repoints the Contact;
- simple PostgreSQL last-write-wins concurrency is sufficient for this slice;
- no ETag/version/distributed-locking framework is required.

## Reveal transaction

Reveal does **not** use `ActionResolution`.

Transaction:

1. authorize GM;
2. load and validate Contact;
3. load Contact's bound prepared fragment server-side;
4. resolve/validate recipient assigned Player Character;
5. create/update `CharacterKnowledge = AWARE`;
6. append one meaningful disclosure DomainEvent/history record;
7. commit once.

Repeated Reveal to an already-aware recipient is idempotent and must not duplicate CharacterKnowledge or disclosure history.

Contact create/edit DomainEvents are not required for Slice 2 unless implementation demonstrates a concrete Product need.

No outbox is required.

---

# 13. Authorization / security contract

- every Contact command/query derives GM campaign membership server-side;
- `campaign_id` alone is not authorization;
- Contact, Character, Location, KnowledgeFragment and reveal recipient must be same-campaign validated;
- Player cannot create/update/search/read canonical Contact summaries or Reveal;
- search never searches Principals/accounts;
- search never returns cross-campaign Contacts;
- GM note, hidden prepared claim and `gm_veracity` are never included in Player JSON before Reveal;
- after Reveal, Player receives the authorized claim only;
- no canonical Contact DTO may be sent to Player and hidden in React;
- no source provenance is persisted/projected in Slice 2.

---

# 14. Acceptance criteria and test expectations

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

# 18. Specialist review outcome

## UX

**Final consolidated position:** blocker resolved.

Accepted UX contract:

- prepared information is authored inline with Contact preparation;
- one prepared information item => direct Reveal, no selector;
- 0/1/many result behavior as specified;
- duplicate names disambiguated with role + Location;
- campaign-level search entry point available from live flow;
- compact summary prioritizes name/role/Location/information;
- GM note is secondary;
- pre-existing Location is a scenario precondition;
- source provenance is deferred.

## Game Design

**Final position:** APPROVE.

Minimum contract:

- Contact is a fictional campaign entity/source/context, not a mechanically complete NPC;
- required gameplay fields are name, role, scenario Location and one prepared information item;
- optional GM note is not gameplay-required;
- no relationship/disposition/reputation/stats are required;
- no roll is required when the GM establishes that the Contact provides the information;
- accepted when-to-roll semantics remain sufficient for optional uncertain situations;
- direct Reveal is sufficient actual play;
- no source provenance is required.

## Architecture

**Final consolidated position:** blockers resolved by this specification.

Accepted minimum contract:

- reuse Character identity + narrow Contact typed table/profile;
- inline information authoring creates Contact + KnowledgeFragment atomically;
- explicit Truth status supplies required `gm_veracity`;
- replacing prepared information creates a new KnowledgeFragment;
- PostgreSQL `ILIKE` search only; no full-text/trigram yet;
- bounded Contact GM API/read models;
- Reveal bypasses ActionResolution and directly reuses Knowledge disclosure semantics;
- Reveal is synchronous, atomic and idempotent;
- no new ADR required if implementation remains within this contract;
- no new horizontal infrastructure.

---

# 19. Human arbitration

**No substantive Human arbitration remains.**

The only previously identified material questions have converged:

- **source provenance:** UX + Game Design + Architecture agree to defer it;
- **Contact identity:** Architecture selected Character identity + narrow Contact typed state without conflicting Product/Game Design semantics;
- **search scope:** Contacts-only campaign search remains accepted for this slice;
- **use in play:** Game Design confirms direct Reveal is sufficient actual play;
- **inline information authoring:** UX, Game Design and Architecture agree;
- **veracity:** explicit bounded GM Truth status resolves the accepted Knowledge persistence requirement without a silent default.

No Human choice is needed unless the Human Project Owner wishes to reopen one of these converged decisions.

---

# 20. Acceptance gate

All cross-domain review blockers identified on PR #11 are resolved in this consolidated specification.

**Remaining blockers:** NONE.

This specification is therefore:

**READY FOR PRODUCT/HUMAN ACCEPTANCE — IMPLEMENTATION NOT YET AUTHORIZED**

The slice is still not marked `ACCEPTED` in this PR and `docs/planning/current-slice.md` is unchanged.

Next step:

1. Human Project Owner confirms acceptance of this final consolidated contract, or explicitly reopens a material point.
2. Product records the accepted Slice 2 decision and updates `docs/planning/current-slice.md`.
3. Only after that merge is implementation authorized.

No implementation should begin before those acceptance records are in `main`.
