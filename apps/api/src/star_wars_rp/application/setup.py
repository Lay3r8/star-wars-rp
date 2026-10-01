import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from star_wars_rp.application.campaigns import require_gm
from star_wars_rp.modules.characters.models import Character
from star_wars_rp.modules.custom_d20.models import CustomD20CharacterProfile
from star_wars_rp.modules.entities.models import Entity
from star_wars_rp.modules.knowledge.models import KnowledgeFragment
from star_wars_rp.modules.world.models import Location


def create_character(
    db: Session,
    gm_principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
    name: str,
    slicing_modifier: int,
) -> dict:
    require_gm(db, gm_principal_id, campaign_id)
    entity = Entity(campaign_id=campaign_id, entity_type="character")
    db.add(entity)
    db.flush()
    character = Character(entity_id=entity.id, campaign_id=campaign_id, name=name.strip())
    profile = CustomD20CharacterProfile(
        character_id=entity.id,
        campaign_id=campaign_id,
        slicing_modifier=slicing_modifier,
    )
    db.add_all([character, profile])
    db.commit()
    return {"id": entity.id, "name": character.name, "slicing_modifier": slicing_modifier}


def list_characters(db: Session, gm_principal_id: uuid.UUID, campaign_id: uuid.UUID) -> list[dict]:
    require_gm(db, gm_principal_id, campaign_id)
    rows = db.execute(
        select(Character, CustomD20CharacterProfile.slicing_modifier)
        .join(
            CustomD20CharacterProfile,
            (CustomD20CharacterProfile.campaign_id == Character.campaign_id)
            & (CustomD20CharacterProfile.character_id == Character.entity_id),
        )
        .where(Character.campaign_id == campaign_id)
        .order_by(Character.name)
    ).all()
    return [
        {"id": character.entity_id, "name": character.name, "slicing_modifier": modifier}
        for character, modifier in rows
    ]


def create_location(
    db: Session,
    gm_principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
    name: str,
) -> dict:
    require_gm(db, gm_principal_id, campaign_id)
    entity = Entity(campaign_id=campaign_id, entity_type="location")
    db.add(entity)
    db.flush()
    location = Location(entity_id=entity.id, campaign_id=campaign_id, name=name.strip())
    db.add(location)
    db.commit()
    return {"id": entity.id, "name": location.name}


def list_locations(db: Session, gm_principal_id: uuid.UUID, campaign_id: uuid.UUID) -> list[dict]:
    require_gm(db, gm_principal_id, campaign_id)
    rows = db.scalars(
        select(Location).where(Location.campaign_id == campaign_id).order_by(Location.name)
    ).all()
    return [{"id": location.entity_id, "name": location.name} for location in rows]


def create_knowledge_fragment(
    db: Session,
    gm_principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
    claim_text: str,
    gm_veracity: str,
) -> dict:
    require_gm(db, gm_principal_id, campaign_id)
    fragment = KnowledgeFragment(
        campaign_id=campaign_id,
        claim_text=claim_text.strip(),
        gm_veracity=gm_veracity,
    )
    db.add(fragment)
    db.commit()
    db.refresh(fragment)
    return {
        "id": fragment.id,
        "claim_text": fragment.claim_text,
        "gm_veracity": fragment.gm_veracity,
    }


def list_knowledge_fragments(
    db: Session,
    gm_principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
) -> list[dict]:
    require_gm(db, gm_principal_id, campaign_id)
    rows = db.scalars(
        select(KnowledgeFragment)
        .where(KnowledgeFragment.campaign_id == campaign_id)
        .order_by(KnowledgeFragment.created_at)
    ).all()
    return [
        {"id": fragment.id, "claim_text": fragment.claim_text, "gm_veracity": fragment.gm_veracity}
        for fragment in rows
    ]
