from datetime import datetime, timezone
import secrets
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from star_wars_rp.application.campaigns import ROLE_PLAYER, require_gm
from star_wars_rp.application.history import append_domain_event
from star_wars_rp.application.knowledge import make_character_aware
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
AWAITING_ADJUDICATION = "AWAITING_ADJUDICATION"
FINALIZED = "FINALIZED"
SUCCESS = "SUCCESS"
FAILURE = "FAILURE"


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
        raise InvalidOperation("Slice 3 success recipient must be the acting character")


def _effect_context(db: Session, resolution: ActionResolution) -> tuple[Character, KnowledgeFragment]:
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
    if recipient is None or fragment is None:
        raise InvalidOperation("Resolution success effect is no longer valid")
    return recipient, fragment


def _previous_final_outcome(db: Session, resolution: ActionResolution) -> str | None:
    if resolution.adjudication_revision < 2:
        return None
    event = db.scalar(
        select(DomainEvent)
        .where(
            DomainEvent.campaign_id == resolution.campaign_id,
            DomainEvent.subject_id == resolution.id,
            DomainEvent.event_type == "resolution.adjudication_corrected",
        )
        .order_by(DomainEvent.occurred_at.desc(), DomainEvent.id.desc())
        .limit(1)
    )
    if event is None:
        return None
    value = event.payload.get("previous_final_outcome")
    return value if value in {SUCCESS, FAILURE} else None


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
    recipient, fragment = _effect_context(db, resolution)
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
        "mechanical_result": resolution.mechanical_result,
        "final_outcome": resolution.final_outcome,
        "failure_adjudication": resolution.failure_adjudication,
        "adjudication_reason": resolution.adjudication_reason,
        "adjudicated_at": resolution.adjudicated_at,
        "adjudication_revision": resolution.adjudication_revision,
        "is_overridden": bool(
            resolution.final_outcome
            and resolution.mechanical_result
            and resolution.final_outcome != resolution.mechanical_result
        ),
        "is_corrected": resolution.adjudication_revision > 1,
        "previous_final_outcome": _previous_final_outcome(db, resolution),
        "success_preview": {
            "recipient_character_id": resolution.success_recipient_character_id,
            "recipient_name": recipient.name,
            "fragment_id": resolution.success_fragment_id,
            "claim_text": fragment.claim_text,
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


def get_latest_resolution(
    db: Session,
    gm_principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
) -> dict | None:
    require_gm(db, gm_principal_id, campaign_id)
    resolution = db.scalar(
        select(ActionResolution)
        .where(ActionResolution.campaign_id == campaign_id)
        .order_by(ActionResolution.created_at.desc(), ActionResolution.id.desc())
        .limit(1)
    )
    return serialize_resolution(db, resolution) if resolution is not None else None


def roll_resolution(
    db: Session,
    gm_principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
    resolution_id: uuid.UUID,
) -> dict:
    require_gm(db, gm_principal_id, campaign_id)
    resolution = _resolution(db, campaign_id, resolution_id, for_update=True)

    if resolution.state != READY:
        if resolution.natural_roll is not None:
            return serialize_resolution(db, resolution)
        raise Conflict("Resolution is not ready to roll")

    _validate_bound_references(db, resolution)
    natural = secrets.randbelow(20) + 1
    total, success = resolve_check(natural, resolution.resolved_modifier, resolution.dc)
    resolution.natural_roll = natural
    resolution.total = total
    resolution.mechanical_result = SUCCESS if success else FAILURE
    resolution.state = AWAITING_ADJUDICATION
    resolution.rolled_at = datetime.now(timezone.utc)
    db.commit()
    return serialize_resolution(db, resolution)


def _normalize_reason(reason: str | None) -> str | None:
    if reason is None:
        return None
    value = reason.strip()
    return value or None


def _failure_adjudication(
    resolution: ActionResolution,
    supplied: str | None,
) -> str:
    value = supplied.strip() if supplied is not None else resolution.risk.strip()
    if not value:
        raise InvalidOperation("Failure adjudication is required")
    return value


def _current_matches_finalize(
    resolution: ActionResolution,
    *,
    final_outcome: str,
    failure_adjudication: str | None,
    reason: str | None,
) -> bool:
    if resolution.adjudication_revision != 1:
        return False
    if resolution.final_outcome != final_outcome:
        return False
    expected_failure = (
        _failure_adjudication(resolution, failure_adjudication)
        if final_outcome == FAILURE
        else None
    )
    expected_reason = (
        _normalize_reason(reason)
        if resolution.mechanical_result != final_outcome
        else None
    )
    return (
        resolution.failure_adjudication == expected_failure
        and resolution.adjudication_reason == expected_reason
    )


def finalize_resolution(
    db: Session,
    gm_principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
    resolution_id: uuid.UUID,
    final_outcome: str,
    failure_adjudication: str | None = None,
    reason: str | None = None,
) -> dict:
    require_gm(db, gm_principal_id, campaign_id)
    if final_outcome not in {SUCCESS, FAILURE}:
        raise InvalidOperation("Final outcome must be SUCCESS or FAILURE")

    resolution = _resolution(db, campaign_id, resolution_id, for_update=True)

    if resolution.state == FINALIZED:
        if _current_matches_finalize(
            resolution,
            final_outcome=final_outcome,
            failure_adjudication=failure_adjudication,
            reason=reason,
        ):
            return serialize_resolution(db, resolution)
        raise Conflict("Resolution is already finalized; use Correct outcome")

    if resolution.state != AWAITING_ADJUDICATION:
        raise Conflict("Resolution must be rolled before Finalize")

    _validate_bound_references(db, resolution)
    recipient, fragment = _effect_context(db, resolution)
    now = datetime.now(timezone.utc)
    overridden = resolution.mechanical_result != final_outcome
    stored_reason = _normalize_reason(reason) if overridden else None

    if final_outcome == SUCCESS:
        make_character_aware(
            db,
            campaign_id,
            resolution.success_recipient_character_id,
            resolution.success_fragment_id,
        )
        concrete_failure = None
    else:
        concrete_failure = _failure_adjudication(resolution, failure_adjudication)

    resolution.final_outcome = final_outcome
    resolution.failure_adjudication = concrete_failure
    resolution.adjudication_reason = stored_reason
    resolution.adjudicated_by_principal_id = gm_principal_id
    resolution.adjudicated_at = now
    resolution.adjudication_revision = 1
    resolution.state = FINALIZED

    payload = {
        "resolution_id": str(resolution.id),
        "adjudication_revision": 1,
        "mechanical_result": resolution.mechanical_result,
        "final_outcome": final_outcome,
        "overridden": overridden,
    }
    if stored_reason is not None:
        payload["adjudication_reason"] = stored_reason
    if concrete_failure is not None:
        payload["failure_adjudication"] = concrete_failure
    if final_outcome == SUCCESS:
        payload.update(
            {
                "recipient_character_id": str(resolution.success_recipient_character_id),
                "recipient_name": recipient.name,
                "fragment_id": str(resolution.success_fragment_id),
                "claim_text": fragment.claim_text,
            }
        )

    append_domain_event(
        db,
        campaign_id=campaign_id,
        event_type="resolution.adjudication_finalized",
        subject_type="action_resolution",
        subject_id=resolution.id,
        actor_principal_id=gm_principal_id,
        payload=payload,
    )
    db.commit()
    return serialize_resolution(db, resolution)


def correct_resolution(
    db: Session,
    gm_principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
    resolution_id: uuid.UUID,
    expected_adjudication_revision: int,
    final_outcome: str,
    correction_reason: str,
    failure_adjudication: str | None = None,
) -> dict:
    require_gm(db, gm_principal_id, campaign_id)
    if final_outcome not in {SUCCESS, FAILURE}:
        raise InvalidOperation("Final outcome must be SUCCESS or FAILURE")

    correction_reason = correction_reason.strip()
    if not correction_reason:
        raise InvalidOperation("Correction reason is required")

    resolution = _resolution(db, campaign_id, resolution_id, for_update=True)
    if resolution.state != FINALIZED:
        raise Conflict("Only a finalized resolution can be corrected")
    if resolution.adjudication_revision != expected_adjudication_revision:
        raise Conflict("Adjudication revision changed; reload before correcting")

    _validate_bound_references(db, resolution)
    previous_final_outcome = resolution.final_outcome
    previous_failure_adjudication = resolution.failure_adjudication
    concrete_failure = (
        _failure_adjudication(resolution, failure_adjudication)
        if final_outcome == FAILURE
        else None
    )

    if (
        previous_final_outcome == final_outcome
        and previous_failure_adjudication == concrete_failure
    ):
        raise InvalidOperation("Correction must change the adjudication")

    knowledge_key = {
        "campaign_id": campaign_id,
        "character_id": resolution.success_recipient_character_id,
        "fragment_id": resolution.success_fragment_id,
    }
    knowledge_before = db.get(CharacterKnowledge, knowledge_key)
    success_disclosure_applied_now = False
    prior_success_disclosure_retained = False

    if final_outcome == SUCCESS:
        if knowledge_before is None:
            success_disclosure_applied_now = True
        make_character_aware(
            db,
            campaign_id,
            resolution.success_recipient_character_id,
            resolution.success_fragment_id,
        )
    elif previous_final_outcome == SUCCESS and knowledge_before is not None:
        prior_success_disclosure_retained = True

    previous_revision = resolution.adjudication_revision
    resolution.final_outcome = final_outcome
    resolution.failure_adjudication = concrete_failure
    resolution.adjudication_reason = correction_reason
    resolution.adjudicated_by_principal_id = gm_principal_id
    resolution.adjudicated_at = datetime.now(timezone.utc)
    resolution.adjudication_revision = previous_revision + 1

    append_domain_event(
        db,
        campaign_id=campaign_id,
        event_type="resolution.adjudication_corrected",
        subject_type="action_resolution",
        subject_id=resolution.id,
        actor_principal_id=gm_principal_id,
        payload={
            "resolution_id": str(resolution.id),
            "previous_revision": previous_revision,
            "new_revision": resolution.adjudication_revision,
            "previous_final_outcome": previous_final_outcome,
            "final_outcome": final_outcome,
            "previous_failure_adjudication": previous_failure_adjudication,
            "failure_adjudication": concrete_failure,
            "correction_reason": correction_reason,
            "success_disclosure_applied_now": success_disclosure_applied_now,
            "prior_success_disclosure_retained": prior_success_disclosure_retained,
        },
    )
    db.commit()
    return serialize_resolution(db, resolution)
