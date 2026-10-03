# Current Vertical Slice

## Slice 4 — GM Requests a Roll, Player Rolls, GM Adjudicates

**Status:** ACCEPTED  
**Accepted:** 2026-10-03  
**Owner:** Product Lead / Human Project Owner  
**Specification:** `docs/planning/slice-4-spec.md`

## Goal

Validate one bounded two-principal live-resolution workflow in which the GM defines the existing slicing ActionResolution, the assigned Player triggers the single authoritative backend Roll, and the GM retains the accepted Slice 3 Finalize / Override / Correct authority.

## Accepted scenario

```text
GM creates one PLAYER-authority slicing resolution
-> assigned Player sees a safe actionable request
-> Player triggers authoritative backend Roll
-> immutable mechanical result
-> GM reviews
-> GM Finalizes or Overrides
-> Slice 3 Correct outcome remains available
-> both sides converge without manual global Refresh
```

## Required Slice 4 contracts

- existing slicing mechanic only;
- `roll_authority = GM | PLAYER` on ActionResolution;
- existing/migrated rows default to `GM`;
- Slice 4 scenario uses `PLAYER`;
- only the assigned Player may Roll a PLAYER-authority resolution;
- GM cannot Roll a PLAYER-authority resolution;
- no `EITHER` authority mode;
- backend generates the authoritative d20;
- Player Roll request contains no die or mutable resolution-contract fields;
- exactly one raw roll may exist;
- Slice 3 mechanical evidence remains immutable;
- GM retains Finalize / Override / Correct;
- Intent is explicitly Player-visible for PLAYER-authority requests;
- `risk_visibility = GM_ONLY | PLAYER_VISIBLE`;
- hidden Risk is never inferred to be Player-visible;
- DC remains hidden from the Player;
- success effect/claim remains hidden before disclosure;
- dedicated Player-safe pending/current resolution projection;
- no structured Target / Subject requirement;
- Q-009 remains deferred;
- no manual global Refresh as intended live flow;
- bounded HTTP polling/re-fetch is sufficient for waiting states;
- no WebSockets/SSE/broker/notification platform;
- existing Contact Reveal remains independent of ActionResolution.

## Required API direction

Keep the GM endpoints, including the existing GM Roll path for `roll_authority = GM`.

Add the bounded Player workflow:

```text
GET  /api/player/campaigns/{campaign_id}/resolutions/pending
POST /api/player/campaigns/{campaign_id}/resolutions/{resolution_id}/roll
```

The Player Roll request body is empty and cannot supply:

- die;
- modifier;
- DC;
- actor;
- mechanic;
- Intent;
- Risk;
- final outcome;
- any other resolution mutation.

## Persistence direction

Narrowly evolve the existing ActionResolution with:

```text
roll_authority: GM | PLAYER
risk_visibility: GM_ONLY | PLAYER_VISIBLE
```

Do not add Request, Task, Invitation, Participant, Acknowledgement, Notification, Expiry, generic visibility rules or a second Resolution aggregate.

## Authorization

Player Roll authorization is backend-derived from:

```text
authenticated principal
-> PLAYER CampaignMembership
-> PlayerCharacterAssignment
-> same campaign
-> resolution actor == assigned Character
-> roll_authority == PLAYER
-> state == READY
```

Player cannot Finalize, Override or Correct.

## Freshness

Use immediate re-fetch after local mutation and bounded HTTP polling only while one side waits for the other.

The accepted Product target is approximately 2 seconds for polling during waiting states.

## Acceptance criteria

The normative acceptance criteria and test contract are defined in `docs/planning/slice-4-spec.md`.

At minimum implementation must prove:

- assigned Player sees the safe pending request;
- GM_ONLY Risk, DC and success claim do not leak;
- PLAYER_VISIBLE Risk appears;
- Player triggers one backend-authoritative Roll;
- duplicate/concurrent Player Roll produces one raw roll;
- Player cannot Roll GM-authority resolution;
- GM cannot Roll PLAYER-authority resolution;
- Slice 3 Finalize/Override/Correct remains intact;
- both override directions remain valid;
- Player/GM observe request, roll result and final outcome without global manual Refresh;
- campaign isolation and Player assignment remain server-authoritative;
- migration defaults existing rows to GM / GM_ONLY.

## Explicit Slice 4 exclusions

- multiple Players in one resolution;
- lead/assist;
- roll aggregation;
- opposed rolls;
- Player-authored resolutions;
- Player Finalize/Override/Correct;
- client-generated authoritative dice;
- physical-dice verification;
- request decline/acceptance;
- request expiry;
- generic Request/Task/Invitation framework;
- participant/acknowledgement tables;
- notifications platform;
- WebSockets/SSE;
- broker/worker;
- generic realtime infrastructure;
- generic visibility/ACL framework;
- universal Target / Subject;
- target_entity_id;
- generic ActionResolution engine;
- combat;
- rerolls;
- configurable Player DC visibility.

## Deferred questions

Only genuinely deferred questions remain in `docs/planning/open-questions.md`.

Deferred items are non-normative and must not be inferred as accepted Slice 4 requirements.
