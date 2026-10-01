import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from star_wars_rp.application.campaigns import require_gm
from star_wars_rp.modules.history.models import DomainEvent


def campaign_history(
    db: Session,
    gm_principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
) -> list[dict]:
    require_gm(db, gm_principal_id, campaign_id)
    events = db.scalars(
        select(DomainEvent)
        .where(DomainEvent.campaign_id == campaign_id)
        .order_by(DomainEvent.occurred_at.desc())
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
