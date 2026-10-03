import uuid

from sqlalchemy import CheckConstraint, DateTime, ForeignKeyConstraint, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from star_wars_rp.db import Base


class ActionResolution(Base):
    __tablename__ = "action_resolution"
    __table_args__ = (
        CheckConstraint(
            "state IN ('READY', 'AWAITING_ADJUDICATION', 'FINALIZED')",
            name="ck_action_resolution_state",
        ),
        CheckConstraint(
            "mechanical_result IS NULL OR mechanical_result IN ('SUCCESS', 'FAILURE')",
            name="ck_action_resolution_mechanical_result",
        ),
        CheckConstraint(
            "final_outcome IS NULL OR final_outcome IN ('SUCCESS', 'FAILURE')",
            name="ck_action_resolution_final_outcome",
        ),
        CheckConstraint("mechanic = 'slicing'", name="ck_action_resolution_mechanic"),
        CheckConstraint(
            """
            (
                natural_roll IS NULL
                AND total IS NULL
                AND mechanical_result IS NULL
                AND rolled_at IS NULL
            )
            OR
            (
                natural_roll BETWEEN 1 AND 20
                AND total = natural_roll + resolved_modifier
                AND mechanical_result =
                    CASE WHEN total >= dc THEN 'SUCCESS' ELSE 'FAILURE' END
                AND rolled_at IS NOT NULL
            )
            """,
            name="ck_action_resolution_mechanical_consistency",
        ),
        CheckConstraint(
            """
            (
                state = 'READY'
                AND natural_roll IS NULL
                AND final_outcome IS NULL
                AND adjudication_revision = 0
                AND adjudicated_by_principal_id IS NULL
                AND adjudicated_at IS NULL
            )
            OR
            (
                state = 'AWAITING_ADJUDICATION'
                AND natural_roll IS NOT NULL
                AND final_outcome IS NULL
                AND adjudication_revision = 0
                AND adjudicated_by_principal_id IS NULL
                AND adjudicated_at IS NULL
            )
            OR
            (
                state = 'FINALIZED'
                AND natural_roll IS NOT NULL
                AND final_outcome IS NOT NULL
                AND adjudication_revision >= 1
                AND adjudicated_by_principal_id IS NOT NULL
                AND adjudicated_at IS NOT NULL
            )
            """,
            name="ck_action_resolution_stage_consistency",
        ),
        CheckConstraint(
            """
            final_outcome <> 'FAILURE'
            OR (
                failure_adjudication IS NOT NULL
                AND length(btrim(failure_adjudication)) > 0
            )
            """,
            name="ck_action_resolution_failure_adjudication",
        ),
        CheckConstraint(
            "final_outcome <> 'SUCCESS' OR failure_adjudication IS NULL",
            name="ck_action_resolution_success_has_no_failure_adjudication",
        ),
        CheckConstraint(
            """
            adjudication_revision < 2
            OR (
                adjudication_reason IS NOT NULL
                AND length(btrim(adjudication_reason)) > 0
            )
            """,
            name="ck_action_resolution_correction_reason",
        ),
        CheckConstraint(
            "adjudication_revision >= 0",
            name="ck_action_resolution_revision_nonnegative",
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
        ForeignKeyConstraint(
            ["campaign_id", "adjudicated_by_principal_id"],
            ["campaign_membership.campaign_id", "campaign_membership.principal_id"],
            name="fk_resolution_adjudicator_membership",
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
    mechanical_result: Mapped[str | None] = mapped_column(String(16), nullable=True)
    final_outcome: Mapped[str | None] = mapped_column(String(16), nullable=True)
    failure_adjudication: Mapped[str | None] = mapped_column(Text, nullable=True)
    adjudication_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    adjudicated_by_principal_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    adjudicated_at = mapped_column(DateTime(timezone=True), nullable=True)
    adjudication_revision: Mapped[int] = mapped_column(nullable=False, default=0, server_default="0")
    created_by_principal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    created_at = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    rolled_at = mapped_column(DateTime(timezone=True), nullable=True)
