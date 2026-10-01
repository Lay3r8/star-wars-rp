import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from star_wars_rp.api.dependencies import current_principal
from star_wars_rp.api.schemas import (
    AddPlayerRequest,
    AssignmentRequest,
    CampaignCreate,
    CampaignOut,
    MemberOut,
)
from star_wars_rp.application.campaigns import (
    add_player_member,
    assign_player_character,
    create_campaign,
    list_campaigns,
    list_members,
)
from star_wars_rp.db import get_db
from star_wars_rp.modules.auth.models import Principal


router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("", response_model=list[CampaignOut])
def campaigns(principal: Principal = Depends(current_principal), db: Session = Depends(get_db)):
    return list_campaigns(db, principal.id)


@router.post("", status_code=201)
def create(body: CampaignCreate, principal: Principal = Depends(current_principal), db: Session = Depends(get_db)):
    campaign = create_campaign(db, principal.id, body.name)
    return {"id": campaign.id, "name": campaign.name, "role": "GM"}


@router.get("/{campaign_id}/members", response_model=list[MemberOut])
def members(campaign_id: uuid.UUID, principal: Principal = Depends(current_principal), db: Session = Depends(get_db)):
    return list_members(db, principal.id, campaign_id)


@router.post("/{campaign_id}/members", response_model=MemberOut, status_code=201)
def add_player(
    campaign_id: uuid.UUID,
    body: AddPlayerRequest,
    principal: Principal = Depends(current_principal),
    db: Session = Depends(get_db),
):
    membership = add_player_member(db, principal.id, campaign_id, body.username)
    member = next(item for item in list_members(db, principal.id, campaign_id) if item["principal_id"] == membership.principal_id)
    return member


@router.put("/{campaign_id}/player-assignment", status_code=204)
def assign(
    campaign_id: uuid.UUID,
    body: AssignmentRequest,
    principal: Principal = Depends(current_principal),
    db: Session = Depends(get_db),
):
    assign_player_character(
        db,
        principal.id,
        campaign_id,
        body.player_principal_id,
        body.character_id,
    )
    return None
