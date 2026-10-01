import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from star_wars_rp.application.auth import normalize_username
from star_wars_rp.errors import Conflict, Forbidden, NotFound
from star_wars_rp.modules.auth.models import Principal
from star_wars_rp.modules.campaigns.models import Campaign, CampaignMembership, PlayerCharacterAssignment
from star_wars_rp.modules.characters.models import Character


ROLE_GM = "GM"
ROLE_PLAYER = "PLAYER"


def require_membership(
    db: Session,
    principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
    role: str | None = None,
) -> CampaignMembership:
    membership = db.get(
        CampaignMembership,
        {"campaign_id": campaign_id, "principal_id": principal_id},
    )
    if membership is None:
        raise Forbidden("Not a member of this campaign")
    if role is not None and membership.role != role:
        raise Forbidden(f"{role} membership required")
    return membership


def require_gm(db: Session, principal_id: uuid.UUID, campaign_id: uuid.UUID) -> CampaignMembership:
    return require_membership(db, principal_id, campaign_id, ROLE_GM)


def create_campaign(db: Session, principal_id: uuid.UUID, name: str) -> Campaign:
    campaign = Campaign(name=name.strip())
    db.add(campaign)
    db.flush()
    db.add(CampaignMembership(campaign_id=campaign.id, principal_id=principal_id, role=ROLE_GM))
    db.commit()
    db.refresh(campaign)
    return campaign


def list_campaigns(db: Session, principal_id: uuid.UUID) -> list[dict]:
    rows = db.execute(
        select(Campaign, CampaignMembership.role)
        .join(CampaignMembership, CampaignMembership.campaign_id == Campaign.id)
        .where(CampaignMembership.principal_id == principal_id)
        .order_by(Campaign.created_at)
    ).all()
    return [{"id": campaign.id, "name": campaign.name, "role": role} for campaign, role in rows]


def add_player_member(
    db: Session,
    gm_principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
    username: str,
) -> CampaignMembership:
    require_gm(db, gm_principal_id, campaign_id)
    target = db.scalar(select(Principal).where(Principal.username == normalize_username(username)))
    if target is None:
        raise NotFound("Player principal not found")
    if target.id == gm_principal_id:
        raise Conflict("GM and Player must be distinct principals")

    existing = db.get(
        CampaignMembership,
        {"campaign_id": campaign_id, "principal_id": target.id},
    )
    if existing:
        raise Conflict("Principal is already a campaign member")

    membership = CampaignMembership(campaign_id=campaign_id, principal_id=target.id, role=ROLE_PLAYER)
    db.add(membership)
    db.commit()
    return membership


def list_members(db: Session, gm_principal_id: uuid.UUID, campaign_id: uuid.UUID) -> list[dict]:
    require_gm(db, gm_principal_id, campaign_id)
    rows = db.execute(
        select(
            CampaignMembership.principal_id,
            Principal.username,
            CampaignMembership.role,
            PlayerCharacterAssignment.character_id,
        )
        .join(Principal, Principal.id == CampaignMembership.principal_id)
        .outerjoin(
            PlayerCharacterAssignment,
            (PlayerCharacterAssignment.campaign_id == CampaignMembership.campaign_id)
            & (PlayerCharacterAssignment.player_principal_id == CampaignMembership.principal_id),
        )
        .where(CampaignMembership.campaign_id == campaign_id)
        .order_by(CampaignMembership.created_at)
    ).all()
    return [
        {
            "principal_id": principal_id,
            "username": username,
            "role": role,
            "assigned_character_id": character_id,
        }
        for principal_id, username, role, character_id in rows
    ]


def assign_player_character(
    db: Session,
    gm_principal_id: uuid.UUID,
    campaign_id: uuid.UUID,
    player_principal_id: uuid.UUID,
    character_id: uuid.UUID,
) -> PlayerCharacterAssignment:
    require_gm(db, gm_principal_id, campaign_id)
    player_membership = require_membership(db, player_principal_id, campaign_id, ROLE_PLAYER)

    character = db.scalar(
        select(Character).where(
            Character.campaign_id == campaign_id,
            Character.entity_id == character_id,
        )
    )
    if character is None:
        raise NotFound("Character not found in campaign")

    other = db.scalar(
        select(PlayerCharacterAssignment).where(
            PlayerCharacterAssignment.campaign_id == campaign_id,
            PlayerCharacterAssignment.character_id == character_id,
            PlayerCharacterAssignment.player_principal_id != player_membership.principal_id,
        )
    )
    if other is not None:
        raise Conflict("Character is already assigned to another Player")

    assignment = db.get(
        PlayerCharacterAssignment,
        {"campaign_id": campaign_id, "player_principal_id": player_principal_id},
    )
    if assignment is None:
        assignment = PlayerCharacterAssignment(
            campaign_id=campaign_id,
            player_principal_id=player_principal_id,
            character_id=character_id,
        )
        db.add(assignment)
    else:
        assignment.character_id = character_id

    db.commit()
    return assignment
