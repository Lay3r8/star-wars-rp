"""Evolve Slice 1 ActionResolution for Slice 3 adjudication.

Revision ID: 0003_slice3_adjudication
Revises: 0002_slice2_contacts
Create Date: 2026-10-02
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0003_slice3_adjudication"
down_revision: str | None = "0002_slice2_contacts"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _legacy_terminal_event_problem(connection) -> tuple[int, int]:
    missing = connection.execute(
        sa.text(
            """
            SELECT count(*)
            FROM action_resolution ar
            WHERE ar.state IN ('CLOSED_SUCCESS', 'CLOSED_FAILURE')
              AND (
                SELECT count(*)
                FROM domain_event de
                WHERE de.campaign_id = ar.campaign_id
                  AND de.subject_id = ar.id
                  AND (
                    (ar.state = 'CLOSED_SUCCESS' AND de.event_type = 'resolution.success_applied')
                    OR
                    (ar.state = 'CLOSED_FAILURE' AND de.event_type = 'resolution.failure_closed')
                  )
              ) = 0
            """
        )
    ).scalar_one()
    duplicate = connection.execute(
        sa.text(
            """
            SELECT count(*)
            FROM action_resolution ar
            WHERE ar.state IN ('CLOSED_SUCCESS', 'CLOSED_FAILURE')
              AND (
                SELECT count(*)
                FROM domain_event de
                WHERE de.campaign_id = ar.campaign_id
                  AND de.subject_id = ar.id
                  AND (
                    (ar.state = 'CLOSED_SUCCESS' AND de.event_type = 'resolution.success_applied')
                    OR
                    (ar.state = 'CLOSED_FAILURE' AND de.event_type = 'resolution.failure_closed')
                  )
              ) > 1
            """
        )
    ).scalar_one()
    return missing, duplicate


def upgrade() -> None:
    connection = op.get_bind()

    op.drop_constraint("ck_action_resolution_state", "action_resolution", type_="check")
    op.drop_constraint("ck_action_resolution_outcome", "action_resolution", type_="check")

    op.alter_column("action_resolution", "outcome", new_column_name="mechanical_result")
    op.alter_column("action_resolution", "closed_at", new_column_name="adjudicated_at")

    op.add_column(
        "action_resolution",
        sa.Column("final_outcome", sa.String(length=16), nullable=True),
    )
    op.add_column(
        "action_resolution",
        sa.Column("adjudication_reason", sa.Text(), nullable=True),
    )
    op.add_column(
        "action_resolution",
        sa.Column("adjudicated_by_principal_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "action_resolution",
        sa.Column("adjudication_revision", sa.Integer(), server_default="0", nullable=False),
    )

    missing, duplicate = _legacy_terminal_event_problem(connection)
    if missing or duplicate:
        raise RuntimeError(
            "Cannot migrate finalized ActionResolution rows: each legacy CLOSED row must have "
            f"exactly one matching terminal DomainEvent (missing={missing}, duplicate={duplicate})."
        )

    connection.execute(
        sa.text(
            """
            UPDATE action_resolution ar
            SET adjudicated_by_principal_id = (
                SELECT de.actor_principal_id
                FROM domain_event de
                WHERE de.campaign_id = ar.campaign_id
                  AND de.subject_id = ar.id
                  AND (
                    (ar.state = 'CLOSED_SUCCESS' AND de.event_type = 'resolution.success_applied')
                    OR
                    (ar.state = 'CLOSED_FAILURE' AND de.event_type = 'resolution.failure_closed')
                  )
                LIMIT 1
            )
            WHERE ar.state IN ('CLOSED_SUCCESS', 'CLOSED_FAILURE')
            """
        )
    )

    connection.execute(
        sa.text(
            """
            UPDATE action_resolution
            SET
                final_outcome = CASE
                    WHEN state = 'CLOSED_SUCCESS' THEN 'SUCCESS'
                    WHEN state = 'CLOSED_FAILURE' THEN 'FAILURE'
                    ELSE NULL
                END,
                adjudication_revision = CASE
                    WHEN state IN ('CLOSED_SUCCESS', 'CLOSED_FAILURE') THEN 1
                    ELSE 0
                END,
                state = CASE
                    WHEN state IN ('SUCCESS_PENDING_APPLY', 'FAILURE_PENDING_CLOSE')
                        THEN 'AWAITING_ADJUDICATION'
                    WHEN state IN ('CLOSED_SUCCESS', 'CLOSED_FAILURE')
                        THEN 'FINALIZED'
                    ELSE state
                END
            """
        )
    )

    op.create_foreign_key(
        "fk_resolution_adjudicator_membership",
        "action_resolution",
        "campaign_membership",
        ["campaign_id", "adjudicated_by_principal_id"],
        ["campaign_id", "principal_id"],
    )

    op.create_check_constraint(
        "ck_action_resolution_state",
        "action_resolution",
        "state IN ('READY', 'AWAITING_ADJUDICATION', 'FINALIZED')",
    )
    op.create_check_constraint(
        "ck_action_resolution_mechanical_result",
        "action_resolution",
        "mechanical_result IS NULL OR mechanical_result IN ('SUCCESS', 'FAILURE')",
    )
    op.create_check_constraint(
        "ck_action_resolution_final_outcome",
        "action_resolution",
        "final_outcome IS NULL OR final_outcome IN ('SUCCESS', 'FAILURE')",
    )
    op.create_check_constraint(
        "ck_action_resolution_mechanical_consistency",
        "action_resolution",
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
    )
    op.create_check_constraint(
        "ck_action_resolution_stage_consistency",
        "action_resolution",
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
    )
    op.create_check_constraint(
        "ck_action_resolution_failure_adjudication",
        "action_resolution",
        """
        final_outcome <> 'FAILURE'
        OR (
            failure_adjudication IS NOT NULL
            AND length(btrim(failure_adjudication)) > 0
        )
        """,
    )
    op.create_check_constraint(
        "ck_action_resolution_success_has_no_failure_adjudication",
        "action_resolution",
        "final_outcome <> 'SUCCESS' OR failure_adjudication IS NULL",
    )
    op.create_check_constraint(
        "ck_action_resolution_correction_reason",
        "action_resolution",
        """
        adjudication_revision < 2
        OR (
            adjudication_reason IS NOT NULL
            AND length(btrim(adjudication_reason)) > 0
        )
        """,
    )
    op.create_check_constraint(
        "ck_action_resolution_revision_nonnegative",
        "action_resolution",
        "adjudication_revision >= 0",
    )


def downgrade() -> None:
    connection = op.get_bind()

    op.drop_constraint("ck_action_resolution_revision_nonnegative", "action_resolution", type_="check")
    op.drop_constraint("ck_action_resolution_correction_reason", "action_resolution", type_="check")
    op.drop_constraint(
        "ck_action_resolution_success_has_no_failure_adjudication",
        "action_resolution",
        type_="check",
    )
    op.drop_constraint("ck_action_resolution_failure_adjudication", "action_resolution", type_="check")
    op.drop_constraint("ck_action_resolution_stage_consistency", "action_resolution", type_="check")
    op.drop_constraint("ck_action_resolution_mechanical_consistency", "action_resolution", type_="check")
    op.drop_constraint("ck_action_resolution_final_outcome", "action_resolution", type_="check")
    op.drop_constraint("ck_action_resolution_mechanical_result", "action_resolution", type_="check")
    op.drop_constraint("ck_action_resolution_state", "action_resolution", type_="check")
    op.drop_constraint("fk_resolution_adjudicator_membership", "action_resolution", type_="foreignkey")

    connection.execute(
        sa.text(
            """
            UPDATE action_resolution
            SET state = CASE
                WHEN state = 'READY' THEN 'READY'
                WHEN state = 'AWAITING_ADJUDICATION' AND mechanical_result = 'SUCCESS'
                    THEN 'SUCCESS_PENDING_APPLY'
                WHEN state = 'AWAITING_ADJUDICATION' AND mechanical_result = 'FAILURE'
                    THEN 'FAILURE_PENDING_CLOSE'
                WHEN state = 'FINALIZED' AND final_outcome = 'SUCCESS'
                    THEN 'CLOSED_SUCCESS'
                WHEN state = 'FINALIZED' AND final_outcome = 'FAILURE'
                    THEN 'CLOSED_FAILURE'
                ELSE state
            END
            """
        )
    )

    op.drop_column("action_resolution", "adjudication_revision")
    op.drop_column("action_resolution", "adjudicated_by_principal_id")
    op.drop_column("action_resolution", "adjudication_reason")
    op.drop_column("action_resolution", "final_outcome")

    op.alter_column("action_resolution", "adjudicated_at", new_column_name="closed_at")
    op.alter_column("action_resolution", "mechanical_result", new_column_name="outcome")

    op.create_check_constraint(
        "ck_action_resolution_outcome",
        "action_resolution",
        "outcome IS NULL OR outcome IN ('SUCCESS', 'FAILURE')",
    )
    op.create_check_constraint(
        "ck_action_resolution_state",
        "action_resolution",
        "state IN ('READY', 'SUCCESS_PENDING_APPLY', 'FAILURE_PENDING_CLOSE', 'CLOSED_SUCCESS', 'CLOSED_FAILURE')",
    )
