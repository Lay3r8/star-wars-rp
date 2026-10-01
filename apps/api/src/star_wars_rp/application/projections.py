import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from star_wars_rp.application.campaigns import ROLE_PLAYER, require_membership
from star_wars_rp.errors import NotFound
from star_wars_rp.modules.campaigns.models import PlayerCharacterAssignment
from star_wars_rp.modules.characters.models import Character
from star_wars_rp.modules.custom_d20.models import CustomD20CharacterProfile
from star_wars_rp.modules.knowledge.models import CharacterKnowledge, KnowledgeFragment


def player_character_projection(
    db: Session,
    principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
) -> dict:
    require_membership(db, principal_id, campaign_id, ROLE_PLAYER)
    assignment = db.get(
        PlayerCharacterAssignment,
        {"campaign_id": campaign_id, "player_principal_id": principal_id},
    )
    if assignment is None:
        raise NotFound("No character assignment for Player")

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
