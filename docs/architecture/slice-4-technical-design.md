# Slice 4 Technical Design — GM Requests a Roll, Player Rolls, GM Adjudicates

Status: IMPLEMENTATION BASELINE  
Owner: Principal Software Architect / Lead Developer  
Slice contract: `docs/planning/slice-4-spec.md`

## Scope

Slice 4 narrowly extends the existing slicing-specific `ActionResolution` so that one assigned Player may trigger the single authoritative backend Roll for a GM-authored resolution.

It does not generalize ActionResolution, add group participation, or introduce realtime infrastructure.

## Persistent model

`ActionResolution` adds exactly two first-party fields:

- `roll_authority: GM | PLAYER`;
- `risk_visibility: GM_ONLY | PLAYER_VISIBLE`.

Migration defaults all existing rows to:

- `roll_authority = GM`;
- `risk_visibility = GM_ONLY`.

Existing workflow state remains unchanged:

- `READY`;
- `AWAITING_ADJUDICATION`;
- `FINALIZED`.

No Request, Task, Participant, Notification, Expiry or Target/Subject table is introduced.

## Roll transaction

GM and Player paths use one shared one-shot mechanical operation after different authorization checks.

### GM authority

The existing GM endpoint remains valid only when:

```text
roll_authority = GM
```

### Player authority

Player Roll authorization is derived server-side:

```text
authenticated principal
-> PLAYER CampaignMembership
-> PlayerCharacterAssignment
-> same campaign
-> resolution actor == assigned Character
-> roll_authority = PLAYER
```

The Player command accepts an empty HTTP body only.

The shared transaction:

1. locks the ActionResolution row;
2. returns existing mechanical evidence for a duplicate already-rolled request;
3. otherwise requires READY;
4. validates same-campaign bound references;
5. generates one backend d20;
6. calculates total and mechanical result using the existing Custom D20 rule;
7. persists immutable evidence;
8. transitions to AWAITING_ADJUDICATION;
9. commits once.

No DomainEvent is added for Roll.

## Player pending/current projection

`GET /api/player/campaigns/{campaign_id}/resolutions/pending` derives the assigned Character server-side and returns only the latest non-finalized PLAYER-authority resolution for that Character.

READY projection:

- resolution id;
- actor id/name;
- display mechanic;
- Location id/name;
- Intent;
- Risk only when `risk_visibility = PLAYER_VISIBLE`;
- state.

AWAITING_ADJUDICATION additionally includes:

- natural d20;
- resolved modifier;
- total;
- mechanical result.

It never includes:

- DC;
- GM-only Risk;
- Risk visibility metadata;
- success fragment/claim;
- gm_veracity;
- finalization/correction controls or reasons;
- canonical Resolution DTO fields not explicitly required.

Finalized state continues to use the Slice 3 Player-safe projection.

## Freshness

No global Refresh is required for the Slice 4 live path.

- the Player surface polls the bounded pending/current read model at approximately two-second intervals while waiting for request/result/finalization;
- Player Roll immediately re-fetches authoritative state after mutation or network uncertainty;
- the GM resolution surface polls only while a PLAYER-authority resolution is READY;
- polling stops after the relevant waiting stage is left.

No WebSocket, SSE, broker, worker or notification subsystem is introduced.

## Frontend

The existing GM Resolution workspace adds:

- Roll authority selection;
- Risk visibility selection;
- explicit warning that Intent is Player-visible for Player Roll requests;
- waiting-for-Player state;
- hidden GM Roll control for PLAYER authority.

The Player resolution panel adds one actionable pending request card, then becomes read-only after Roll and reuses the finalized Slice 3 summary after adjudication.

## Explicit non-design

No:

- generic ActionResolution framework;
- Target/Subject field;
- request/task/invitation model;
- participant/acknowledgement model;
- decline/expiry workflow;
- group roll;
- Player-authored resolution;
- Player Finalize/Override/Correct;
- client-authoritative dice;
- generic visibility/ACL framework;
- WebSocket/SSE;
- broker/worker;
- event-driven RPC;
- combat;
- reroll mechanics.

## Tests

Slice 4 verification covers:

- migration defaults;
- safe pending Player projection;
- explicit Risk visibility;
- Player Roll authz;
- GM/Player roll-authority separation;
- empty Player Roll command;
- backend-authoritative dice;
- duplicate/concurrent one-shot Roll behavior;
- mechanical-evidence immutability;
- Slice 3 override/finalization regression;
- two-browser polling flow without global Refresh;
- hidden Risk/DC/success-claim leakage prevention;
- existing Slice 1–3 regression suite.
