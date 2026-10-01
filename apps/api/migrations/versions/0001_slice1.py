"""Initial Slice 1 schema.

Revision ID: 0001_slice1
Revises:
Create Date: 2026-10-01
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0001_slice1"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "principal",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_principal_username", "principal", ["username"], unique=False)

    op.create_table(
        "campaign",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "campaign_membership",
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("principal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("role IN ('GM', 'PLAYER')", name="ck_campaign_membership_role"),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaign.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["principal_id"], ["principal.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("campaign_id", "principal_id"),
        sa.UniqueConstraint("campaign_id", "principal_id", name="uq_campaign_membership_campaign_principal"),
    )

    op.create_table(
        "entity",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaign.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("campaign_id", "id", name="uq_entity_campaign_id"),
    )
    op.create_index("ix_entity_campaign_id", "entity", ["campaign_id"], unique=False)

    op.create_table(
        "character",
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.ForeignKeyConstraint(
            ["campaign_id", "entity_id"],
            ["entity.campaign_id", "entity.id"],
            name="fk_character_entity",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("entity_id"),
        sa.UniqueConstraint("campaign_id", "entity_id", name="uq_character_campaign_entity"),
    )
    op.create_index("ix_character_campaign_id", "character", ["campaign_id"], unique=False)

    op.create_table(
        "custom_d20_character_profile",
        sa.Column("character_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slicing_modifier", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["campaign_id", "character_id"],
            ["character.campaign_id", "character.entity_id"],
            name="fk_d20_profile_character",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("character_id"),
        sa.UniqueConstraint("campaign_id", "character_id", name="uq_d20_profile_campaign_character"),
    )
    op.create_index(
        "ix_custom_d20_character_profile_campaign_id",
        "custom_d20_character_profile",
        ["campaign_id"],
        unique=False,
    )

    op.create_table(
        "location",
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.ForeignKeyConstraint(
            ["campaign_id", "entity_id"],
            ["entity.campaign_id", "entity.id"],
            name="fk_location_entity",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("entity_id"),
        sa.UniqueConstraint("campaign_id", "entity_id", name="uq_location_campaign_entity"),
    )
    op.create_index("ix_location_campaign_id", "location", ["campaign_id"], unique=False)

    op.create_table(
        "knowledge_fragment",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("claim_text", sa.Text(), nullable=False),
        sa.Column("gm_veracity", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("gm_veracity IN ('TRUE', 'FALSE', 'UNKNOWN')", name="ck_knowledge_veracity"),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaign.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("campaign_id", "id", name="uq_knowledge_fragment_campaign_id"),
    )
    op.create_index("ix_knowledge_fragment_campaign_id", "knowledge_fragment", ["campaign_id"], unique=False)

    op.create_table(
        "character_knowledge",
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("character_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("fragment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("state", sa.String(length=16), nullable=False),
        sa.Column("acquired_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("state = 'AWARE'", name="ck_character_knowledge_state"),
        sa.ForeignKeyConstraint(
            ["campaign_id", "character_id"],
            ["character.campaign_id", "character.entity_id"],
            name="fk_character_knowledge_character",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["campaign_id", "fragment_id"],
            ["knowledge_fragment.campaign_id", "knowledge_fragment.id"],
            name="fk_character_knowledge_fragment",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("campaign_id", "character_id", "fragment_id"),
    )

    op.create_table(
        "player_character_assignment",
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("player_principal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("character_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["campaign_id", "player_principal_id"],
            ["campaign_membership.campaign_id", "campaign_membership.principal_id"],
            name="fk_assignment_membership",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["campaign_id", "character_id"],
            ["character.campaign_id", "character.entity_id"],
            name="fk_assignment_character",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("campaign_id", "player_principal_id"),
        sa.UniqueConstraint("campaign_id", "character_id", name="uq_assignment_campaign_character"),
    )

    op.create_table(
        "action_resolution",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_character_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("context_location_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("intent", sa.Text(), nullable=False),
        sa.Column("risk", sa.Text(), nullable=False),
        sa.Column("mechanic", sa.String(length=32), nullable=False),
        sa.Column("dc", sa.Integer(), nullable=False),
        sa.Column("resolved_modifier", sa.Integer(), nullable=False),
        sa.Column("success_recipient_character_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("success_fragment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("state", sa.String(length=32), nullable=False),
        sa.Column("natural_roll", sa.Integer(), nullable=True),
        sa.Column("total", sa.Integer(), nullable=True),
        sa.Column("outcome", sa.String(length=16), nullable=True),
        sa.Column("failure_adjudication", sa.Text(), nullable=True),
        sa.Column("created_by_principal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("rolled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("mechanic = 'slicing'", name="ck_action_resolution_mechanic"),
        sa.CheckConstraint(
            "natural_roll IS NULL OR natural_roll BETWEEN 1 AND 20",
            name="ck_action_resolution_natural_roll",
        ),
        sa.CheckConstraint(
            "outcome IS NULL OR outcome IN ('SUCCESS', 'FAILURE')",
            name="ck_action_resolution_outcome",
        ),
        sa.CheckConstraint(
            "state IN ('READY', 'SUCCESS_PENDING_APPLY', 'FAILURE_PENDING_CLOSE', 'CLOSED_SUCCESS', 'CLOSED_FAILURE')",
            name="ck_action_resolution_state",
        ),
        sa.CheckConstraint(
            "success_recipient_character_id = actor_character_id",
            name="ck_action_resolution_recipient_is_actor",
        ),
        sa.ForeignKeyConstraint(
            ["campaign_id", "actor_character_id"],
            ["character.campaign_id", "character.entity_id"],
            name="fk_resolution_actor",
        ),
        sa.ForeignKeyConstraint(
            ["campaign_id", "context_location_id"],
            ["location.campaign_id", "location.entity_id"],
            name="fk_resolution_location",
        ),
        sa.ForeignKeyConstraint(
            ["campaign_id", "success_recipient_character_id"],
            ["character.campaign_id", "character.entity_id"],
            name="fk_resolution_recipient",
        ),
        sa.ForeignKeyConstraint(
            ["campaign_id", "success_fragment_id"],
            ["knowledge_fragment.campaign_id", "knowledge_fragment.id"],
            name="fk_resolution_fragment",
        ),
        sa.ForeignKeyConstraint(
            ["campaign_id", "created_by_principal_id"],
            ["campaign_membership.campaign_id", "campaign_membership.principal_id"],
            name="fk_resolution_creator_membership",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("campaign_id", "id", name="uq_action_resolution_campaign_id"),
    )
    op.create_index("ix_action_resolution_campaign_id", "action_resolution", ["campaign_id"], unique=False)

    op.create_table(
        "domain_event",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("subject_type", sa.String(length=80), nullable=False),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_principal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["campaign_id", "actor_principal_id"],
            ["campaign_membership.campaign_id", "campaign_membership.principal_id"],
            name="fk_domain_event_actor_membership",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_domain_event_campaign_id", "domain_event", ["campaign_id"], unique=False)
    op.create_index("ix_domain_event_subject_id", "domain_event", ["subject_id"], unique=False)
    op.create_index("ix_domain_event_occurred_at", "domain_event", ["occurred_at"], unique=False)


def downgrade() -> None:
    op.drop_table("domain_event")
    op.drop_table("action_resolution")
    op.drop_table("player_character_assignment")
    op.drop_table("character_knowledge")
    op.drop_table("knowledge_fragment")
    op.drop_table("location")
    op.drop_table("custom_d20_character_profile")
    op.drop_table("character")
    op.drop_table("entity")
    op.drop_table("campaign_membership")
    op.drop_table("campaign")
    op.drop_table("principal")
