import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from star_wars_rp.api.dependencies import current_principal
from star_wars_rp.api.schemas import PlayerProjectionOut, PlayerResolutionSummaryOut
from star_wars_rp.application.projections import (
    player_character_projection,
    player_resolution_projection,
)
from star_wars_rp.db import get_db
from star_wars_rp.modules.auth.models import Principal


router = APIRouter(prefix="/player", tags=["player"])


@router.get("/campaigns/{campaign_id}/character", response_model=PlayerProjectionOut)
def character_projection(
    campaign_id: uuid.UUID,
    principal: Principal = Depends(current_principal),
    db: Session = Depends(get_db),
):
    return player_character_projection(db, principal.id, campaign_id)


@router.get(
    "/campaigns/{campaign_id}/resolutions/latest",
    response_model=PlayerResolutionSummaryOut | None,
)
def latest_resolution_projection(
    campaign_id: uuid.UUID,
    principal: Principal = Depends(current_principal),
    db: Session = Depends(get_db),
):
    return player_resolution_projection(db, principal.id, campaign_id)
