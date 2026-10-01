# Slice 2 Final Specification — Prepare, Find and Use a Contact in Play

**Status:** ACCEPTED  
**Owner:** Product Lead  
**Selected direction:** Option C from `docs/planning/slice-2-candidates.md`  
**Implementation authorization:** OPEN AFTER THIS ACCEPTANCE RECORD IS MERGED TO `main`

## Purpose

Define the final reviewed Slice 2 contract for:

```text
prepare Contact
-> edit if needed
-> find quickly during live play
-> open compact summary
-> reveal one prepared piece of information
```

This slice is intentionally narrow.

It must not become:

- a generic CMS;
- a full NPC system;
- a relationship/reputation engine;
- a global search platform;
- a frontend-wide redesign;
- a Scene/Session subsystem.

---

# 1. Review consolidation

The UX, Game Design and Architecture reviews are complete.

## Comment disposition

| Comment | Classification | Resolution |
|---|---|---|
| Contact preparation must author the one prepared information item inline | CROSS-DOMAIN DECISION | Accepted. Inline authoring is mandatory for the acceptance path. |
| Inline information needs explicit `gm_veracity` | CROSS-DOMAIN DECISION | Accepted. GM provides a bounded **Truth status**: TRUE / FALSE / UNKNOWN. |
| Do not select the only prepared information during live use | CLARIFICATION | Accepted. Contact summary exposes a direct Reveal action. |
| Define 0/1/many search behavior | DOMAIN CHANGE | Accepted into UX contract. |
| Search entry point must not freeze global IA | CLARIFICATION | Accepted. One campaign-level entry point only. |
| Compact summary prioritizes name/role/Location/information; GM note secondary | DOMAIN CHANGE | Accepted. |
| Location must be explicit precondition, not new authoring scope | CLARIFICATION | Accepted. |
| Player-visible source provenance | SAFE TO DEFER | Deferred. Player receives the claim only. |
| No social/disposition/reputation/stat system | ACCEPT WITHOUT CHANGE | Confirmed by Game Design. |
| No mandatory roll in acceptance path | ACCEPT WITHOUT CHANGE | Confirmed by Game Design. |
| Direct Reveal counts as sufficient actual play | ACCEPT WITHOUT CHANGE | Confirmed by Game Design. |
| Contact uses Character identity + narrow typed Contact state | DOMAIN CHANGE | Accepted Architecture contract. |
| Replacing prepared information creates a new KnowledgeFragment | DOMAIN CHANGE | Accepted Architecture contract. |
| Reveal bypasses Slice-1 ActionResolution persistence | CLARIFICATION | Confirmed. |
| PostgreSQL `ILIKE` search; no trigram/full-text yet | DOMAIN CHANGE | Accepted. |
| Contact create/edit DomainEvents not required by default | SAFE TO DEFER | Deferred; Reveal history remains required. |

**No review introduces a contradiction with an ACCEPTED decision.**

---

# 2. Exact scenario

Before the session, the GM prepares:

- **Contact:** Nira Voss
- **Role:** Imperial dock clerk and discreet informant
- **Location:** Dock 47
- **GM note:** optional
- **Information Nira knows:** "A customs audit is scheduled for Dock 47 tomorrow at 06:00."
- **Truth status:** TRUE

The campaign already contains:

- Dock 47 as a Location;
- one GM Principal;
- one Player Principal;
- one assigned Player Character.

During live play, the Player Character asks who at Dock 47 might know about upcoming Imperial activity.

The GM:

1. opens the campaign Contact search;
2. types `Nira` or `dock clerk`;
3. selects Nira Voss;
4. opens the compact summary;
5. sees the prepared information;
6. chooses **Reveal…**;
7. sees the exact recipient Character and exact claim;
8. confirms Reveal;
9. the Player Character's projection now contains the claim.

No roll is required because the GM has established that Nira provides the information.

If a future situation is uncertain, risky and has meaningful success/failure, the accepted when-to-roll rule still applies, but that branch is outside this Slice 2 acceptance path.

---

# 3. Actors

## GM — required

The GM can:

- create the Contact;
- edit the Contact;
- search Contacts in the current campaign;
- open the compact Contact summary;
- reveal the prepared information.

## Player — required

The Player is included only to prove the disclosure path.

The Player:

- is authenticated separately;
- is assigned to one Character;
- cannot see the prepared information before Reveal;
- sees the exact claim after Reveal.

The Player does not need:

- Contact search;
- Contact authoring;
- Contact detail UI;
- social action UI;
- Contact directory.

---

# 4. Initial state

The acceptance scenario starts with:

- one Campaign;
- one authenticated GM membership;
- one authenticated Player membership;
- one Player-to-Character assignment;
- one existing Location: Dock 47;
- no Nira Contact yet;
- no prepared Nira claim yet;
- no CharacterKnowledge for that claim.

**Location authoring is explicitly out of scope.**

If the campaign has no Location, the Contact creation UI must show a clear empty state rather than silently depending on the old Slice 1 bootstrap surface.

---

# 5. Minimum Contact fields

## Product contract

The Contact requires only:

1. **Name** — required.
2. **Role / short fictional function** — required.
3. **Associated Location** — required for this scenario.
4. **GM note** — optional.
5. **Prepared information** — exactly one item for Slice 2:
   - player-visible claim text;
   - GM Truth status: TRUE / FALSE / UNKNOWN.

The prepared information is authored inline in the Contact workflow.

The GM must not be required to pre-create a technical KnowledgeFragment elsewhere.

## Explicitly excluded Contact fields

No requirement for:

- motivation;
- disposition;
- relationship state;
- reputation;
- faction;
- species/class;
- skills/stats;
- combat profile;
- inventory;
- biography/personality;
- schedule;
- objectives;
- favour/debt;
- source reliability;
- portrait.

---

# 6. Minimum Game Design contract

Game Design has approved the following:

- Contact is a fictional campaign entity/source/context, not a mechanically complete NPC.
- Name, short role, scenario Location and one prepared information item are sufficient.
- GM note is optional Product/UX data, not a gameplay requirement.
- No relationship/disposition/reputation/social-stat mechanic is required.
- No social roll is required when the GM establishes that the Contact willingly provides the information.
- Existing when-to-roll semantics remain authoritative for optional uncertain situations.
- Direct Reveal is sufficient actual play for this slice.
- The Contact-to-information association does not imply ownership of canonical truth.
- `KnowledgeFragment` remains the proposition/claim.
- `gm_veracity` remains independent of the Contact.
- After Reveal, `CharacterKnowledge = AWARE` remains sufficient.
- Player-visible source provenance is not required.

---

# 7. Preparation workflow

The required flow is:

```text
Create Contact
-> enter name
-> enter role
-> select existing Location
-> optional GM note
-> author one information item
-> choose Truth status
-> Save
-> clear success/error state
```

## UX contract

The preparation surface must:

- be a durable Contact workflow, not an extension of the numbered Slice 1 bootstrap cards;
- use domain language;
- show observable mutation state;
- prevent accidental duplicate Save while pending;
- provide actionable errors;
- expose known constraints before submission;
- use an authorized Location selector;
- show a meaningful empty state if no Location exists;
- author the one prepared information item inline;
- not expose raw IDs, KnowledgeFragment terminology or persistence state.

## Persistence contract

A successful Save makes the Contact normal durable campaign state immediately.

There is:

- no draft lifecycle;
- no candidate state;
- no separate Knowledge administration step.

---

# 8. Edit workflow

The GM can edit:

- name;
- role;
- Location;
- GM note;
- prepared information.

## Prepared information replacement

Replacing the prepared information must:

- create a new KnowledgeFragment;
- repoint the Contact to the new fragment;
- leave previously revealed CharacterKnowledge referencing the old fragment unchanged.

Previously disclosed knowledge is not silently rewritten or retracted.

Cleanup of old unreferenced fragments is safe to defer.

## UX contract

Edit must:

- show pending/success/error state;
- distinguish editing from revealing;
- reflect saved values after success;
- preserve updates after reload.

---

# 9. Live search workflow

Required flow:

```text
Open campaign Contact search
-> type query
-> see results
-> select Contact
-> compact summary
```

The entry point must be available from the live campaign workflow without navigating through a deep administration hierarchy.

It does not define the future global navigation architecture.

## 0 / 1 / many behavior

- **0 results:** retain query and show `No Contacts found`.
- **1 result:** show one normal selectable row; do not auto-open.
- **many results:** show enough context to disambiguate.

Each result row shows:

- name;
- role;
- Location.

Duplicate names are valid.

## Minimum keyboard behavior

- Arrow Up/Down moves highlighted result;
- Enter opens highlighted result;
- Escape closes search/summary and returns to prior live context.

A keyboard shortcut to open search is useful but not required.

---

# 10. Search semantics

## Scope

- current campaign only;
- GM only;
- Contacts only.

This is not:

- Principal search;
- Player search;
- multi-entity global search.

## Searchable fields

Required:

- Contact name;
- Contact role.

Not required:

- Location name;
- GM note;
- hidden claim text.

## Matching

- case-insensitive;
- partial textual match;
- sufficient for `Nira`, `dock`, `clerk`.

No fuzzy or semantic search.

## Ordering

1. name matches before role-only matches;
2. lower-cased Contact name;
3. stable Contact id as tie-breaker.

A small hard result cap such as 20 or 50 is sufficient.

No pagination requirement.

---

# 11. Compact summary

The live compact summary shows:

## Primary

- name;
- role;
- Location;
- prepared information;
- direct **Reveal…** action.

## Secondary

- GM note, if present.

GM note may be collapsed or visually de-emphasized.

The summary must not expose:

- Entity terminology;
- KnowledgeFragment terminology;
- persistence/read-model terminology;
- raw ids;
- internal statuses.

---

# 12. Exact use-in-play action

The exact action is:

> Reveal the Contact's one prepared information item to the assigned Player Character.

Flow:

```text
Contact summary
-> Reveal…
-> preview recipient + exact claim
-> confirm Reveal
-> CharacterKnowledge = AWARE
-> Player projection contains claim
```

There is no prepared-information selector because the slice supports exactly one item.

## Disclosure preview

Before commit, the GM sees:

- recipient Character;
- exact player-visible claim.

No additional confirmation modal is required if the preview and Reveal action are already explicit.

## Source provenance

Deferred.

The Player sees the claim only.

Do not persist or display `Source: Nira Voss` in Slice 2.

---

# 13. Architecture and data contract

## Contact identity

Use:

- existing Entity registry;
- existing Character identity;
- a narrow typed Contact profile/table.

Do not:

- create a second independent NPC identity system;
- add nullable Contact fields to every Character;
- use generic JSONB NPC documents.

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

Campaign-scoped composite constraints/references should be used where applicable.

## Knowledge ownership

Claim text and `gm_veracity` remain owned by KnowledgeFragment.

Contact stores only the prepared association.

---

# 14. API / command contract

No generic CRUD framework.

Minimum bounded operations:

```text
CreateContact
UpdateContact
SearchContacts
GetContactSummary
RevealPreparedInformation
```

Equivalent HTTP routes may be:

```text
POST   /campaigns/{campaign_id}/contacts
PATCH  /campaigns/{campaign_id}/contacts/{contact_id}
GET    /campaigns/{campaign_id}/contacts/{contact_id}
GET    /campaigns/{campaign_id}/contacts/search?q=...
POST   /campaigns/{campaign_id}/contacts/{contact_id}/reveal
```

Exact route naming is implementation detail.

## Create transaction

Input contains:

- name;
- role;
- location id;
- optional GM note;
- prepared claim text;
- Truth status / `gm_veracity`.

One transaction creates:

1. Entity/Character identity;
2. Contact state;
3. KnowledgeFragment;
4. Contact -> KnowledgeFragment association.

Failure leaves no partial Contact or orphaned acceptance-path knowledge.

## Update transaction

- validates same-campaign references;
- updates name/role/Location/note atomically;
- replacing prepared information creates a new KnowledgeFragment;
- simple PostgreSQL last-write-wins concurrency is sufficient.

No ETag/version/distributed-locking framework.

## Reveal transaction

Reveal does not use ActionResolution.

Transaction:

1. authorize GM;
2. load/validate Contact;
3. load bound prepared fragment server-side;
4. resolve/validate recipient assigned Player Character;
5. make CharacterKnowledge = AWARE;
6. append one meaningful disclosure DomainEvent;
7. commit once.

Repeated Reveal to an already-aware recipient is idempotent:

- no duplicate CharacterKnowledge;
- no duplicate disclosure history.

Contact create/edit DomainEvents are not required.

No outbox is required.

---

# 15. Search implementation contract

PostgreSQL only.

Conceptually:

```text
campaign_id = current campaign
AND (
  Character.name ILIKE '%' || :q || '%'
  OR Contact.role ILIKE '%' || :q || '%'
)
```

## Indexing

Use only ordinary campaign/reference indexes.

Do not add:

- full-text search;
- pg_trgm;
- Elasticsearch/OpenSearch.

A campaign-scoped scan is acceptable at expected Slice 2 scale.

## Read models

### Search result

- Contact id;
- name;
- role;
- Location name.

Do not include:

- GM note;
- hidden claim.

### GM compact summary

- name;
- role;
- Location;
- optional GM note;
- prepared claim;
- exact Reveal preview data.

No Player Contact projection is required.

---

# 16. Authorization and security contract

Every Contact command/query requires server-derived GM campaign membership.

`campaign_id` alone is not authorization.

Backend/DB constraints validate same-campaign consistency for:

- Contact;
- Character;
- Location;
- KnowledgeFragment;
- Reveal recipient.

The Player cannot:

- create Contact;
- update Contact;
- search Contacts;
- read canonical GM Contact summary;
- Reveal.

The search endpoint:

- never searches Principals;
- never enumerates accounts;
- never returns cross-campaign Contacts.

Before Reveal the Player receives none of:

- prepared hidden claim;
- GM note;
- `gm_veracity`;
- canonical Contact data not explicitly authorized.

After Reveal the Player receives the authorized claim only.

No canonical Contact DTO is sent to Player and hidden in React.

No source provenance is persisted/projected.

---

# 17. Acceptance criteria

## Preparation and edit

1. Authenticated GM can create a Contact in an authorized campaign.
2. Contact creation requires only the accepted minimum fields.
3. GM can select an existing same-campaign Location.
4. GM authors the one prepared information item inline.
5. GM explicitly chooses Truth status: TRUE / FALSE / UNKNOWN.
6. One successful Save atomically creates Contact state + KnowledgeFragment association.
7. Failed creation leaves no partial Contact or orphaned prepared knowledge.
8. Save exposes observable pending/success/error state.
9. Repeated activation while pending cannot create accidental duplicate state.
10. Reload preserves Contact and prepared information.
11. GM can edit Contact fields.
12. Replacing prepared information does not rewrite/retract already revealed CharacterKnowledge.
13. Reload/search reflects edited canonical values.

## Search

14. GM has a campaign-level Contact search entry point usable from live workflow.
15. Search is current-campaign only.
16. Search matches name and role case-insensitively by partial text.
17. Search never returns another campaign's Contact.
18. 0 results retains query and shows empty state.
19. 1 result remains a normal selectable row.
20. Many results show name + role + Location.
21. Duplicate Contact names are allowed.
22. Ordering is deterministic.
23. Arrow Up/Down, Enter and Escape support the required minimum keyboard flow.
24. Selecting a result opens compact summary without deep admin navigation.

## Compact summary and use in play

25. Summary shows name, role, Location and prepared information.
26. GM note is secondary.
27. Summary exposes direct Reveal action.
28. No information selector is required.
29. Reveal preview shows exact recipient Character and exact claim.
30. Player cannot commit Reveal.
31. Before Reveal, claim is absent from Player projection.
32. Reveal is backend-authorized and same-campaign validated.
33. Reveal commits CharacterKnowledge = AWARE atomically.
34. Repeated Reveal is idempotent.
35. After Reveal, Player projection contains exact claim.
36. GM note and `gm_veracity` remain absent from Player JSON.
37. Reveal does not create or require ActionResolution.
38. Reload preserves Contact and disclosure state.

## Scope / architecture

39. Search uses existing PostgreSQL/application topology.
40. No generic CMS/entity editor is introduced.
41. No social/relationship engine is introduced.
42. No Scene/Session subsystem is introduced.
43. No generic ActionResolution engine is introduced.
44. No new distributed infrastructure is introduced.

---

# 18. Test expectations

## PostgreSQL integration tests

Minimum coverage:

1. GM creates Contact + inline KnowledgeFragment atomically.
2. Failed creation leaves no partial state.
3. Cross-campaign Location rejected.
4. Cross-campaign Contact/Knowledge/recipient references rejected.
5. Player cannot create/update/search/read GM Contact summary/reveal.
6. Edit persists after reload.
7. Replacing prepared information does not alter already revealed CharacterKnowledge.
8. Search strictly campaign-scoped.
9. Partial case-insensitive name match.
10. Partial case-insensitive role match.
11. Name-match precedence + deterministic ordering, including duplicate names.
12. Search result excludes GM note and hidden claim.
13. Before Reveal, claim absent from Player projection.
14. Reveal creates/maintains CharacterKnowledge = AWARE atomically.
15. Repeated Reveal is idempotent and does not duplicate history.
16. After Reveal, exact claim appears in authorized Player projection.
17. `gm_veracity` and GM note never appear in Player JSON.
18. Reveal does not create ActionResolution.

## E2E

One Playwright acceptance path:

```text
pre-existing Location
+ GM
+ Player
+ assigned Character
-> GM creates Nira with inline information + Truth status
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

Duplicate-name ordering and cross-campaign isolation may remain integration tests.

---

# 19. Explicit exclusions

## Product / UX

- complete campaign CMS;
- generic entity editor;
- global navigation redesign;
- full NPC profile;
- Player Contact directory;
- Player global search;
- Principal/account search;
- invitation/onboarding redesign;
- realtime update system;
- generic notification platform;
- i18n implementation;
- duplicate-content engine;
- generic undo;
- archive/delete.

## Game Design

- relationship/disposition;
- reputation;
- social combat;
- favour/debt;
- social skills;
- NPC combat stats;
- progression;
- Force;
- combat/encounters.

## Architecture

- Scene;
- Session;
- Elasticsearch/OpenSearch;
- pg_trgm/full-text search for Slice 2;
- generic search abstraction;
- graph database;
- event-driven indexing;
- generic CRUD/meta-form framework;
- generic ActionResolution engine;
- Rule Effect DSL;
- outbox worker;
- broker/queue;
- cache platform;
- WebSockets/SSE;
- microservices;
- plugin runtime;
- generic pagination framework;
- provenance graph.

## Content

- procedural generation;
- automatic Contact generation;
- faction authoring;
- relationship graph;
- objectives/threads;
- item/vehicle authoring;
- portraits/image generation;
- rich-text/wiki/journal system.

---

# 20. Specialist review outcome

## UX

**Blocker resolved.**

Accepted UX contract:

- inline information authoring;
- direct Reveal for the single item;
- 0/1/many search behavior;
- role + Location disambiguation;
- campaign-level live search entry point;
- compact summary with primary/secondary hierarchy;
- Location as precondition;
- source provenance deferred.

## Game Design

**APPROVE.**

No new mechanic required.

## Architecture

**Blockers resolved.**

Accepted minimum:

- Character identity + narrow Contact typed state;
- atomic inline information creation;
- explicit Truth status;
- new fragment on information replacement;
- PostgreSQL ILIKE search;
- bounded Contact APIs/read models;
- direct Knowledge disclosure;
- synchronous atomic idempotent Reveal;
- no new ADR required if implementation remains inside this contract.

---

# 21. Human acceptance

**Accepted by Human Project Owner on 2026-10-01.**

The final consolidated contract is accepted as written.

Previously open cross-domain points are resolved as follows:

- source provenance: deferred;
- Contact identity: Character + narrow Contact typed state;
- search scope: Contacts only;
- use in play: direct Reveal;
- inline information authoring: required;
- veracity: explicit Truth status.

These accepted Slice 2 decisions do not automatically accept any broader deferred capability.

---

# 22. Acceptance gate

**Remaining blockers: NONE.**

This specification is now **ACCEPTED**.

Implementation is authorized **only after** this accepted specification, the updated decision log, and the updated `docs/planning/current-slice.md` are merged into `main`.

No implementation should begin from the PR branch alone.
