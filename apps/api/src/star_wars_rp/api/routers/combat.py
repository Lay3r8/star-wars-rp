import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from star_wars_rp.api.combat_schemas import (
    CombatCommand,
    CombatEncounterCreate,
    GmCombatEncounterOut,
    PlayerCombatEncounterOut,
)
from star_wars_rp.api.dependencies import current_principal
from star_wars_rp.application.combat import (
    create_encounter,
    gm_encounter_projection,
    patrol_attack,
    player_attack,
    player_encounter_projection,
    player_escape,
)
from star_wars_rp.db import get_db
from star_wars_rp.modules.auth.models import Principal


router = APIRouter(tags=["combat"])


@router.post(
    "/campaigns/{campaign_id}/combat-encounters",
    response_model=GmCombatEncounterOut,
    status_code=201,
)
def start_encounter(
    campaign_id: uuid.UUID,
    body: CombatEncounterCreate,
    principal: Principal = Depends(current_principal),
    db: Session = Depends(get_db),
):
    return create_encounter(
        db,
        principal.id,
        campaign_id,
        body.player_character_id,
        body.location_id,
    )


@router.get(
    "/campaigns/{campaign_id}/combat-encounters/latest",
    response_model=GmCombatEncounterOut | None,
)
def latest_gm_encounter(
    campaign_id: uuid.UUID,
    principal: Principal = Depends(current_principal),
    db: Session = Depends(get_db),
):
    return gm_encounter_projection(db, principal.id, campaign_id)


@router.post(
    "/campaigns/{campaign_id}/combat-encounters/{encounter_id}/patrol-attack",
    response_model=GmCombatEncounterOut,
)
def resolve_patrol_attack(
    campaign_id: uuid.UUID,
    encounter_id: uuid.UUID,
    body: CombatCommand,
    principal: Principal = Depends(current_principal),
    db: Session = Depends(get_db),
):
    return patrol_attack(
        db,
        principal.id,
        campaign_id,
        encounter_id,
        body.expected_round,
    )


@router.get(
    "/player/campaigns/{campaign_id}/combat-encounters/latest",
    response_model=PlayerCombatEncounterOut | None,
)
def latest_player_encounter(
    campaign_id: uuid.UUID,
    principal: Principal = Depends(current_principal),
    db: Session = Depends(get_db),
):
    return player_encounter_projection(db, principal.id, campaign_id)


@router.post(
    "/player/campaigns/{campaign_id}/combat-encounters/{encounter_id}/attack",
    response_model=PlayerCombatEncounterOut,
)
def resolve_player_attack(
    campaign_id: uuid.UUID,
    encounter_id: uuid.UUID,
    body: CombatCommand,
    principal: Principal = Depends(current_principal),
    db: Session = Depends(get_db),
):
    return player_attack(
        db,
        principal.id,
        campaign_id,
        encounter_id,
        body.expected_round,
    )


@router.post(
    "/player/campaigns/{campaign_id}/combat-encounters/{encounter_id}/escape",
    response_model=PlayerCombatEncounterOut,
)
def resolve_player_escape(
    campaign_id: uuid.UUID,
    encounter_id: uuid.UUID,
    body: CombatCommand,
    principal: Principal = Depends(current_principal),
    db: Session = Depends(get_db),
):
    return player_escape(
        db,
        principal.id,
        campaign_id,
        encounter_id,
        body.expected_round,
    )
