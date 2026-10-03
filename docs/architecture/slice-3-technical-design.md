# Slice 3 Technical Design — Roll, Review, Adjudicate, Correct

Status: IMPLEMENTATION BASELINE  
Owner: Principal Software Architect / Lead Developer  
Slice contract: `docs/planning/current-slice.md`

## Scope

Slice 3 narrowly evolves the existing slicing-specific `ActionResolution`.

It does not introduce a generic Resolution or Adjudication aggregate.

## Persistent model

`ActionResolution` keeps the existing bound actor/context/Intent/Risk/DC/success-effect fields.

Mechanical evidence is:

- `natural_roll`;
- `resolved_modifier`;
- `total`;
- `dc`;
- `mechanical_result`;
- `rolled_at`.

Current adjudication is:

- `final_outcome`;
- `failure_adjudication`;
- `adjudication_reason`;
- `adjudicated_by_principal_id`;
- `adjudicated_at`;
- `adjudication_revision`.

Workflow state is stage-only:

- `READY`;
- `AWAITING_ADJUDICATION`;
- `FINALIZED`.

Override and Corrected are derived concepts, not workflow states.

## Immutability

After Roll, Product commands never accept or assign raw roll, modifier, total, DC or mechanical result.

PostgreSQL CHECK constraints additionally require a rolled row to be mathematically coherent:

`total = natural_roll + resolved_modifier`, with mechanical result derived from total vs DC.

No trigger is introduced to prevent privileged administrative SQL repair.

## Transactions

Roll, Finalize and Correct all use the existing synchronous SQLAlchemy/PostgreSQL transaction boundary and row-level locking.

Finalize SUCCESS atomically commits:

- current adjudication revision 1;
- CharacterKnowledge AWARE;
- `resolution.adjudication_finalized`.

Finalize FAILURE atomically commits:

- current adjudication revision 1;
- concrete failure adjudication;
- `resolution.adjudication_finalized`.

Correct atomically:

- validates expected adjudication revision;
- records a superseding current adjudication;
- increments revision;
- applies the bounded FAILURE -> SUCCESS disclosure if needed;
- never deletes already-disclosed CharacterKnowledge;
- appends `resolution.adjudication_corrected`.

DomainEvent is history only and never drives canonical mutation.

## Player projection

`GET /api/player/campaigns/{campaign_id}/resolutions/latest` derives the Player Character from server-authoritative assignment.

Only the latest resolution for that assigned actor is eligible, and only after FINALIZED.

The projection contains:

- raw d20;
- resolved modifier;
- total;
- mechanical result;
- current final outcome;
- overridden marker;
- corrected marker;
- compact previous-outcome notice after correction.

It excludes:

- DC;
- Risk;
- failure adjudication;
- adjudication/correction reasons;
- gm_veracity;
- full correction history.

## Legacy migration

Alembic `0003_slice3_adjudication`:

- renames `outcome` to `mechanical_result`;
- renames `closed_at` to current `adjudicated_at`;
- maps old pending states to `AWAITING_ADJUDICATION`;
- maps old CLOSED rows to `FINALIZED`, revision 1;
- backfills adjudicating GM from the matching legacy terminal DomainEvent;
- refuses to fabricate ownership if a closed legacy row has no unique terminal event;
- preserves legacy DomainEvents and CharacterKnowledge.

A dedicated migration test exercises populated 0002 data before upgrading to 0003.

## Explicit non-design

No:

- generic resolution/adjudication framework;
- workflow/state-machine engine;
- undo/change-set engine;
- generic consequence/compensation engine;
- event sourcing;
- command bus;
- Rule Effect DSL;
- broker/worker;
- realtime;
- combat;
- Player rolling;
- collaborative rolls.
