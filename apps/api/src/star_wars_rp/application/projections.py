import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from star_wars_rp.application.campaigns import ROLE_PLAYER, require_membership
from star_wars_rp.errors import NotFound
from star_wars_rp.modules.campaigns.models import PlayerCharacterAssignment
from star_wars_rp.modules.characters.models import Character
from star_wars_rp.modules.custom_d20.models import CustomD20CharacterProfile
from star_wars_rp.modules.history.models import DomainEvent
from star_wars_rp.modules.knowledge.models import CharacterKnowledge, KnowledgeFragment
from star_wars_rp.modules.resolutions.models import ActionResolution
from star_wars_rp.modules.world.models import Location


def _player_assignment(
    db: Session,
    principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
) -> PlayerCharacterAssignment:
    require_membership(db, principal_id, campaign_id, ROLE_PLAYER)
    assignment = db.get(
        PlayerCharacterAssignment,
        {"campaign_id": campaign_id, "player_principal_id": principal_id},
    )
    if assignment is None:
        raise NotFound("No character assignment for Player")
    return assignment


def player_character_projection(
    db: Session,
    principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
) -> dict:
    assignment = _player_assignment(db, principal_id, campaign_id)

    character = db.scalar(
        select(Character).where(
            Character.campaign_id == campaign_id,
            Character.entity_id == assignment.character_id,
        )
    )
    profile = db.scalar(
        select(CustomD20CharacterProfile).where(
            CustomD20CharacterProfile.campaign_id == campaign_id,
            CustomD20CharacterProfile.character_id == assignment.character_id,
        )
    )
    if character is None or profile is None:
        raise NotFound("Assigned character is unavailable")

    knowledge_rows = db.execute(
        select(CharacterKnowledge, KnowledgeFragment.claim_text)
        .join(
            KnowledgeFragment,
            (KnowledgeFragment.campaign_id == CharacterKnowledge.campaign_id)
            & (KnowledgeFragment.id == CharacterKnowledge.fragment_id),
        )
        .where(
            CharacterKnowledge.campaign_id == campaign_id,
            CharacterKnowledge.character_id == assignment.character_id,
            CharacterKnowledge.state == "AWARE",
        )
        .order_by(CharacterKnowledge.acquired_at)
    ).all()

    return {
        "campaign_id": campaign_id,
        "character": {
            "id": character.entity_id,
            "name": character.name,
            "slicing_modifier": profile.slicing_modifier,
        },
        "knowledge": [
            {
                "fragment_id": record.fragment_id,
                "state": record.state,
                "claim_text": claim_text,
            }
            for record, claim_text in knowledge_rows
        ],
    }



def player_pending_resolution_projection(
    db: Session,
    principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
    resolution_id: uuid.UUID | None = None,
) -> dict | None:
    assignment = _player_assignment(db, principal_id, campaign_id)

    stmt = (
        select(ActionResolution, Character.name, Location.name)
        .join(
            Character,
            (Character.campaign_id == ActionResolution.campaign_id)
            & (Character.entity_id == ActionResolution.actor_character_id),
        )
        .join(
            Location,
            (Location.campaign_id == ActionResolution.campaign_id)
            & (Location.entity_id == ActionResolution.context_location_id),
        )
        .where(
            ActionResolution.campaign_id == campaign_id,
            ActionResolution.actor_character_id == assignment.character_id,
            ActionResolution.roll_authority == "PLAYER",
            ActionResolution.state.in_(["READY", "AWAITING_ADJUDICATION"]),
        )
    )
    if resolution_id is not None:
        stmt = stmt.where(ActionResolution.id == resolution_id)
    else:
        stmt = stmt.order_by(
            ActionResolution.created_at.desc(),
            ActionResolution.id.desc(),
        ).limit(1)

    row = db.execute(stmt).first()
    if row is None:
        return None

    resolution, actor_name, location_name = row
    rolled = resolution.state == "AWAITING_ADJUDICATION"
    return {
        "resolution_id": resolution.id,
        "actor_character_id": resolution.actor_character_id,
        "actor_name": actor_name,
        "mechanic": "Slicing",
        "context_location_id": resolution.context_location_id,
        "context_location_name": location_name,
        "intent": resolution.intent,
        "known_risk": (
            resolution.risk
            if resolution.risk_visibility == "PLAYER_VISIBLE"
            else None
        ),
        "state": resolution.state,
        "natural_roll": resolution.natural_roll if rolled else None,
        "resolved_modifier": resolution.resolved_modifier if rolled else None,
        "total": resolution.total if rolled else None,
        "mechanical_result": resolution.mechanical_result if rolled else None,
    }

def player_resolution_projection(
    db: Session,
    principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
) -> dict | None:
    assignment = _player_assignment(db, principal_id, campaign_id)

    resolution = db.scalar(
        select(ActionResolution)
        .where(
            ActionResolution.campaign_id == campaign_id,
            ActionResolution.actor_character_id == assignment.character_id,
        )
        .order_by(ActionResolution.created_at.desc(), ActionResolution.id.desc())
        .limit(1)
    )
    if resolution is None or resolution.state != "FINALIZED":
        return None

    previous_final_outcome = None
    if resolution.adjudication_revision > 1:
        correction = db.scalar(
            select(DomainEvent)
            .where(
                DomainEvent.campaign_id == campaign_id,
                DomainEvent.subject_id == resolution.id,
                DomainEvent.event_type == "resolution.adjudication_corrected",
            )
            .order_by(DomainEvent.occurred_at.desc(), DomainEvent.id.desc())
            .limit(1)
        )
        if correction is not None:
            candidate = correction.payload.get("previous_final_outcome")
            if candidate in {"SUCCESS", "FAILURE"}:
                previous_final_outcome = candidate

    return {
        "resolution_id": resolution.id,
        "natural_roll": resolution.natural_roll,
        "resolved_modifier": resolution.resolved_modifier,
        "total": resolution.total,
        "mechanical_result": resolution.mechanical_result,
        "final_outcome": resolution.final_outcome,
        "is_overridden": resolution.final_outcome != resolution.mechanical_result,
        "is_corrected": resolution.adjudication_revision > 1,
        "previous_final_outcome": previous_final_outcome,
    }
