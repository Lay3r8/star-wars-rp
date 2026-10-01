import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from star_wars_rp.api.dependencies import current_principal
from star_wars_rp.api.schemas import CloseFailureRequest, ResolutionCreate, ResolutionOut
from star_wars_rp.application.resolutions import (
    apply_success,
    close_failure,
    create_resolution,
    get_resolution,
    roll_resolution,
    serialize_resolution,
)
from star_wars_rp.db import get_db
from star_wars_rp.modules.auth.models import Principal


router = APIRouter(prefix="/campaigns/{campaign_id}/resolutions", tags=["resolutions"])


@router.post("", response_model=ResolutionOut, status_code=201)
def create(
    campaign_id: uuid.UUID,
    body: ResolutionCreate,
    principal: Principal = Depends(current_principal),
    db: Session = Depends(get_db),
):
    resolution = create_resolution(
        db,
        principal.id,
        campaign_id,
        body.actor_character_id,
        body.context_location_id,
        body.intent,
        body.risk,
        body.dc,
        body.success_recipient_character_id,
        body.success_fragment_id,
    )
    return serialize_resolution(db, resolution)


@router.get("/{resolution_id}", response_model=ResolutionOut)
def read(
    campaign_id: uuid.UUID,
    resolution_id: uuid.UUID,
    principal: Principal = Depends(current_principal),
    db: Session = Depends(get_db),
):
    return get_resolution(db, principal.id, campaign_id, resolution_id)


@router.post("/{resolution_id}/roll", response_model=ResolutionOut)
def roll(
    campaign_id: uuid.UUID,
    resolution_id: uuid.UUID,
    principal: Principal = Depends(current_principal),
    db: Session = Depends(get_db),
):
    return roll_resolution(db, principal.id, campaign_id, resolution_id)


@router.post("/{resolution_id}/apply", response_model=ResolutionOut)
def apply(
    campaign_id: uuid.UUID,
    resolution_id: uuid.UUID,
    principal: Principal = Depends(current_principal),
    db: Session = Depends(get_db),
):
    return apply_success(db, principal.id, campaign_id, resolution_id)


@router.post("/{resolution_id}/close-failure", response_model=ResolutionOut)
def close(
    campaign_id: uuid.UUID,
    resolution_id: uuid.UUID,
    body: CloseFailureRequest,
    principal: Principal = Depends(current_principal),
    db: Session = Depends(get_db),
):
    return close_failure(db, principal.id, campaign_id, resolution_id, body.adjudication)
