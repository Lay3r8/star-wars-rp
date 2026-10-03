# Slice 4 Specification — GM Requests a Roll, Player Rolls, GM Adjudicates

**Status:** ACCEPTED  
**Owner:** Product Lead  
**Selection:** Candidate A from `docs/planning/slice-4-candidates.md`  
**Implementation authorization:** YES after merge of this PR  
**Accepted:** 2026-10-03

This specification consolidates the completed Game Design, UX and Architecture reviews of PR #17 and was explicitly accepted by the Human Project Owner on 2026-10-03.

After this PR is merged to `main`, this document is the normative Slice 4 contract and implementation may begin on a separate Architecture branch.

---

# 1. Goal

Prove one bounded two-principal live-resolution workflow:

```text
GM creates one Player-roll slicing resolution
-> assigned Player sees a safe actionable request
-> Player triggers the single authoritative backend Roll
-> immutable mechanical result
-> GM reviews
-> GM Finalizes or Overrides
-> existing Slice 3 Correct outcome remains available
-> both sides converge on current state without global manual Refresh
```

The slice changes **who may trigger Roll**.

It does not change:

- the slicing mechanic;
- backend-authoritative randomness;
- immutable mechanical evidence;
- GM final adjudication authority;
- correction/supersession semantics;
- the pre-bound success effect.

---

# 2. Exact user scenario

Globox has already chosen, in the fiction, to slice the Imperial Cargo Terminal.

The GM prepares the existing bounded slicing resolution:

- actor: Globox;
- context: Imperial Cargo Terminal;
- mechanic: slicing;
- Intent: one Player-safe description of the attempted action;
- Risk: one concrete GM-side risk;
- Risk visibility: GM_ONLY or PLAYER_VISIBLE;
- DC;
- resolved slicing modifier;
- success recipient = Globox;
- success KnowledgeFragment;
- roll authority = PLAYER.

The Player opens their existing campaign workspace and sees one actionable pending-roll card.

Example Player-safe request:

```text
Globox
Slicing — Imperial Cargo Terminal

Action:
Obtain information about Senator Traitrus.

Known stakes:
Vic may realize you are investigating him.   // only when explicitly PLAYER_VISIBLE

[ Roll ]
```

The Player presses **Roll**.

The browser sends no die value.

The backend generates exactly one d20 using the existing Slice 3 Roll logic.

After Roll:

- the Player sees the immutable mechanical evidence;
- the GM sees the same mechanical evidence;
- only the GM may Finalize / Override / Correct.

---

# 3. Initial state

Before creation:

- one campaign exists;
- one authenticated GM is a GM campaign member;
- one authenticated Player is a PLAYER campaign member;
- the Player is assigned server-side to Globox;
- Globox has a slicing modifier;
- the context Location exists in the same campaign;
- the success KnowledgeFragment exists in the same campaign.

The GM creates the resolution using the existing slicing creation flow plus:

```text
roll_authority = PLAYER
risk_visibility = GM_ONLY | PLAYER_VISIBLE
```

No Player-authored ActionResolution is introduced.

---

# 4. Roll-authority contract

## Existing GM workflow must remain valid

Slice 4 must not silently turn every READY ActionResolution into a Player request.

Add one bounded first-party field on the existing ActionResolution:

```text
roll_authority = GM | PLAYER
```

Existing and migrated Slice 1-3 rows are:

```text
roll_authority = GM
```

Slice 4's accepted scenario creates:

```text
roll_authority = PLAYER
```

## PLAYER authority means only Roll trigger authority

For `roll_authority = PLAYER`, the assigned Player may trigger generation of the one authoritative raw roll.

The Player may not change:

- actor;
- context Location;
- Intent;
- Risk;
- Risk visibility;
- mechanic;
- modifier;
- DC;
- success recipient;
- success fragment;
- raw die value;
- final outcome;
- failure adjudication;
- override reason;
- correction reason.

## GM authority on a Player request

For this bounded slice:

> the GM may **not** trigger Roll on a `roll_authority = PLAYER` resolution.

Reason:

- the user value being tested is direct Player mechanical agency;
- it avoids an unnecessary GM-vs-Player Roll race;
- it keeps authorization semantics exact;
- the existing `roll_authority = GM` path remains available for tables where the GM should roll.

If the table wants the GM to roll instead, the GM creates a GM-authority resolution.

No `EITHER` mode is introduced.

---

# 5. Exactly-one-roll contract

The accepted Slice 3 mechanical contract remains unchanged.

For a Player-authority resolution:

```text
READY
-> Player Roll command
-> backend-generated d20
-> AWAITING_ADJUDICATION
```

Exactly one raw roll may exist.

Duplicate/concurrent Player requests use the existing row lock and one-shot semantics:

- first valid transaction creates the roll;
- later requests observe the already-rolled state;
- no second d20 is generated.

Player-side Roll does not create a new dice mechanic.

---

# 6. Player-visible pre-roll request

## Dedicated safe projection

The Player must not receive the canonical GM `ResolutionOut`.

A dedicated pre-roll/read model exposes only the fields required to understand the request.

Minimum fields:

- resolution id;
- acting Character id/name;
- mechanic display name;
- context Location id/name;
- Intent;
- known Risk/stakes only when explicitly marked PLAYER_VISIBLE;
- request state.

It must not expose:

- DC;
- hidden Risk;
- resolved modifier before Roll unless Game Design/UX later explicitly requires it;
- success fragment or success-preview claim;
- gm_veracity;
- GM notes;
- adjudication fields before they exist;
- arbitrary canonical resolution fields.

## Intent visibility

For `roll_authority = PLAYER`, the GM-facing creation UX must make explicit that **Intent is Player-visible**.

The GM must not place hidden information in this field for a Player request.

No second `player_intent` field is introduced.

---

# 7. Risk / stakes visibility

The current `risk` field remains the concrete GM-side Risk used by the Slice 3 failure path.

Slice 4 adds one bounded visibility field:

```text
risk_visibility = GM_ONLY | PLAYER_VISIBLE
```

Default:

```text
GM_ONLY
```

For Player-authority resolutions:

- `PLAYER_VISIBLE` => the pending request shows the Risk as known stakes;
- `GM_ONLY` => the pending request omits it completely.

The frontend must never infer visibility from the presence of Risk text.

This does not establish a generic field-level visibility framework.

---

# 8. Target / Subject

Slice 4 does **not** resolve Q-009.

No new Target / Subject persistence is required.

The pending Player request must be understandable using:

- actor;
- mechanic;
- context Location;
- Player-visible Intent;
- optionally Player-visible Risk.

If a future mechanic requires a durable mechanical target or fictional subject, that future slice must define its own semantics.

Q-009 remains OPEN — DEFERRED.

---

# 9. Player flow

The common Player path is intentionally minimal:

```text
pending request appears
-> Player reads action/context/known stakes
-> Roll
-> mechanical evidence appears
-> wait for GM adjudication
-> finalized result appears
```

No:

- Accept Request;
- Confirm Roll modal;
- Submit Result step;
- decline flow;
- expiry flow;
- notification inbox.

After Roll, the Player is read-only for that resolution.

---

# 10. GM flow

The GM uses the existing resolution creation surface with:

- Roll authority choice;
- Risk visibility choice.

For a Player-authority request:

```text
Create resolution
-> waiting for Player Roll
-> mechanical result appears
-> Slice 3 Finalize / Override
-> optional later Correct outcome
```

The GM must not see an enabled Roll action for a Player-authority resolution.

The Slice 3 adjudication UX remains otherwise unchanged.

---

# 11. Freshness contract

Manual global Refresh is **not** the intended live workflow.

No push/realtime transport is required.

Use:

- immediate re-fetch after the current user performs a mutation;
- bounded HTTP polling while one side is waiting for the other side.

Product requirement:

> under normal operation, a pending request, submitted mechanical result, and final adjudication should become visible to the waiting party without manual global Refresh and within a short live-play interval.

For Slice 4, bounded polling at approximately 2 seconds is sufficient.

Polling should run only while the relevant resolution is in a waiting state and stop when:

- state changes to the next non-waiting stage;
- the component unmounts;
- campaign changes.

No WebSockets, SSE, broker or notification platform.

---

# 12. Player-visible post-Roll / finalized state

After Player Roll but before GM Finalize, Player sees:

- raw d20;
- resolved modifier;
- total;
- mechanical result;
- waiting-for-GM status.

Still hidden:

- DC;
- hidden Risk;
- success effect;
- GM adjudication controls.

After Finalize, reuse the accepted Slice 3 Player-safe semantics:

- raw d20;
- modifier;
- total;
- mechanical result;
- current final outcome;
- overridden marker;
- corrected marker;
- compact previous outcome where already accepted.

No DC or GM reasons become visible.

---

# 13. Data / persistence contract

Narrowly evolve existing `ActionResolution`.

Add:

```text
roll_authority: GM | PLAYER
risk_visibility: GM_ONLY | PLAYER_VISIBLE
```

No new aggregate/table is required.

Do not add:

- Request;
- Task;
- Invitation;
- Participant;
- Acknowledgement;
- Notification;
- Expiry;
- generic visibility rule tables.

Existing state remains:

```text
READY
AWAITING_ADJUDICATION
FINALIZED
```

A READY + PLAYER resolution is the pending Player roll request.

---

# 14. API / command contract

## GM create

Existing GM endpoint remains:

```text
POST /api/campaigns/{campaign_id}/resolutions
```

Creation accepts the two new bounded fields:

```text
roll_authority
risk_visibility
```

Existing clients/legacy behavior default to:

```text
roll_authority = GM
risk_visibility = GM_ONLY
```

## GM Roll

Existing:

```text
POST /api/campaigns/{campaign_id}/resolutions/{resolution_id}/roll
```

remains GM-only and is valid only when:

```text
roll_authority = GM
```

For PLAYER authority, return an understandable conflict/forbidden domain error.

## Player pending/current request

Add a dedicated safe read endpoint, conceptually:

```text
GET /api/player/campaigns/{campaign_id}/resolutions/pending
```

It returns the latest eligible non-finalized PLAYER-authority resolution for the assigned Character, or null.

The endpoint may return:

- READY pending request;
- AWAITING_ADJUDICATION waiting-for-GM state.

FINALIZED continues to use the accepted Slice 3 finalized projection.

## Player Roll

Add:

```text
POST /api/player/campaigns/{campaign_id}/resolutions/{resolution_id}/roll
```

Request body:

```text
empty
```

The endpoint must not accept:

- die;
- modifier;
- DC;
- actor;
- mechanic;
- Intent;
- Risk;
- final outcome;
- any resolution-contract mutation.

The application service reuses the same backend Roll implementation after a different authorization check.

---

# 15. Authorization / security contract

Player Roll authorization derives server-side:

```text
authenticated principal
-> PLAYER CampaignMembership
-> PlayerCharacterAssignment
-> same campaign
-> resolution.actor_character_id == assigned Character
-> resolution.roll_authority == PLAYER
-> resolution.state == READY
```

No client-supplied Character identity is authoritative.

A Player cannot:

- read another Character's pending request;
- Roll another Character's resolution;
- Roll GM-authority resolution;
- Roll after the one roll already exists;
- Finalize;
- Override;
- Correct;
- inspect DC;
- inspect GM-only Risk;
- inspect success effect/claim before disclosure.

Campaign isolation remains strict for every embedded reference.

---

# 16. Transaction boundary

Both GM-authority and Player-authority Roll paths call one shared domain operation after authorization.

Player Roll transaction:

```text
authorize eligible Player
-> SELECT ActionResolution FOR UPDATE
-> require READY
-> require roll_authority = PLAYER
-> validate bound same-campaign references
-> generate backend d20 exactly once
-> calculate total/mechanical result
-> persist immutable evidence
-> state = AWAITING_ADJUDICATION
-> commit
```

No canonical success/failure consequence occurs at Roll.

Finalize/Override/Correct remain the accepted Slice 3 transactions.

---

# 17. History / DomainEvent

No new DomainEvent is required merely because the Player triggered Roll.

Slice 3 behavior remains:

- Roll changes current resolution state;
- Finalize appends `resolution.adjudication_finalized`;
- Correct appends `resolution.adjudication_corrected`.

If later Product requirements need "who rolled" as meaningful history, that must be justified separately.

Do not introduce a generic command/audit event framework.

---

# 18. Migration expectations

One small Alembic migration is expected.

For existing rows:

```text
roll_authority = GM
risk_visibility = GM_ONLY
```

Both columns should be non-null after migration.

No other Slice 3 mechanical/adjudication data is rewritten.

No migration for Target / Subject.

No new table.

---

# 19. Error / stale-state behavior

## Already rolled

If the Player attempts Roll after the authoritative roll exists:

- do not generate another die;
- return current safe state or an understandable already-rolled response;
- UI replaces Roll with current result/status.

## Network uncertainty

If the Player does not know whether Roll succeeded due to a network error:

- re-fetch authoritative pending/current resolution state;
- only show Roll again if backend still says READY.

## Wrong Player / campaign

Return normal authorization/not-found behavior without revealing hidden campaign information.

## GM attempts Player-authority Roll

Do not silently roll.

UI should not offer the action; backend still rejects it.

---

# 20. Acceptance criteria

## Creation / request

1. GM can create a slicing ActionResolution with `roll_authority = PLAYER`.
2. Existing GM-authority creation remains supported.
3. PLAYER request requires an actor currently assigned to a Player Character under the existing Slice contract.
4. Intent is stored and projected as Player-visible request text.
5. Risk visibility is explicit and defaults GM_ONLY.

## Pending Player projection

6. Assigned Player sees their eligible READY PLAYER-authority resolution.
7. Another Player does not see it.
8. Non-member does not see it.
9. Projection includes actor, mechanic, context and Intent.
10. PLAYER_VISIBLE Risk appears.
11. GM_ONLY Risk does not appear.
12. DC does not appear.
13. success fragment/claim does not appear.
14. arbitrary canonical resolution fields do not leak.

## Player Roll

15. Assigned Player can Roll an eligible PLAYER-authority READY resolution.
16. Player Roll request contains no authoritative die value.
17. Backend generates natural d20.
18. Existing Slice 3 mechanical calculation is unchanged.
19. Exactly one raw roll is persisted.
20. Duplicate Player Roll does not create another die.
21. Concurrent duplicate Player Rolls create one result.
22. Player cannot Roll a GM-authority resolution.
23. GM cannot Roll a PLAYER-authority resolution.
24. Player cannot Roll another Character's resolution.
25. Player cannot change actor/mechanic/modifier/DC/Intent/Risk/effect via Roll.

## Post-Roll

26. State becomes AWAITING_ADJUDICATION.
27. Player sees raw d20, modifier, total and mechanical result.
28. Player cannot Roll again.
29. Player cannot Finalize/Override/Correct.
30. GM sees the same mechanical evidence.
31. GM Finalize/Override behavior remains Slice 3 compliant.

## Final / correction regression

32. mechanical FAILURE -> final SUCCESS remains supported.
33. mechanical SUCCESS -> final FAILURE remains supported.
34. raw/mechanical evidence remains immutable.
35. Correct outcome remains GM-only.
36. supersession and irreversible-disclosure behavior remain unchanged.
37. finalized Player projection remains Slice 3-safe.

## Freshness

38. Player request appears without manual global Refresh.
39. GM sees Player Roll result without manual global Refresh.
40. Player sees GM Finalize outcome without manual global Refresh.
41. bounded polling stops when no waiting state remains.
42. no push/realtime infrastructure is required.

## Regression / scope

43. Contact Reveal remains independent from ActionResolution.
44. existing GM-only Slice 3 Roll path remains valid for GM-authority resolutions.
45. no generic Request/Task/Participant/Notification model exists.
46. no Target/Subject field is introduced.
47. no client-authoritative dice exists.
48. no multi-Player/group semantics exists.
49. no generic realtime transport is introduced.
50. no generic ActionResolution engine is introduced.

---

# 21. Test contract

## PostgreSQL integration tests

Must cover:

- migration defaults for existing rows;
- PLAYER vs GM roll authority;
- Risk visibility persistence;
- assigned Player pending projection;
- hidden Risk/DC/success effect non-leakage;
- PLAYER_VISIBLE Risk visibility;
- Player Roll authorization;
- wrong Player/campaign rejection;
- GM rejected on PLAYER Roll;
- Player rejected on GM Roll;
- duplicate/concurrent Player Roll one-shot behavior;
- immutable mechanical evidence;
- Slice 3 Finalize/Override/Correct regressions.

## Frontend / E2E

At minimum one two-browser Playwright scenario:

```text
GM creates PLAYER-authority slicing request
-> Player sees request without global Refresh
-> request shows safe action context
-> Player clicks Roll
-> backend result appears Player-side
-> GM sees same result without global Refresh
-> GM overrides or finalizes
-> Player sees final outcome without global Refresh
```

A second E2E/security path proves:

- GM_ONLY Risk hidden;
- DC hidden;
- Player cannot use GM mutation controls.

At least one E2E should exercise an override after Player-triggered Roll to prove Slice 3 adjudication remains intact.

CI must not depend on external realtime services.

---

# 22. Explicit exclusions

Slice 4 does not include:

- multiple Players in one resolution;
- collaborative lead/assist;
- roll aggregation;
- opposed rolls;
- Player-authored resolutions;
- Player Finalize/Override/Correct;
- client-generated authoritative dice;
- physical-dice verification;
- request acceptance/decline workflow;
- request expiry;
- generic Request/Task/Invitation model;
- participant table;
- acknowledgement tracking;
- notification center;
- push notifications;
- WebSockets;
- SSE;
- broker/worker;
- generic realtime infrastructure;
- generic visibility/ACL framework;
- universal Target/Subject;
- target_entity_id;
- generic ActionResolution engine;
- combat;
- rerolls;
- configurable Player DC visibility.

---

# 23. Review disagreements and Product dispositions

## Roll eligibility representation

**FACT**

Architecture identified two valid bounded implementations: every READY resolution Player-eligible, or one explicit authority field.

**DOMAIN OWNER POSITION**

Architecture prefers zero schema change only if every READY resolution is semantically a Player request. Game Design and UX require a clear distinction between Player-requested and other workflows.

**PRODUCT IMPACT**

Preserve existing GM-only Roll behavior and add explicit `roll_authority = GM | PLAYER`.

**HUMAN DECISION REQUIRED: NO**

---

## Whether GM may Roll a Player request

**FACT**

Game Design permits either Product choice if exactly one authoritative roll exists. UX identifies concurrency as extra complexity. Architecture can support either.

**PRODUCT IMPACT**

For the selected Player-agency hypothesis, PLAYER-authority means only the Player may trigger Roll. GM-only rolling remains available through GM-authority resolutions.

This removes unnecessary race semantics and avoids adding an EITHER mode.

**HUMAN DECISION REQUIRED: NO**

---

## Player-visible stakes

**FACT**

Game Design requires fictionally known stakes to be showable while preserving hidden consequences. UX warns against projecting canonical Risk automatically. Architecture requires an explicit safe projection.

**PRODUCT IMPACT**

Keep existing Risk and add bounded `risk_visibility = GM_ONLY | PLAYER_VISIBLE`.

No generic visibility framework.

**HUMAN DECISION REQUIRED: NO**

---

## Structured Target / Subject

**FACT**

All three reviews agree Candidate A does not require a universal structured target.

**PRODUCT IMPACT**

No Target/Subject field. Q-009 remains deferred. Player request uses human-readable existing context.

**HUMAN DECISION REQUIRED: NO**

---

## Freshness transport

**FACT**

UX requires no manual global Refresh as intended flow. Architecture confirms bounded HTTP polling is sufficient.

**PRODUCT IMPACT**

Use bounded polling/re-fetch; do not add WebSockets/SSE.

**HUMAN DECISION REQUIRED: NO**

---

## Decline / expiry

**FACT**

Game Design and UX do not require either for the bounded scenario.

**PRODUCT IMPACT**

Both deferred.

**HUMAN DECISION REQUIRED: NO**

---

# 24. Human arbitration

**NO MATERIAL HUMAN ARBITRATION REMAINS**

The three domain reviews converge on a bounded contract, and the remaining choices have been resolved by Product without changing the Human-selected Product direction.

---

# 25. Implementation gate

**Slice 4 is ACCEPTED.**

Implementation remains blocked only until this normative PR is merged to `main`.

After merge:

- `docs/planning/current-slice.md` identifies Slice 4 as the current accepted slice;
- `docs/planning/decision-log.md` records D-008 as ACCEPTED;
- implementation may begin on a separate short-lived Architecture branch;
- all explicit exclusions and security constraints in this specification remain binding.
