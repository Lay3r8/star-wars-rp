# Slice 1 Technical Design — Slice the terminal, reveal the secret

Status: IMPLEMENTATION BASELINE
Owner: Principal Software Architect / Lead Developer
Slice contract: `docs/planning/current-slice.md`
Branch: `ai/architecture/slice-1`

## 1. Normative baseline

This design implements the accepted Slice 1 contract without reopening accepted decisions.

Normative constraints:

- React frontend.
- FastAPI backend.
- PostgreSQL authoritative mutable state.
- Modular monolith.
- Docker Compose for local orchestration.
- Tunnel provider is transport-only.
- `campaign_id` is a strict isolation invariant, not sufficient authorization.
- GM and Player are distinct authenticated principals.
- Player-facing data uses explicit projections.
- `KnowledgeFragment` is canonical claim data with GM-side veracity.
- absence of `CharacterKnowledge` means Unknown.
- Slice 1 uses only `CharacterKnowledge = Aware`.
- `DomainEvent` is append-only audit/history output and is not internal RPC.
- no outbox worker, event sourcing, generic consequence engine, Rule Effect DSL, Session, Scene, generation, realtime, combat, or plugin runtime.

## 2. Architectural challenge result

No accepted decision must be reopened.

The accepted contracts can be implemented without:

- duplicate sources of truth;
- distributed transactions;
- asynchronous command routing;
- a generic workflow engine;
- a generic rules interpreter;
- frontend authorization;
- speculative extension points.

The main implementation risks are cross-campaign references, trusting caller-supplied identity/role data, non-idempotent Apply, and accidentally duplicating history state. The design below addresses each directly.

## 3. Runtime topology

```text
Browser
  |
  | same-origin /api through Vite dev proxy
  v
React + Vite
  |
  v
FastAPI modular monolith
  |
  v
PostgreSQL

Optional ngrok / Cloudflare Tunnel
  |
  +-- exposes the frontend origin only
      and does not participate in auth/authz
```

No broker, worker, cache, search service, or realtime service is required.

## 4. Backend module boundaries

The backend is one deployable application with explicit package boundaries.

```text
auth
  Principal identity, password verification, signed login cookie

campaigns
  Campaign, membership, role, player-to-character assignment,
  authorization queries

entities
  Cross-cutting Entity identity registry

characters
  Character identity/name

world
  Location

custom_d20
  Slice 1 precomputed slicing modifier
  pure D20 resolution function

knowledge
  KnowledgeFragment
  CharacterKnowledge
  reveal mutation

resolutions
  ActionResolution persistence/lifecycle
  orchestration of Roll, Apply, Close Failure

history
  DomainEvent append
  GM-readable history projection
```

Dependency direction:

```text
HTTP routers
   |
application services
   |
   +--> campaigns authorization
   +--> resolutions
           +--> custom_d20
           +--> knowledge
           +--> history
   |
SQLAlchemy models / PostgreSQL
```

Rules:

- `knowledge` does not call back into `resolutions`.
- `DomainEvent` handlers never drive canonical Slice 1 mutations.
- no repository/interface layer is introduced over SQLAlchemy for Slice 1; services receive a SQLAlchemy Session directly.
- pure mechanical logic remains outside HTTP and ORM code.

## 5. Authentication strategy

Slice 1 uses local username/password principals.

- password hashes use Argon2;
- successful login issues a short-lived signed JWT containing only the principal identifier;
- the JWT is stored in an HttpOnly, SameSite cookie;
- role, membership, campaign access, and character assignment are never encoded as authoritative token claims;
- every privileged request reloads authorization state from PostgreSQL;
- the cookie Secure flag is configuration-driven so local HTTP works while tunnel HTTPS can require secure cookies.

This is deliberately not a generic identity-provider abstraction.

## 6. Minimal persistent model

### Principal

```text
principal
- id UUID PK
- username unique
- password_hash
- created_at
```

### Campaign

```text
campaign
- id UUID PK
- name
- created_at
```

### CampaignMembership

```text
campaign_membership
- campaign_id FK
- principal_id FK
- role: GM | PLAYER
- created_at
PK(campaign_id, principal_id)
```

Role is server-authoritative.

### Entity

```text
entity
- id UUID PK
- campaign_id FK
- entity_type: character | location
- created_at
UNIQUE(campaign_id, id)
```

Entity remains identity-only. No generic JSON property bag is added.

### Character

```text
character
- entity_id PK
- campaign_id
- name
FK(campaign_id, entity_id) -> entity(campaign_id, id)
```

### CustomD20CharacterProfile

```text
custom_d20_character_profile
- character_id PK
- campaign_id
- slicing_modifier
FK(campaign_id, character_id) -> character(campaign_id, entity_id)
```

The modifier belongs to Custom D20, not generic Character state.

### Location

```text
location
- entity_id PK
- campaign_id
- name
FK(campaign_id, entity_id) -> entity(campaign_id, id)
```

No persistent Scene is introduced. ActionResolution references the current Location directly.

### PlayerCharacterAssignment

```text
player_character_assignment
- campaign_id
- player_principal_id
- character_id
PK(campaign_id, player_principal_id)
UNIQUE(campaign_id, character_id)
FK(campaign_id, player_principal_id) -> campaign_membership
FK(campaign_id, character_id) -> character
```

The application additionally enforces that the membership role is PLAYER.

### KnowledgeFragment

```text
knowledge_fragment
- id UUID PK
- campaign_id FK
- claim_text
- gm_veracity: TRUE | FALSE | UNKNOWN
- created_at
UNIQUE(campaign_id, id)
```

`claim_text` is the Slice 1 player-visible claim once disclosed. GM veracity is never part of the player projection.

### CharacterKnowledge

```text
character_knowledge
- campaign_id
- character_id
- fragment_id
- state: AWARE
- acquired_at
PK(campaign_id, character_id, fragment_id)
FK(campaign_id, character_id) -> character
FK(campaign_id, fragment_id) -> knowledge_fragment
```

There are no deferred belief/provenance fields.

### ActionResolution

```text
action_resolution
- id UUID PK
- campaign_id
- actor_character_id
- context_location_id
- intent
- risk
- mechanic = "slicing"
- dc
- resolved_modifier
- success_recipient_character_id
- success_fragment_id
- state
- natural_roll nullable until Roll
- total nullable until Roll
- outcome nullable until Roll
- failure_adjudication nullable until Close Failure
- created_by_principal_id
- created_at
- rolled_at nullable until Roll
- closed_at nullable until Apply/Close
```

Lifecycle-only nullability is intentional and not future-proofing.

State vocabulary:

```text
READY
SUCCESS_PENDING_APPLY
FAILURE_PENDING_CLOSE
CLOSED_SUCCESS
CLOSED_FAILURE
```

No generic state-machine framework is used.

The success effect is represented directly by:

- `success_recipient_character_id`;
- `success_fragment_id`.

There is no generic `ConsequenceProposal` table.

### DomainEvent

```text
domain_event
- id UUID PK
- campaign_id
- event_type
- subject_type
- subject_id
- actor_principal_id
- payload JSONB
- occurred_at
```

Slice 1 significant events:

- `resolution.success_applied`
- `resolution.failure_closed`

The ActionResolution row remains the source of truth for resolution state. DomainEvent is append-only audit/history output.

## 7. Authorization boundaries

All authorization is backend-side.

### Authenticated principal

Every protected endpoint obtains principal identity only from the validated login cookie.

### GM operations

GM membership is required for:

- adding a campaign member;
- creating/reading GM campaign content;
- assigning a Player to a Character;
- creating a resolution;
- rolling/resolving;
- applying success;
- closing failure;
- reading GM history.

### Player operations

Player membership and assignment are required for the player projection.

The player endpoint does not accept a character identifier. It resolves the assigned Character server-side.

### Reference validation

For every resolution operation the backend verifies same-campaign ownership of:

- actor Character;
- context Location;
- recipient Character;
- KnowledgeFragment;
- player assignment where relevant.

Cross-campaign references are rejected even when individual identifiers exist.

## 8. ActionResolution use cases and transaction boundaries

### Create resolution

Input is the pre-roll contract:

- actor;
- context;
- Intent;
- concrete Risk;
- DC;
- success recipient;
- success KnowledgeFragment.

The service:

1. authenticates/authorizes GM;
2. validates all references against the campaign;
3. validates the recipient is the acting Character for Slice 1;
4. loads the precomputed slicing modifier;
5. persists `READY`.

The success effect is therefore durable before Roll.

### Roll / Resolve

Allowed only from `READY`.

One transaction:

1. re-authorize GM;
2. lock/load resolution;
3. revalidate referenced campaign data;
4. generate one natural D20;
5. calculate `natural + resolved_modifier >= dc`;
6. persist roll, total, outcome, rolled timestamp;
7. transition to `SUCCESS_PENDING_APPLY` or `FAILURE_PENDING_CLOSE`.

No canonical Knowledge mutation occurs here.

### Apply success

Allowed only for a successful resolution.

One transaction:

1. re-authorize GM;
2. lock/load resolution;
3. revalidate campaign references;
4. if already `CLOSED_SUCCESS`, return current result without adding another mutation/event;
5. reject any other terminal/incompatible state;
6. insert/update `CharacterKnowledge = AWARE`;
7. transition resolution to `CLOSED_SUCCESS`;
8. append `resolution.success_applied` DomainEvent;
9. commit once.

This makes retries/double-submit safe.

### Close failure

Allowed only from `FAILURE_PENDING_CLOSE`.

One transaction:

1. re-authorize GM;
2. lock/load resolution;
3. require non-empty concrete adjudication;
4. persist adjudication;
5. transition to `CLOSED_FAILURE`;
6. append `resolution.failure_closed` DomainEvent;
7. commit once.

A repeated identical Close may return the already closed result; changing a closed adjudication is not part of Slice 1.

## 9. Player projection

Player API returns a dedicated DTO built from:

- server-derived assignment;
- Character;
- Custom D20 profile;
- CharacterKnowledge;
- authorized KnowledgeFragment claim text.

It never returns:

- `gm_veracity`;
- hidden KnowledgeFragments;
- GM resolution data;
- canonical models followed by frontend redaction.

Before Apply, no CharacterKnowledge row exists and the claim is absent.

After Apply, `Aware` causes the claim to appear.

## 10. HTTP API contract

Prefix: `/api`.

Authentication:

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/logout`
- `GET /auth/me`

Campaign:

- `GET /campaigns`
- `POST /campaigns`
- `GET /campaigns/{campaign_id}/members`
- `POST /campaigns/{campaign_id}/members`

Slice content, GM only:

- `GET|POST /campaigns/{campaign_id}/characters`
- `GET|POST /campaigns/{campaign_id}/locations`
- `GET|POST /campaigns/{campaign_id}/knowledge-fragments`
- `PUT /campaigns/{campaign_id}/player-assignment`

Resolution, GM only:

- `POST /campaigns/{campaign_id}/resolutions`
- `GET /campaigns/{campaign_id}/resolutions/{resolution_id}`
- `POST /campaigns/{campaign_id}/resolutions/{resolution_id}/roll`
- `POST /campaigns/{campaign_id}/resolutions/{resolution_id}/apply`
- `POST /campaigns/{campaign_id}/resolutions/{resolution_id}/close-failure`

History, GM only:

- `GET /campaigns/{campaign_id}/history`

Player projection:

- `GET /player/campaigns/{campaign_id}/character`

The API uses JSON except the HttpOnly cookie transport.

## 11. Frontend boundaries

React owns:

- forms and display state;
- compact GM Slice 1 flow;
- Apply preview presentation;
- Player projection display;
- manual refresh/re-fetch.

React does not own:

- authorization;
- role truth;
- player assignment truth;
- outcome calculation;
- hidden-knowledge filtering;
- resolution lifecycle validation;
- idempotency.

No frontend router dependency is required for Slice 1; a small authenticated application state is sufficient.

## 12. Migrations

Alembic owns PostgreSQL schema changes.

Slice 1 starts with one explicit initial migration containing only the required tables, constraints, indexes, and check constraints.

Application startup does not call `metadata.create_all()` in normal runtime.

## 13. Testing

### Unit tests

- pure D20 calculation;
- password/JWT helpers;
- resolution transition guards where useful.

### PostgreSQL integration tests

Must prove the accepted test contract, including:

1. hidden claim absent before Apply;
2. claim visible after Apply;
3. GM/Player authorization server-side;
4. Player cannot call GM commands;
5. assignment server-authoritative;
6. cross-campaign reads rejected;
7. cross-campaign mutations rejected;
8. embedded cross-campaign references rejected;
9. Apply atomic;
10. repeated Apply safe;
11. rollback cannot split Knowledge/Resolution/History;
12. failed resolution can be adjudicated and closed;
13. reload reconstructs resolution and bound effect.

Additional tests:

- role is read from DB, not JWT/client input;
- GM veracity never appears in Player JSON;
- Close on success and Apply on failure are rejected;
- Roll is rejected after Roll/terminal state.

### E2E

One Playwright scenario covers:

- register GM and Player;
- GM creates campaign/content and assignment;
- Player confirms secret absent;
- GM resolves forced-success check and Applies;
- Player refreshes and sees claim.

A second short path covers forced failure and GM Close.

## 14. Current library baseline

Verified stable baseline at implementation start (2026-10-01):

Backend:

- Python 3.14
- FastAPI 0.142.2
- SQLAlchemy 2.0.54
- Alembic 1.20.0
- Pydantic 2.13.5
- psycopg 3.3.6
- PyJWT 2.15.1
- pwdlib 0.3.1
- Uvicorn 0.53.0
- pytest 9.1.1

Frontend:

- React 19.3.0
- Vite 8.3.1
- TypeScript 7.0.2
- @vitejs/plugin-react 6.1.1
- Playwright 1.63.0

Exact compatibility is verified by build/tests on the slice branch; prereleases are excluded.

## 15. Explicit non-design

Slice 1 does not add placeholders, nullable fields, interfaces, tables, or services for deferred capabilities.

In particular, it does not create:

- Session/Scene IDs on ActionResolution;
- generic effect payloads;
- generic rule expressions;
- outbox tables/workers;
- generator metadata;
- event subscribers for canonical mutations;
- generic undo/change-set storage;
- plugin/package runtime;
- realtime channels;
- generic combat fields.
