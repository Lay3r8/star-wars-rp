import uuid

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, ForeignKeyConstraint, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from star_wars_rp.db import Base


class Campaign(Base):
    __tablename__ = "campaign"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class CampaignMembership(Base):
    __tablename__ = "campaign_membership"
    __table_args__ = (
        CheckConstraint("role IN ('GM', 'PLAYER')", name="ck_campaign_membership_role"),
        UniqueConstraint("campaign_id", "principal_id", name="uq_campaign_membership_campaign_principal"),
    )

    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaign.id", ondelete="CASCADE"), primary_key=True
    )
    principal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("principal.id", ondelete="CASCADE"), primary_key=True
    )
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    created_at = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class PlayerCharacterAssignment(Base):
    __tablename__ = "player_character_assignment"
    __table_args__ = (
        ForeignKeyConstraint(
            ["campaign_id", "player_principal_id"],
            ["campaign_membership.campaign_id", "campaign_membership.principal_id"],
            ondelete="CASCADE",
            name="fk_assignment_membership",
        ),
        ForeignKeyConstraint(
            ["campaign_id", "character_id"],
            ["character.campaign_id", "character.entity_id"],
            ondelete="CASCADE",
            name="fk_assignment_character",
        ),
        UniqueConstraint("campaign_id", "character_id", name="uq_assignment_campaign_character"),
    )

    campaign_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    player_principal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    character_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
