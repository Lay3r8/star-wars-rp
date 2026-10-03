import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event, func, select

from conftest import register_and_login
from star_wars_rp.application.resolutions import finalize_resolution
from star_wars_rp.db import SessionLocal
from star_wars_rp.modules.campaigns.models import CampaignMembership, PlayerCharacterAssignment
from star_wars_rp.modules.history.models import DomainEvent
from star_wars_rp.modules.knowledge.models import CharacterKnowledge
from star_wars_rp.modules.resolutions.models import ActionResolution


def setup_campaign(
    gm: TestClient,
    player: TestClient,
    suffix: str,
    dc: int,
    *,
    roll_authority: str = "GM",
    risk_visibility: str = "GM_ONLY",
):
    player_info = register_and_login(player, f"player-{suffix}")
    gm_info = register_and_login(gm, f"gm-{suffix}")

    campaign = gm.post("/api/campaigns", json={"name": f"Campaign {suffix}"}).json()
    campaign_id = campaign["id"]

    response = gm.post(
        f"/api/campaigns/{campaign_id}/members",
        json={"username": f"player-{suffix}"},
    )
    assert response.status_code == 201, response.text

    character = gm.post(
        f"/api/campaigns/{campaign_id}/characters",
        json={"name": "Kara Venn", "slicing_modifier": 2},
    ).json()
    location = gm.post(
        f"/api/campaigns/{campaign_id}/locations",
        json={"name": "Imperial Cargo Terminal"},
    ).json()
    fragment = gm.post(
        f"/api/campaigns/{campaign_id}/knowledge-fragments",
        json={
            "claim_text": "The confiscated shipment was transferred to Dock 47.",
            "gm_veracity": "TRUE",
        },
    ).json()

    response = gm.put(
        f"/api/campaigns/{campaign_id}/player-assignment",
        json={
            "player_principal_id": player_info["id"],
            "character_id": character["id"],
        },
    )
    assert response.status_code == 204, response.text

    resolution = gm.post(
        f"/api/campaigns/{campaign_id}/resolutions",
        json={
            "actor_character_id": character["id"],
            "context_location_id": location["id"],
            "intent": "Discover where the confiscated shipment was transferred.",
            "risk": "On failure, Imperial security notices the intrusion.",
            "roll_authority": roll_authority,
            "risk_visibility": risk_visibility,
            "dc": dc,
            "success_recipient_character_id": character["id"],
            "success_fragment_id": fragment["id"],
        },
    )
    assert resolution.status_code == 201, resolution.text

    return {
        "campaign": campaign,
        "character": character,
        "location": location,
        "fragment": fragment,
        "resolution": resolution.json(),
        "player": player_info,
        "gm": gm_info,
    }


def test_success_reveal_is_authorized_atomic_and_idempotent():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        data = setup_campaign(gm, player, "success", dc=1)
        campaign_id = data["campaign"]["id"]
        resolution_id = data["resolution"]["id"]

        before = player.get(f"/api/player/campaigns/{campaign_id}/character")
        assert before.status_code == 200
        assert before.json()["knowledge"] == []

        for command, body in [
            ("roll", None),
            ("finalize", {"final_outcome": "SUCCESS"}),
            (
                "correct",
                {
                    "expected_adjudication_revision": 1,
                    "final_outcome": "FAILURE",
                    "failure_adjudication": "Not allowed",
                    "correction_reason": "Not allowed",
                },
            ),
        ]:
            response = (
                player.post(
                    f"/api/campaigns/{campaign_id}/resolutions/{resolution_id}/{command}",
                    json=body,
                )
                if body is not None
                else player.post(
                    f"/api/campaigns/{campaign_id}/resolutions/{resolution_id}/{command}"
                )
            )
            assert response.status_code == 403

        rolled = gm.post(f"/api/campaigns/{campaign_id}/resolutions/{resolution_id}/roll")
        assert rolled.status_code == 200, rolled.text
        assert rolled.json()["mechanical_result"] == "SUCCESS"
        assert rolled.json()["state"] == "AWAITING_ADJUDICATION"
        assert rolled.json()["final_outcome"] is None

        first_finalize = gm.post(
            f"/api/campaigns/{campaign_id}/resolutions/{resolution_id}/finalize",
            json={"final_outcome": "SUCCESS"},
        )
        second_finalize = gm.post(
            f"/api/campaigns/{campaign_id}/resolutions/{resolution_id}/finalize",
            json={"final_outcome": "SUCCESS"},
        )
        assert first_finalize.status_code == 200, first_finalize.text
        assert second_finalize.status_code == 200, second_finalize.text
        assert second_finalize.json()["state"] == "FINALIZED"
        assert second_finalize.json()["adjudication_revision"] == 1

        with SessionLocal() as db:
            knowledge_count = db.scalar(select(func.count()).select_from(CharacterKnowledge))
            event_count = db.scalar(
                select(func.count())
                .select_from(DomainEvent)
                .where(DomainEvent.event_type == "resolution.adjudication_finalized")
            )
            assert knowledge_count == 1
            assert event_count == 1

        after = player.get(f"/api/player/campaigns/{campaign_id}/character")
        assert after.status_code == 200
        assert after.json()["knowledge"][0]["claim_text"] == data["fragment"]["claim_text"]
        assert "gm_veracity" not in after.text

        player_resolution = player.get(
            f"/api/player/campaigns/{campaign_id}/resolutions/latest"
        )
        assert player_resolution.status_code == 200
        assert set(player_resolution.json()) == {
            "resolution_id",
            "natural_roll",
            "resolved_modifier",
            "total",
            "mechanical_result",
            "final_outcome",
            "is_overridden",
            "is_corrected",
            "previous_final_outcome",
        }
        player_resolution_body = player_resolution.json()
        assert "dc" not in player_resolution_body
        assert "adjudication_reason" not in player_resolution_body

        reloaded = gm.get(f"/api/campaigns/{campaign_id}/resolutions/{resolution_id}")
        assert reloaded.status_code == 200
        assert reloaded.json()["state"] == "FINALIZED"
        assert reloaded.json()["final_outcome"] == "SUCCESS"


def test_failure_uses_risk_and_finalizes_cleanly():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        data = setup_campaign(gm, player, "failure", dc=100)
        campaign_id = data["campaign"]["id"]
        resolution_id = data["resolution"]["id"]

        rolled = gm.post(f"/api/campaigns/{campaign_id}/resolutions/{resolution_id}/roll")
        assert rolled.status_code == 200
        assert rolled.json()["mechanical_result"] == "FAILURE"

        finalized = gm.post(
            f"/api/campaigns/{campaign_id}/resolutions/{resolution_id}/finalize",
            json={"final_outcome": "FAILURE"},
        )
        assert finalized.status_code == 200, finalized.text
        assert finalized.json()["state"] == "FINALIZED"
        assert finalized.json()["failure_adjudication"] == data["resolution"]["risk"]

        projection = player.get(f"/api/player/campaigns/{campaign_id}/character").json()
        assert projection["knowledge"] == []

        history = gm.get(f"/api/campaigns/{campaign_id}/history")
        assert history.status_code == 200
        assert "finalized FAILURE" in history.json()[0]["message"]


def test_cross_campaign_access_and_embedded_references_are_rejected():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        first = setup_campaign(gm, player, "one", dc=1)

        second_campaign = gm.post("/api/campaigns", json={"name": "Campaign two"}).json()
        second_id = second_campaign["id"]
        gm.post(f"/api/campaigns/{second_id}/members", json={"username": "player-one"})
        second_character = gm.post(
            f"/api/campaigns/{second_id}/characters",
            json={"name": "Second Kara", "slicing_modifier": 2},
        ).json()
        second_location = gm.post(
            f"/api/campaigns/{second_id}/locations",
            json={"name": "Second Terminal"},
        ).json()
        gm.put(
            f"/api/campaigns/{second_id}/player-assignment",
            json={
                "player_principal_id": first["player"]["id"],
                "character_id": second_character["id"],
            },
        )

        cross_assignment = gm.put(
            f"/api/campaigns/{first['campaign']['id']}/player-assignment",
            json={
                "player_principal_id": first["player"]["id"],
                "character_id": second_character["id"],
            },
        )
        assert cross_assignment.status_code == 404

        response = gm.post(
            f"/api/campaigns/{second_id}/resolutions",
            json={
                "actor_character_id": second_character["id"],
                "context_location_id": second_location["id"],
                "intent": "Read a secret.",
                "risk": "Security notices.",
                "dc": 1,
                "success_recipient_character_id": second_character["id"],
                "success_fragment_id": first["fragment"]["id"],
            },
        )
        assert response.status_code in {404, 422}

        outsider = TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app)
        register_and_login(outsider, "outsider")
        assert outsider.get(
            f"/api/player/campaigns/{first['campaign']['id']}/character"
        ).status_code == 403
        assert outsider.get(
            f"/api/player/campaigns/{first['campaign']['id']}/resolutions/latest"
        ).status_code == 403
        outsider.close()


def test_finalize_rolls_back_if_event_insert_fails():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        data = setup_campaign(gm, player, "rollback", dc=1)
        campaign_id = data["campaign"]["id"]
        resolution_id = data["resolution"]["id"]
        rolled = gm.post(f"/api/campaigns/{campaign_id}/resolutions/{resolution_id}/roll")
        assert rolled.json()["mechanical_result"] == "SUCCESS"

        def fail_domain_event_insert(_mapper, _connection, _target):
            raise RuntimeError("forced DomainEvent insert failure")

        event.listen(DomainEvent, "before_insert", fail_domain_event_insert)
        try:
            with SessionLocal() as db:
                with pytest.raises(RuntimeError, match="forced DomainEvent"):
                    finalize_resolution(
                        db,
                        uuid.UUID(data["gm"]["id"]),
                        uuid.UUID(campaign_id),
                        uuid.UUID(resolution_id),
                        "SUCCESS",
                    )
                db.rollback()
        finally:
            event.remove(DomainEvent, "before_insert", fail_domain_event_insert)

        with SessionLocal() as db:
            resolution = db.get(ActionResolution, uuid.UUID(resolution_id))
            assert resolution.state == "AWAITING_ADJUDICATION"
            assert resolution.final_outcome is None
            assert db.scalar(select(func.count()).select_from(CharacterKnowledge)) == 0
            assert db.scalar(select(func.count()).select_from(DomainEvent)) == 0


def test_role_authorization_is_reloaded_from_database():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm:
        gm_info = register_and_login(gm, "role-change-gm")
        campaign = gm.post("/api/campaigns", json={"name": "Role source"}).json()
        campaign_id = uuid.UUID(campaign["id"])

        with SessionLocal() as db:
            membership = db.get(
                CampaignMembership,
                {
                    "campaign_id": campaign_id,
                    "principal_id": uuid.UUID(gm_info["id"]),
                },
            )
            membership.role = "PLAYER"
            db.commit()

        response = gm.post(
            f"/api/campaigns/{campaign_id}/characters",
            json={"name": "Must fail", "slicing_modifier": 1},
        )
        assert response.status_code == 403


def test_assignment_is_server_authoritative():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        data = setup_campaign(gm, player, "assignment", dc=1)
        campaign_id = uuid.UUID(data["campaign"]["id"])
        player_id = uuid.UUID(data["player"]["id"])

        with SessionLocal() as db:
            assignment = db.get(
                PlayerCharacterAssignment,
                {"campaign_id": campaign_id, "player_principal_id": player_id},
            )
            assert assignment is not None
            assert assignment.character_id == uuid.UUID(data["character"]["id"])

        projection = player.get(f"/api/player/campaigns/{campaign_id}/character")
        assert projection.status_code == 200
        assert projection.json()["character"]["id"] == data["character"]["id"]
