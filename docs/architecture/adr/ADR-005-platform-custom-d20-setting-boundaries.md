# ADR-005 — Platform Core, Custom D20, and Setting Pack boundaries

## Status

ACCEPTED

## Context

The platform needs reusable cross-cutting capabilities without prematurely building a runtime that can dynamically swap arbitrary RPG systems.

## Decision

Custom D20 is a first-party game system for the MVP.

Platform Core contains only concepts that are genuinely cross-cutting across game-system/setting concerns.

Species, Class, Skills, Talents, progression mechanics, and Force mechanics belong to Custom D20 rather than Platform Core.

Setting Packs are primarily data-oriented. They provide setting data and reference mechanics that Custom D20 explicitly supports.

Campaign-specific horror/entity mechanics remain outside Platform Core unless later evidence shows they are truly cross-cutting.

## Consequences

- First-party mechanics may use normal application-owned migrations.
- The MVP does not require a generic dynamically interchangeable game-system runtime.
- Setting data remains separable from mechanical semantics.
- Cross-domain changes to game rules require Game Design review.

## Alternatives considered

- Put all current Star Wars RPG concepts into Platform Core: rejected because it creates false generality.
- Build an arbitrary hot-swappable game-system plugin runtime now: rejected as premature complexity.
