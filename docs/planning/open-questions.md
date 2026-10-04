# Open Questions

Questions requiring future cross-domain arbitration are recorded here.

Every item in this file is **OPEN — DEFERRED** and therefore non-normative until a future accepted slice or explicit decision resolves it.

Resolved Slice 3, Slice 4 and Slice 5 decisions do **not** belong here. This includes binary Override in both directions, correction-by-supersession, Player-side Roll for explicitly PLAYER-authority resolutions, backend-authoritative randomness, explicit Risk visibility, the accepted bounded-polling strategies, and Slice 5's combat-specific Encounter contract.

## Format

### Q-XXX — Title

**Owner:**  
**Affected domains:**  
**Context:**  
**Options:**  
**Decision required:**  
**Status:** OPEN — DEFERRED

---

### Q-001 — Player-visible knowledge source provenance

**Owner:** Game Design / UX / Architecture  
**Affected domains:** Game Design, UX, Architecture, Security  
**Context:** Slice 2 reveals the claim only. It does not persist or display `Source: Nira Voss` to the Player. Source provenance may become useful in a later knowledge/investigation slice where remembering who supplied a claim affects Player decisions.  
**Options:** claim-only; persisted/displayed source provenance; richer provenance model.  
**Decision required:** only when a future accepted scenario needs source provenance.  
**Status:** OPEN — DEFERRED

### Q-002 — Contact/NPC model expansion

**Owner:** Product / Game Design / Architecture  
**Affected domains:** Product, Game Design, Architecture, UX  
**Context:** Slice 2 accepts only a narrow Contact typed profile using Character identity. It does not define the canonical full NPC model. Future Product direction expects Characters/NPCs to gain capabilities incrementally, potentially including 0..N knowledge, inventory and mechanical profiles when selected slices require them.  
**Options:** add fields/capabilities incrementally per accepted slice; define richer NPC model later if repeated scenarios justify it.  
**Decision required:** only when a future slice needs additional NPC mechanics/data.  
**Status:** OPEN — DEFERRED

### Q-003 — Multi-entity/global campaign search

**Owner:** Product / UX / Architecture  
**Affected domains:** Product, UX, Architecture, Security  
**Context:** Slice 2 search is GM-only, current-campaign, Contacts-only. It does not establish a generic global search platform.  
**Options:** remain entity-specific; evolve to multi-entity campaign search; later command-palette/global-search experience.  
**Decision required:** only when a future workflow needs search across multiple entity types.  
**Status:** OPEN — DEFERRED

### Q-004 — Search scaling strategy

**Owner:** Architecture  
**Affected domains:** Architecture, UX, Product  
**Context:** Slice 2 accepts PostgreSQL `ILIKE` search at expected campaign scale.  
**Options:** retain simple PostgreSQL search; add `pg_trgm`; add PostgreSQL full-text; external search only if measured need justifies it.  
**Decision required:** only after measured scale/latency demonstrates a need.  
**Status:** OPEN — DEFERRED

### Q-005 — Realtime Player updates

**Owner:** Product / UX / Architecture  
**Affected domains:** Product, UX, Architecture  
**Context:** Slice 4 accepts bounded HTTP polling for its one-Player live roll workflow, and Slice 5 accepts immediate re-fetch plus bounded polling targeting approximately one second during active sequential combat. Both explicitly reject push transport as unnecessary for their accepted workflows. A future workflow may still demonstrate that polling is insufficient.  
**Options:** retain bounded polling; SSE; WebSockets; another bounded push mechanism.  
**Decision required:** only when a future accepted live-play workflow demonstrates measured usability or freshness requirements that the Slice 4/5 polling patterns cannot satisfy.  
**Status:** OPEN — DEFERRED

### Q-006 — Contact/entity authoring lifecycle

**Owner:** Product / UX / Architecture  
**Affected domains:** Product, UX, Architecture  
**Context:** Existing slices do not require generic archive/delete/restore or generic authoring undo. Persistent campaign references/history mean lifecycle semantics must be domain-specific.  
**Options:** targeted history; archive/deactivate; restore; selective correction; hard-delete only when safe; no broader lifecycle until needed.  
**Decision required:** only when a future workflow needs authoring lifecycle controls.  
**Status:** OPEN — DEFERRED

### Q-007 — Player-visible DC policy beyond Slice 3

**Owner:** Product / Game Design / UX  
**Affected domains:** Product, Game Design, UX, Security  
**Context:** Slice 3 and Slice 4 keep ActionResolution DC hidden from the Player. Slice 5 explicitly exposes the combat Defence threshold inside bounded combat action feedback. These are mechanic-specific decisions and still do not establish one universal visibility rule for all future checks.  
**Options:** keep thresholds hidden by default; expose them for specific mechanics/workflows; configurable table-style policy if later justified.  
**Decision required:** only when a future accepted mechanic requires a general threshold-visibility policy beyond the mechanic-specific Slice 3-5 decisions.  
**Status:** OPEN — DEFERRED

### Q-008 — Future reroll / metacurrency semantics

**Owner:** Game Design / Product  
**Affected domains:** Game Design, Product, UX, Architecture  
**Context:** Slice 3 defines one immutable raw roll per ActionResolution and explicitly excludes reroll mechanics, fate points/metacurrency and advantage/disadvantage expansion. A future reroll mechanic must not be modeled as editing the historical raw roll.  
**Options:** new roll event/resolution; bounded reroll lineage; metacurrency-specific rule contract.  
**Decision required:** only when a future accepted rules slice introduces rerolls or metacurrency.  
**Status:** OPEN — DEFERRED

### Q-009 — Structured action Target / Subject

**Owner:** Product / Game Design / UX / Architecture  
**Affected domains:** Product, Game Design, UX, Architecture, Security  
**Context:** Manual testing across Slices 3-4 shows that Actor + mechanic + Location context + free-text Intent/Risk may not clearly identify what an action is fictionally about. Slice 5 evaluated this need but did not require a universal Subject model: combat has one server-derived hostile target and explicitly excludes universal Target/Subject semantics. The broader fictional Subject may still be ephemeral and need no persistent Entity at all; optional Entity enrichment must not be presumed.  
**Options:** display/free-text subject; one optional Subject with optional Entity enrichment; mechanic-specific structured subject/target; multiple subjects where a future mechanic proves the need; another bounded representation.  
**Decision required:** revisit only when a future accepted non-combat or multi-target workflow actually requires structured fictional Subject semantics. Game Design must distinguish mechanical target, fictional subject, effect recipient and contextual entity; UX must establish minimum live-entry cost; Architecture must wait for those contracts before choosing persistence. Do not infer target_entity_id, Entity-only semantics, singular cardinality, requiredness or universal applicability.  
**Status:** OPEN — DEFERRED
