# Open Questions

Questions requiring future cross-domain arbitration are recorded here.

These questions are explicitly **deferred** from the accepted Slice 2 contract. They are not implementation requirements for Slice 2.

## Format

### Q-XXX — Title

**Owner:**  
**Affected domains:**  
**Context:**  
**Options:**  
**Decision required:**  
**Status:** OPEN

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
**Context:** Slice 2 accepts only a narrow Contact typed profile using Character identity. It does not define the canonical full NPC model.  
**Options:** add fields incrementally per accepted slice; define richer NPC model later if repeated scenarios justify it.  
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
**Context:** Slice 2 accepts PostgreSQL `ILIKE` search with ordinary indexes at expected campaign scale.  
**Options:** retain simple scan; add `pg_trgm`; add PostgreSQL full-text; external search only if measured need justifies it.  
**Decision required:** only after measured scale/latency demonstrates a need.  
**Status:** OPEN — DEFERRED

### Q-005 — Realtime Player disclosure updates

**Owner:** Product / UX / Architecture  
**Affected domains:** Product, UX, Architecture  
**Context:** Slice 2 may continue using refresh/re-fetch for Player-visible disclosure. Realtime delivery is explicitly outside scope.  
**Options:** manual refresh; polling; SSE; WebSockets; another bounded push mechanism.  
**Decision required:** when a future accepted live-play workflow demonstrates that manual refresh materially harms usability.  
**Status:** OPEN — DEFERRED

### Q-006 — Contact authoring history and lifecycle

**Owner:** Product / UX / Architecture  
**Affected domains:** Product, UX, Architecture  
**Context:** Slice 2 does not require Contact create/edit DomainEvents, archive/delete, or generic undo. Disclosure history remains meaningful and required.  
**Options:** targeted history; archive/deactivate; selective undo/correction; no broader lifecycle until needed.  
**Decision required:** only when a future workflow needs authoring audit/lifecycle controls.  
**Status:** OPEN — DEFERRED
