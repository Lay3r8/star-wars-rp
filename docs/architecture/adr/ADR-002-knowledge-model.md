# ADR-002 — Canonical claims and character knowledge

## Status

ACCEPTED

## Context

The application must distinguish GM-side reality from what individual characters have heard, believe, doubt, or know. False information and partial knowledge are first-class gameplay concerns.

## Decision

`KnowledgeFragment` represents a proposition/claim in the campaign knowledge graph and carries GM-side veracity metadata.

`CharacterKnowledge` represents the epistemic state of one character toward one `KnowledgeFragment`.

Absence of `CharacterKnowledge` means that the fragment is unknown to that character.

Character ignorance is therefore not a `KnowledgeFragment` truth/veracity state.

## Consequences

- The same claim can be false in GM reality but believed by one or more characters.
- Different characters can hold different epistemic states for the same claim.
- Player-visible knowledge must be derived from character knowledge, not from canonical entity fields alone.
- Game Design remains responsible for the exact allowed epistemic states and any gameplay effects tied to them.

## Alternatives considered

- One truth/visibility flag on canonical data: rejected because it cannot represent misinformation and differing beliefs.
- Copying canonical facts into per-character records: rejected because it duplicates identity and provenance.
