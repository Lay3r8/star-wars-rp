# Slice 5 Proposed Specification — Escape the Imperial Patrol

**Status:** PROPOSED — CROSS-DOMAIN REVIEW REQUIRED  
**Owner:** Product Lead  
**Selected candidate:** Candidate B — Personal-Scale Combat Encounter  
**Implementation authorization:** NO  
**Current-slice impact:** NONE until explicit Human acceptance

This specification turns the reviewed and consolidated Candidate B contract in `docs/planning/slice-5-candidates.md` into the exact proposed Slice 5 normative contract.

It does **not** mark Slice 5 ACCEPTED.

---

# 1. Product goal

Prove one complete, objective-driven, personal-scale combat encounter that is genuinely playable end to end without building the complete combat system.

The slice must validate:

- repeated Player combat decisions;
- deterministic turn progression;
- backend-authoritative attack rolls;
- deterministic damage/state changes;
- encounter-scoped health;
- one abstract hostile group;
- objective-driven victory that does not require enemy elimination;
- GM pacing/authority without routine per-action adjudication;
- safe live Player/GM synchronization;
- combat-specific persistence that does not generalize the current Slicing ActionResolution.

The slice is successful if the Human functional test feels like one small but real combat encounter rather than a technical combat demo.

---

# 2. Exact combat scenario

Globox is cornered by one Imperial Patrol group in a bounded same-campaign Location.

Acceptance-fixture fiction:

> Globox is trying to escape an Imperial patrol before being incapacitated.

The exact Location is a persisted campaign Location selected by the GM when starting the encounter. The acceptance fixture may use a docking-bay Location.

The encounter starts with one primary objective:

> **Escape the Imperial Patrol.**

The encounter supports two Player choices:

```text
Attack the Patrol
or
Advance the Escape
```

The Patrol has one legal behavior:

```text
Attack Globox
```

The complete live sequence is:

```text
GM starts encounter
-> Round 1 / Globox turn
-> Player chooses Attack or Escape
-> action commits deterministic combat state
-> if terminal: encounter ends
-> otherwise current actor becomes Patrol
-> GM chooses Resolve Patrol Attack
-> attack commits deterministic combat state
-> if terminal: encounter ends
-> otherwise round increments and current actor returns to Globox
-> repeat until terminal
```

No other routine combat action is part of the accepted path.

---

# 3. Initial state

Before the GM starts the encounter:

- one campaign exists;
- one authenticated GM is a GM campaign member;
- one authenticated Player is a PLAYER campaign member;
- that Player is assigned to Globox through the existing `PlayerCharacterAssignment`;
- Globox exists as a same-campaign Character;
- one same-campaign Location exists for the encounter;
- there is no conflicting ACTIVE CombatEncounter for Globox.

When the GM starts the encounter, the backend initializes all Slice-5 tuning server-side.

## Globox tuning

```text
Attack Modifier: +3
Defence: 12
Combat Vitality initial/current: 4
Attack Damage: 2
```

## Imperial Patrol tuning

```text
Display name: Imperial Patrol
Attack Modifier: +2
Defence: 12
Group Strength initial/current: 4
Attack Damage: 2
```

## Escape tuning

```text
Escape Progress: 0
Escape Target: 3
```

## Encounter state

```text
status = ACTIVE
round = 1
current_actor = PLAYER
ended_at = null
objective = "Escape the Imperial Patrol"
```

These values are **Slice 5 encounter tuning only**.

They do not establish:

- final Custom D20 combat balance;
- permanent Character attack/defence statistics;
- permanent Character health;
- final weapon damage rules;
- a universal hostile-group scale.

---

# 4. Encounter objective

The primary objective is:

> **Escape the Imperial Patrol.**

The Player can achieve this objective in either of two ways:

```text
Escape Progress >= 3
OR
Imperial Patrol Group Strength <= 0
```

The Player loses the encounter when:

```text
Globox Combat Vitality <= 0
```

Enemy neutralization is therefore an **alternative path to escape**, not a mandatory "defeat every enemy" victory condition.

The encounter has no:

- secondary objectives;
- victory points;
- morale track;
- surrender system;
- timed round limit.

---

# 5. Actors and combatants

Slice 5 contains exactly two acting sides.

## Player side

One existing Character:

```text
Globox
```

Globox remains the Character assigned to the authenticated Player.

No generic Combatant entity/table is introduced.

## Hostile side

One encounter-scoped abstract hostile group:

```text
Imperial Patrol
```

The Patrol is not represented as:

- individual stormtrooper Characters;
- multiple NPC rows;
- per-minion combatants;
- a persistent campaign Entity unless a future slice explicitly requires that.

For Slice 5, the hostile unit exists only as state inside the CombatEncounter.

---

# 6. Turn order

Turn order is deterministic.

No initiative roll exists.

Exact order:

```text
Round 1:
  1. PLAYER / Globox
  2. PATROL

Round 2+:
  repeat the same order
```

## Start

```text
round = 1
current_actor = PLAYER
```

## After a non-terminal Player action

```text
current_actor = PATROL
round unchanged
```

## After a non-terminal Patrol action

```text
round += 1
current_actor = PLAYER
```

## On terminal transition

```text
current_actor = null
ended_at = now
```

If a Player action reaches a terminal threshold, the Patrol turn does not occur.

If a Patrol action incapacitates Globox, the next Player turn does not occur.

No:

- initiative score;
- initiative UI;
- phase system;
- End Turn command;
- turn skipping;
- delay/ready action.

---

# 7. Action economy

Each acting side receives exactly **one Action per turn**.

## Player legal actions

Exactly two:

1. **Attack**
2. **Escape**

The Player action itself consumes the turn.

## Patrol legal action

Exactly one:

1. **Attack Globox**

The Patrol action itself consumes the turn.

No:

- movement action;
- bonus action;
- free action;
- reaction;
- opportunity attack;
- multiple attacks;
- action points;
- action carry-over.

---

# 8. Attack / Defence rule

All combat attacks use the already-proven bounded D20 threshold shape:

```text
natural d20 + Attack Modifier >= Defence
=> HIT

otherwise
=> MISS
```

The d20 is generated by the backend.

The client never submits the natural roll.

## Globox attack

```text
backend d20 + 3
vs
Patrol Defence 12
```

## Patrol attack

```text
backend d20 + 2
vs
Globox Defence 12
```

## Natural 1 / 20

Natural 1 and natural 20 have no special meaning in Slice 5.

They are ordinary d20 values.

## Not part of Slice 5

No:

- opposed roll;
- defence roll;
- critical hit;
- fumble;
- degree of success;
- advantage/disadvantage;
- attack reroll;
- configurable attack modifiers;
- universal Defence formula.

`Defence` is a Slice-5 static combat threshold only.

---

# 9. Damage rule

Damage is fixed.

```text
HIT -> 2 damage
MISS -> 0 damage
```

Damage is not rolled.

Damage is applied synchronously in the same transaction as the attack result.

Damage cannot reduce health/strength below zero.

No:

- weapon-specific damage;
- armour reduction;
- resistance;
- damage type;
- critical multiplier;
- damage roll.

---

# 10. Health and incapacitation

Health is encounter-scoped only.

## Globox

```text
Combat Vitality initial = 4
Combat Vitality range = 0..4
```

When:

```text
Combat Vitality <= 0
```

then:

```text
status = INCAPACITATED
current_actor = null
ended_at = now
```

The encounter ends immediately.

`INCAPACITATED` means only:

> Globox cannot continue this encounter.

It does not define:

- death;
- unconscious duration;
- wounds;
- injuries;
- recovery;
- healing;
- persistent penalties.

The GM controls the subsequent fiction outside the bounded encounter state.

## Imperial Patrol

```text
Group Strength initial = 4
Group Strength range = 0..4
```

When:

```text
Group Strength <= 0
```

then:

```text
status = PATROL_NEUTRALIZED
current_actor = null
ended_at = now
```

The encounter ends immediately in Player victory.

Intermediate Group Strength values do not alter the Patrol's Attack Modifier, Defence or Damage.

---

# 11. Hostile-group behavior

The Imperial Patrol is one abstract hostile unit.

It has:

- one display name;
- one Attack Modifier;
- one Defence;
- one fixed Damage value;
- one Group Strength pool;
- one turn per round.

The Patrol has no tactical decision tree.

Exact behavior:

> if the encounter is ACTIVE and it is the Patrol turn, its only legal action is Attack Globox.

There is no NPC AI.

Product adopts the reviewed UX/Architecture pacing decision:

> The GM explicitly presses **Resolve Patrol Attack**.

The Patrol attack is **not** automatically chained after the Player action.

This preserves:

- GM pacing;
- clear user attribution;
- separate observable mutations;
- simple authorization;
- no System principal.

---

# 12. Range and position

Slice 5 has no range/position subsystem.

The scenario establishes fictionally that:

- Globox can attack the Patrol;
- the Patrol can attack Globox;
- Globox can spend an action advancing the escape objective.

`Escape Progress` is the only spatial abstraction required by this scenario.

Do not add:

- tactical grid;
- map coordinates;
- movement distance;
- range bands;
- cover;
- line of sight;
- engagement zones.

These remain future combat concerns only when a concrete action choice depends on them.

---

# 13. Player commands

Player commands exist only for the assigned Character and only on the Player turn.

Proposed API contract:

## Read current/latest encounter

```text
GET /api/player/campaigns/{campaign_id}/combat-encounters/latest
```

Returns the explicit Player-safe projection or null when no relevant encounter exists.

## Attack

```text
POST /api/player/campaigns/{campaign_id}/combat-encounters/{encounter_id}/attack
```

Request body:

```json
{
  "expected_round": 1
}
```

The Player does **not** supply:

- actor;
- target;
- die;
- modifier;
- Defence;
- damage;
- health;
- Group Strength;
- Escape Progress;
- next actor;
- status.

The target is server-derived as the one Patrol group.

### Player Attack transaction

```text
authorize Player + assignment
-> SELECT CombatEncounter FOR UPDATE
-> require ACTIVE
-> require current_actor = PLAYER
-> require expected_round = current round
-> backend d20
-> calculate total / HIT-MISS
-> if HIT: Patrol Strength -= 2, clamp at 0
-> if Patrol Strength == 0:
     status = PATROL_NEUTRALIZED
     current_actor = null
     ended_at = now
   else:
     current_actor = PATROL
-> append combat.player_attack_resolved history
-> commit atomically
```

## Escape

```text
POST /api/player/campaigns/{campaign_id}/combat-encounters/{encounter_id}/escape
```

Request body:

```json
{
  "expected_round": 1
}
```

### Player Escape transaction

```text
authorize Player + assignment
-> SELECT CombatEncounter FOR UPDATE
-> require ACTIVE
-> require current_actor = PLAYER
-> require expected_round = current round
-> Escape Progress += 1
-> if Escape Progress >= 3:
     status = ESCAPED
     current_actor = null
     ended_at = now
   else:
     current_actor = PATROL
-> append combat.escape_advanced history
-> commit atomically
```

Escape makes no d20 roll.

---

# 14. GM commands

## Start encounter

```text
POST /api/campaigns/{campaign_id}/combat-encounters
```

Request body:

```json
{
  "player_character_id": "<uuid>",
  "location_id": "<uuid>"
}
```

The client does not supply tuning values.

The backend creates the exact accepted Slice 5 scenario state.

Creation requires:

- GM membership;
- same-campaign Character;
- same-campaign Location;
- Character assigned to a PLAYER campaign member;
- no conflicting ACTIVE encounter for that Character.

## Read latest encounter

```text
GET /api/campaigns/{campaign_id}/combat-encounters/latest
```

Returns the GM combat projection.

## Resolve Patrol Attack

```text
POST /api/campaigns/{campaign_id}/combat-encounters/{encounter_id}/patrol-attack
```

Request body:

```json
{
  "expected_round": 1
}
```

### Patrol Attack transaction

```text
require GM
-> SELECT CombatEncounter FOR UPDATE
-> require ACTIVE
-> require current_actor = PATROL
-> require expected_round = current round
-> backend d20
-> calculate total / HIT-MISS
-> if HIT: Globox Vitality -= 2, clamp at 0
-> if Vitality == 0:
     status = INCAPACITATED
     current_actor = null
     ended_at = now
   else:
     round += 1
     current_actor = PLAYER
-> append combat.patrol_attack_resolved history
-> commit atomically
```

No manual End Encounter command.

No GM routine Finalize/Override.

No combat correction command in Slice 5.

---

# 15. Deterministic state changes

The following are mechanically complete and commit synchronously:

- authoritative attack d20;
- attack total;
- HIT/MISS;
- fixed damage;
- Combat Vitality reduction;
- Group Strength reduction;
- Escape Progress +1;
- round transition;
- current-actor transition;
- incapacitation threshold;
- patrol-neutralization threshold;
- escape threshold;
- terminal encounter status.

These are not consequence proposals.

They do not wait for GM confirmation.

This is consistent with D-004:

> bounded deterministic effects may be mechanically committed under an accepted policy.

---

# 16. GM adjudication boundaries

The GM retains final authority over fiction outside the accepted mechanical contract.

GM-adjudicated concerns include:

- whether an unusual fictional action outside Attack/Escape is possible;
- narrative description of attacks/hits/misses;
- interpretation of Globox's incapacitation after the encounter;
- consequences beyond CombatEncounter state;
- any edge case not represented by accepted commands.

Slice 5 does not add a generic "Other Action" command.

An unusual action is handled outside the bounded combat controls by GM authority.

Routine combat actions do not use Slice-3 `Finalize / Override / Correct`.

This does not supersede D-004.

---

# 17. Encounter persistence

Create one first-party combat-specific relational aggregate:

```text
CombatEncounter
```

Suggested table:

```text
combat_encounter
```

Minimum persisted fields:

- `id UUID PK`;
- `campaign_id`;
- `location_id`;
- `player_character_id`;
- `objective`;
- `status`;
- `round`;
- `current_actor`;
- `player_attack_modifier`;
- `player_defence`;
- `player_attack_damage`;
- `player_vitality_initial`;
- `player_vitality`;
- `hostile_name`;
- `patrol_attack_modifier`;
- `patrol_defence`;
- `patrol_attack_damage`;
- `patrol_strength_initial`;
- `patrol_strength`;
- `escape_progress`;
- `escape_target`;
- `created_by_principal_id`;
- `created_at`;
- `ended_at nullable`.

## Status vocabulary

Exactly:

```text
ACTIVE
ESCAPED
PATROL_NEUTRALIZED
INCAPACITATED
```

## Current actor vocabulary

Exactly:

```text
PLAYER
PATROL
NULL when terminal
```

## Required persistence invariants

- initial Vitality > 0;
- initial Group Strength > 0;
- Escape Target > 0;
- current Vitality between 0 and initial;
- current Strength between 0 and initial;
- Escape Progress between 0 and target;
- round >= 1;
- ACTIVE => current_actor non-null and ended_at null;
- terminal => current_actor null and ended_at non-null;
- ESCAPED => Escape Progress reached target;
- PATROL_NEUTRALIZED => Group Strength = 0;
- INCAPACITATED => Combat Vitality = 0.

A narrow partial uniqueness rule preventing more than one ACTIVE encounter for the same campaign + Player Character is allowed.

## Explicit architecture boundary

Do **not** alter or generalize Slicing `ActionResolution` for combat.

Do not add:

- generic Combatant;
- generic Scene;
- generic Encounter framework/builder;
- generic action-command table;
- generic workflow/state-machine framework;
- Rule Effect DSL;
- generic combat engine.

PostgreSQL remains the authoritative current state.

---

# 18. History

Combat current state is read from `CombatEncounter`.

Append-only `DomainEvent` history records significant combat actions.

Accepted event types:

```text
combat.player_attack_resolved
combat.escape_advanced
combat.patrol_attack_resolved
```

Player/Patrol attack event payload may include:

- encounter id;
- round;
- raw roll;
- modifier;
- total;
- Defence threshold;
- HIT/MISS;
- damage;
- health/strength before;
- health/strength after;
- terminal status if reached.

Escape event payload may include:

- encounter id;
- round;
- progress before;
- progress after;
- terminal status if reached.

State mutation and history append must commit atomically.

No `CombatAction` table is required.

No event sourcing.

No separate encounter-ended event is required.

---

# 19. Authorization and security

Backend authorization is authoritative.

## Encounter creation

Requires:

```text
authenticated principal
-> GM CampaignMembership
-> same-campaign Character
-> same-campaign Location
-> assigned PLAYER Character
```

## Player Attack/Escape

Requires:

```text
authenticated principal
-> PLAYER CampaignMembership
-> PlayerCharacterAssignment
-> encounter.player_character_id == assignment.character_id
-> same campaign
-> encounter.status == ACTIVE
-> encounter.current_actor == PLAYER
-> expected_round == encounter.round
```

## Patrol Attack

Requires:

```text
authenticated principal
-> GM CampaignMembership
-> same-campaign encounter
-> encounter.status == ACTIVE
-> encounter.current_actor == PATROL
-> expected_round == encounter.round
```

## Client-authoritative values forbidden

Player and GM clients cannot override through mutation payload:

- natural d20;
- Attack Modifier;
- Defence;
- Damage;
- Combat Vitality;
- Group Strength;
- Escape Progress;
- target;
- next actor;
- terminal status;
- encounter tuning.

Every entity/reference lookup is campaign-scoped.

Wrong-Player/cross-campaign requests must not leak hidden encounter existence beyond normal authorization/not-found semantics.

---

# 20. Concurrency and stale commands

Combat commands use PostgreSQL row locking on the CombatEncounter.

Every turn mutation carries:

```text
expected_round
```

The server also validates `current_actor`.

This is required because the Player becomes current actor again in later rounds.

Example stale request:

```text
Round 1 Player Attack is delayed
-> Round 1 already completed
-> Round 2 returns to PLAYER
-> delayed request still carries expected_round = 1
-> request is rejected / current state re-fetched
```

At-most-once state mutation is required.

No global idempotency-key framework is required.

While a mutation is pending, UI must prevent duplicate activation.

On stale/conflict response, the UI re-fetches current encounter state and presents an understandable message rather than technical revision terminology.

---

# 21. Player-safe read model

Canonical `CombatEncounter` must never be serialized directly to the Player client.

Use an explicit Player projection.

Minimum Player DTO:

- encounter id;
- objective;
- status;
- round;
- current actor;
- Player Character id/name;
- current/initial Combat Vitality;
- Patrol display name;
- current/initial Group Strength;
- Patrol status;
- Escape Progress / target;
- derived `can_attack`;
- derived `can_escape`;
- compact safe `last_action`.

## Derived legal actions

`can_attack` and `can_escape` are true only when:

- encounter is ACTIVE;
- current actor is PLAYER;
- authenticated Player owns the encounter Character.

## Last-action combat feedback

For the selected combat UX, `last_action` may expose attack feedback:

- acting side;
- raw d20;
- applicable modifier;
- total;
- Defence threshold;
- HIT/MISS;
- damage;
- before/after bounded Vitality or Strength;
- round;
- resulting terminal status if any.

Escape feedback may expose:

- progress before;
- progress after;
- resulting status.

This visibility is accepted specifically for this combat encounter.

It does not establish a universal policy that all hostile canonical stats must be Player-visible in future mechanics.

## GM projection

The GM projection may additionally expose the server-derived:

- `can_resolve_patrol_attack`.

The GM surface must not need to edit scenario tuning during the accepted path.

---

# 22. Live update / freshness strategy

No manual global Refresh is required for the intended combat workflow.

Use:

- immediate re-fetch after own mutation;
- immediate re-fetch after stale/conflict response;
- bounded HTTP polling while waiting for the other side;
- stop polling when the encounter is terminal.

Target cadence:

> approximately 1 second while actively waiting during combat.

This is a UX/implementation tuning target.

A bounded value near this target may be adjusted if testing shows a better balance.

No:

- WebSockets;
- SSE;
- message broker;
- background worker;
- push-notification subsystem.

The selected encounter has strictly sequential actions and does not justify realtime push infrastructure.

---

# 23. End conditions

Terminal conditions are deterministic and evaluated in the mutation that reaches the threshold.

## Escaped

```text
Escape Progress >= Escape Target
=> status = ESCAPED
```

## Patrol neutralized

```text
Patrol Group Strength <= 0
=> status = PATROL_NEUTRALIZED
```

## Incapacitated

```text
Globox Combat Vitality <= 0
=> status = INCAPACITATED
```

For all terminal states:

- `current_actor = null`;
- `ended_at = now`;
- no further combat action is legal;
- action controls disappear/disable;
- UI shows clear terminal feedback.

No separate GM confirmation is required.

---

# 24. UX contract

The combat surface must continuously show:

1. current actor;
2. objective / Escape Progress;
3. Globox Vitality;
4. Patrol Strength;
5. round;
6. latest action result.

## Player interaction cost

Routine common path:

```text
Attack -> one click
Escape -> one click
```

No:

- target selector;
- Intent;
- Risk;
- confirm modal;
- Roll button after choosing Attack;
- damage confirmation;
- End Turn.

If implementation technically separates action selection and d20 generation, the UX must still present Attack as one Player interaction.

## GM interaction cost

Routine hostile turn:

```text
Resolve Patrol Attack -> one click
```

No tactical choice menu.

## Pending state

While a mutation is in flight:

- disable relevant action controls;
- communicate pending state;
- prevent duplicate activation.

## Feedback examples

Player hit:

```text
Roll 14 + 3 = 17 vs Defence 12 — HIT
Patrol takes 2 damage
Group Strength 4 -> 2
```

Player miss:

```text
Roll 6 + 3 = 9 vs Defence 12 — MISS
No damage
```

Escape:

```text
Escape Progress 1 -> 2 / 3
```

Patrol hit:

```text
Patrol roll 13 + 2 = 15 vs Defence 12 — HIT
Globox takes 2 damage
Vitality 4 -> 2
```

Terminal UI:

- `Escaped`;
- `Patrol neutralized — escape secured`;
- `Incapacitated`.

---

# 25. Acceptance criteria

## Encounter creation

1. GM can start one combat encounter for assigned Globox at a same-campaign Location.
2. Backend initializes exact Slice 5 tuning server-side.
3. Client cannot submit/override tuning values.
4. Encounter starts ACTIVE, Round 1, Player turn.
5. A conflicting second ACTIVE encounter for the same Character is rejected.

## Player projection

6. Assigned Player sees the active encounter without global Refresh.
7. Wrong Player cannot read/use it.
8. Projection is explicit and does not serialize canonical model directly.
9. Objective, round, current actor, Vitality, Patrol Strength and Escape Progress are visible.
10. `can_attack` / `can_escape` are server-derived.
11. Player cannot use combat actions on Patrol turn or after terminal state.

## Player Attack

12. Attack is one Player interaction.
13. Player sends only `expected_round`.
14. Backend generates the d20.
15. `d20 + 3 >= 12` determines HIT/MISS.
16. Natural 1/20 receive no special behavior.
17. HIT applies exactly 2 damage.
18. MISS applies 0 damage.
19. Patrol Strength cannot fall below 0.
20. Non-terminal Attack changes turn to Patrol.
21. Patrol Strength 0 ends as PATROL_NEUTRALIZED.
22. No GM Finalize/Override is required.
23. Attack target is server-derived.

## Escape

24. Escape is one Player interaction.
25. Escape makes no d20 roll.
26. Escape Progress increases exactly by 1.
27. Non-terminal Escape changes turn to Patrol.
28. Progress 3 ends as ESCAPED.
29. No confirmation/Finalize is required.

## Patrol Attack

30. Only GM can Resolve Patrol Attack.
31. Command is legal only on Patrol turn and matching round.
32. Backend generates Patrol d20.
33. `d20 + 2 >= 12` determines HIT/MISS.
34. HIT applies exactly 2 damage.
35. MISS applies 0 damage.
36. Vitality cannot fall below 0.
37. Non-terminal Patrol Attack increments round and returns turn to Player.
38. Vitality 0 ends as INCAPACITATED.

## Deterministic terminal behavior

39. All terminal thresholds are applied in the triggering transaction.
40. Terminal encounter has null current actor and non-null ended_at.
41. No further combat action is legal after terminal.
42. No manual End Encounter command exists.

## Concurrency / stale state

43. Duplicate/concurrent Player Attack applies at most once.
44. Duplicate/concurrent Escape increments at most once.
45. Duplicate/concurrent Patrol Attack applies at most once.
46. Delayed stale command with previous `expected_round` is rejected even if the same actor becomes current again later.
47. UI re-fetches authoritative state after stale/conflict.

## History

48. Every committed combat action appends one bounded DomainEvent in the same transaction.
49. Reload reconstructs current combat state from CombatEncounter, not event replay.
50. Latest safe action feedback remains available after reload.

## Freshness

51. Player sees encounter start without manual global Refresh.
52. GM sees Player action/result without manual global Refresh.
53. Player sees Patrol resolution/next turn without manual global Refresh.
54. Polling stops when encounter is terminal.
55. No push/realtime infrastructure is required.

## Regression / boundaries

56. Existing Slicing ActionResolution remains unchanged for combat.
57. Slice 1-4 core workflows remain functional.
58. No permanent Character health field is introduced.
59. No generic Scene/Combatant/combat engine/rules DSL is introduced.
60. No grid/range/cover subsystem is introduced.

---

# 26. Testing strategy

The accepted post-Slice-4 development testing policy applies.

## Required backend rule/invariant tests

Cover:

- d20 + modifier vs Defence => HIT/MISS;
- natural 1/20 ordinary;
- HIT damage = 2;
- MISS damage = 0;
- damage clamps at 0;
- Escape increments exactly 1;
- Escape makes no roll;
- deterministic Player-first start;
- Player action -> Patrol;
- Patrol action -> next round Player;
- ESCAPED threshold;
- PATROL_NEUTRALIZED threshold;
- INCAPACITATED threshold;
- no action after terminal;
- required persistence invariants.

## Required backend security tests

Cover:

- non-member denied;
- wrong Player denied;
- Player assignment enforced;
- cross-campaign encounter rejected;
- Player only acts on Player turn;
- GM-only Patrol action;
- client cannot inject die/modifier/Defence/damage/health/progress/target/status/tuning;
- Player projection exposes only approved fields.

## Required integration/concurrency tests

Cover:

- Start Encounter transaction;
- full multi-turn encounter sequence;
- duplicate/concurrent Attack at most once;
- duplicate/concurrent Escape at most once;
- duplicate/concurrent Patrol attack at most once;
- stale `expected_round` rejected;
- action mutation + DomainEvent atomicity;
- state survives/reloads from PostgreSQL;
- safe `last_action` survives reload;
- terminal state cannot accept further commands.

## Frontend

Required:

- TypeScript typecheck;
- production build.

## Migration

Expected migration is additive:

- create `combat_encounter`;
- add FKs/checks/indexes;
- optional partial ACTIVE uniqueness index.

No existing mutable data needs transformation under the proposed contract.

Therefore:

> a dedicated populated-data migration test is not required by default.

Normal Alembic upgrade-to-head in CI remains required.

If implementation unexpectedly changes existing tables/data, Architecture must reassess migration-test risk.

## E2E

Normally require **one valuable combat happy path**.

Recommended deterministic-structure path:

```text
GM starts encounter
-> Player Escape
-> GM Resolve Patrol Attack
-> Player Escape if still active
-> GM Resolve Patrol Attack if still active
-> Player Escape if still active
-> accepted terminal state
```

Because Patrol attack rolls are random, the accepted terminal may be:

- INCAPACITATED before escape;
- or ESCAPED after Progress 3.

Playwright does not need to exhaust HIT/MISS/terminal/security matrices.

Those belong in backend tests.

## Human functional test

Mandatory before implementation PR merge.

The final Product acceptance before Human testing must supply a concrete functional test plan.

That Human test must assess at minimum:

- combat readability;
- pace;
- one-click routine actions;
- GM pacing with Resolve Patrol Attack;
- meaningful Attack-vs-Escape decision;
- no excessive bookkeeping;
- clear terminal outcome;
- no manual global Refresh dependency.

---

# 27. Explicit exclusions

Slice 5 does **not** include:

- initiative roll;
- initiative statistic;
- tactical map;
- VTT;
- grid;
- coordinates;
- exact movement;
- range bands;
- cover;
- line of sight;
- reactions;
- opportunity attacks;
- bonus/free actions;
- multiple attacks;
- multiple independent hostile groups;
- Player target selection;
- individual stormtrooper Character records;
- per-minion HP;
- armour system;
- weapon catalogue;
- weapon selection;
- weapon-specific damage;
- rolled damage;
- critical hits;
- fumbles;
- degrees of success;
- advantage/disadvantage;
- permanent Character health;
- wounds;
- injuries;
- death rules;
- healing/recovery;
- advanced status/condition system;
- Force powers;
- talents;
- progression;
- NPC AI;
- morale;
- surrender;
- unusual-action command palette;
- generic combat correction/Undo;
- generic encounter builder;
- generic Scene;
- Session introduced solely for combat;
- generic Combatant table;
- generic action command model;
- generic state-machine/workflow engine;
- generic combat engine;
- Rule Effect DSL;
- combat represented through Slicing ActionResolution;
- universal Target/Subject model;
- WebSockets;
- SSE;
- broker/worker;
- microservices;
- distributed cache.

---

# 28. Cross-domain review focus

This exact specification is proposed from the already-consolidated Candidate B reviews.

Cross-domain reviewers should challenge only whether this spec faithfully encodes those reviewed contracts and whether any exact API/persistence/security detail introduces a material contradiction.

A second design loop is **not** expected unless review identifies a material dependency affecting another domain.

Key review checks:

## Game Design

- exact numeric tuning matches reviewed scenario;
- deterministic effects do not overstep GM authority;
- no excluded combat mechanic slipped into the spec;
- encounter-scoped health remains explicitly non-universal.

## UX

- Attack/Escape remain one-click routine actions;
- GM Patrol action remains one compact action;
- always-visible combat information is sufficient;
- no unnecessary confirmations/forms;
- feedback and stale-state behavior are understandable.

## Architecture

- CombatEncounter remains combat-specific and relational;
- no ActionResolution generalization;
- server-authoritative transitions/tuning;
- row locking + expected_round correctly bounds concurrency;
- explicit Player projection;
- DomainEvent remains history, not source of current state;
- no unnecessary platform abstraction.

---

# 29. Acceptance gate

This specification is:

**PROPOSED — CROSS-DOMAIN REVIEW REQUIRED**

It is not ACCEPTED.

Until explicit Human acceptance after review:

- do not modify `docs/planning/current-slice.md`;
- do not add a Slice 5 ACCEPTED decision;
- do not begin implementation;
- do not create implementation migrations/code from this proposal as if normative.

After reviews are complete, Product will consolidate only material changes or arbitrations.

If no material blocker remains, the Human Project Owner may explicitly accept Slice 5, after which the normative planning documents can be finalized in the repository.
