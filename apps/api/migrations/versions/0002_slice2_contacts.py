"""Add Slice 2 Contact profile.

Revision ID: 0002_slice2_contacts
Revises: 0001_slice1
Create Date: 2026-10-01
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0002_slice2_contacts"
down_revision: str | None = "0001_slice1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "contact",
        sa.Column("character_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(length=240), nullable=False),
        sa.Column("location_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("gm_note", sa.Text(), nullable=True),
        sa.Column("prepared_fragment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["campaign_id", "character_id"],
            ["character.campaign_id", "character.entity_id"],
            name="fk_contact_character",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["campaign_id", "location_id"],
            ["location.campaign_id", "location.entity_id"],
            name="fk_contact_location",
        ),
        sa.ForeignKeyConstraint(
            ["campaign_id", "prepared_fragment_id"],
            ["knowledge_fragment.campaign_id", "knowledge_fragment.id"],
            name="fk_contact_prepared_fragment",
        ),
        sa.PrimaryKeyConstraint("character_id"),
        sa.UniqueConstraint("campaign_id", "character_id", name="uq_contact_campaign_character"),
    )
    op.create_index("ix_contact_campaign_id", "contact", ["campaign_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_contact_campaign_id", table_name="contact")
    op.drop_table("contact")
