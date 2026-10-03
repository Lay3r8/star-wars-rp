import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from star_wars_rp.application.campaigns import require_gm
from star_wars_rp.modules.history.models import DomainEvent


def append_domain_event(
    db: Session,
    *,
    campaign_id: uuid.UUID,
    event_type: str,
    subject_type: str,
    subject_id: uuid.UUID,
    actor_principal_id: uuid.UUID,
    payload: dict,
) -> DomainEvent:
    event = DomainEvent(
        campaign_id=campaign_id,
        event_type=event_type,
        subject_type=subject_type,
        subject_id=subject_id,
        actor_principal_id=actor_principal_id,
        payload=payload,
    )
    db.add(event)
    return event


def campaign_history(
    db: Session,
    gm_principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
) -> list[dict]:
    require_gm(db, gm_principal_id, campaign_id)
    events = db.scalars(
        select(DomainEvent)
        .where(DomainEvent.campaign_id == campaign_id)
        .order_by(DomainEvent.occurred_at.desc(), DomainEvent.id.desc())
    ).all()

    result = []
    for event in events:
        payload = event.payload
        if event.event_type == "resolution.success_applied":
            message = (
                f"{payload.get('recipient_name', 'Character')} learned: "
                f"{payload.get('claim_text', '')}"
            )
        elif event.event_type == "resolution.failure_closed":
            message = payload.get("adjudication", "Failed resolution closed")
        elif event.event_type == "resolution.adjudication_finalized":
            mechanical = payload.get("mechanical_result", "?")
            final = payload.get("final_outcome", "?")
            suffix = " (GM override)" if payload.get("overridden") else ""
            message = f"Resolution finalized {final}; mechanical result was {mechanical}{suffix}."
        elif event.event_type == "resolution.adjudication_corrected":
            message = (
                "Resolution corrected "
                f"{payload.get('previous_final_outcome', '?')} -> {payload.get('final_outcome', '?')}."
            )
        elif event.event_type == "contact.information_revealed":
            message = (
                f"{payload.get('recipient_name', 'Character')} learned from "
                f"{payload.get('contact_name', 'Contact')}: {payload.get('claim_text', '')}"
            )
        else:
            message = event.event_type

        result.append(
            {
                "id": event.id,
                "event_type": event.event_type,
                "subject_id": event.subject_id,
                "occurred_at": event.occurred_at,
                "message": message,
            }
        )
    return result
