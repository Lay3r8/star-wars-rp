# Slice 1 Product Closeout Notes

Status: PROPOSED FOR MERGE AFTER / WITH SLICE 1 CLOSEOUT  
Owner: Product Lead  
Source inputs:
- accepted Slice 1 contract in `docs/planning/current-slice.md`;
- Product acceptance review of PR #7;
- Human Project Owner manual test observations.

## Purpose

Capture durable Product/UX lessons from Slice 1 without turning temporary bootstrap/setup surfaces into long-lived product commitments.

This document is **not** a request to polish or refactor the temporary Slice 1 process, API, frontend screens, or authentication workflow merely because they were used for the proof.

The implementation proved the accepted core loop. The useful follow-up is to preserve the reusable interaction principles and unresolved product questions before later UX/frontend work replaces these surfaces.

## Slice 1 outcome

Product acceptance of PR #7 is PASS.

The important product result from manual testing is that the core functional loop works:

```text
Intent / Risk
-> D20 resolution
-> terminal GM action
-> persisted consequence/history
-> safe player disclosure
```

The observed friction is concentrated primarily in the bootstrap/administration interface around that loop rather than in the accepted gameplay contract itself.

## Do not polish temporary Slice 1 bootstrap screens by default

The current numbered setup surfaces such as:

- Add Player;
- Create Character;
- Create Location;
- Create hidden claim;
- Assign Player;

exist primarily to manufacture the minimum context needed to prove Slice 1.

They must not automatically become the information architecture or authoring workflows of the future GM product.

Do **not** create implementation work solely to perfect these screens if a later accepted UX design will replace them.

Likewise, do not treat current Slice 1 API shapes or local authentication as permanent product contracts unless a later decision explicitly adopts them.

## Durable UX principles discovered during manual testing

The following principles should survive replacement of the Slice 1 frontend.

### UX-01 — Every user-triggered mutation needs explicit state feedback

A mutation-capable interaction should have a coherent user-visible lifecycle such as:

```text
idle
-> pending
-> success OR error
```

The user should not need to infer whether a create/assign/apply action was received.

Where duplicate submission could create additional state, the primary action should be disabled or otherwise protected while the request is pending.

This is a cross-cutting interaction principle, not a `Create Location`-specific fix.

### UX-02 — Normalize technical API failures into user-readable errors

The product UI must not expose raw framework error shapes or values such as `[object Object]`.

Client-side error handling should eventually provide one reusable normalization boundary for:

- validation errors;
- authentication failures;
- authorization failures;
- domain conflicts;
- unexpected server failures.

The exact implementation belongs to the future frontend architecture and should not be retrofitted into temporary screens unless they remain in use.

### UX-03 — Communicate known input constraints before submission

When the application knows a constraint that the user can reasonably satisfy before submitting, the UI should communicate it through:

- label/help text;
- input constraints;
- inline validation where useful.

Users should not need to discover basic syntax/length requirements through an HTTP validation error.

### UX-04 — Prevent accidental duplicate actions without inventing false domain uniqueness

UX protection against double-submit and domain identity rules are separate concerns.

For example:

- two Locations may legitimately share a name;
- two KnowledgeFragments may legitimately have similar or identical text.

Do not add arbitrary `UNIQUE(name)` or `UNIQUE(claim_text)` constraints merely to mask an interaction problem.

Nominal duplicate detection, if ever needed, requires its own Product/domain decision.

### UX-05 — Do not expose a false global GM/Player account model

The current accepted mental model is:

```text
Principal
  -> Campaign A: GM
  -> Campaign B: PLAYER
```

A Principal is not intrinsically a global "GM account" or "Player account".

Future registration/login wording must not imply otherwise.

Role belongs to campaign membership unless Product explicitly reopens that decision.

### UX-06 — Selection controls depend on the authorized collection and workflow

For entities already available inside the authorized campaign context, selection should use an appropriate control such as:

- prefilled value when unambiguous;
- select for very small lists;
- searchable combobox when lists become large enough;
- clear empty state when no option exists.

Selecting/inviting a Principal who is not yet part of the campaign is a separate Product/Security workflow.

Do not introduce a global account autocomplete or directory endpoint solely to improve the temporary Slice 1 "Add Player" screen.

### UX-07 — Hide persistence and implementation terminology from normal workflows

The user should operate in domain/game concepts, not storage concepts.

Internal concepts such as persistence status, table identity, transaction state, event records, projection internals, or API lifecycle should only surface when they genuinely help the user.

The successful Slice 1 pattern of showing the exact recipient/claim before Apply is useful because it communicates the **fictional/product effect**, not because it reveals persistence mechanics.

### UX-08 — Prefer compact live-session interactions

Live-session workflows should minimize avoidable form filling and navigation.

Where actor, context, mechanic, recipient, or another field is uniquely determined by current context, prefer prefilling or direct display over redundant selection.

This principle survives the eventual replacement of the Slice 1 GM workspace.

### UX-09 — Irreversible disclosure deserves explicit confirmation

Revealing hidden information to a player is cognitively irreversible even if database state can later be corrected.

Before such a disclosure, the GM should clearly see the recipient and exact player-visible information.

This is distinct from requiring confirmation for every trivial deterministic mutation.

### UX-10 — FR/EN is a future product requirement

The current Slice 1 UI is English-only.

The product should support French and English before a broader player-facing phase where francophone users are expected to use the application regularly.

This does **not** justify adding a localization framework solely to the temporary Slice 1 frontend.

Future frontend work should, however, avoid making localization needlessly harder through unnecessary proliferation of embedded product copy.

## Product questions intentionally not solved by Slice 1 feedback

### Player invitation / selection

The future workflow for bringing Players into a campaign remains undefined.

Reasonable future patterns may include invitation links, usernames, explicit campaign invitations, or another identity workflow.

This decision has Product, UX, Security, and Architecture impact.

No global Principal directory/search should be implemented before this workflow is designed.

### Duplicate-content assistance

The product may later benefit from warnings about apparently duplicate Locations, NPCs, claims, or other content.

Whether this is useful, and what constitutes a duplicate, remains domain-specific and is not established by Slice 1.

### Final identity provider

Local username/password authentication was sufficient to prove Slice 1.

It is not accepted as the final identity strategy.

### Realtime player updates

Manual refresh/re-fetch was an accepted Slice 1 concession.

It is not the target live-player experience.

The eventual interaction requirement should be decided before choosing polling, server push, WebSockets, SSE, or another implementation.

## DevEx observation — corporate TLS interception

Corporate TLS interception such as Zscaler is an environment-specific developer concern, not a product architecture requirement.

The appropriate future DevEx direction is an optional local configuration that can supply a corporate CA without changing standard builds or CI behavior.

Candidate convention:

```text
CORPORATE_CA_FILE=<optional local CA path>
```

with a local Docker/Compose override or equivalent mechanism.

Do not make a corporate CA mandatory and do not encode Zscaler-specific assumptions into the normal product build.

## Explicit non-actions

These manual-test observations do **not** justify, by themselves:

- polishing all current Slice 1 bootstrap cards;
- redesigning the temporary local-auth screen;
- adding a global GM/Player role to Principal;
- adding uniqueness constraints on Location name;
- adding uniqueness constraints on KnowledgeFragment claim text;
- creating a Principal directory/search endpoint;
- adding realtime infrastructure;
- introducing i18n infrastructure into a frontend expected to be replaced;
- changing the accepted ActionResolution contract;
- reopening Slice 1.

## Recommended coordination before the next implementation slice

Before implementation of another substantial user-facing slice:

1. UX should incorporate the durable principles above into the authoritative UX guidance.
2. Product and UX should define the intended GM/player workflow relevant to the selected next slice rather than extending the Slice 1 bootstrap UI by inertia.
3. Architecture should only implement reusable frontend/error/mutation infrastructure when the next accepted workflow demonstrates the need.
4. Corporate TLS/CA support, if needed for ongoing development, should remain a separate Architecture/DevEx concern.
5. Product should select the next vertical slice through the normal cross-domain process rather than assuming combat, generation, search, or UI polish automatically comes next.

## Closeout status

PR #7 has passed Product acceptance and has been marked Product READY TO MERGE.

The next planning cycle should begin from `main` **after PR #7 is merged**.

No Slice 2 is defined by this document.
