import uuid

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, ForeignKeyConstraint, Index, String, Text, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from star_wars_rp.db import Base


class CombatEncounter(Base):
    __tablename__ = "combat_encounter"
    __table_args__ = (
        CheckConstraint(
            "status IN ('ACTIVE', 'ESCAPED', 'PATROL_NEUTRALIZED', 'INCAPACITATED')",
            name="ck_combat_encounter_status",
        ),
        CheckConstraint(
            "current_actor IS NULL OR current_actor IN ('PLAYER', 'PATROL')",
            name="ck_combat_encounter_current_actor",
        ),
        CheckConstraint("player_vitality_initial > 0", name="ck_combat_player_vitality_initial"),
        CheckConstraint("patrol_strength_initial > 0", name="ck_combat_patrol_strength_initial"),
        CheckConstraint("escape_target > 0", name="ck_combat_escape_target"),
        CheckConstraint(
            "player_vitality BETWEEN 0 AND player_vitality_initial",
            name="ck_combat_player_vitality_range",
        ),
        CheckConstraint(
            "patrol_strength BETWEEN 0 AND patrol_strength_initial",
            name="ck_combat_patrol_strength_range",
        ),
        CheckConstraint(
            "escape_progress BETWEEN 0 AND escape_target",
            name="ck_combat_escape_progress_range",
        ),
        CheckConstraint("round >= 1", name="ck_combat_round_positive"),
        CheckConstraint(
            """
            (status = 'ACTIVE' AND current_actor IS NOT NULL AND ended_at IS NULL)
            OR
            (status <> 'ACTIVE' AND current_actor IS NULL AND ended_at IS NOT NULL)
            """,
            name="ck_combat_encounter_lifecycle",
        ),
        CheckConstraint(
            "status <> 'ESCAPED' OR escape_progress = escape_target",
            name="ck_combat_escaped_threshold",
        ),
        CheckConstraint(
            "status <> 'PATROL_NEUTRALIZED' OR patrol_strength = 0",
            name="ck_combat_patrol_neutralized_threshold",
        ),
        CheckConstraint(
            "status <> 'INCAPACITATED' OR player_vitality = 0",
            name="ck_combat_incapacitated_threshold",
        ),
        ForeignKeyConstraint(
            ["campaign_id", "location_id"],
            ["location.campaign_id", "location.entity_id"],
            name="fk_combat_encounter_location",
        ),
        ForeignKeyConstraint(
            ["campaign_id", "player_character_id"],
            ["character.campaign_id", "character.entity_id"],
            name="fk_combat_encounter_player_character",
        ),
        ForeignKeyConstraint(
            ["campaign_id", "created_by_principal_id"],
            ["campaign_membership.campaign_id", "campaign_membership.principal_id"],
            name="fk_combat_encounter_creator_membership",
        ),
        UniqueConstraint("campaign_id", "id", name="uq_combat_encounter_campaign_id"),
        Index(
            "uq_combat_encounter_active_character",
            "campaign_id",
            "player_character_id",
            unique=True,
            postgresql_where=text("status = 'ACTIVE'"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaign.id", ondelete="CASCADE"), nullable=False, index=True
    )
    location_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    player_character_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    objective: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ACTIVE")
    round: Mapped[int] = mapped_column(nullable=False, default=1)
    current_actor: Mapped[str | None] = mapped_column(String(16), nullable=True, default="PLAYER")

    player_attack_modifier: Mapped[int] = mapped_column(nullable=False)
    player_defence: Mapped[int] = mapped_column(nullable=False)
    player_attack_damage: Mapped[int] = mapped_column(nullable=False)
    player_vitality_initial: Mapped[int] = mapped_column(nullable=False)
    player_vitality: Mapped[int] = mapped_column(nullable=False)

    hostile_name: Mapped[str] = mapped_column(String(120), nullable=False)
    patrol_attack_modifier: Mapped[int] = mapped_column(nullable=False)
    patrol_defence: Mapped[int] = mapped_column(nullable=False)
    patrol_attack_damage: Mapped[int] = mapped_column(nullable=False)
    patrol_strength_initial: Mapped[int] = mapped_column(nullable=False)
    patrol_strength: Mapped[int] = mapped_column(nullable=False)

    escape_progress: Mapped[int] = mapped_column(nullable=False)
    escape_target: Mapped[int] = mapped_column(nullable=False)

    created_by_principal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    created_at = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    ended_at = mapped_column(DateTime(timezone=True), nullable=True)
