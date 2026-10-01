import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from star_wars_rp.api.dependencies import current_principal
from star_wars_rp.api.schemas import HistoryItemOut
from star_wars_rp.application.history import campaign_history
from star_wars_rp.db import get_db
from star_wars_rp.modules.auth.models import Principal


router = APIRouter(prefix="/campaigns/{campaign_id}/history", tags=["history"])


@router.get("", response_model=list[HistoryItemOut])
def history(
    campaign_id: uuid.UUID,
    principal: Principal = Depends(current_principal),
    db: Session = Depends(get_db),
):
    return campaign_history(db, principal.id, campaign_id)
