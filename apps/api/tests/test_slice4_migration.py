import uuid

from alembic import command
from alembic.config import Config
from sqlalchemy import text

from star_wars_rp.db import engine


def test_slice4_migration_defaults_existing_resolutions_to_gm_and_hidden_risk():
    config = Config("alembic.ini")
    command.downgrade(config, "0003_slice3_adjudication")

    gm_id = uuid.uuid4()
    player_id = uuid.uuid4()
    campaign_id = uuid.uuid4()
    actor_id = uuid.uuid4()
    location_id = uuid.uuid4()
    fragment_id = uuid.uuid4()
    resolution_id = uuid.uuid4()

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO principal (id, username, password_hash)
                VALUES
                    (:gm_id, 's4-migration-gm', 'hash'),
                    (:player_id, 's4-migration-player', 'hash')
                """
            ),
            {"gm_id": gm_id, "player_id": player_id},
        )
        connection.execute(
            text("INSERT INTO campaign (id, name) VALUES (:id, 'Slice 4 migration')"),
            {"id": campaign_id},
        )
        connection.execute(
            text(
                """
                INSERT INTO campaign_membership (campaign_id, principal_id, role)
                VALUES
                    (:campaign_id, :gm_id, 'GM'),
                    (:campaign_id, :player_id, 'PLAYER')
                """
            ),
            {"campaign_id": campaign_id, "gm_id": gm_id, "player_id": player_id},
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
            {"actor_id": actor_id, "location_id": location_id, "campaign_id": campaign_id},
        )
        connection.execute(
            text(
                """
                INSERT INTO character (entity_id, campaign_id, name)
                VALUES (:actor_id, :campaign_id, 'Globox')
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
                INSERT INTO player_character_assignment
                    (campaign_id, player_principal_id, character_id)
                VALUES (:campaign_id, :player_id, :actor_id)
                """
            ),
            {"campaign_id": campaign_id, "player_id": player_id, "actor_id": actor_id},
        )
        connection.execute(
            text(
                """
                INSERT INTO knowledge_fragment
                    (id, campaign_id, claim_text, gm_veracity)
                VALUES (:fragment_id, :campaign_id, 'Dock 47.', 'TRUE')
                """
            ),
            {"fragment_id": fragment_id, "campaign_id": campaign_id},
        )
        connection.execute(
            text(
                """
                INSERT INTO action_resolution (
                    id, campaign_id, actor_character_id, context_location_id,
                    intent, risk, mechanic, dc, resolved_modifier,
                    success_recipient_character_id, success_fragment_id,
                    state, adjudication_revision, created_by_principal_id
                ) VALUES (
                    :id, :campaign_id, :actor_id, :location_id,
                    'Find the shipment', 'Security notices.', 'slicing', 10, 2,
                    :actor_id, :fragment_id,
                    'READY', 0, :gm_id
                )
                """
            ),
            {
                "id": resolution_id,
                "campaign_id": campaign_id,
                "actor_id": actor_id,
                "location_id": location_id,
                "fragment_id": fragment_id,
                "gm_id": gm_id,
            },
        )

    command.upgrade(config, "head")

    with engine.begin() as connection:
        row = connection.execute(
            text(
                """
                SELECT roll_authority, risk_visibility, state, natural_roll,
                       mechanical_result, final_outcome, adjudication_revision
                FROM action_resolution
                WHERE id = :id
                """
            ),
            {"id": resolution_id},
        ).mappings().one()

        assert row["roll_authority"] == "GM"
        assert row["risk_visibility"] == "GM_ONLY"
        assert row["state"] == "READY"
        assert row["natural_roll"] is None
        assert row["mechanical_result"] is None
        assert row["final_outcome"] is None
        assert row["adjudication_revision"] == 0
