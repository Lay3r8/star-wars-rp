import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from star_wars_rp.api.dependencies import current_principal
from star_wars_rp.api.schemas import (
    ContactCreate,
    ContactSearchResult,
    ContactSummary,
    ContactUpdate,
    RevealContactInformationRequest,
    RevealContactInformationResult,
)
from star_wars_rp.application.contacts import (
    create_contact,
    get_contact_summary,
    reveal_prepared_information,
    search_contacts,
    update_contact,
)
from star_wars_rp.db import get_db
from star_wars_rp.modules.auth.models import Principal


router = APIRouter(prefix="/campaigns/{campaign_id}/contacts", tags=["contacts"])


@router.post("", response_model=ContactSummary, status_code=201)
def create(
    campaign_id: uuid.UUID,
    body: ContactCreate,
    principal: Principal = Depends(current_principal),
    db: Session = Depends(get_db),
):
    return create_contact(
        db,
        principal.id,
        campaign_id,
        name=body.name,
        role=body.role,
        location_id=body.location_id,
        gm_note=body.gm_note,
        claim_text=body.prepared_information.claim_text,
        gm_veracity=body.prepared_information.gm_veracity,
    )


@router.get("/search", response_model=list[ContactSearchResult])
def search(
    campaign_id: uuid.UUID,
    q: str = Query(min_length=1, max_length=200),
    principal: Principal = Depends(current_principal),
    db: Session = Depends(get_db),
):
    return search_contacts(db, principal.id, campaign_id, q)


@router.get("/{contact_id}", response_model=ContactSummary)
def summary(
    campaign_id: uuid.UUID,
    contact_id: uuid.UUID,
    principal: Principal = Depends(current_principal),
    db: Session = Depends(get_db),
):
    return get_contact_summary(db, principal.id, campaign_id, contact_id)


@router.patch("/{contact_id}", response_model=ContactSummary)
def update(
    campaign_id: uuid.UUID,
    contact_id: uuid.UUID,
    body: ContactUpdate,
    principal: Principal = Depends(current_principal),
    db: Session = Depends(get_db),
):
    return update_contact(
        db,
        principal.id,
        campaign_id,
        contact_id,
        name=body.name,
        role=body.role,
        location_id=body.location_id,
        gm_note=body.gm_note,
        claim_text=body.prepared_information.claim_text,
        gm_veracity=body.prepared_information.gm_veracity,
    )


@router.post("/{contact_id}/reveal", response_model=RevealContactInformationResult)
def reveal(
    campaign_id: uuid.UUID,
    contact_id: uuid.UUID,
    body: RevealContactInformationRequest,
    principal: Principal = Depends(current_principal),
    db: Session = Depends(get_db),
):
    return reveal_prepared_information(
        db,
        principal.id,
        campaign_id,
        contact_id,
        body.recipient_character_id,
    )
