# Slice 2 Technical Design — Prep, Find and Use a Contact

Status: IMPLEMENTATION BASELINE  
Owner: Principal Software Architect / Lead Developer  
Slice contract: `docs/planning/current-slice.md`

## Scope

This design implements only the accepted Slice 2 contract.

It reuses the existing React + FastAPI + PostgreSQL modular monolith and does not introduce a new ADR.

## Domain placement

A Contact is a person-like campaign entity:

- `Entity` remains the campaign-scoped identity registry;
- `Character` owns the person's display name;
- a narrow typed `Contact` table owns Contact-only preparation state;
- `KnowledgeFragment` owns claim text and GM veracity;
- `CharacterKnowledge` remains the Player Character epistemic state.

Conceptually:

```text
Contact
- campaign_id
- character_id -> Character
- role
- location_id -> Location
- gm_note nullable
- prepared_fragment_id -> KnowledgeFragment
```

No generic NPC schema or JSON document is introduced.

## Create / edit

Create is one PostgreSQL transaction:

1. authorize GM;
2. validate same-campaign Location;
3. create Entity + Character;
4. create inline KnowledgeFragment with explicit Truth status;
5. create Contact association;
6. commit once.

Edit is direct accepted-state mutation. Name/role/Location/note update in place.

When claim text or Truth status changes, edit creates a new KnowledgeFragment and repoints Contact. Previously revealed CharacterKnowledge continues referencing the previous fragment.

Simple PostgreSQL last-write-wins concurrency is sufficient.

## Search

Search is GM-only and campaign-scoped.

It uses PostgreSQL `ILIKE` against Character name and Contact role. Ordering is:

1. name matches;
2. role-only matches;
3. lower-cased name;
4. Contact id.

Results are capped at 20. No pagination, pg_trgm, full-text, cache, or external search service is introduced.

Search results contain only Contact id, name, role and Location name.

## Read model

The GM compact summary contains:

- name;
- role;
- Location;
- optional GM note;
- prepared claim and Truth status;
- reveal preview when a single assigned recipient can be determined.

No Player Contact projection exists.

## Reveal

Reveal bypasses ActionResolution.

One transaction:

1. authorize GM;
2. lock/load Contact;
3. load its prepared KnowledgeFragment;
4. validate the submitted recipient is an assigned same-campaign Player Character;
5. create/maintain CharacterKnowledge = AWARE;
6. append `contact.information_revealed` DomainEvent only on first disclosure;
7. commit once.

Locking the Contact serializes concurrent duplicate Reveal requests for the same Contact, preserving idempotency without a generic idempotency framework.

The Player projection continues to expose only the claim. GM note, Contact state, source provenance and gm_veracity remain absent.

## Frontend

Slice 2 introduces durable Contact-specific surfaces:

- bounded Contact create/edit;
- campaign Contact search;
- compact GM summary;
- Reveal preview/confirm.

These are separate from the Slice 1 bootstrap cards and do not define a complete future information architecture.

## Explicit non-design

No:

- generic repository layer;
- generic CRUD/entity editor;
- generic search service;
- generic NPC model;
- Scene/Session;
- ActionResolution generalization;
- Rule Effect DSL;
- provenance model;
- realtime;
- cache;
- worker/broker/outbox;
- plugin/provider abstraction.
