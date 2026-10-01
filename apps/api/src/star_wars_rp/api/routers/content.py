import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from star_wars_rp.api.dependencies import current_principal
from star_wars_rp.api.schemas import (
    CharacterCreate,
    CharacterOut,
    KnowledgeFragmentCreate,
    KnowledgeFragmentOut,
    LocationCreate,
    LocationOut,
)
from star_wars_rp.application.setup import (
    create_character,
    create_knowledge_fragment,
    create_location,
    list_characters,
    list_knowledge_fragments,
    list_locations,
)
from star_wars_rp.db import get_db
from star_wars_rp.modules.auth.models import Principal


router = APIRouter(prefix="/campaigns/{campaign_id}", tags=["campaign content"])


@router.get("/characters", response_model=list[CharacterOut])
def characters(campaign_id: uuid.UUID, principal: Principal = Depends(current_principal), db: Session = Depends(get_db)):
    return list_characters(db, principal.id, campaign_id)


@router.post("/characters", response_model=CharacterOut, status_code=201)
def create_character_route(
    campaign_id: uuid.UUID,
    body: CharacterCreate,
    principal: Principal = Depends(current_principal),
    db: Session = Depends(get_db),
):
    return create_character(db, principal.id, campaign_id, body.name, body.slicing_modifier)


@router.get("/locations", response_model=list[LocationOut])
def locations(campaign_id: uuid.UUID, principal: Principal = Depends(current_principal), db: Session = Depends(get_db)):
    return list_locations(db, principal.id, campaign_id)


@router.post("/locations", response_model=LocationOut, status_code=201)
def create_location_route(
    campaign_id: uuid.UUID,
    body: LocationCreate,
    principal: Principal = Depends(current_principal),
    db: Session = Depends(get_db),
):
    return create_location(db, principal.id, campaign_id, body.name)


@router.get("/knowledge-fragments", response_model=list[KnowledgeFragmentOut])
def fragments(campaign_id: uuid.UUID, principal: Principal = Depends(current_principal), db: Session = Depends(get_db)):
    return list_knowledge_fragments(db, principal.id, campaign_id)


@router.post("/knowledge-fragments", response_model=KnowledgeFragmentOut, status_code=201)
def create_fragment_route(
    campaign_id: uuid.UUID,
    body: KnowledgeFragmentCreate,
    principal: Principal = Depends(current_principal),
    db: Session = Depends(get_db),
):
    return create_knowledge_fragment(
        db,
        principal.id,
        campaign_id,
        body.claim_text,
        body.gm_veracity,
    )
