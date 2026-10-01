import uuid

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from star_wars_rp.application.campaigns import require_gm
from star_wars_rp.application.history import append_domain_event
from star_wars_rp.application.knowledge import make_character_aware
from star_wars_rp.errors import InvalidOperation, NotFound
from star_wars_rp.modules.campaigns.models import CampaignMembership, PlayerCharacterAssignment
from star_wars_rp.modules.characters.models import Character
from star_wars_rp.modules.contacts.models import Contact
from star_wars_rp.modules.entities.models import Entity
from star_wars_rp.modules.knowledge.models import CharacterKnowledge, KnowledgeFragment
from star_wars_rp.modules.world.models import Location


def _require_location(db: Session, campaign_id: uuid.UUID, location_id: uuid.UUID) -> Location:
    location = db.scalar(
        select(Location).where(
            Location.campaign_id == campaign_id,
            Location.entity_id == location_id,
        )
    )
    if location is None:
        raise NotFound("Location not found in campaign")
    return location


def _contact(db: Session, campaign_id: uuid.UUID, contact_id: uuid.UUID, *, for_update: bool = False) -> Contact:
    stmt = select(Contact).where(
        Contact.campaign_id == campaign_id,
        Contact.character_id == contact_id,
    )
    if for_update:
        stmt = stmt.with_for_update()
    contact = db.scalar(stmt)
    if contact is None:
        raise NotFound("Contact not found in campaign")
    return contact


def _character(db: Session, campaign_id: uuid.UUID, character_id: uuid.UUID) -> Character:
    character = db.scalar(
        select(Character).where(
            Character.campaign_id == campaign_id,
            Character.entity_id == character_id,
        )
    )
    if character is None:
        raise NotFound("Character not found in campaign")
    return character


def _fragment(db: Session, campaign_id: uuid.UUID, fragment_id: uuid.UUID) -> KnowledgeFragment:
    fragment = db.scalar(
        select(KnowledgeFragment).where(
            KnowledgeFragment.campaign_id == campaign_id,
            KnowledgeFragment.id == fragment_id,
        )
    )
    if fragment is None:
        raise NotFound("Prepared information not found in campaign")
    return fragment


def _assigned_recipient(
    db: Session,
    campaign_id: uuid.UUID,
    recipient_character_id: uuid.UUID,
) -> Character:
    assignment = db.scalar(
        select(PlayerCharacterAssignment)
        .join(
            CampaignMembership,
            (CampaignMembership.campaign_id == PlayerCharacterAssignment.campaign_id)
            & (CampaignMembership.principal_id == PlayerCharacterAssignment.player_principal_id),
        )
        .where(
            PlayerCharacterAssignment.campaign_id == campaign_id,
            PlayerCharacterAssignment.character_id == recipient_character_id,
            CampaignMembership.role == "PLAYER",
        )
    )
    if assignment is None:
        raise NotFound("Recipient is not an assigned Player Character in campaign")
    return _character(db, campaign_id, recipient_character_id)


def _single_reveal_preview(db: Session, campaign_id: uuid.UUID, claim_text: str) -> dict | None:
    rows = db.execute(
        select(PlayerCharacterAssignment.character_id, Character.name)
        .join(
            Character,
            (Character.campaign_id == PlayerCharacterAssignment.campaign_id)
            & (Character.entity_id == PlayerCharacterAssignment.character_id),
        )
        .where(PlayerCharacterAssignment.campaign_id == campaign_id)
        .order_by(Character.name, PlayerCharacterAssignment.character_id)
        .limit(2)
    ).all()
    if len(rows) != 1:
        return None
    character_id, name = rows[0]
    return {
        "recipient_character_id": character_id,
        "recipient_name": name,
        "claim_text": claim_text,
    }


def _required_text(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise InvalidOperation(f"{field_name} must not be blank")
    return normalized


def create_contact(
    db: Session,
    gm_principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
    *,
    name: str,
    role: str,
    location_id: uuid.UUID,
    gm_note: str | None,
    claim_text: str,
    gm_veracity: str,
) -> dict:
    require_gm(db, gm_principal_id, campaign_id)
    _require_location(db, campaign_id, location_id)
    name = _required_text(name, "Name")
    role = _required_text(role, "Role")
    claim_text = _required_text(claim_text, "Prepared information")

    entity = Entity(campaign_id=campaign_id, entity_type="character")
    db.add(entity)
    db.flush()

    character = Character(entity_id=entity.id, campaign_id=campaign_id, name=name)
    fragment = KnowledgeFragment(
        campaign_id=campaign_id,
        claim_text=claim_text,
        gm_veracity=gm_veracity,
    )
    db.add_all([character, fragment])
    db.flush()

    contact = Contact(
        campaign_id=campaign_id,
        character_id=character.entity_id,
        role=role,
        location_id=location_id,
        gm_note=(gm_note.strip() or None) if gm_note else None,
        prepared_fragment_id=fragment.id,
    )
    db.add(contact)
    db.commit()
    return get_contact_summary(db, gm_principal_id, campaign_id, contact.character_id)


def update_contact(
    db: Session,
    gm_principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
    contact_id: uuid.UUID,
    *,
    name: str,
    role: str,
    location_id: uuid.UUID,
    gm_note: str | None,
    claim_text: str,
    gm_veracity: str,
) -> dict:
    require_gm(db, gm_principal_id, campaign_id)
    contact = _contact(db, campaign_id, contact_id, for_update=True)
    character = _character(db, campaign_id, contact.character_id)
    _require_location(db, campaign_id, location_id)
    current_fragment = _fragment(db, campaign_id, contact.prepared_fragment_id)
    name = _required_text(name, "Name")
    role = _required_text(role, "Role")
    normalized_claim = _required_text(claim_text, "Prepared information")

    if normalized_claim != current_fragment.claim_text or gm_veracity != current_fragment.gm_veracity:
        replacement = KnowledgeFragment(
            campaign_id=campaign_id,
            claim_text=normalized_claim,
            gm_veracity=gm_veracity,
        )
        db.add(replacement)
        db.flush()
        contact.prepared_fragment_id = replacement.id

    character.name = name
    contact.role = role
    contact.location_id = location_id
    contact.gm_note = (gm_note.strip() or None) if gm_note else None

    db.commit()
    return get_contact_summary(db, gm_principal_id, campaign_id, contact_id)


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def search_contacts(
    db: Session,
    gm_principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
    query: str,
    *,
    limit: int = 20,
) -> list[dict]:
    require_gm(db, gm_principal_id, campaign_id)
    query = query.strip()
    if not query:
        return []

    pattern = f"%{_escape_like(query)}%"
    name_match = Character.name.ilike(pattern, escape="\\")
    role_match = Contact.role.ilike(pattern, escape="\\")

    rows = db.execute(
        select(
            Contact.character_id,
            Character.name,
            Contact.role,
            Location.name.label("location_name"),
        )
        .join(
            Character,
            (Character.campaign_id == Contact.campaign_id)
            & (Character.entity_id == Contact.character_id),
        )
        .join(
            Location,
            (Location.campaign_id == Contact.campaign_id)
            & (Location.entity_id == Contact.location_id),
        )
        .where(Contact.campaign_id == campaign_id, name_match | role_match)
        .order_by(
            case((name_match, 0), else_=1),
            func.lower(Character.name),
            Contact.character_id,
        )
        .limit(limit)
    ).all()

    return [
        {
            "contact_id": contact_id,
            "name": name,
            "role": role,
            "location_name": location_name,
        }
        for contact_id, name, role, location_name in rows
    ]


def get_contact_summary(
    db: Session,
    gm_principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
    contact_id: uuid.UUID,
) -> dict:
    require_gm(db, gm_principal_id, campaign_id)
    row = db.execute(
        select(Contact, Character.name, Location.name, KnowledgeFragment)
        .join(
            Character,
            (Character.campaign_id == Contact.campaign_id)
            & (Character.entity_id == Contact.character_id),
        )
        .join(
            Location,
            (Location.campaign_id == Contact.campaign_id)
            & (Location.entity_id == Contact.location_id),
        )
        .join(
            KnowledgeFragment,
            (KnowledgeFragment.campaign_id == Contact.campaign_id)
            & (KnowledgeFragment.id == Contact.prepared_fragment_id),
        )
        .where(Contact.campaign_id == campaign_id, Contact.character_id == contact_id)
    ).first()
    if row is None:
        raise NotFound("Contact not found in campaign")

    contact, name, location_name, fragment = row
    return {
        "contact_id": contact.character_id,
        "name": name,
        "role": contact.role,
        "location_id": contact.location_id,
        "location_name": location_name,
        "gm_note": contact.gm_note,
        "prepared_information": {
            "claim_text": fragment.claim_text,
            "gm_veracity": fragment.gm_veracity,
        },
        "reveal_preview": _single_reveal_preview(db, campaign_id, fragment.claim_text),
    }


def reveal_prepared_information(
    db: Session,
    gm_principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
    contact_id: uuid.UUID,
    recipient_character_id: uuid.UUID,
) -> dict:
    require_gm(db, gm_principal_id, campaign_id)
    contact = _contact(db, campaign_id, contact_id, for_update=True)
    contact_character = _character(db, campaign_id, contact.character_id)
    fragment = _fragment(db, campaign_id, contact.prepared_fragment_id)
    recipient = _assigned_recipient(db, campaign_id, recipient_character_id)

    existing = db.get(
        CharacterKnowledge,
        {
            "campaign_id": campaign_id,
            "character_id": recipient_character_id,
            "fragment_id": fragment.id,
        },
    )
    if existing is not None:
        return {
            "contact_id": contact.character_id,
            "recipient_character_id": recipient.entity_id,
            "recipient_name": recipient.name,
            "claim_text": fragment.claim_text,
            "state": "AWARE",
            "already_revealed": True,
        }

    make_character_aware(
        db,
        campaign_id=campaign_id,
        character_id=recipient_character_id,
        fragment_id=fragment.id,
    )
    append_domain_event(
        db,
        campaign_id=campaign_id,
        event_type="contact.information_revealed",
        subject_type="contact",
        subject_id=contact.character_id,
        actor_principal_id=gm_principal_id,
        payload={
            "contact_id": str(contact.character_id),
            "contact_name": contact_character.name,
            "recipient_character_id": str(recipient.entity_id),
            "recipient_name": recipient.name,
            "fragment_id": str(fragment.id),
            "claim_text": fragment.claim_text,
        },
    )
    db.commit()
    return {
        "contact_id": contact.character_id,
        "recipient_character_id": recipient.entity_id,
        "recipient_name": recipient.name,
        "claim_text": fragment.claim_text,
        "state": "AWARE",
        "already_revealed": False,
    }
