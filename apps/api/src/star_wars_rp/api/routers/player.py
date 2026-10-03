import uuid

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from star_wars_rp.api.dependencies import current_principal
from star_wars_rp.api.schemas import (
    PlayerPendingResolutionOut,
    PlayerProjectionOut,
    PlayerResolutionSummaryOut,
)
from star_wars_rp.application.projections import (
    player_character_projection,
    player_pending_resolution_projection,
    player_resolution_projection,
)
from star_wars_rp.application.resolutions import roll_resolution_for_player
from star_wars_rp.db import get_db
from star_wars_rp.errors import InvalidOperation
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


@router.get(
    "/campaigns/{campaign_id}/resolutions/pending",
    response_model=PlayerPendingResolutionOut | None,
    response_model_exclude_none=True,
)
def pending_resolution_projection(
    campaign_id: uuid.UUID,
    principal: Principal = Depends(current_principal),
    db: Session = Depends(get_db),
):
    return player_pending_resolution_projection(db, principal.id, campaign_id)


@router.post(
    "/campaigns/{campaign_id}/resolutions/{resolution_id}/roll",
    response_model=PlayerPendingResolutionOut,
    response_model_exclude_none=True,
)
async def player_roll(
    campaign_id: uuid.UUID,
    resolution_id: uuid.UUID,
    request: Request,
    principal: Principal = Depends(current_principal),
    db: Session = Depends(get_db),
):
    if await request.body():
        raise InvalidOperation("Player Roll request body must be empty")
    roll_resolution_for_player(db, principal.id, campaign_id, resolution_id)
    projection = player_pending_resolution_projection(
        db,
        principal.id,
        campaign_id,
        resolution_id,
    )
    if projection is None:
        raise InvalidOperation("Rolled resolution is no longer pending adjudication")
    return projection
