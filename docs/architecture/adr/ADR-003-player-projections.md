# ADR-003 — Explicit player-facing projections

## Status

ACCEPTED

## Context

Canonical campaign objects may contain GM-only information, hidden relationships, true identities, and facts that differ from what a player character believes.

## Decision

Player-facing endpoints return explicit projection/read-model DTOs.

Canonical persistence/domain models are not serialized directly to player clients and then filtered in the frontend.

Projection construction must apply:

- actor authorization;
- `campaign_id` isolation;
- character ownership/membership rules;
- knowledge visibility rules;
- any additional UX/game-design disclosure rules.

## Consequences

- Security does not depend on the frontend hiding fields.
- A player view can intentionally differ from canonical GM reality.
- Read models may duplicate some shape definitions, which is accepted to keep disclosure explicit.
- UX defines required player-visible information; Architecture defines the safe projection boundary.

## Alternatives considered

- Serialize canonical objects and redact fields ad hoc: rejected because omission errors can leak GM information.
- Frontend-only visibility: rejected because it is not an authorization boundary.
