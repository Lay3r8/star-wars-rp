# Slice 1 Product Closeout Notes

Status: SLICE 1 PRODUCT CLOSEOUT — READY FOR MERGE  
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

## UX guidance after Slice 1

The durable interaction lessons from the manual test have now been reviewed by the UX owner and are recorded authoritatively in:

- `docs/ux/interaction-principles.md`

That document is now the source of truth for durable UX guidance strengthened by Slice 1.

Product does **not** redefine or duplicate those principles here.

For Product planning, the relevant consequences are:

- temporary Slice 1 bootstrap/admin surfaces must not become future information architecture through inertia;
- future accepted user-facing slices must respect the UX guidance for mutation feedback, actionable errors, visible constraints, duplicate-submit protection, campaign-contextual roles, authorized selection sets, domain language, compact live interactions, and hidden-information disclosure;
- FR/EN readiness, live-update freshness, player invitation/identity discovery, and duplicate-content assistance remain proposals/open or cross-domain questions at the status defined by the UX document;
- these lessons are inputs to future slice design, not a reason to reopen or polish Slice 1.

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

1. Product and UX should define the intended GM/player workflow relevant to the selected next slice rather than extending the Slice 1 bootstrap UI by inertia.
2. Future user-facing work should apply the authoritative guidance in `docs/ux/interaction-principles.md`.
3. Architecture should only implement reusable frontend/error/mutation infrastructure when the next accepted workflow demonstrates the need.
4. Corporate TLS/CA support, if needed for ongoing development, should remain a separate Architecture/DevEx concern.
5. Product should select the next vertical slice through the normal cross-domain process rather than assuming combat, generation, search, or UI polish automatically comes next.

## Closeout status

Slice 1 implementation from PR #7 is merged in `main`.

The UX closeout from PR #9 is also merged in `main`, and `docs/ux/interaction-principles.md` is now the authoritative UX guidance produced from Slice 1 learnings.

This Product closeout remains a planning/closure artifact. It records Product interpretation, unresolved Product questions, explicit non-actions, and coordination boundaries.

It does **not** select Slice 2, rank Slice 2 candidates, or reopen Slice 1.

The Slice 2 selection process is handled separately through the Product candidate-review artifact.
