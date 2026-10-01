# Current Vertical Slice

## Slice 2 — Prep a Contact, Find Them Instantly, Use Them in Play

**Status:** ACCEPTED  
**Accepted:** 2026-10-01  
**Owner:** Product Lead / Human Project Owner  
**Specification:** `docs/planning/slice-2-spec.md`

## Goal

Validate that the application can support a durable GM preparation-to-live-play workflow:

```text
prepare Contact
-> edit if needed
-> find quickly during live play
-> open compact summary
-> reveal one prepared piece of information
-> persist safe Player disclosure
```

## Accepted scenario

The GM prepares Nira Voss before the session with:

- name;
- short role;
- existing Location;
- optional GM note;
- one prepared information item;
- explicit Truth status: `TRUE`, `FALSE`, or `UNKNOWN`.

During live play the GM searches the current campaign for Nira, opens a compact summary, previews the exact recipient Character and exact claim, and explicitly Reveals that claim.

No social roll is required in the acceptance path because the GM has established that Nira provides the information.

## Required Slice 2 contracts

- GM and Player remain distinct authenticated principals.
- Contact reuses Character identity plus a narrow typed Contact profile/state.
- Contact preparation authors the one information item inline.
- Contact creation atomically persists Contact state + KnowledgeFragment association.
- Replacing prepared information creates a new KnowledgeFragment and does not rewrite previously revealed CharacterKnowledge.
- Search is GM-only, current-campaign only, Contacts-only.
- Search fields: Contact name + role.
- Matching: case-insensitive partial text.
- Ordering: name matches before role-only matches, then deterministic name/id ordering.
- 0/1/many result behavior and minimum keyboard interaction follow the accepted UX contract.
- Compact summary shows name, role, Location, prepared information, and direct Reveal; GM note is secondary.
- Reveal bypasses Slice-1-specific ActionResolution persistence.
- Reveal is backend-authorized, synchronous, atomic and idempotent.
- After Reveal, `CharacterKnowledge = AWARE` and the Player projection contains the exact claim.
- GM note and `gm_veracity` remain hidden from Player.
- Player-visible source provenance is deferred.
- PostgreSQL remains the only required search/persistence technology.

## Acceptance criteria

The normative acceptance criteria and test expectations are defined in `docs/planning/slice-2-spec.md`.

At minimum, implementation must demonstrate end-to-end:

```text
pre-existing Location + GM + Player + assigned Character
-> GM creates Contact with inline information + Truth status
-> Save feedback
-> edit
-> reload
-> search
-> compact summary
-> preview recipient + exact claim
-> Reveal
-> Player receives exact claim
-> reload preserves Contact and disclosure state
```

## Explicit Slice 2 exclusions

- complete campaign CMS;
- generic entity editor;
- full NPC system;
- relationship/disposition/reputation systems;
- social combat;
- combat/encounters;
- Scene/Session;
- procedural generation;
- Player Contact search/directory;
- Principal/account search;
- multi-entity global search;
- realtime/WebSockets/SSE;
- Elasticsearch/OpenSearch;
- pg_trgm/full-text search for this slice;
- generic ActionResolution engine;
- Rule Effect DSL;
- outbox worker/broker;
- microservices;
- plugin runtime;
- generic undo/archive/delete;
- Player-visible source provenance;
- i18n implementation.

## Deferred questions

Deferred items remain non-normative and must not be inferred as accepted requirements from this slice.

See `docs/planning/open-questions.md`.
