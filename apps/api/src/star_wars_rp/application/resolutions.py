from datetime import datetime, timezone
import secrets
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from star_wars_rp.application.campaigns import ROLE_PLAYER, require_gm
from star_wars_rp.errors import Conflict, InvalidOperation, NotFound
from star_wars_rp.modules.campaigns.models import CampaignMembership, PlayerCharacterAssignment
from star_wars_rp.modules.characters.models import Character
from star_wars_rp.modules.custom_d20.models import CustomD20CharacterProfile
from star_wars_rp.modules.custom_d20.rules import resolve_check
from star_wars_rp.modules.history.models import DomainEvent
from star_wars_rp.modules.knowledge.models import CharacterKnowledge, KnowledgeFragment
from star_wars_rp.modules.resolutions.models import ActionResolution
from star_wars_rp.modules.world.models import Location


READY = "READY"
SUCCESS_PENDING_APPLY = "SUCCESS_PENDING_APPLY"
FAILURE_PENDING_CLOSE = "FAILURE_PENDING_CLOSE"
CLOSED_SUCCESS = "CLOSED_SUCCESS"
CLOSED_FAILURE = "CLOSED_FAILURE"


def _resolution(
    db: Session,
    campaign_id: uuid.UUID,
    resolution_id: uuid.UUID,
    *,
    for_update: bool = False,
) -> ActionResolution:
    stmt = select(ActionResolution).where(
        ActionResolution.campaign_id == campaign_id,
        ActionResolution.id == resolution_id,
    )
    if for_update:
        stmt = stmt.with_for_update()
    value = db.scalar(stmt)
    if value is None:
        raise NotFound("Resolution not found in campaign")
    return value


def _validate_bound_references(db: Session, resolution: ActionResolution) -> None:
    campaign_id = resolution.campaign_id
    actor = db.scalar(
        select(Character).where(
            Character.campaign_id == campaign_id,
            Character.entity_id == resolution.actor_character_id,
        )
    )
    location = db.scalar(
        select(Location).where(
            Location.campaign_id == campaign_id,
            Location.entity_id == resolution.context_location_id,
        )
    )
    recipient = db.scalar(
        select(Character).where(
            Character.campaign_id == campaign_id,
            Character.entity_id == resolution.success_recipient_character_id,
        )
    )
    fragment = db.scalar(
        select(KnowledgeFragment).where(
            KnowledgeFragment.campaign_id == campaign_id,
            KnowledgeFragment.id == resolution.success_fragment_id,
        )
    )
    assignment = db.scalar(
        select(PlayerCharacterAssignment)
        .join(
            CampaignMembership,
            (CampaignMembership.campaign_id == PlayerCharacterAssignment.campaign_id)
            & (CampaignMembership.principal_id == PlayerCharacterAssignment.player_principal_id),
        )
        .where(
            PlayerCharacterAssignment.campaign_id == campaign_id,
            PlayerCharacterAssignment.character_id == resolution.actor_character_id,
            CampaignMembership.role == ROLE_PLAYER,
        )
    )
    if not all([actor, location, recipient, fragment, assignment]):
        raise InvalidOperation("Resolution contains an invalid or cross-campaign reference")
    if resolution.actor_character_id != resolution.success_recipient_character_id:
        raise InvalidOperation("Slice 1 success recipient must be the acting character")


def create_resolution(
    db: Session,
    gm_principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
    actor_character_id: uuid.UUID,
    context_location_id: uuid.UUID,
    intent: str,
    risk: str,
    dc: int,
    success_recipient_character_id: uuid.UUID,
    success_fragment_id: uuid.UUID,
) -> ActionResolution:
    require_gm(db, gm_principal_id, campaign_id)
    profile = db.scalar(
        select(CustomD20CharacterProfile).where(
            CustomD20CharacterProfile.campaign_id == campaign_id,
            CustomD20CharacterProfile.character_id == actor_character_id,
        )
    )
    if profile is None:
        raise NotFound("Custom D20 profile not found for actor")

    resolution = ActionResolution(
        campaign_id=campaign_id,
        actor_character_id=actor_character_id,
        context_location_id=context_location_id,
        intent=intent.strip(),
        risk=risk.strip(),
        mechanic="slicing",
        dc=dc,
        resolved_modifier=profile.slicing_modifier,
        success_recipient_character_id=success_recipient_character_id,
        success_fragment_id=success_fragment_id,
        state=READY,
        created_by_principal_id=gm_principal_id,
    )
    _validate_bound_references(db, resolution)
    db.add(resolution)
    db.commit()
    db.refresh(resolution)
    return resolution


def serialize_resolution(db: Session, resolution: ActionResolution) -> dict:
    recipient = db.scalar(
        select(Character).where(
            Character.campaign_id == resolution.campaign_id,
            Character.entity_id == resolution.success_recipient_character_id,
        )
    )
    fragment = db.scalar(
        select(KnowledgeFragment).where(
            KnowledgeFragment.campaign_id == resolution.campaign_id,
            KnowledgeFragment.id == resolution.success_fragment_id,
        )
    )
    return {
        "id": resolution.id,
        "campaign_id": resolution.campaign_id,
        "actor_character_id": resolution.actor_character_id,
        "context_location_id": resolution.context_location_id,
        "intent": resolution.intent,
        "risk": resolution.risk,
        "mechanic": resolution.mechanic,
        "dc": resolution.dc,
        "resolved_modifier": resolution.resolved_modifier,
        "state": resolution.state,
        "natural_roll": resolution.natural_roll,
        "total": resolution.total,
        "outcome": resolution.outcome,
        "failure_adjudication": resolution.failure_adjudication,
        "success_preview": {
            "recipient_character_id": resolution.success_recipient_character_id,
            "recipient_name": recipient.name if recipient else "",
            "fragment_id": resolution.success_fragment_id,
            "claim_text": fragment.claim_text if fragment else "",
        },
    }


def get_resolution(
    db: Session,
    gm_principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
    resolution_id: uuid.UUID,
) -> dict:
    require_gm(db, gm_principal_id, campaign_id)
    return serialize_resolution(db, _resolution(db, campaign_id, resolution_id))


def roll_resolution(
    db: Session,
    gm_principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
    resolution_id: uuid.UUID,
) -> dict:
    require_gm(db, gm_principal_id, campaign_id)
    resolution = _resolution(db, campaign_id, resolution_id, for_update=True)
    if resolution.state != READY:
        raise Conflict("Resolution has already been rolled or closed")

    _validate_bound_references(db, resolution)
    natural = secrets.randbelow(20) + 1
    total, success = resolve_check(natural, resolution.resolved_modifier, resolution.dc)
    resolution.natural_roll = natural
    resolution.total = total
    resolution.outcome = "SUCCESS" if success else "FAILURE"
    resolution.state = SUCCESS_PENDING_APPLY if success else FAILURE_PENDING_CLOSE
    resolution.rolled_at = datetime.now(timezone.utc)
    db.commit()
    return serialize_resolution(db, resolution)


def apply_success(
    db: Session,
    gm_principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
    resolution_id: uuid.UUID,
) -> dict:
    require_gm(db, gm_principal_id, campaign_id)
    resolution = _resolution(db, campaign_id, resolution_id, for_update=True)

    if resolution.state == CLOSED_SUCCESS:
        return serialize_resolution(db, resolution)
    if resolution.state != SUCCESS_PENDING_APPLY:
        raise Conflict("Only a successful pending resolution can be applied")

    _validate_bound_references(db, resolution)
    knowledge = db.get(
        CharacterKnowledge,
        {
            "campaign_id": campaign_id,
            "character_id": resolution.success_recipient_character_id,
            "fragment_id": resolution.success_fragment_id,
        },
    )
    if knowledge is None:
        knowledge = CharacterKnowledge(
            campaign_id=campaign_id,
            character_id=resolution.success_recipient_character_id,
            fragment_id=resolution.success_fragment_id,
            state="AWARE",
        )
        db.add(knowledge)
    else:
        knowledge.state = "AWARE"

    fragment = db.scalar(
        select(KnowledgeFragment).where(
            KnowledgeFragment.campaign_id == campaign_id,
            KnowledgeFragment.id == resolution.success_fragment_id,
        )
    )
    recipient = db.scalar(
        select(Character).where(
            Character.campaign_id == campaign_id,
            Character.entity_id == resolution.success_recipient_character_id,
        )
    )

    resolution.state = CLOSED_SUCCESS
    resolution.closed_at = datetime.now(timezone.utc)
    db.add(
        DomainEvent(
            campaign_id=campaign_id,
            event_type="resolution.success_applied",
            subject_type="action_resolution",
            subject_id=resolution.id,
            actor_principal_id=gm_principal_id,
            payload={
                "resolution_id": str(resolution.id),
                "recipient_character_id": str(resolution.success_recipient_character_id),
                "recipient_name": recipient.name,
                "fragment_id": str(resolution.success_fragment_id),
                "claim_text": fragment.claim_text,
                "intent": resolution.intent,
            },
        )
    )
    db.commit()
    return serialize_resolution(db, resolution)


def close_failure(
    db: Session,
    gm_principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
    resolution_id: uuid.UUID,
    adjudication: str,
) -> dict:
    require_gm(db, gm_principal_id, campaign_id)
    resolution = _resolution(db, campaign_id, resolution_id, for_update=True)
    adjudication = adjudication.strip()

    if resolution.state == CLOSED_FAILURE:
        if resolution.failure_adjudication == adjudication:
            return serialize_resolution(db, resolution)
        raise Conflict("Closed failure adjudication cannot be replaced in Slice 1")
    if resolution.state != FAILURE_PENDING_CLOSE:
        raise Conflict("Only a failed pending resolution can be closed")
    if not adjudication:
        raise InvalidOperation("Failure adjudication is required")

    _validate_bound_references(db, resolution)
    resolution.failure_adjudication = adjudication
    resolution.state = CLOSED_FAILURE
    resolution.closed_at = datetime.now(timezone.utc)
    db.add(
        DomainEvent(
            campaign_id=campaign_id,
            event_type="resolution.failure_closed",
            subject_type="action_resolution",
            subject_id=resolution.id,
            actor_principal_id=gm_principal_id,
            payload={
                "resolution_id": str(resolution.id),
                "intent": resolution.intent,
                "risk": resolution.risk,
                "adjudication": adjudication,
            },
        )
    )
    db.commit()
    return serialize_resolution(db, resolution)
