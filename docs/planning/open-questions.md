# Open Questions

Questions requiring future cross-domain arbitration are recorded here.

Every item in this file is **OPEN — DEFERRED** and therefore non-normative until a future accepted slice or explicit decision resolves it.

Resolved Slice 3 decisions — including binary Override in both directions, correction-by-supersession, required correction reason, optional override reason, Player resolution visibility without DC, and narrow evolution of the existing ActionResolution — do **not** belong here.

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
**Context:** Slice 2 and Slice 3 do not establish a realtime transport requirement. Refresh/re-fetch or bounded polling remains sufficient for their accepted workflows. Future collaborative/live workflows may create a stronger freshness requirement.  
**Options:** manual refresh; polling; SSE; WebSockets; another bounded push mechanism.  
**Decision required:** when a future accepted live-play workflow demonstrates that request/response or refresh materially harms usability.  
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
**Context:** Slice 3 explicitly keeps DC hidden from the Player while exposing raw roll, modifier, total, mechanical result and final outcome. That decision is normative for Slice 3 only and does not establish a universal hidden-DC rule for all future mechanics.  
**Options:** keep DC hidden by default; expose DC for specific mechanics/workflows; configurable table-style policy if later justified.  
**Decision required:** only when a future accepted mechanic or Player workflow benefits from explicit DC visibility.  
**Status:** OPEN — DEFERRED

### Q-008 — Future reroll / metacurrency semantics

**Owner:** Game Design / Product  
**Affected domains:** Game Design, Product, UX, Architecture  
**Context:** Slice 3 defines one immutable raw roll per ActionResolution and explicitly excludes reroll mechanics, fate points/metacurrency and advantage/disadvantage expansion. A future reroll mechanic must not be modeled as editing the historical raw roll.  
**Options:** new roll event/resolution; bounded reroll lineage; metacurrency-specific rule contract.  
**Decision required:** only when a future accepted rules slice introduces rerolls or metacurrency.  
**Status:** OPEN — DEFERRED
