import uuid

from alembic import command
from alembic.config import Config
from sqlalchemy import text

from star_wars_rp.db import engine


def test_slice3_data_migration_maps_legacy_resolution_rows():
    config = Config("alembic.ini")
    command.downgrade(config, "0002_slice2_contacts")

    gm_id = uuid.uuid4()
    campaign_id = uuid.uuid4()
    actor_id = uuid.uuid4()
    location_id = uuid.uuid4()
    fragment_id = uuid.uuid4()
    ready_id = uuid.uuid4()
    pending_success_id = uuid.uuid4()
    pending_failure_id = uuid.uuid4()
    closed_success_id = uuid.uuid4()
    closed_failure_id = uuid.uuid4()

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO principal (id, username, password_hash)
                VALUES (:id, 'migration-gm', 'hash')
                """
            ),
            {"id": gm_id},
        )
        connection.execute(
            text("INSERT INTO campaign (id, name) VALUES (:id, 'Migration campaign')"),
            {"id": campaign_id},
        )
        connection.execute(
            text(
                """
                INSERT INTO campaign_membership (campaign_id, principal_id, role)
                VALUES (:campaign_id, :gm_id, 'GM')
                """
            ),
            {"campaign_id": campaign_id, "gm_id": gm_id},
        )
        connection.execute(
            text(
                """
                INSERT INTO entity (id, campaign_id, entity_type)
                VALUES
                    (:actor_id, :campaign_id, 'character'),
                    (:location_id, :campaign_id, 'location')
                """
            ),
            {
                "actor_id": actor_id,
                "location_id": location_id,
                "campaign_id": campaign_id,
            },
        )
        connection.execute(
            text(
                """
                INSERT INTO character (entity_id, campaign_id, name)
                VALUES (:actor_id, :campaign_id, 'Kara Venn')
                """
            ),
            {"actor_id": actor_id, "campaign_id": campaign_id},
        )
        connection.execute(
            text(
                """
                INSERT INTO custom_d20_character_profile
                    (character_id, campaign_id, slicing_modifier)
                VALUES (:actor_id, :campaign_id, 2)
                """
            ),
            {"actor_id": actor_id, "campaign_id": campaign_id},
        )
        connection.execute(
            text(
                """
                INSERT INTO location (entity_id, campaign_id, name)
                VALUES (:location_id, :campaign_id, 'Imperial Cargo Terminal')
                """
            ),
            {"location_id": location_id, "campaign_id": campaign_id},
        )
        connection.execute(
            text(
                """
                INSERT INTO knowledge_fragment
                    (id, campaign_id, claim_text, gm_veracity)
                VALUES
                    (:fragment_id, :campaign_id, 'Dock 47.', 'TRUE')
                """
            ),
            {"fragment_id": fragment_id, "campaign_id": campaign_id},
        )

        base_sql = """
            INSERT INTO action_resolution (
                id, campaign_id, actor_character_id, context_location_id,
                intent, risk, mechanic, dc, resolved_modifier,
                success_recipient_character_id, success_fragment_id,
                state, natural_roll, total, outcome, failure_adjudication,
                created_by_principal_id, rolled_at, closed_at
            ) VALUES (
                :id, :campaign_id, :actor_id, :location_id,
                'Find the shipment', 'Security notices.', 'slicing', 10, 2,
                :actor_id, :fragment_id,
                :state, :natural_roll, :total, :outcome, :failure_adjudication,
                :gm_id, :rolled_at, :closed_at
            )
        """

        rows = [
            {
                "id": ready_id,
                "state": "READY",
                "natural_roll": None,
                "total": None,
                "outcome": None,
                "failure_adjudication": None,
                "rolled_at": None,
                "closed_at": None,
            },
            {
                "id": pending_success_id,
                "state": "SUCCESS_PENDING_APPLY",
                "natural_roll": 12,
                "total": 14,
                "outcome": "SUCCESS",
                "failure_adjudication": None,
                "rolled_at": "2026-10-01T10:00:00+00:00",
                "closed_at": None,
            },
            {
                "id": pending_failure_id,
                "state": "FAILURE_PENDING_CLOSE",
                "natural_roll": 3,
                "total": 5,
                "outcome": "FAILURE",
                "failure_adjudication": None,
                "rolled_at": "2026-10-01T10:01:00+00:00",
                "closed_at": None,
            },
            {
                "id": closed_success_id,
                "state": "CLOSED_SUCCESS",
                "natural_roll": 15,
                "total": 17,
                "outcome": "SUCCESS",
                "failure_adjudication": None,
                "rolled_at": "2026-10-01T10:02:00+00:00",
                "closed_at": "2026-10-01T10:03:00+00:00",
            },
            {
                "id": closed_failure_id,
                "state": "CLOSED_FAILURE",
                "natural_roll": 2,
                "total": 4,
                "outcome": "FAILURE",
                "failure_adjudication": "Imperial security notices.",
                "rolled_at": "2026-10-01T10:04:00+00:00",
                "closed_at": "2026-10-01T10:05:00+00:00",
            },
        ]
        for row in rows:
            connection.execute(
                text(base_sql),
                {
                    **row,
                    "campaign_id": campaign_id,
                    "actor_id": actor_id,
                    "location_id": location_id,
                    "fragment_id": fragment_id,
                    "gm_id": gm_id,
                },
            )

        connection.execute(
            text(
                """
                INSERT INTO character_knowledge
                    (campaign_id, character_id, fragment_id, state)
                VALUES (:campaign_id, :actor_id, :fragment_id, 'AWARE')
                """
            ),
            {
                "campaign_id": campaign_id,
                "actor_id": actor_id,
                "fragment_id": fragment_id,
            },
        )
        for event_type, subject_id in [
            ("resolution.success_applied", closed_success_id),
            ("resolution.failure_closed", closed_failure_id),
        ]:
            connection.execute(
                text(
                    """
                    INSERT INTO domain_event (
                        id, campaign_id, event_type, subject_type,
                        subject_id, actor_principal_id, payload
                    ) VALUES (
                        :id, :campaign_id, :event_type, 'action_resolution',
                        :subject_id, :gm_id, '{}'::jsonb
                    )
                    """
                ),
                {
                    "id": uuid.uuid4(),
                    "campaign_id": campaign_id,
                    "event_type": event_type,
                    "subject_id": subject_id,
                    "gm_id": gm_id,
                },
            )

    command.upgrade(config, "head")

    with engine.begin() as connection:
        mapped = {
            row.id: row
            for row in connection.execute(
                text(
                    """
                    SELECT
                        id, state, natural_roll, total, mechanical_result,
                        final_outcome, failure_adjudication,
                        adjudicated_by_principal_id, adjudication_revision,
                        adjudicated_at
                    FROM action_resolution
                    WHERE campaign_id = :campaign_id
                    """
                ),
                {"campaign_id": campaign_id},
            ).mappings()
        }

        assert mapped[ready_id].state == "READY"
        assert mapped[ready_id].adjudication_revision == 0

        assert mapped[pending_success_id].state == "AWAITING_ADJUDICATION"
        assert mapped[pending_success_id].mechanical_result == "SUCCESS"
        assert mapped[pending_success_id].natural_roll == 12
        assert mapped[pending_success_id].total == 14
        assert mapped[pending_success_id].final_outcome is None

        assert mapped[pending_failure_id].state == "AWAITING_ADJUDICATION"
        assert mapped[pending_failure_id].mechanical_result == "FAILURE"
        assert mapped[pending_failure_id].natural_roll == 3
        assert mapped[pending_failure_id].total == 5

        assert mapped[closed_success_id].state == "FINALIZED"
        assert mapped[closed_success_id].final_outcome == "SUCCESS"
        assert mapped[closed_success_id].adjudication_revision == 1
        assert mapped[closed_success_id].adjudicated_by_principal_id == gm_id
        assert mapped[closed_success_id].adjudicated_at is not None

        assert mapped[closed_failure_id].state == "FINALIZED"
        assert mapped[closed_failure_id].final_outcome == "FAILURE"
        assert mapped[closed_failure_id].failure_adjudication == "Imperial security notices."
        assert mapped[closed_failure_id].adjudication_revision == 1
        assert mapped[closed_failure_id].adjudicated_by_principal_id == gm_id

        assert connection.execute(
            text("SELECT count(*) FROM character_knowledge")
        ).scalar_one() == 1
        assert connection.execute(
            text(
                """
                SELECT count(*)
                FROM domain_event
                WHERE event_type IN ('resolution.success_applied', 'resolution.failure_closed')
                """
            )
        ).scalar_one() == 2
