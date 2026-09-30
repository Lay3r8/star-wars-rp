# ADR-001 — Entity identity registry and extension data

## Status

ACCEPTED

## Context

The platform needs stable first-party domain models while also allowing campaign/setting extensions to attach structured data without requiring plugin-specific SQL migrations.

## Decision

`Entity` is an identity registry scoped by `campaign_id`.

Stable first-party domain concepts use typed relational tables.

Dynamic extension-owned data is stored separately in `EntityExtensionData` and must include:

- `entity_id`
- `namespace`
- `schema_id`
- `schema_version`
- `payload` as JSONB

`Entity` itself must not become a generic untyped property bag.

All entity references remain campaign-scoped.

## Consequences

- Core queries retain relational integrity and readable schemas.
- Extensions can evolve data independently of core tables.
- Application validation must validate extension payloads against their declared schema/version.
- JSONB does not remove the need for explicit data migrations when an extension schema changes.

## Alternatives considered

- One large JSONB document on `Entity`: rejected because it weakens domain ownership and queryability.
- EAV storage: rejected because it adds complexity and poor type semantics.
- SQL tables created dynamically by plugins: rejected for MVP operational simplicity.
