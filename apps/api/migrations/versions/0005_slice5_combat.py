"""Add Slice 5 personal-scale CombatEncounter.

Revision ID: 0005_slice5_combat
Revises: 0004_slice4_player_roll
Create Date: 2026-10-04
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0005_slice5_combat"
down_revision: str | None = "0004_slice4_player_roll"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "combat_encounter",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("location_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("player_character_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("objective", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("round", sa.Integer(), nullable=False),
        sa.Column("current_actor", sa.String(length=16), nullable=True),
        sa.Column("player_attack_modifier", sa.Integer(), nullable=False),
        sa.Column("player_defence", sa.Integer(), nullable=False),
        sa.Column("player_attack_damage", sa.Integer(), nullable=False),
        sa.Column("player_vitality_initial", sa.Integer(), nullable=False),
        sa.Column("player_vitality", sa.Integer(), nullable=False),
        sa.Column("hostile_name", sa.String(length=120), nullable=False),
        sa.Column("patrol_attack_modifier", sa.Integer(), nullable=False),
        sa.Column("patrol_defence", sa.Integer(), nullable=False),
        sa.Column("patrol_attack_damage", sa.Integer(), nullable=False),
        sa.Column("patrol_strength_initial", sa.Integer(), nullable=False),
        sa.Column("patrol_strength", sa.Integer(), nullable=False),
        sa.Column("escape_progress", sa.Integer(), nullable=False),
        sa.Column("escape_target", sa.Integer(), nullable=False),
        sa.Column("created_by_principal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('ACTIVE', 'ESCAPED', 'PATROL_NEUTRALIZED', 'INCAPACITATED')",
            name="ck_combat_encounter_status",
        ),
        sa.CheckConstraint(
            "current_actor IS NULL OR current_actor IN ('PLAYER', 'PATROL')",
            name="ck_combat_encounter_current_actor",
        ),
        sa.CheckConstraint("player_vitality_initial > 0", name="ck_combat_player_vitality_initial"),
        sa.CheckConstraint("patrol_strength_initial > 0", name="ck_combat_patrol_strength_initial"),
        sa.CheckConstraint("escape_target > 0", name="ck_combat_escape_target"),
        sa.CheckConstraint(
            "player_vitality BETWEEN 0 AND player_vitality_initial",
            name="ck_combat_player_vitality_range",
        ),
        sa.CheckConstraint(
            "patrol_strength BETWEEN 0 AND patrol_strength_initial",
            name="ck_combat_patrol_strength_range",
        ),
        sa.CheckConstraint(
            "escape_progress BETWEEN 0 AND escape_target",
            name="ck_combat_escape_progress_range",
        ),
        sa.CheckConstraint("round >= 1", name="ck_combat_round_positive"),
        sa.CheckConstraint(
            """
            (status = 'ACTIVE' AND current_actor IS NOT NULL AND ended_at IS NULL)
            OR
            (status <> 'ACTIVE' AND current_actor IS NULL AND ended_at IS NOT NULL)
            """,
            name="ck_combat_encounter_lifecycle",
        ),
        sa.CheckConstraint(
            "status <> 'ESCAPED' OR escape_progress = escape_target",
            name="ck_combat_escaped_threshold",
        ),
        sa.CheckConstraint(
            "status <> 'PATROL_NEUTRALIZED' OR patrol_strength = 0",
            name="ck_combat_patrol_neutralized_threshold",
        ),
        sa.CheckConstraint(
            "status <> 'INCAPACITATED' OR player_vitality = 0",
            name="ck_combat_incapacitated_threshold",
        ),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaign.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["campaign_id", "location_id"],
            ["location.campaign_id", "location.entity_id"],
            name="fk_combat_encounter_location",
        ),
        sa.ForeignKeyConstraint(
            ["campaign_id", "player_character_id"],
            ["character.campaign_id", "character.entity_id"],
            name="fk_combat_encounter_player_character",
        ),
        sa.ForeignKeyConstraint(
            ["campaign_id", "created_by_principal_id"],
            ["campaign_membership.campaign_id", "campaign_membership.principal_id"],
            name="fk_combat_encounter_creator_membership",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("campaign_id", "id", name="uq_combat_encounter_campaign_id"),
    )
    op.create_index(
        "ix_combat_encounter_campaign_id",
        "combat_encounter",
        ["campaign_id"],
        unique=False,
    )
    op.create_index(
        "uq_combat_encounter_active_character",
        "combat_encounter",
        ["campaign_id", "player_character_id"],
        unique=True,
        postgresql_where=sa.text("status = 'ACTIVE'"),
    )


def downgrade() -> None:
    op.drop_index("uq_combat_encounter_active_character", table_name="combat_encounter")
    op.drop_index("ix_combat_encounter_campaign_id", table_name="combat_encounter")
    op.drop_table("combat_encounter")
