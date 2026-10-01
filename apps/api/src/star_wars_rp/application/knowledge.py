import uuid

from sqlalchemy.orm import Session

from star_wars_rp.modules.knowledge.models import CharacterKnowledge


def make_character_aware(
    db: Session,
    campaign_id: uuid.UUID,
    character_id: uuid.UUID,
    fragment_id: uuid.UUID,
) -> CharacterKnowledge:
    knowledge = db.get(
        CharacterKnowledge,
        {
            "campaign_id": campaign_id,
            "character_id": character_id,
            "fragment_id": fragment_id,
        },
    )
    if knowledge is None:
        knowledge = CharacterKnowledge(
            campaign_id=campaign_id,
            character_id=character_id,
            fragment_id=fragment_id,
            state="AWARE",
        )
        db.add(knowledge)
    else:
        knowledge.state = "AWARE"
    return knowledge
