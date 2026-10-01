# UX Interaction Principles

Status: ACTIVE UX GUIDANCE  
Owner: Senior Product / UX Designer  
Origin: Slice 1 closeout synchronization after the accepted and implemented "Slice the terminal, reveal the secret" vertical slice.

## Purpose

This document records durable UX guidance learned from Slice 1.

It deliberately separates:

- interaction principles that should survive replacement of the Slice 1 frontend;
- proposals that still need validation in later workflows;
- open UX questions;
- cross-domain decisions that UX must not make alone.

It does **not** preserve the temporary Slice 1 bootstrap screens as future information architecture, select the next vertical slice, redefine Product scope, or prescribe frontend implementation details.

The numbered Slice 1 setup surfaces, local authentication UI, manual player refresh, and exact bootstrap control layout are proof-oriented implementation details unless a later accepted workflow explicitly reuses them.

---

# ACCEPTED UX GUIDANCE

These principles are normative for future user-facing UX unless an explicit later UX or cross-domain decision supersedes them.

## UX-A01 — Mutations must have an observable lifecycle

A user-triggered mutation must never leave the user guessing whether the action was received, is still running, succeeded, or failed.

The interaction should represent an observable lifecycle equivalent to:

```text
ready
-> in progress
-> completed OR failed
```

The exact presentation is contextual:

- a pending button state may communicate in-progress work;
- the resulting state itself may be sufficient success feedback when the change is immediately obvious;
- a toast, inline confirmation, activity entry, or status message may be appropriate when the result is otherwise ambiguous;
- failures must remain visible long enough to understand and act on them.

This is an interaction requirement, not a requirement to expose technical request or persistence states to users.

### Duplicate submission

While an operation is in progress, the UI must prevent accidental repeated activation when repetition could create duplicate state, conflicting state, or unnecessary requests.

Possible interaction mechanisms include disabling the initiating control, deduplicating an activation, or otherwise making repeated submission harmless.

This does **not** imply any domain-level uniqueness rule.

---

## UX-A02 — Technical failures must become actionable user feedback

Normal product workflows must not expose raw framework/API error payloads, stack-oriented terminology, opaque status codes, or values such as `[object Object]`.

The user-facing result should explain, as far as safely possible:

1. what prevented completion;
2. what the user can do next, when an action is available.

Examples of distinct user-facing categories include:

- invalid or incomplete input;
- authentication required;
- action not permitted;
- conflicting/current-state problem;
- unexpected failure.

UX defines the understandable outcome. The reusable error-normalization mechanism and API error contract remain Architecture-owned.

### Security constraint

Authorization and not-found messaging must not reveal hidden campaign information merely to make an error more specific.

---

## UX-A03 — Known satisfiable constraints should be visible before submission

When the system knows an input requirement that the user can reasonably satisfy before submission, the interface should communicate it before the request is sent.

Use the least intrusive appropriate mechanism:

- clear label or example;
- help text;
- input constraints;
- inline validation;
- disabled submission only when the reason is understandable.

The backend remains authoritative. Client-side validation improves usability; it does not replace domain or security validation.

Server-only or race-dependent constraints may still fail after apparently valid client input and must follow UX-A02.

---

## UX-A04 — Interaction safeguards and domain identity are different problems

Preventing an accidental double-submit does not establish that two domain objects with similar content are invalid duplicates.

The interface must not imply domain uniqueness that has not been accepted.

For example, UX must not assume that identical or similar names, labels, claims, NPC descriptions, or location names are intrinsically invalid.

Potential duplicate-content detection, warning, merging, or uniqueness rules require separate domain/Product decisions.

---

## UX-A05 — Role-dependent UX is campaign-contextual

Under the currently accepted Slice 1 security model, a `Principal` is an authenticated identity and GM/Player role is derived from `CampaignMembership`.

The UX must therefore avoid describing an identity as intrinsically a global "GM account" or "Player account" when the relevant role is campaign-specific.

Role-dependent navigation, permissions, labels, and actions should be presented in the active campaign context.

This guidance reflects the current accepted backend authority model. It does not independently decide future identity-provider or organization-level role models.

---

## UX-A06 — Selection controls must fit the authorized choice set

The choice component should match both the workflow and the size/shape of the collection the user is actually authorized to choose from.

Preferred progression:

- if context uniquely determines the value: prefill or display it instead of asking again;
- for a very small explicit collection: simple selection is appropriate;
- for a larger known collection: searchable selection/combobox may be appropriate;
- if the collection is empty: show a meaningful empty state and next action where permitted.

Do not create a selector whose apparent choice set exceeds what the user is authorized to discover.

Selecting an existing campaign member and discovering/inviting an identity that is not yet part of the campaign are different workflows.

---

## UX-A07 — Use user/domain language, not persistence language

Normal workflows should expose concepts that match the user's task and game understanding.

Do not make users reason in terms of:

- database/table identity;
- ORM or DTO terminology;
- raw `DomainEvent` names;
- transaction state;
- projection internals;
- API lifecycle;
- persistence-specific status names;
- extension payload/storage structure.

Technical terminology may appear in diagnostics or administration only when it genuinely helps the intended user.

History should describe meaningful campaign actions and consequences, not the storage operations used to produce them.

---

## UX-A08 — Live-session interactions must minimize redundant input

During live play, latency includes cognitive and interaction cost, not only network time.

Live workflows should therefore:

- keep the current action and consequences on one compact interaction surface when practical;
- avoid unnecessary navigation;
- avoid multi-step wizards for bounded actions;
- prefill values already determined by current context;
- show fixed contextual values directly instead of forcing reconfirmation through selectors;
- request only information needed for the decision currently being made.

Slice 1 validated this direction by successfully prefilling actor/context/mechanic where unambiguous.

This principle does not require every live action to be completed in a fixed number of clicks.

---

## UX-A09 — Hidden-information disclosure requires an explicit commit boundary

Revealing hidden information is cognitively irreversible: correcting database state later cannot make a player "unsee" information.

Before a disclosure commits, the GM must be able to understand:

- **who** will receive the information;
- **what exact player-visible information** will be disclosed.

The confirmation may be the normal commit action itself, such as an `Apply` action with a clear preview. A second modal is not automatically required.

The UX should add confirmation friction because the action has meaningful disclosure risk, not merely because it changes persistent state.

Backend authorization and projection filtering remain authoritative regardless of confirmation UX.

---

## UX-A10 — Temporary bootstrap/admin surfaces are not product information architecture

Proof-oriented setup controls must not become future workflows through inertia.

The Slice 1 cards used to create principals, memberships, characters, locations, hidden claims, and assignments existed to manufacture test context for one vertical slice.

Future GM/player workflows must be designed from accepted jobs-to-be-done and context, not by progressively polishing or extending those temporary cards.

The same principle applies to:

- temporary local authentication screens;
- manual refresh controls;
- exact Slice 1 form grouping;
- implementation-oriented labels;
- proof-specific navigation.

A temporary surface may be retained only when a later workflow independently validates it.

---

## UX-A11 — User-visible truth and persistence truth must remain conceptually separated

The interface should communicate the product/game effect of an action rather than its storage representation.

Examples:

- "Reveal this information to Ryn" is useful;
- "Create CharacterKnowledge row" is not normal user language.
- "Ryn learned..." is useful history;
- "KnowledgeFragment projection updated" is not.

This principle is especially important when one user action causes several atomic persistence changes.

---

# PROPOSED UX GUIDANCE

These directions are recommended but are not yet strong enough to be treated as normative across the product.

## UX-P01 — Reusable product surfaces should be localization-ready

There is a credible future need for both French and English.

For reusable frontend surfaces, UX recommends avoiding design choices that make later localization unnecessarily expensive, for example:

- layouts that only work for short English strings;
- important meaning encoded into fixed-width text;
- excessive copy embedded directly inside many components;
- icons or abbreviations whose meaning depends on one language.

This does **not** require adding an i18n framework to temporary or disposable UI.

The milestone at which FR/EN becomes a release requirement remains a Product decision.

---

## UX-P02 — Live player state should eventually update without explicit manual refresh

Manual refresh/re-fetch was acceptable for Slice 1 verification but is not a desirable target interaction during live play.

The durable UX need is:

> when another authorized action changes information currently relevant to the player, the player should receive that new state with minimal manual coordination.

UX does not currently prescribe polling, SSE, WebSockets, push, or another transport.

The actual freshness requirement should be defined by a future accepted workflow before Architecture selects a mechanism.

---

# OPEN UX QUESTIONS

The following remain intentionally unresolved after Slice 1.

## OQ-01 — How does a new player join or get invited to a campaign?

Open interaction models include, for example:

- invitation link;
- username/account invitation;
- campaign code;
- explicit request/approval flow;
- another identity-provider-mediated workflow.

The design must establish what identities are discoverable, by whom, and at what point.

Until this is resolved, UX must not assume a global Principal directory.

---

## OQ-02 — Should the product assist with apparent duplicate content?

Potentially useful future behavior could include warnings for similar NPCs, locations, claims, or other authored content.

Open questions include:

- what similarity means per domain concept;
- whether the warning is useful or noisy;
- whether duplicates should merely be surfaced, linked, merged, or ignored.

Slice 1 provides no basis for a universal duplicate-content rule.

---

## OQ-03 — What identity/login experience replaces the Slice 1 local-auth proof?

The local username/password UI was sufficient for Slice 1 but is not a durable UX decision.

The final login/onboarding experience depends on Product, Security, and Architecture choices about identity.

---

## OQ-04 — What freshness is required for live GM/player collaboration?

Before choosing realtime technology, future workflow design must answer:

- which changes must appear immediately;
- what delay is acceptable;
- which events require attention/notification versus silent refresh;
- how disconnected/reconnecting clients behave.

---

## OQ-05 — What is the required FR/EN scope and language-selection model?

Product still needs to decide:

- by which release/milestone both languages are required;
- whether locale is per Principal, device/session, campaign, or another scope;
- whether user-authored campaign content is ever translated by the product or remains authored content;
- whether rules/setting-pack content carries localized variants.

UX should not invent these semantics from the Slice 1 observation alone.

---

# CROSS-DOMAIN DECISION REQUIRED

The following points constrain UX but cannot be made normative by UX alone.

## CD-01 — Player invitation, identity discovery, and Principal visibility

A future invitation flow may require discovering identities outside the current campaign, but a global searchable Principal directory would create Product, privacy, and authorization implications.

### PRODUCT IMPACT

Product must define who can invite whom and what onboarding promise the application provides.

### GAME DESIGN IMPACT

None expected for the base invitation workflow.

### ARCHITECTURE IMPACT

Architecture must define identity lookup/invitation contracts only after the intended workflow and visibility rules are known.

### SECURITY IMPACT

Identity enumeration, privacy, authorization, rate limiting, and information disclosure must be considered before exposing any directory/search capability.

---

## CD-02 — Future role model beyond current CampaignMembership

Current UX must reflect the accepted campaign-scoped GM/Player role behavior.

Any future proposal for global roles, organization roles, multiple GM permission levels, spectators, content authors, or other identities would require explicit reopening rather than being inferred from UI needs.

### PRODUCT IMPACT

Changes personas, permissions, onboarding, and navigation.

### GAME DESIGN IMPACT

Potential impact if new roles can participate in adjudication or play.

### ARCHITECTURE IMPACT

Changes authorization and persistence contracts.

### SECURITY IMPACT

Role authority must remain backend-derived; client labels or token claims cannot become the security boundary.

---

## CD-03 — FR/EN release requirement and localization architecture

UX can design localization-ready surfaces but cannot declare the shipping milestone or implementation architecture.

### PRODUCT IMPACT

Product must prioritize and define the bilingual release requirement.

### GAME DESIGN IMPACT

Game-system terminology may require an authoritative localized vocabulary.

### ARCHITECTURE IMPACT

Architecture/frontend implementation must choose localization infrastructure when a concrete accepted slice requires it.

### SECURITY IMPACT

No special impact beyond avoiding locale-dependent authorization/business logic.

---

## CD-04 — Live update requirement and transport

UX can state that manual refresh is not the long-term target for live collaboration, but transport is not a UX decision.

### PRODUCT IMPACT

Product must determine whether live freshness is mandatory for the relevant MVP workflows.

### GAME DESIGN IMPACT

Some future mechanics may impose stronger timing requirements than Slice 1.

### ARCHITECTURE IMPACT

Polling, SSE, WebSockets, or another mechanism should be selected from concrete latency/freshness needs rather than anticipated scale.

### SECURITY IMPACT

Any live channel must enforce the same campaign, role, assignment, and disclosure boundaries as normal read APIs.

---

# Slice 1 observations explicitly treated as temporary

The following are **not** promoted to durable product UX by this document:

- the numbered bootstrap card sequence;
- the exact "Add Player", "Create Character", "Create Location", "Create hidden claim", and "Assign Player" forms;
- local username/password authentication UI;
- manual browser refresh as normal live behavior;
- the exact API request/response shapes exposed by Slice 1 implementation;
- a globally searchable Principal list;
- an i18n framework;
- a generic duplicate-content detector;
- a generic notification/toast system;
- a generic undo framework;
- Slice 1-specific field ordering when future context can remove fields entirely.

---

# Relationship to existing UX guidance

This document complements `docs/ux/pre-kickoff-sync.md`.

Where the pre-kickoff document describes proposals and questions before implementation, this document records interaction guidance strengthened by the completed Slice 1 and its manual test.

Accepted Architecture, Product, Game Design, Security, and planning decisions remain authoritative in their respective areas. This document does not silently supersede them.
