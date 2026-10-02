# Slice 3 Final Proposed Specification — Roll, Review and Adjudicate

**Status:** PROPOSED — READY FOR HUMAN ACCEPTANCE  
**Owner:** Product Lead  
**Selection source:** `docs/planning/slice-3-candidates.md`  
**Implementation authorization:** NO  
**Current-slice impact:** NONE until Human acceptance

This specification consolidates the completed Game Design, UX and Architecture reviews of PR #15.

It is final at Product level, but Slice 3 is **not ACCEPTED** until the Human Project Owner explicitly approves it.

---

# 1. Exact user scenario

Slice 3 reuses the existing Slice-1 slicing scenario.

No second mechanic is introduced.

Kara Venn attempts to slice an Imperial Cargo Terminal to discover where a confiscated shipment was transferred.

The bounded resolution contract is:

```text
Intent + Risk + slicing mechanic + DC + pre-bound success effect
-> Roll
-> immutable RAW ROLL
-> immutable MECHANICAL RESULT
-> GM adjudication
-> Finalize
-> bounded consequence commit
-> optional later Correct outcome
-> new adjudication supersedes prior adjudication
-> append-only coherent history
```

The pre-bound success effect remains:

> Kara becomes AWARE of the KnowledgeFragment:
> "The confiscated shipment was transferred to Dock 47."

The failure Risk remains:

> "On failure, Imperial security notices the intrusion."

If that Risk already fully expresses the concrete failure consequence, it may be used unchanged at Finalize.

---

# 2. Initial state

Before resolution creation:

- one campaign exists;
- one authenticated GM is a GM campaign member;
- one authenticated Player is a PLAYER campaign member;
- the Player is server-authoritatively assigned to Kara Venn;
- Kara Venn has a Custom D20 slicing modifier;
- the Imperial Cargo Terminal Location exists in the same campaign;
- the success KnowledgeFragment exists in the same campaign;
- Kara does not yet have CharacterKnowledge for that fragment.

At resolution creation:

- actor = Kara Venn;
- context = Imperial Cargo Terminal;
- mechanic = slicing;
- GM supplies Intent, Risk and DC;
- resolved modifier is bound from Kara's current slicing profile;
- success recipient = Kara Venn;
- success fragment = pre-bound Dock 47 KnowledgeFragment;
- state = READY.

The slice preserves the existing actor = recipient constraint and the same pre-bound success effect.

---

# 3. RAW ROLL contract

## FACT

Game Design, UX and Architecture agree:

- RAW ROLL is the backend-generated natural D20;
- it is created exactly once for the resolution;
- after Roll it is historical mechanical evidence.

## Final contract

```text
raw_roll = natural d20 in [1..20]
```

After Roll:

- raw_roll is immutable through all Product commands;
- Accept/Finalize cannot change it;
- Override cannot change it;
- Correct outcome cannot change it;
- it is never deleted because adjudication changes.

A genuine reroll is a new rules/fictional event and remains outside Slice 3.

Administrative database repair is not part of Product semantics.

---

# 4. MECHANICAL RESULT contract

The mechanical result is derived from locked inputs:

```text
mechanical_total = raw_roll + resolved_modifier
mechanical_result = SUCCESS if mechanical_total >= DC else FAILURE
```

After Roll, all of the following are immutable through normal application commands:

- raw_roll;
- resolved_modifier;
- total;
- DC;
- mechanical_result.

The mechanical result is an immutable truth about the roll under those inputs.

It is **not** automatically the final fictional outcome.

---

# 5. GM adjudication model

## General concept

**Adjudication** is the GM-authoritative interpretation used to decide which bounded consequence path becomes canonical.

**Override** is only the exceptional case where:

```text
final_outcome != mechanical_result
```

The final outcome remains binary for Slice 3:

- SUCCESS;
- FAILURE.

Both override directions are valid:

- mechanical FAILURE -> final SUCCESS;
- mechanical SUCCESS -> final FAILURE.

The GM is expected to have a coherent fictional/rules rationale when overriding, but no enumerated rules list is introduced.

The override reason field is optional.

---

# 6. Normal Finalize path

The common path is one primary action after Roll.

There is no separate Accept step followed by a second confirmation.

## Mechanical SUCCESS

```text
Roll
-> show mechanical evidence
-> show exact success consequence preview
-> Finalize Success
-> apply CharacterKnowledge = AWARE
-> persist final_outcome = SUCCESS
-> append finalization history
-> state = FINALIZED
```

The visible consequence preview itself is the confirmation.

No modal is required.

## Mechanical FAILURE

```text
Roll
-> show mechanical evidence
-> show/edit concrete failure consequence
-> Finalize Failure
-> persist final_outcome = FAILURE
-> do not reveal success fragment
-> append finalization history
-> state = FINALIZED
```

The failure consequence:

- may default to the predeclared Risk;
- may be edited/refined by the GM;
- must be non-empty at persistence time.

No duplicate prose entry is required when Risk is already sufficient.

---

# 7. Override path

Override is available only:

- after Roll;
- while state = AWAITING_ADJUDICATION;
- to an authorized campaign GM.

It is visually secondary to the normal Finalize action.

User-facing entry point:

**Override outcome…**

## Override may change

Only:

- final_outcome.

For this binary slice:

```text
mechanical SUCCESS -> final FAILURE
mechanical FAILURE -> final SUCCESS
```

## Override may not change

- raw roll;
- resolved modifier;
- total;
- DC;
- mechanical result;
- actor;
- Location;
- success recipient;
- success KnowledgeFragment;
- campaign;
- Player assignment.

If those were wrong, the original resolution contract was wrong; Override is not the repair tool.

## Override reason

Optional.

It may be persisted for GM audit/history when supplied.

It is not required for Finalize.

## Override-to-SUCCESS

Before Finalize, show:

- immutable mechanical evidence;
- mechanical FAILURE;
- proposed final SUCCESS;
- exact recipient;
- exact claim to be disclosed.

Finalize applies the same pre-bound success effect as normal success.

## Override-to-FAILURE

Before Finalize, show:

- immutable mechanical evidence;
- mechanical SUCCESS;
- proposed final FAILURE;
- concrete failure consequence.

Risk may prefill that consequence.

---

# 8. Correction / supersession path

Correction is allowed only after initial Finalize.

The normative user-facing term is:

**Correct outcome**

Do not use:

- Undo;
- Rollback;
- Reopen;

as the primary semantic term.

## Contract

Correction creates a **new adjudication** that supersedes the previous adjudication.

It does not reopen or mutate the mechanical roll.

```text
Final adjudication A
-> Correct outcome
-> Final adjudication B
-> B becomes current authoritative adjudication
-> A remains historical
```

The resolution remains FINALIZED.

A corrected state is derived from adjudication revision, not represented as a new workflow state.

## Required correction input

- expected current adjudication revision;
- replacement final outcome;
- failure adjudication if replacement outcome = FAILURE;
- short correction reason: required.

## Supported correction types

1. FAILURE -> SUCCESS;
2. SUCCESS -> FAILURE;
3. FAILURE -> FAILURE with corrected failure-adjudication text.

A no-op correction is rejected.

Mechanical correction is not supported.

---

# 9. Irreversible-effect semantics

The slice explicitly distinguishes:

## Technically mutable current DB state

Examples:

- current final_outcome;
- current failure_adjudication;
- current adjudicating GM;
- current adjudication timestamp;
- current adjudication revision;
- success disclosure that has not yet happened.

## Cognitively irreversible human effect

For Slice 3:

- a claim already shown to the human Player.

Technical reversibility does not imply cognitive reversibility.

## FAILURE -> SUCCESS correction

If the resolution was finalized FAILURE:

- no success claim was revealed;
- correction to SUCCESS may apply the pre-bound success Knowledge consequence;
- CharacterKnowledge becomes AWARE;
- old FAILURE remains in history;
- current final outcome becomes SUCCESS.

This is the one bounded additive compensation supported by Slice 3.

## SUCCESS -> FAILURE correction after disclosure

If SUCCESS already caused the claim to be shown:

- current final outcome may become FAILURE;
- concrete failure adjudication is required;
- original SUCCESS remains in history;
- disclosure remains in history;
- CharacterKnowledge remains AWARE;
- the system must not claim the Player "unlearned" the information.

This deliberate current state is valid:

```text
current final outcome = FAILURE
CharacterKnowledge = AWARE
```

If the fiction needs reconciliation, the GM may narratively explain it.

Slice 3 does not automate a compensating fiction.

---

# 10. Exact consequence used by this slice

There is only one success consequence:

```text
make Kara Venn AWARE of the pre-bound Dock 47 KnowledgeFragment
```

There is only one failure-consequence shape:

```text
one concrete GM-authored failure adjudication string
```

The existing Risk may be used as that string unchanged.

No generic effect list, consequence DSL or arbitrary mutation envelope is introduced.

---

# 11. Player visibility

## Product decision after cross-domain review

Slice 3 **does include** a small read-only Player resolution summary after Finalize.

Reason:

- the slice is specifically establishing that mechanical evidence and GM adjudication are distinct;
- hiding that distinction from the Player would weaken the trust/clarity hypothesis being validated;
- Game Design and UX both support exposing the distinction if a Player summary exists;
- Architecture confirms a bounded explicit projection is feasible.

## Exact Player-visible fields

For the assigned Character's finalized resolution:

- raw d20: YES;
- resolved modifier: YES;
- total: YES;
- mechanical result: YES;
- current final outcome: YES;
- overridden marker: YES, derived from final_outcome != mechanical_result;
- corrected marker: YES, derived from adjudication_revision > 1;
- compact prior outcome notice after correction: YES, only when UX needs to explain a visible change.

Not Player-visible:

- DC;
- override reason;
- correction reason;
- failure adjudication text;
- GM-only Risk/stakes not otherwise disclosed;
- gm_veracity;
- full correction history;
- arbitrary canonical ActionResolution fields.

## Why DC is excluded

No domain requires DC visibility for this slice.

Excluding it:

- keeps hidden-difficulty/table-style flexibility;
- reduces disclosure scope;
- still proves mechanical-result vs final-outcome transparency.

A later Product decision may expose DC if another workflow requires it.

---

# 12. Data / persistence contract

## Architecture direction accepted into the final proposed spec

Evolve the existing Slice-1-specific `ActionResolution`.

Do not replace it.

Do not introduce a generic Resolution or Adjudication aggregate.

## Existing bound fields remain

- id;
- campaign_id;
- actor_character_id;
- context_location_id;
- intent;
- risk;
- mechanic = slicing;
- dc;
- resolved_modifier;
- success_recipient_character_id;
- success_fragment_id;
- created_by_principal_id;
- created_at.

## Mechanical evidence

Rename the ambiguous existing:

```text
outcome
```

to:

```text
mechanical_result
```

Keep:

- natural_roll;
- resolved_modifier;
- total;
- dc;
- mechanical_result;
- rolled_at.

## Current adjudication fields

Add only:

```text
final_outcome: SUCCESS | FAILURE | null
failure_adjudication: text | null
adjudication_reason: text | null
adjudicated_by_principal_id: UUID | null
adjudicated_at: timestamptz | null
adjudication_revision: integer NOT NULL default 0
```

Derived, not persisted:

```text
is_overridden = final_outcome != mechanical_result
is_corrected = adjudication_revision > 1
```

## Stage-only state

Use:

```text
READY
AWAITING_ADJUDICATION
FINALIZED
```

Do not persist SUCCESS/FAILURE inside workflow state.

Do not add CORRECTED as a state.

---

# 13. Persistence consistency / immutability boundaries

## Application-level immutability

After Roll, no normal command accepts or assigns:

- natural_roll;
- resolved_modifier;
- total;
- dc;
- mechanical_result.

Finalize and Correct load those from PostgreSQL.

Both commands row-lock the resolution.

## DB consistency constraints

PostgreSQL must enforce coherent mechanical rows.

Conceptually:

```text
unrolled:
  natural_roll IS NULL
  total IS NULL
  mechanical_result IS NULL
  rolled_at IS NULL

rolled:
  natural_roll BETWEEN 1 AND 20
  total = natural_roll + resolved_modifier
  mechanical_result matches total >= dc
  rolled_at IS NOT NULL
```

State/adjudication consistency:

```text
READY:
  no mechanical result
  final_outcome IS NULL
  revision = 0

AWAITING_ADJUDICATION:
  mechanical evidence exists
  final_outcome IS NULL
  revision = 0

FINALIZED:
  mechanical evidence exists
  final_outcome IS NOT NULL
  revision >= 1
  adjudicated_by IS NOT NULL
  adjudicated_at IS NOT NULL
```

Additional constraints:

```text
final_outcome = FAILURE
  => failure_adjudication non-empty

final_outcome = SUCCESS
  => failure_adjudication IS NULL

revision >= 2
  => adjudication_reason non-empty
```

No DB trigger is required to enforce absolute immutability against direct privileged SQL.

That is outside the Product command boundary and disproportionate for Slice 3.

---

# 14. API / command contract

Keep:

```text
POST /campaigns/{campaign_id}/resolutions
POST /campaigns/{campaign_id}/resolutions/{resolution_id}/roll
GET  /campaigns/{campaign_id}/resolutions/{resolution_id}
GET  /campaigns/{campaign_id}/resolutions/latest
```

Replace the old terminal mutation semantics with:

```text
POST /campaigns/{campaign_id}/resolutions/{resolution_id}/finalize
POST /campaigns/{campaign_id}/resolutions/{resolution_id}/correct
```

The old public:

```text
/apply
/close-failure
```

must not remain alternative finalization paths for Slice 3 because they bypass the new explicit adjudication contract.

## Finalize request

Conceptually:

```text
final_outcome: SUCCESS | FAILURE
failure_adjudication?: string
reason?: string
```

Rules:

- final outcome may match or differ from mechanical result;
- reason optional;
- failure adjudication required for final FAILURE;
- request contains no mechanical evidence fields.

## Correct request

Conceptually:

```text
expected_adjudication_revision: integer
final_outcome: SUCCESS | FAILURE
failure_adjudication?: string
correction_reason: string required
```

Request must not contain:

- raw roll;
- modifier;
- total;
- DC;
- mechanical result;
- actor;
- Location;
- recipient;
- KnowledgeFragment.

## Player read model

Add a dedicated Player-safe resolution summary endpoint/read model.

Authorization derives the Player's assigned Character server-side.

No arbitrary Character id is accepted.

Only finalized resolutions for that assigned actor are eligible.

---

# 15. Authorization / security

Backend-authoritative rules:

- only authenticated campaign GM may create the resolution;
- only GM may Roll;
- only GM may Finalize;
- only GM may Override through Finalize;
- only GM may Correct;
- Player cannot mutate adjudication;
- current role is loaded from PostgreSQL;
- all bound references remain campaign-scoped;
- client cannot supply or rewrite mechanical evidence;
- Player summary uses an explicit projection.

Add/retain campaign-scoped integrity for:

- actor;
- Location;
- success recipient;
- success KnowledgeFragment;
- adjudicating campaign member.

Membership FK does not replace role authorization.

---

# 16. Transaction boundaries

All operations remain synchronous inside the modular monolith.

No event handler performs canonical state mutations.

## Roll

One transaction:

```text
authorize GM
-> SELECT FOR UPDATE
-> require READY
-> validate same-campaign bound refs
-> backend generate d20
-> calculate total/mechanical_result
-> persist evidence
-> state = AWAITING_ADJUDICATION
-> commit
```

No canonical success/failure consequence is committed.

## Finalize SUCCESS

One transaction:

```text
authorize GM
-> SELECT FOR UPDATE
-> require AWAITING_ADJUDICATION
-> validate requested final outcome
-> apply CharacterKnowledge = AWARE idempotently
-> persist current adjudication revision 1
-> append resolution.adjudication_finalized
-> state = FINALIZED
-> commit
```

## Finalize FAILURE

One transaction:

```text
authorize GM
-> SELECT FOR UPDATE
-> require AWAITING_ADJUDICATION
-> require concrete failure adjudication
-> persist current adjudication revision 1
-> append resolution.adjudication_finalized
-> state = FINALIZED
-> commit
```

## Correct FAILURE -> SUCCESS

One transaction:

```text
authorize GM
-> SELECT FOR UPDATE
-> require FINALIZED
-> validate expected revision
-> require correction reason
-> capture previous adjudication
-> make CharacterKnowledge AWARE idempotently
-> update current adjudication
-> revision += 1
-> append resolution.adjudication_corrected
-> commit
```

## Correct SUCCESS -> FAILURE

One transaction:

```text
authorize GM
-> SELECT FOR UPDATE
-> require FINALIZED
-> validate expected revision
-> require correction reason
-> require failure adjudication
-> capture previous adjudication
-> DO NOT delete CharacterKnowledge
-> update current adjudication
-> revision += 1
-> append resolution.adjudication_corrected
-> commit
```

## Correct FAILURE text only

Allowed.

Requires:

- changed text;
- correction reason;
- revision increment;
- correction event.

No-op is rejected.

---

# 17. Idempotency / concurrency

Use row-level locking.

## Finalize

If retried after successful initial Finalize:

- if request exactly matches the current revision-1 adjudication, return current state without duplicate event/effect;
- if request differs, reject and require Correct.

## Correct

Use:

```text
expected_adjudication_revision
```

Two concurrent corrections from revision 1:

- first succeeds -> revision 2;
- second fails with revision conflict;
- no duplicate consequence/history.

No generic idempotency-key platform is introduced.

---

# 18. DomainEvent / history expectations

PostgreSQL relational `ActionResolution` remains source of current state.

DomainEvent remains append-only significant history.

No event replay is required to read current state.

## New event: resolution.adjudication_finalized

One event for initial Finalize.

Minimum payload:

```text
resolution_id
adjudication_revision = 1
mechanical_result
final_outcome
overridden
adjudication_reason?       // optional, GM history
failure_adjudication?      // GM history
```

For final SUCCESS, may include existing bounded disclosure audit data:

- recipient_character_id;
- recipient_name;
- fragment_id;
- claim_text.

## New event: resolution.adjudication_corrected

Minimum payload:

```text
resolution_id
previous_revision
new_revision
previous_final_outcome
final_outcome
previous_failure_adjudication?
failure_adjudication?
correction_reason
success_disclosure_applied_now
prior_success_disclosure_retained
```

No generic `effects[]` envelope.

## Legacy events

Do not rewrite:

- resolution.success_applied;
- resolution.failure_closed;
- Contact disclosure events.

Legacy history remains valid.

The history projection may render both legacy and Slice-3 event types.

---

# 19. Migration expectations

Add one normal Alembic migration, conceptually:

```text
0003_slice3_adjudication
```

## Schema migration

1. rename `outcome` -> `mechanical_result`;
2. replace old outcome-encoded state CHECK with:
   - READY;
   - AWAITING_ADJUDICATION;
   - FINALIZED;
3. add:
   - final_outcome;
   - adjudication_reason;
   - adjudicated_by_principal_id;
   - adjudicated_at;
   - adjudication_revision default 0;
4. retain failure_adjudication as current failure consequence;
5. add consistency constraints;
6. add campaign-scoped FK for adjudicated_by principal;
7. replace ambiguous `closed_at` semantics with current adjudication timestamp semantics.

Preferred migration:

```text
closed_at -> adjudicated_at
```

The latest correction updates current adjudicated_at.

Original finalization timestamp remains in DomainEvent history.

## Legacy row mapping

### READY

```text
READY
-> READY
mechanical_result = NULL
final_outcome = NULL
revision = 0
```

### SUCCESS_PENDING_APPLY

```text
-> AWAITING_ADJUDICATION
mechanical_result = SUCCESS
final_outcome = NULL
revision = 0
```

### FAILURE_PENDING_CLOSE

```text
-> AWAITING_ADJUDICATION
mechanical_result = FAILURE
final_outcome = NULL
revision = 0
```

### CLOSED_SUCCESS

```text
-> FINALIZED
final_outcome = SUCCESS
revision = 1
adjudicated_at = old closed_at
```

Existing CharacterKnowledge remains untouched.

### CLOSED_FAILURE

```text
-> FINALIZED
final_outcome = FAILURE
failure_adjudication preserved
revision = 1
adjudicated_at = old closed_at
```

## Legacy adjudicating GM

Backfill from matching legacy terminal DomainEvent actor:

- resolution.success_applied;
- resolution.failure_closed.

Do not silently use created_by_principal_id when a terminal event is missing.

If a closed legacy row lacks its matching terminal event, migration should fail clearly rather than fabricate adjudication ownership.

Legacy DomainEvents remain unchanged.

---

# 20. Acceptance criteria

## Mechanical evidence

1. Roll generates exactly one backend d20.
2. Duplicate Roll does not generate a second die.
3. raw_roll is unchanged by Finalize.
4. modifier is unchanged by Finalize.
5. total is unchanged by Finalize.
6. DC is unchanged by Finalize.
7. mechanical_result is unchanged by Finalize.
8. all five remain unchanged through every Correct.
9. DB rejects mechanically inconsistent rolled rows.
10. reload preserves mechanical evidence.

## Adjudication

11. Roll transitions READY -> AWAITING_ADJUDICATION only.
12. Roll sets no final_outcome.
13. Roll commits no success/failure consequence.
14. normal Finalize may use final_outcome = mechanical_result.
15. Override may use final_outcome != mechanical_result.
16. both override directions are supported.
17. Override never mutates mechanical evidence.
18. final SUCCESS applies only the pre-bound Knowledge effect.
19. final FAILURE does not apply the success effect.
20. final FAILURE persists a concrete failure adjudication.
21. Risk may be used unchanged as that consequence.
22. initial Finalize creates revision 1 and state FINALIZED.
23. repeated identical Finalize is idempotent.

## Correction

24. Correct requires state FINALIZED.
25. Correct requires expected revision.
26. Correct requires a non-empty correction reason.
27. Correct never mutates mechanical evidence.
28. Correction leaves workflow state FINALIZED.
29. Correction increments adjudication revision exactly once.
30. prior adjudication remains in append-only history.
31. latest adjudication is current relational state.
32. FAILURE -> SUCCESS may apply CharacterKnowledge AWARE.
33. SUCCESS -> FAILURE after disclosure retains CharacterKnowledge AWARE.
34. FAILURE -> FAILURE text correction is supported.
35. no-op correction is rejected.
36. stale correction revision produces no mutation/history.

## Irreversible effects

37. Already-disclosed CharacterKnowledge is never removed merely to simulate unlearning.
38. History retains the original disclosure.
39. Current final outcome may legitimately be FAILURE while CharacterKnowledge remains AWARE.
40. No generic undo/rollback semantics are exposed.

## Player visibility

41. Assigned Player can read only their finalized resolution summary.
42. Player sees raw d20, modifier, total, mechanical result and current final outcome.
43. Player sees overridden marker when mechanical != final.
44. Player sees corrected marker when revision > 1.
45. Player does not receive DC.
46. Player does not receive override reason.
47. Player does not receive correction reason.
48. Player does not receive failure adjudication text.
49. Player does not receive gm_veracity.
50. Another Player/Character cannot read the summary.

## Authorization

51. Player cannot Roll.
52. Player cannot Finalize.
53. Player cannot Correct.
54. non-member cannot mutate/read GM resolution endpoints.
55. current GM role is loaded from PostgreSQL.
56. cross-campaign references remain rejected.

## Transactions/history

57. Finalize SUCCESS is atomic across adjudication + CharacterKnowledge + DomainEvent.
58. Finalize FAILURE is atomic across adjudication + DomainEvent.
59. Correct FAILURE -> SUCCESS is atomic across adjudication + CharacterKnowledge + DomainEvent.
60. Correct SUCCESS -> FAILURE is atomic across adjudication + DomainEvent while retaining knowledge.
61. event insert failure rolls back the corresponding current-state mutation.
62. initial finalization appends exactly one finalization event.
63. each successful correction appends exactly one correction event.
64. current state is not reconstructed through event replay.

## Regression / scope

65. Slice 2 Contact Reveal remains independent of ActionResolution.
66. Contact Reveal still creates no ActionResolution.
67. existing campaign isolation tests remain green.
68. no generic Resolution aggregate is introduced.
69. no generic Adjudication table is introduced.
70. no generic workflow/state-machine framework is introduced.
71. no generic undo/change-set framework is introduced.
72. no generic compensation system is introduced.
73. no generic consequence/effect engine is introduced.
74. no Rule Effect DSL is introduced.
75. no realtime infrastructure is introduced.
76. no Player-side rolling is introduced.

---

# 21. Test contract

## Unit / pure rule tests

- D20 total and SUCCESS/FAILURE calculation unchanged;
- any small pure adjudication helper if introduced;
- state/validation helpers where useful.

## PostgreSQL integration tests

Must cover all acceptance invariants, especially:

- mechanical evidence immutability;
- DB mechanical consistency constraints;
- both Override directions;
- normal Finalize success/failure;
- Risk-as-failure-consequence;
- optional override reason;
- required correction reason;
- both cross-outcome correction directions;
- retained CharacterKnowledge on corrected SUCCESS -> FAILURE;
- failure-text-only correction;
- no-op correction rejection;
- idempotent Finalize;
- optimistic revision conflict on Correct;
- atomic rollback when DomainEvent insert fails;
- authorization;
- cross-campaign validation;
- Player-safe resolution projection;
- Contact Reveal regression.

## Migration test

A dedicated data migration test must:

1. start from migration `0002_slice2_contacts`;
2. create representative rows for:
   - READY;
   - SUCCESS_PENDING_APPLY;
   - FAILURE_PENDING_CLOSE;
   - CLOSED_SUCCESS + terminal event + CharacterKnowledge;
   - CLOSED_FAILURE + terminal event;
3. upgrade to Slice 3 migration;
4. verify exact state mapping;
5. verify mechanical values unchanged;
6. verify adjudicating GM backfill;
7. verify CharacterKnowledge unchanged;
8. verify legacy events unchanged.

## E2E

At minimum:

### E2E 1 — normal success

```text
GM creates slicing resolution
-> Roll mechanical SUCCESS
-> Player summary not finalized yet / success consequence absent
-> GM Finalize Success
-> Player gets claim
-> Player summary shows mechanical SUCCESS + final SUCCESS
-> reload preserves state
```

### E2E 2 — Override failure to success

```text
Roll mechanical FAILURE
-> GM Override outcome
-> Finalize Success
-> claim disclosed
-> Player summary shows mechanical FAILURE + final SUCCESS + overridden
```

### E2E 3 — Override success to failure

```text
Roll mechanical SUCCESS
-> GM Override outcome
-> Finalize Failure using Risk or refined failure text
-> claim not disclosed
-> Player summary shows mechanical SUCCESS + final FAILURE + overridden
```

### E2E 4 — correction failure to success

```text
final FAILURE
-> GM Correct outcome with reason
-> final SUCCESS
-> claim now disclosed
-> corrected marker visible
-> prior failure retained in GM history
```

### E2E 5 — correction success to failure after disclosure

```text
final SUCCESS
-> Player sees claim
-> GM Correct outcome to FAILURE with reason
-> inline irreversible-disclosure warning shown
-> Player still sees claim
-> Player summary shows current FAILURE + corrected
-> GM history preserves prior SUCCESS/disclosure
```

At least the Player-facing E2Es use distinct authenticated GM and Player principals.

---

# 22. Explicit exclusions

Slice 3 does not include:

- generic resolution engine;
- generic Resolution aggregate for hypothetical mechanics;
- generic Adjudication aggregate/table;
- generic workflow engine;
- generic state-machine framework;
- generic undo;
- generic change-set engine;
- arbitrary rollback;
- generic compensation framework;
- generic consequence/effect engine;
- Rule Effect DSL;
- event sourcing;
- command bus;
- event-driven internal RPC;
- generic audit framework;
- generic version-history framework;
- generic idempotency platform;
- DB triggers solely to simulate immutable/event-sourced data;
- combat;
- encounter system;
- Player-side rolling;
- collaborative/group actions;
- realtime/WebSockets/SSE;
- rerolls;
- crits;
- degrees of success;
- opposed rolls;
- advantage/disadvantage expansion;
- mechanical repair UI;
- full Player resolution-history browser;
- Player-visible GM reasons;
- Player-visible DC;
- generic Scene/Session;
- broker/worker;
- microservices;
- a second D20 mechanic introduced only for generality.

---

# 23. Consolidated disagreements and dispositions

## Disagreement 1 — Override authority

**FACT**

Initial Product proposal allowed both binary directions.

**DOMAIN OWNER POSITION**

Game Design explicitly supports both directions, provided mechanical evidence is unchanged and the GM has a plausible fiction/rules rationale.

UX and Architecture support the same model.

**PRODUCT IMPACT**

No conflict remains.

Both directions stay in scope.

**HUMAN DECISION REQUIRED: NO**

---

## Disagreement 2 — Override reason

**FACT**

Initial Product proposal: optional.

**DOMAIN OWNER POSITION**

Game Design: not mechanically required.  
UX: optional, secondary, non-blocking.  
Architecture: supports optional storage.

**PRODUCT IMPACT**

Keep override reason optional and GM-only.

**HUMAN DECISION REQUIRED: NO**

---

## Disagreement 3 — Correction reason

**FACT**

Initial Product proposal: required.

**DOMAIN OWNER POSITION**

Game Design: not mechanically required but fully compatible.  
UX: should be required because correction changes finalized authority.  
Architecture: uses it as a required invariant for revision >= 2.

**PRODUCT IMPACT**

Keep correction reason required.

**HUMAN DECISION REQUIRED: NO**

---

## Disagreement 4 — Failure consequence entry

**FACT**

Initial Product spec implied concrete failure adjudication input.

**DOMAIN OWNER POSITION**

Game Design: predeclared Risk may itself be the final failure consequence.  
UX: prefill/use Risk and require editing only when needed.  
Architecture: persist the concrete current failure-adjudication string regardless of whether copied from Risk.

**PRODUCT IMPACT**

No duplicate text entry.

Risk is the default concrete failure consequence and may be refined.

**HUMAN DECISION REQUIRED: NO**

---

## Disagreement 5 — Correction semantics

**FACT**

The initial document used correction/reopen terminology in places.

**DOMAIN OWNER POSITION**

Game Design: correction creates a new superseding adjudication; do not reopen roll.  
UX: use Correct outcome, never Undo/Rollback/Reopen as the primary interaction.  
Architecture: state remains FINALIZED; revision increments.

**PRODUCT IMPACT**

Adopt supersession semantics and Correct outcome terminology.

**HUMAN DECISION REQUIRED: NO**

---

## Disagreement 6 — SUCCESS -> FAILURE after disclosure

**FACT**

The human Player may already know the claim.

**DOMAIN OWNER POSITION**

All three reviews agree that CharacterKnowledge must remain AWARE and prior disclosure remains historical.

Game Design clarifies that current final outcome describes the current adjudication of the resolution, not a reconstruction of every irreversible world/history fact.

**PRODUCT IMPACT**

Retain knowledge; no generic compensation or retroactive erasure.

**HUMAN DECISION REQUIRED: NO**

---

## Disagreement 7 — Player resolution visibility

**FACT**

Initial Product spec proposed transparency but allowed the summary to be deferred.

**DOMAIN OWNER POSITION**

Game Design: if shown, mechanical result and final outcome should both be visible and override must not be disguised.  
UX: supports a compact summary and does not require full history.  
Architecture: bounded explicit projection is straightforward; exact field set must be frozen.

**PRODUCT IMPACT**

Product selects the compact Player summary for Slice 3 because it directly validates the trust/authority hypothesis.

Exact fields are frozen in section 11.

**HUMAN DECISION REQUIRED: NO**

---

## Disagreement 8 — Player-visible DC

**FACT**

No domain requires DC visibility.

**DOMAIN OWNER POSITION**

Game Design: not a blocker.  
UX: not required.  
Architecture: can support either choice.

**PRODUCT IMPACT**

Exclude DC from Player projection for this slice.

This preserves hidden-difficulty flexibility and reduces disclosure scope.

**HUMAN DECISION REQUIRED: NO**

---

## Disagreement 9 — evolve vs replace ActionResolution

**FACT**

Current ActionResolution remains deliberately slicing-specific.

**DOMAIN OWNER POSITION**

Architecture explicitly recommends evolving it rather than creating a second resolution model because Slice 3 remains the same mechanic/scenario.

No Game Design or UX requirement conflicts.

**PRODUCT IMPACT**

Adopt narrow evolution.

No generic replacement.

**HUMAN DECISION REQUIRED: NO**

---

# 24. Human arbitration

**NO MATERIAL HUMAN ARBITRATION REMAINS**

The three specialist reviews now converge on one bounded implementation contract.

The remaining step is not domain arbitration but Human acceptance of the final proposed Slice 3 scope.

---

# 25. Acceptance gate

This specification is:

**READY FOR HUMAN ACCEPTANCE**

It is not yet ACCEPTED.

Until the Human Project Owner explicitly approves:

- do not modify `docs/planning/current-slice.md`;
- do not add an ACCEPTED Slice 3 decision to `decision-log.md`;
- do not start implementation;
- do not merge PR #15 as implementation authorization.

After explicit Human acceptance, Product may update the normative planning state and authorize the Architecture implementation phase through the normal branch/PR workflow.
