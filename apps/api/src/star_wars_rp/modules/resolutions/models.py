import uuid

from sqlalchemy import CheckConstraint, DateTime, ForeignKeyConstraint, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from star_wars_rp.db import Base


class ActionResolution(Base):
    __tablename__ = "action_resolution"
    __table_args__ = (
        CheckConstraint(
            "state IN ('READY', 'SUCCESS_PENDING_APPLY', 'FAILURE_PENDING_CLOSE', 'CLOSED_SUCCESS', 'CLOSED_FAILURE')",
            name="ck_action_resolution_state",
        ),
        CheckConstraint("outcome IS NULL OR outcome IN ('SUCCESS', 'FAILURE')", name="ck_action_resolution_outcome"),
        CheckConstraint("mechanic = 'slicing'", name="ck_action_resolution_mechanic"),
        CheckConstraint(
            "natural_roll IS NULL OR natural_roll BETWEEN 1 AND 20",
            name="ck_action_resolution_natural_roll",
        ),
        CheckConstraint(
            "success_recipient_character_id = actor_character_id",
            name="ck_action_resolution_recipient_is_actor",
        ),
        ForeignKeyConstraint(
            ["campaign_id", "actor_character_id"],
            ["character.campaign_id", "character.entity_id"],
            name="fk_resolution_actor",
        ),
        ForeignKeyConstraint(
            ["campaign_id", "context_location_id"],
            ["location.campaign_id", "location.entity_id"],
            name="fk_resolution_location",
        ),
        ForeignKeyConstraint(
            ["campaign_id", "success_recipient_character_id"],
            ["character.campaign_id", "character.entity_id"],
            name="fk_resolution_recipient",
        ),
        ForeignKeyConstraint(
            ["campaign_id", "success_fragment_id"],
            ["knowledge_fragment.campaign_id", "knowledge_fragment.id"],
            name="fk_resolution_fragment",
        ),
        ForeignKeyConstraint(
            ["campaign_id", "created_by_principal_id"],
            ["campaign_membership.campaign_id", "campaign_membership.principal_id"],
            name="fk_resolution_creator_membership",
        ),
        UniqueConstraint("campaign_id", "id", name="uq_action_resolution_campaign_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    actor_character_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    context_location_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    intent: Mapped[str] = mapped_column(Text, nullable=False)
    risk: Mapped[str] = mapped_column(Text, nullable=False)
    mechanic: Mapped[str] = mapped_column(String(32), nullable=False, default="slicing")
    dc: Mapped[int] = mapped_column(nullable=False)
    resolved_modifier: Mapped[int] = mapped_column(nullable=False)
    success_recipient_character_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    success_fragment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    state: Mapped[str] = mapped_column(String(32), nullable=False, default="READY")
    natural_roll: Mapped[int | None] = mapped_column(nullable=True)
    total: Mapped[int | None] = mapped_column(nullable=True)
    outcome: Mapped[str | None] = mapped_column(String(16), nullable=True)
    failure_adjudication: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_principal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    created_at = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    rolled_at = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at = mapped_column(DateTime(timezone=True), nullable=True)
