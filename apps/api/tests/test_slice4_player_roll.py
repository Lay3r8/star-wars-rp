import concurrent.futures
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select

from conftest import register_and_login
from star_wars_rp.db import SessionLocal
from star_wars_rp.modules.resolutions.models import ActionResolution
from test_slice1_integration import setup_campaign


def _pending(player: TestClient, data: dict):
    return player.get(
        f"/api/player/campaigns/{data['campaign']['id']}/resolutions/pending"
    )


def _player_roll(player: TestClient, data: dict):
    return player.post(
        f"/api/player/campaigns/{data['campaign']['id']}/resolutions/{data['resolution']['id']}/roll"
    )


def test_player_pending_projection_is_safe_and_risk_visibility_is_explicit():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        hidden = setup_campaign(
            gm,
            player,
            "s4-hidden",
            dc=100,
            roll_authority="PLAYER",
            risk_visibility="GM_ONLY",
        )
        response = _pending(player, hidden)
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["state"] == "READY"
        assert body["actor_character_id"] == hidden["character"]["id"]
        assert body["actor_name"] == "Kara Venn"
        assert body["mechanic"] == "Slicing"
        assert body["context_location_id"] == hidden["location"]["id"]
        assert body["context_location_name"] == "Imperial Cargo Terminal"
        assert body["intent"] == hidden["resolution"]["intent"]
        assert set(body) == {
            "resolution_id",
            "actor_character_id",
            "actor_name",
            "mechanic",
            "context_location_id",
            "context_location_name",
            "intent",
            "state",
        }
        for forbidden in [
            "known_risk",
            "risk",
            "risk_visibility",
            "dc",
            "resolved_modifier",
            "success_fragment_id",
            "success_preview",
            "claim_text",
            "gm_veracity",
            "final_outcome",
        ]:
            assert forbidden not in body

    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm2, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player2:
        visible = setup_campaign(
            gm2,
            player2,
            "s4-visible",
            dc=100,
            roll_authority="PLAYER",
            risk_visibility="PLAYER_VISIBLE",
        )
        body = _pending(player2, visible).json()
        assert body["known_risk"] == visible["resolution"]["risk"]
        assert "dc" not in body
        assert visible["fragment"]["claim_text"] not in str(body)


def test_player_roll_is_backend_authoritative_one_shot_and_slice3_override_still_works():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        data = setup_campaign(
            gm,
            player,
            "s4-roll",
            dc=100,
            roll_authority="PLAYER",
            risk_visibility="PLAYER_VISIBLE",
        )
        campaign_id = data["campaign"]["id"]
        resolution_id = data["resolution"]["id"]

        gm_roll = gm.post(
            f"/api/campaigns/{campaign_id}/resolutions/{resolution_id}/roll"
        )
        assert gm_roll.status_code == 409

        injected = player.post(
            f"/api/player/campaigns/{campaign_id}/resolutions/{resolution_id}/roll",
            json={
                "natural_roll": 20,
                "dc": 1,
                "actor_character_id": data["character"]["id"],
                "final_outcome": "SUCCESS",
            },
        )
        assert injected.status_code == 422

        first = _player_roll(player, data)
        second = _player_roll(player, data)
        assert first.status_code == 200, first.text
        assert second.status_code == 200, second.text
        first_body = first.json()
        second_body = second.json()
        assert first_body["state"] == "AWAITING_ADJUDICATION"
        assert first_body["natural_roll"] == second_body["natural_roll"]
        assert first_body["total"] == second_body["total"]
        assert first_body["mechanical_result"] == "FAILURE"
        assert "dc" not in first_body
        assert data["fragment"]["claim_text"] not in str(first_body)

        with SessionLocal() as db:
            persisted = db.get(ActionResolution, uuid.UUID(resolution_id))
            evidence = (
                persisted.natural_roll,
                persisted.resolved_modifier,
                persisted.total,
                persisted.dc,
                persisted.mechanical_result,
            )

        finalized = gm.post(
            f"/api/campaigns/{campaign_id}/resolutions/{resolution_id}/finalize",
            json={
                "final_outcome": "SUCCESS",
                "reason": "Cached transfer records remain readable.",
            },
        )
        assert finalized.status_code == 200, finalized.text
        assert finalized.json()["mechanical_result"] == "FAILURE"
        assert finalized.json()["final_outcome"] == "SUCCESS"
        assert finalized.json()["is_overridden"] is True

        with SessionLocal() as db:
            persisted = db.get(ActionResolution, uuid.UUID(resolution_id))
            assert (
                persisted.natural_roll,
                persisted.resolved_modifier,
                persisted.total,
                persisted.dc,
                persisted.mechanical_result,
            ) == evidence

        final_player = player.get(
            f"/api/player/campaigns/{campaign_id}/resolutions/latest"
        )
        assert final_player.status_code == 200
        assert final_player.json()["mechanical_result"] == "FAILURE"
        assert final_player.json()["final_outcome"] == "SUCCESS"
        assert "dc" not in final_player.json()


def test_player_cannot_roll_gm_authority_or_another_characters_resolution():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        gm_authority = setup_campaign(gm, player, "s4-gm-authority", dc=1)
        assert _pending(player, gm_authority).json() is None
        assert _player_roll(player, gm_authority).status_code == 404

        other = TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app)
        try:
            other_info = register_and_login(other, "s4-other-player")
            add = gm.post(
                f"/api/campaigns/{gm_authority['campaign']['id']}/members",
                json={"username": "s4-other-player"},
            )
            assert add.status_code == 201, add.text
            assert other.get(
                f"/api/player/campaigns/{gm_authority['campaign']['id']}/resolutions/pending"
            ).status_code == 404
            assert other.post(
                f"/api/player/campaigns/{gm_authority['campaign']['id']}/resolutions/{gm_authority['resolution']['id']}/roll"
            ).status_code == 404
            assert other_info["id"] != gm_authority["player"]["id"]
        finally:
            other.close()


def test_concurrent_player_roll_requests_persist_one_raw_roll():
    suffix = "s4-concurrent"
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        data = setup_campaign(
            gm,
            player,
            suffix,
            dc=100,
            roll_authority="PLAYER",
        )

        second_player = TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app)
        try:
            login = second_player.post(
                "/api/auth/login",
                json={"username": f"player-{suffix}", "password": "password123"},
            )
            assert login.status_code == 200, login.text

            url = (
                f"/api/player/campaigns/{data['campaign']['id']}"
                f"/resolutions/{data['resolution']['id']}/roll"
            )
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                responses = list(
                    pool.map(lambda client: client.post(url), [player, second_player])
                )

            assert [response.status_code for response in responses] == [200, 200]
            bodies = [response.json() for response in responses]
            assert bodies[0]["natural_roll"] == bodies[1]["natural_roll"]
            assert bodies[0]["total"] == bodies[1]["total"]
            assert bodies[0]["mechanical_result"] == bodies[1]["mechanical_result"]

            with SessionLocal() as db:
                persisted = db.scalar(
                    select(ActionResolution).where(
                        ActionResolution.id == uuid.UUID(data["resolution"]["id"])
                    )
                )
                assert persisted.state == "AWAITING_ADJUDICATION"
                assert persisted.natural_roll == bodies[0]["natural_roll"]
        finally:
            second_player.close()
