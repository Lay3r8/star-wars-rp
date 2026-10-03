"""Add Slice 4 Player Roll authority and Risk visibility.

Revision ID: 0004_slice4_player_roll
Revises: 0003_slice3_adjudication
Create Date: 2026-10-03
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0004_slice4_player_roll"
down_revision: str | None = "0003_slice3_adjudication"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "action_resolution",
        sa.Column(
            "roll_authority",
            sa.String(length=16),
            server_default="GM",
            nullable=False,
        ),
    )
    op.add_column(
        "action_resolution",
        sa.Column(
            "risk_visibility",
            sa.String(length=24),
            server_default="GM_ONLY",
            nullable=False,
        ),
    )
    op.create_check_constraint(
        "ck_action_resolution_roll_authority",
        "action_resolution",
        "roll_authority IN ('GM', 'PLAYER')",
    )
    op.create_check_constraint(
        "ck_action_resolution_risk_visibility",
        "action_resolution",
        "risk_visibility IN ('GM_ONLY', 'PLAYER_VISIBLE')",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_action_resolution_risk_visibility",
        "action_resolution",
        type_="check",
    )
    op.drop_constraint(
        "ck_action_resolution_roll_authority",
        "action_resolution",
        type_="check",
    )
    op.drop_column("action_resolution", "risk_visibility")
    op.drop_column("action_resolution", "roll_authority")
