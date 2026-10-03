# Slice 3 Product Closeout and Slice 4 Candidate Shortlist

**Status:** HUMAN OPTION SELECTED — SLICE SPECIFICATION REQUIRED  
**Owner:** Product Lead  
**Source of truth:** current main after PR #16 merge

This document does not select Slice 4.

# 1. Slice 3 Product closeout

## Durable validated learnings

Slice 3 is ACCEPTED and implemented in main. Human manual testing and the final implementation confirm:

- mechanical FAILURE -> final SUCCESS works;
- mechanical SUCCESS -> final FAILURE works;
- immutable mechanical result and GM-final outcome coexist and remain visibly distinct;
- correction/supersession works without rewriting mechanical evidence;
- already-disclosed knowledge is not falsely rolled back;
- the stale-state issue found during manual testing was fixed locally: creating or replacing Contact prepared information refreshes the KnowledgeFragment choices used by Success reveal without requiring a global Refresh.

The stale-state correction is a durable UX lesson, not an architectural mandate: directly dependent UI state should become coherent after a mutation without requiring a manual global refresh, but this does not imply realtime infrastructure or a generic invalidation framework.

## Manual-test learning: richer action context

The current ActionResolution stores actor, slicing mechanic, Location context, Intent, Risk and the pre-bound success effect. Manual testing showed that this can still make it unclear what person/object/topic the action is actually directed at.

Conceptual example:

    Actor: Globox
    Action: Slicing
    Context: Imperial Cargo Terminal
    Target / Subject: Vic la Menace
    Intent: obtain information about Senator Traitrus
    Risk: Vic sells you out to the senator

This could later improve live readability, meaningful history, entity linking, search/navigation, generation coherence and mechanics where the object of the action matters.

**Status: PROPOSED — CROSS-DOMAIN QUESTION**

Nothing is decided yet about:

- Target vs Subject vs another concept;
- cardinality;
- mandatory vs optional;
- target_entity_id or any other persistence shape;
- multiple targets;
- non-Entity subjects;
- applicability to every ActionResolution.

This observation must not be interpreted as an accepted schema requirement.

# 2. Slice 4 evaluation principles

A credible Slice 4 candidate must deliver one end-to-end user scenario crossing UX, rules/domain semantics, API, persistence, authorization and tests. It must add material Product learning, reuse Slices 1-3 where useful, remain suitable for one developer and avoid horizontal platform work.

The five candidates below are deliberately not ranked.

# CANDIDATE A — GM Requests a Roll, Player Rolls, GM Adjudicates

## NAME
Collaborative Player Roll — bounded one-Player version

## USER VALUE
A Player can actively roll an action requested by the GM from the Player interface instead of every roll being performed by the GM.

Scenario:

    GM creates one slicing request for Globox
    -> Player sees the authorized action and visible stakes
    -> Player presses Roll
    -> backend generates authoritative d20
    -> both sides see immutable mechanical result
    -> GM Finalizes or Overrides using Slice 3 adjudication

One Player and one Character are enough. Multi-Player aggregation is deferred.

## WHY NOW
Slice 3 resolved the largest prerequisite: mechanical evidence, final adjudication, correction and Player-safe resolution projection now exist.

## WHAT WE LEARN
- whether Player-side participation improves live play;
- minimum Player-visible action/stakes context;
- digital-dice trust boundary;
- whether polling/manual refresh is sufficient or a real live-update requirement emerges;
- how GM adjudication feels after a Player-initiated roll.

## REUSE FROM SLICES 1-3
Very high: GM/Player auth, PlayerCharacterAssignment, slicing mechanic, ActionResolution, backend d20, immutable evidence, Finalize/Override/Correct, Player projection, campaign isolation and two-principal E2E.

## PRODUCT QUESTIONS
- Is one Player-requested roll sufficient, deferring true group collaboration?
- Which stakes/context are Player-visible before Roll?
- Can Player decline?
- Does a request expire?
- May GM still Roll on behalf of the Character?
- What freshness is acceptable?

## GAME DESIGN REQUIRED
- Player roll authority;
- visible vs hidden stakes;
- whether backend-generated randomness is authoritative;
- whether one-Player requested rolling can precede lead/assist/group semantics.

## UX REQUIRED
Define GM waiting/result state and Player requested/rolled/finalized state; determine whether polling/manual refresh is acceptable.

## ARCHITECTURE REQUIRED
Player-authorized Roll command derived from assignment; pending eligible resolution read model; concurrency if GM and Player both attempt Roll; no WebSocket assumption.

## SECURITY IMPACT
High. Player cannot alter actor, DC, modifier, hidden stakes, success effect or final outcome, cannot roll for another Character, and must not submit an arbitrary authoritative die value.

## NEW COMPLEXITY
Moderate: Player mutation authority, shared workflow and freshness coordination.

## RISKS
Accidental expansion into full collaboration, realtime overengineering, hidden-stakes leakage, race conditions and a generic request system.

## EXPLICIT EXCLUSIONS
Multiple Players, lead/assist, aggregation, opposed rolls, combat, required WebSockets, client-trusted dice, generic notifications and generic task/request framework.

## BLOCKERS
Game Design must define roll authority/stakes; UX must define waiting/freshness; Architecture must confirm a bounded extension of the current ActionResolution.

# CANDIDATE B — Escape the Imperial Patrol

## NAME
Personal-Scale Combat

## USER VALUE
Run one short objective-driven Star Wars combat encounter inside the product.

Scenario:

    Globox is stopped by an Imperial patrol
    -> combat starts with objective: escape
    -> current turn/action is shown
    -> attack/check resolves
    -> damage/state persists
    -> encounter advances
    -> escape or incapacitation ends encounter

## WHY NOW
Combat is one of the largest core RPG pillars still unproven. Slices 1-3 now provide D20, Character identity, adjudication, security, history and test foundations.

## WHAT WE LEARN
Minimum combat semantics, viability of cinematic non-grid combat, repeated-action UX cost, minimum persistent combat state and whether a bounded Encounter concept is justified.

## REUSE FROM SLICES 1-3
Character, Location, D20 foundations, adjudication principles, auth, projections, history, PostgreSQL transactions and E2E harness.

## PRODUCT QUESTIONS
GM-mediated vs Player-active actions; one PC vs one hostile group; objective/end condition; Player-visible combat state; encounter-scoped vs durable health.

## GAME DESIGN REQUIRED
Turn order, action economy, attack/defence, damage, health/incapacitation, hostile/minion model, end condition and minimum range/position.

## UX REQUIRED
Compact repeated loop with current actor/objective/target/result/state change; no long Intent/Risk form per routine attack.

## ARCHITECTURE REQUIRED
Small combat-specific Encounter, combatants, turns, damage/health and Player projection; avoid generic Scene/rules engine.

## SECURITY IMPACT
Moderate/high: actor/turn/target/action legality server-authoritative; hidden NPC stats protected.

## NEW COMPLEXITY
High — largest new rules and persistence surface.

## RISKS
Scope explosion, permanent health decisions too early, tactical-map creep, generic effects engine and repetitive UX.

## EXPLICIT EXCLUSIONS
Tactical grid, exact movement, reactions, full armour/weapons, critical injuries, Force, talents, progression, vehicles, NPC AI, generic Scene and generic encounter builder.

## BLOCKERS
Game Design combat micro-contract, then UX repeated-action review, then Architecture.

# CANDIDATE C — Generate, Review and Play One Situation

## NAME
Generated Playable Situation

## USER VALUE
GM generates one small structured playable situation, reviews/edits it, accepts it into campaign state and immediately uses at least one generated element in play.

Candidate package: one Location/context, one Contact/Character, one pressure/threat, one secret/claim and one actionable hook.

## WHY NOW
Procedural generation remains a major intended differentiator and is still unvalidated end-to-end. Existing typed campaign state is now sufficient to canonicalize useful output.

## WHAT WE LEARN
Prep-time value, minimum playable structure, review cost, candidate/canonical lifecycle, integration into existing play and whether generated provenance/context has practical value.

## REUSE FROM SLICES 1-3
Location, Character/Contact, KnowledgeFragment, Contact authoring, GM auth, ActionResolution, disclosure and tests.

## PRODUCT QUESTIONS
Exact package; whole vs partial acceptance; candidate persistence; successful 'used in play' criterion; provider mode; minimum editing.

## GAME DESIGN REQUIRED
Define what makes a generated situation playable: pressure, opportunity, actionable choice, secret and relationships.

## UX REQUIRED
Generate -> review -> minimal edit -> Accept/Reject -> canonical -> use in play; candidate and canonical state must be unmistakable.

## ARCHITECTURE REQUIRED
Narrow generator/provider boundary, structured validation, optional staging only if needed, canonicalization through typed services, external data boundary if applicable.

## SECURITY IMPACT
Potentially high with external provider due to campaign-data egress, API keys and untrusted output.

## NEW COMPLEXITY
Medium/high.

## RISKS
Demo value without prep value, review fatigue, schema driven by generated prose, provider abstraction creep and hidden-data leakage.

## EXPLICIT EXCLUSIONS
Galaxy generation, full plot generation, AI GM, background simulation, faction simulation, image generation, generic provider/plugin framework, automatic canonical writes, queues/workers without need and complete NPC combat stats.

## BLOCKERS
Product/Game Design freeze package/playable criterion; UX review burden; Architecture/Security provider and candidate-lifecycle boundaries.

# CANDIDATE D — Remember What You Know and Where It Came From

## NAME
Player Knowledge Library with Acquisition Context

## USER VALUE
Player gets searchable persistent knowledge where each claim may include safe optional acquisition context such as source, Location, time or related resolution.

Knowledge remains 0..N per Character and no-source knowledge remains valid.

## WHY NOW
Knowledge disclosure is proven, but Player UX remains a flat list. Product directions already identify provenance/context/search as useful future capability.

## WHAT WE LEARN
Whether Players use a knowledge library, which metadata helps, whether optional provenance improves investigation and how contradictory claims should be presented.

## REUSE FROM SLICES 1-3
Very high: KnowledgeFragment, CharacterKnowledge, Location, Contact, ActionResolution, Player projections, PostgreSQL search and auth.

## PRODUCT QUESTIONS
Minimum acquisition fields; optional source; timestamp; related roll context; simple search vs filters; contradiction presentation.

## GAME DESIGN REQUIRED
Whether AWARE is enough, contradictory claims, descriptive vs mechanical provenance/confidence and validity of no-source knowledge.

## UX REQUIRED
Claim-first searchable library, compact optional metadata, missing-source handling and no mandatory provenance bookkeeping for GM.

## ARCHITECTURE REQUIRED
Optional acquisition/provenance representation, safe source/location/resolution references and PostgreSQL search; no knowledge graph.

## SECURITY IMPACT
High because source and Location may themselves be secret; claim disclosure must not imply provenance disclosure.

## NEW COMPLEXITY
Moderate.

## RISKS
Over-modeling epistemology, source leakage, confusion between truth/belief/provenance and premature Quest/thread modeling.

## EXPLICIT EXCLUSIONS
Quest system, provenance graph, automatic propagation, misinformation engine, Believed/Doubted unless proven necessary, vector search, Player-to-Player publication and AI summarization.

## BLOCKERS
Game Design contradiction/provenance semantics, UX metadata minimum and Architecture/Security projection rules.

# CANDIDATE E — Publish a Small Intel Catalogue to a Player

## NAME
Campaign Catalogue Publication

## USER VALUE
GM selects existing Character/Contact and Location entities, previews safe fields, publishes them to one Player, and the Player browses a small read-only discovered-world catalogue.

## WHY NOW
Slice 2 proved search/disclosure and Slice 3 proved explicit Player-safe resolution projections. Entity-level discovery/publication remains unproven.

## WHAT WE LEARN
Value of a Player discovered-world catalogue, meaning of entity discovery, safe fields, update/republish behavior, explicit projection maintainability and whether broader campaign search is really needed.

## REUSE FROM SLICES 1-3
Entity identity, Character/Contact, Location, Contact search, projection boundaries, disclosure preview, auth, history and Player workspace.

## PRODUCT QUESTIONS
What is published; durable discovery grant vs snapshot; one Player enough; whether later GM edits flow through; whether entity publication implies attached claims (proposed default: no); minimum Player browse/search.

## GAME DESIGN REQUIRED
Meaning of knowing/discovering an entity, certainty if any, and distinction between entity recognition and claims.

## UX REQUIRED
GM find/select -> preview safe fields -> publish; Player browse/open safe details; avoid full campaign IA redesign.

## ARCHITECTURE REQUIRED
Bounded discovery/publication grant, explicit projections for exactly two types, idempotent publication and minimal selection/search support; no arbitrary field picker.

## SECURITY IMPACT
Very high: GM notes, prepared claims, gm_veracity, hidden relationships, unpublished entities and cross-campaign state must not leak.

## NEW COMPLEXITY
Moderate/high.

## RISKS
Full campaign-database creep, projection abstraction creep, unclear update semantics, entity-vs-claim confusion and navigation expansion.

## EXPLICIT EXCLUSIONS
All entity types, generic CMS, arbitrary field publication, Player editing/notes, relationship graph, automatic secret publication, realtime and external search.

## BLOCKERS
Product/Game Design discovery semantics and live-vs-snapshot behavior; UX/Security safe preview; Architecture bounded projection/grant model.

# 3. Evaluated but not shortlisted as standalone slices

## Richer ActionResolution Target / Subject
The need is real but adding a structured target field by itself is too close to horizontal schema/UI work. Preserve it as an OPEN cross-domain question and resolve only the minimum needed when a selected vertical scenario actually requires structured subject context, such as Player-side rolling, social/opposed action, combat, generation or investigation.

## Broader campaign search
Not a standalone slice. Search should expand only inside a concrete workflow such as Campaign Catalogue Publication.

## Entity lifecycle/archive
Not a standalone slice. Introduce lifecycle semantics only when a user scenario requires retiring/restoring persistent content safely.

## Realtime/WebSockets
Not a standalone slice. Candidate A may prove an actual freshness requirement; transport follows the requirement.

## Full NPC model
Not shortlisted. Continue progressive Character enrichment by selected vertical slices.

## Generic ActionResolution engine
Explicitly not a candidate. Slice 3 validated bounded evolution. Generalization requires a second real mechanic that proves shared concepts.

# 4. Exact Game Design review questions

### Candidate A
1. Can one Player rolling one GM-requested action be accepted without defining group aggregation?
2. Does Player-side Roll change GM adjudication authority?
3. Which Intent/Risk/stakes are Player-visible?
4. Can hidden Risk remain?
5. Is backend-generated digital randomness authoritative?
6. Can GM also Roll on behalf of the Character?
7. What happens to an unrolled request?

### Candidate B
1. Minimum turn order?
2. Minimum action economy?
3. Attack/defence rule?
4. Damage/health/incapacitation?
5. Hostile/minion model?
6. Range/position needed?
7. Objective/end condition?
8. GM-mediated or Player-active?

### Candidate C
1. Exact minimum playable package?
2. Required relationships between generated elements?
3. What Player choice/action must it enable?
4. Is Location + Contact + pressure + claim + hook sufficient?
5. What counts as used in play?

### Candidate D
1. Is AWARE sufficient?
2. Can contradictory claims coexist?
3. Is provenance descriptive only?
4. Does confidence exist in this slice?
5. Can knowledge have no source?
6. Which acquisition metadata has gameplay value?

### Candidate E
1. What does knowing an entity mean?
2. Is discovery binary?
3. Difference from knowing claims?
4. Does publishing an entity imply any claims? Proposed answer: no.
5. Are Character/Contact + Location enough?
6. Live-linked or snapshot-like knowledge semantics?

# 5. Exact UX review questions

### Candidate A
Minimum request card; visible context/stakes; waiting/submitted/finalized states; acceptable polling/refresh; GM participant status; stale-state handling.

### Candidate B
Always-visible combat state; interactions per attack; non-grid clarity; hostile-group presentation; GM-mediated vs Player-active UX; feedback without form fatigue.

### Candidate C
Candidate vs canonical presentation; acceptable review burden; whole vs partial acceptance; minimum editing; failure/latency UX; time from Generate to play.

### Candidate D
Minimum library IA; claim-first presentation; missing source; contradictions without implying truth; simple search sufficiency; fast GM no-provenance path.

### Candidate E
Minimum select/preview/publish flow; exact safe-field preview; already-published state; Player browse/search; later-edit behavior; avoid global navigation redesign.

# 6. Exact Architecture review questions

### Candidate A
Can current ActionResolution represent a pending GM request without generic workflow; exact Player Roll command; server-derived roller; GM/Player concurrency; pending read model; can HTTP + polling suffice; what would justify SSE/WebSockets?

### Candidate B
Smallest combat-specific Encounter; Encounter vs Character state; encounter-scoped health feasibility; hostile-group representation; reuse vs bypass of ActionResolution; avoid Rule Effect DSL/Scene; concurrency for Player-active turns.

### Candidate C
Provider mode; candidate persistence; minimum staging if needed; validation/canonicalization through typed services; allowable outbound campaign context; synchronous HTTP sufficiency; avoid provider/plugin framework.

### Candidate D
CharacterKnowledge vs separate acquisition record; optional source/Location/ActionResolution refs; provenance optionality; PostgreSQL search; independently authorized metadata fields; avoid graph model.

### Candidate E
Minimum discovery/publication grant; live vs snapshot persistence; explicit two-type projections; transactional/idempotent publication; avoid arbitrary serializer; bounded selection/search; leakage tests.

# 7. Human selection

**Date:** 2026-10-03  
**Human Project Owner selection:** **Candidate A — GM Requests a Roll, Player Rolls, GM Adjudicates**

## Selection meaning

Candidate A is selected as the basis for Slice 4 specification.

This is **not yet an ACCEPTED Slice 4 contract**.

The selected Product direction is deliberately bounded to:

```text
GM creates/request one slicing resolution
-> one assigned Player sees the request
-> Player triggers authoritative backend Roll
-> immutable mechanical result
-> GM reviews
-> GM Finalizes or Overrides
-> existing Slice 3 correction/supersession remains available
```

The selection does **not** yet include:

- multiple Players participating in one resolution;
- lead/assist mechanics;
- aggregation of several dice;
- opposed rolls;
- combat;
- generic realtime infrastructure;
- client-generated authoritative randomness;
- generic request/task/notification framework.

## Why this follows naturally from Slices 1-3

Slice 1 proved:

- GM-authored slicing resolution;
- backend D20;
- explicit success/failure consequence handling.

Slice 2 proved:

- richer live-use GM workflows;
- Player-safe disclosure;
- targeted state refresh after content mutation.

Slice 3 proved:

- immutable mechanical evidence;
- separate GM final adjudication;
- both override directions;
- correction/supersession;
- Player-safe finalized-resolution projection.

Candidate A now tests the next narrow authority boundary:

> the Player may initiate the mechanical Roll for an eligible GM-authored resolution, while the backend remains authoritative for randomness and the GM retains final adjudication authority.

## Specification questions still requiring domain review

### Game Design

- exact Player roll authority;
- which Intent/Risk/stakes are visible before Roll;
- whether hidden Risk remains allowed;
- whether GM may still Roll on behalf of Player;
- whether one-Player requested rolling is explicitly accepted while true group collaboration remains deferred.

### UX

- exact GM request flow;
- Player pending-request card;
- waiting/submitted/finalized states;
- acceptable freshness/polling behavior;
- stale-state handling;
- whether any explicit notification is required.

### Architecture

- whether existing ActionResolution can represent a pending Player-roll request with a narrow extension;
- exact Player Roll command/API;
- server-derived eligible roller;
- concurrency between GM and Player Roll attempts;
- Player read model for pending request;
- whether HTTP + bounded polling is sufficient;
- no realtime infrastructure unless the UX requirement proves it necessary.

---

# 8. Selection gate

After the parallel Game Design, UX and Architecture reviews:

1. Product consolidates only the contracts needed for Candidate A.
2. A second review loop is created only if one domain raises a material dependency affecting another domain contract.
3. Product writes the exact Slice 4 specification.
4. Human acceptance is required before Slice 4 becomes ACCEPTED.
5. `docs/planning/current-slice.md` remains on Slice 3 until that acceptance.
6. No implementation begins before the accepted Slice 4 contract is merged to `main`.
