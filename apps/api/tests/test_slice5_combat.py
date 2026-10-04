import concurrent.futures
import uuid
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event, func, select
from sqlalchemy.exc import IntegrityError

from conftest import register_and_login
from star_wars_rp.application.combat import player_escape
from star_wars_rp.db import SessionLocal
from star_wars_rp.modules.combat.models import CombatEncounter
from star_wars_rp.modules.combat.rules import advance_escape, apply_fixed_damage, resolve_combat_attack
from star_wars_rp.modules.history.models import DomainEvent


def prepare_combat(gm: TestClient, player: TestClient, suffix: str, *, start: bool = True) -> dict:
    player_info = register_and_login(player, f"s5-player-{suffix}")
    gm_info = register_and_login(gm, f"s5-gm-{suffix}")
    campaign = gm.post("/api/campaigns", json={"name": f"Slice 5 {suffix}"}).json()
    campaign_id = campaign["id"]

    response = gm.post(
        f"/api/campaigns/{campaign_id}/members",
        json={"username": f"s5-player-{suffix}"},
    )
    assert response.status_code == 201, response.text

    character = gm.post(
        f"/api/campaigns/{campaign_id}/characters",
        json={"name": "Globox", "slicing_modifier": 0},
    ).json()
    location = gm.post(
        f"/api/campaigns/{campaign_id}/locations",
        json={"name": "Docking Bay 47"},
    ).json()
    assigned = gm.put(
        f"/api/campaigns/{campaign_id}/player-assignment",
        json={
            "player_principal_id": player_info["id"],
            "character_id": character["id"],
        },
    )
    assert assigned.status_code == 204, assigned.text

    encounter = None
    if start:
        started = gm.post(
            f"/api/campaigns/{campaign_id}/combat-encounters",
            json={"player_character_id": character["id"], "location_id": location["id"]},
        )
        assert started.status_code == 201, started.text
        encounter = started.json()

    return {
        "campaign": campaign,
        "player": player_info,
        "gm": gm_info,
        "character": character,
        "location": location,
        "encounter": encounter,
    }


def player_command(player: TestClient, data: dict, command: str, round_number: int):
    return player.post(
        f"/api/player/campaigns/{data['campaign']['id']}/combat-encounters/"
        f"{data['encounter']['encounter_id']}/{command}",
        json={"expected_round": round_number},
    )


def patrol_command(gm: TestClient, data: dict, round_number: int):
    return gm.post(
        f"/api/campaigns/{data['campaign']['id']}/combat-encounters/"
        f"{data['encounter']['encounter_id']}/patrol-attack",
        json={"expected_round": round_number},
    )


def test_combat_rule_helpers_keep_d20_ordinary_and_effects_bounded():
    assert resolve_combat_attack(1, 20, 12, 2) == (21, "HIT", 2)
    assert resolve_combat_attack(20, -20, 12, 2) == (0, "MISS", 0)
    assert apply_fixed_damage(1, 2) == 0
    assert apply_fixed_damage(4, 2) == 2
    assert advance_escape(2, 3) == 3
    assert advance_escape(3, 3) == 3


def test_start_encounter_initializes_server_tuning_and_player_projection_is_explicit():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        data = prepare_combat(gm, player, "initial")
        body = data["encounter"]
        assert body["status"] == "ACTIVE"
        assert body["round"] == 1
        assert body["current_actor"] == "PLAYER"
        assert body["objective"] == "Escape the Imperial Patrol"
        assert body["player_vitality"] == 4
        assert body["patrol_strength"] == 4
        assert body["escape_progress"] == 0
        assert body["escape_target"] == 3
        assert body["can_resolve_patrol_attack"] is False

        with SessionLocal() as db:
            encounter = db.get(CombatEncounter, uuid.UUID(body["encounter_id"]))
            assert encounter is not None
            assert (
                encounter.player_attack_modifier,
                encounter.player_defence,
                encounter.player_attack_damage,
                encounter.player_vitality_initial,
            ) == (3, 12, 2, 4)
            assert (
                encounter.patrol_attack_modifier,
                encounter.patrol_defence,
                encounter.patrol_attack_damage,
                encounter.patrol_strength_initial,
            ) == (2, 12, 2, 4)

        projection = player.get(
            f"/api/player/campaigns/{data['campaign']['id']}/combat-encounters/latest"
        )
        assert projection.status_code == 200, projection.text
        player_body = projection.json()
        assert player_body["player_character_name"] == "Globox"
        assert player_body["hostile_name"] == "Imperial Patrol"
        assert player_body["can_attack"] is True
        assert player_body["can_escape"] is True
        assert player_body["last_action"] is None
        for forbidden in [
            "campaign_id",
            "location_id",
            "created_by_principal_id",
            "player_attack_modifier",
            "player_defence",
            "player_attack_damage",
            "patrol_attack_modifier",
            "patrol_defence",
            "patrol_attack_damage",
            "can_resolve_patrol_attack",
        ]:
            assert forbidden not in player_body


def test_client_cannot_inject_combat_authority_values():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        data = prepare_combat(gm, player, "injection", start=False)
        campaign_id = data["campaign"]["id"]

        injected_start = gm.post(
            f"/api/campaigns/{campaign_id}/combat-encounters",
            json={
                "player_character_id": data["character"]["id"],
                "location_id": data["location"]["id"],
                "player_vitality": 999,
                "patrol_defence": 1,
            },
        )
        assert injected_start.status_code == 422

        started = gm.post(
            f"/api/campaigns/{campaign_id}/combat-encounters",
            json={"player_character_id": data["character"]["id"], "location_id": data["location"]["id"]},
        )
        assert started.status_code == 201, started.text
        data["encounter"] = started.json()

        injected_action = player.post(
            f"/api/player/campaigns/{campaign_id}/combat-encounters/"
            f"{data['encounter']['encounter_id']}/attack",
            json={"expected_round": 1, "natural_roll": 20, "damage": 999, "status": "ESCAPED"},
        )
        assert injected_action.status_code == 422

        current = player.get(
            f"/api/player/campaigns/{campaign_id}/combat-encounters/latest"
        ).json()
        assert current["current_actor"] == "PLAYER"
        assert current["patrol_strength"] == 4


def test_escape_path_turn_progression_history_and_terminal_state():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        data = prepare_combat(gm, player, "escape")

        with patch("star_wars_rp.application.combat.roll_d20", return_value=1):
            for round_number in (1, 2):
                escaped = player_command(player, data, "escape", round_number)
                assert escaped.status_code == 200, escaped.text
                assert escaped.json()["escape_progress"] == round_number
                assert escaped.json()["round"] == round_number
                assert escaped.json()["current_actor"] == "PATROL"
                assert escaped.json()["last_action"]["action"] == "ESCAPE"

                patrol = patrol_command(gm, data, round_number)
                assert patrol.status_code == 200, patrol.text
                assert patrol.json()["round"] == round_number + 1
                assert patrol.json()["current_actor"] == "PLAYER"
                assert patrol.json()["player_vitality"] == 4
                assert patrol.json()["last_action"]["result"] == "MISS"

            terminal = player_command(player, data, "escape", 3)

        assert terminal.status_code == 200, terminal.text
        body = terminal.json()
        assert body["status"] == "ESCAPED"
        assert body["escape_progress"] == 3
        assert body["current_actor"] is None
        assert body["ended_at"] is not None
        assert body["can_attack"] is False
        assert body["can_escape"] is False
        assert body["last_action"]["terminal_status"] == "ESCAPED"

        rejected = player_command(player, data, "attack", 3)
        assert rejected.status_code == 409

        with SessionLocal() as db:
            event_count = db.scalar(
                select(func.count())
                .select_from(DomainEvent)
                .where(DomainEvent.subject_id == uuid.UUID(body["encounter_id"]))
            )
            assert event_count == 5


def test_attack_can_neutralize_patrol_without_gm_finalize():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        data = prepare_combat(gm, player, "neutralize")
        with patch("star_wars_rp.application.combat.roll_d20", return_value=20):
            first = player_command(player, data, "attack", 1)
        assert first.status_code == 200
        assert first.json()["patrol_strength"] == 2
        assert first.json()["last_action"]["result"] == "HIT"
        assert first.json()["last_action"]["damage"] == 2

        with patch("star_wars_rp.application.combat.roll_d20", return_value=1):
            assert patrol_command(gm, data, 1).status_code == 200

        with patch("star_wars_rp.application.combat.roll_d20", return_value=20):
            terminal = player_command(player, data, "attack", 2)
        assert terminal.status_code == 200
        body = terminal.json()
        assert body["status"] == "PATROL_NEUTRALIZED"
        assert body["patrol_strength"] == 0
        assert body["current_actor"] is None
        assert body["last_action"]["terminal_status"] == "PATROL_NEUTRALIZED"


def test_patrol_can_incapacitate_player_and_end_immediately():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        data = prepare_combat(gm, player, "incapacitate")

        assert player_command(player, data, "escape", 1).status_code == 200
        with patch("star_wars_rp.application.combat.roll_d20", return_value=20):
            first = patrol_command(gm, data, 1)
        assert first.status_code == 200
        assert first.json()["player_vitality"] == 2
        assert first.json()["round"] == 2

        assert player_command(player, data, "escape", 2).status_code == 200
        with patch("star_wars_rp.application.combat.roll_d20", return_value=20):
            terminal = patrol_command(gm, data, 2)
        assert terminal.status_code == 200
        body = terminal.json()
        assert body["status"] == "INCAPACITATED"
        assert body["player_vitality"] == 0
        assert body["current_actor"] is None
        assert body["round"] == 2
        assert body["last_action"]["terminal_status"] == "INCAPACITATED"


def test_authorization_assignment_and_campaign_isolation_are_server_authoritative():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        data = prepare_combat(gm, player, "security")
        campaign_id = data["campaign"]["id"]
        encounter_id = data["encounter"]["encounter_id"]

        other = TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app)
        outsider = TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app)
        try:
            other_info = register_and_login(other, "s5-other-player")
            added = gm.post(f"/api/campaigns/{campaign_id}/members", json={"username": "s5-other-player"})
            assert added.status_code == 201
            other_character = gm.post(
                f"/api/campaigns/{campaign_id}/characters",
                json={"name": "Other Character", "slicing_modifier": 0},
            ).json()
            assert gm.put(
                f"/api/campaigns/{campaign_id}/player-assignment",
                json={"player_principal_id": other_info["id"], "character_id": other_character["id"]},
            ).status_code == 204

            assert other.get(
                f"/api/player/campaigns/{campaign_id}/combat-encounters/latest"
            ).json() is None
            assert other.post(
                f"/api/player/campaigns/{campaign_id}/combat-encounters/{encounter_id}/escape",
                json={"expected_round": 1},
            ).status_code == 404

            register_and_login(outsider, "s5-outsider")
            assert outsider.get(
                f"/api/player/campaigns/{campaign_id}/combat-encounters/latest"
            ).status_code == 403
            assert outsider.post(
                f"/api/player/campaigns/{campaign_id}/combat-encounters/{encounter_id}/attack",
                json={"expected_round": 1},
            ).status_code == 403

            second_campaign = gm.post("/api/campaigns", json={"name": "Other campaign"}).json()
            second_location = gm.post(
                f"/api/campaigns/{second_campaign['id']}/locations",
                json={"name": "Wrong Location"},
            ).json()
            cross = gm.post(
                f"/api/campaigns/{campaign_id}/combat-encounters",
                json={
                    "player_character_id": data["character"]["id"],
                    "location_id": second_location["id"],
                },
            )
            assert cross.status_code == 404
        finally:
            other.close()
            outsider.close()


def test_concurrent_player_attack_applies_at_most_once_and_stale_round_is_rejected():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        data = prepare_combat(gm, player, "attack-concurrency")
        second_player = TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app)
        try:
            assert second_player.post(
                "/api/auth/login",
                json={"username": "s5-player-attack-concurrency", "password": "password123"},
            ).status_code == 200
            url = (
                f"/api/player/campaigns/{data['campaign']['id']}/combat-encounters/"
                f"{data['encounter']['encounter_id']}/attack"
            )
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                responses = list(
                    pool.map(
                        lambda client: client.post(url, json={"expected_round": 1}),
                        [player, second_player],
                    )
                )
            assert sorted(response.status_code for response in responses) == [200, 409]

            with SessionLocal() as db:
                count = db.scalar(
                    select(func.count())
                    .select_from(DomainEvent)
                    .where(
                        DomainEvent.subject_id == uuid.UUID(data["encounter"]["encounter_id"]),
                        DomainEvent.event_type == "combat.player_attack_resolved",
                    )
                )
                assert count == 1

            with patch("star_wars_rp.application.combat.roll_d20", return_value=1):
                patrol = patrol_command(gm, data, 1)
            assert patrol.status_code == 200
            assert patrol.json()["round"] == 2
            stale = player.post(url, json={"expected_round": 1})
            assert stale.status_code == 409
            assert "reload" in stale.json()["detail"].lower()
        finally:
            second_player.close()


def test_concurrent_escape_and_patrol_attack_each_apply_at_most_once():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        data = prepare_combat(gm, player, "other-concurrency")
        second_player = TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app)
        second_gm = TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app)
        try:
            assert second_player.post(
                "/api/auth/login",
                json={"username": "s5-player-other-concurrency", "password": "password123"},
            ).status_code == 200
            assert second_gm.post(
                "/api/auth/login",
                json={"username": "s5-gm-other-concurrency", "password": "password123"},
            ).status_code == 200

            escape_url = (
                f"/api/player/campaigns/{data['campaign']['id']}/combat-encounters/"
                f"{data['encounter']['encounter_id']}/escape"
            )
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                escape_responses = list(
                    pool.map(
                        lambda client: client.post(escape_url, json={"expected_round": 1}),
                        [player, second_player],
                    )
                )
            assert sorted(response.status_code for response in escape_responses) == [200, 409]

            patrol_url = (
                f"/api/campaigns/{data['campaign']['id']}/combat-encounters/"
                f"{data['encounter']['encounter_id']}/patrol-attack"
            )
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                patrol_responses = list(
                    pool.map(
                        lambda client: client.post(patrol_url, json={"expected_round": 1}),
                        [gm, second_gm],
                    )
                )
            assert sorted(response.status_code for response in patrol_responses) == [200, 409]

            with SessionLocal() as db:
                escape_count = db.scalar(
                    select(func.count()).select_from(DomainEvent).where(
                        DomainEvent.subject_id == uuid.UUID(data["encounter"]["encounter_id"]),
                        DomainEvent.event_type == "combat.escape_advanced",
                    )
                )
                patrol_count = db.scalar(
                    select(func.count()).select_from(DomainEvent).where(
                        DomainEvent.subject_id == uuid.UUID(data["encounter"]["encounter_id"]),
                        DomainEvent.event_type == "combat.patrol_attack_resolved",
                    )
                )
                assert escape_count == 1
                assert patrol_count == 1
        finally:
            second_player.close()
            second_gm.close()


def test_concurrent_start_is_atomically_unique_per_character():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        data = prepare_combat(gm, player, "create-concurrency", start=False)
        second_gm = TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app)
        try:
            assert second_gm.post(
                "/api/auth/login",
                json={"username": "s5-gm-create-concurrency", "password": "password123"},
            ).status_code == 200
            url = f"/api/campaigns/{data['campaign']['id']}/combat-encounters"
            payload = {
                "player_character_id": data["character"]["id"],
                "location_id": data["location"]["id"],
            }
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                responses = list(pool.map(lambda client: client.post(url, json=payload), [gm, second_gm]))
            assert sorted(response.status_code for response in responses) == [201, 409]

            with SessionLocal() as db:
                active_count = db.scalar(
                    select(func.count()).select_from(CombatEncounter).where(
                        CombatEncounter.campaign_id == uuid.UUID(data["campaign"]["id"]),
                        CombatEncounter.player_character_id == uuid.UUID(data["character"]["id"]),
                        CombatEncounter.status == "ACTIVE",
                    )
                )
                assert active_count == 1
        finally:
            second_gm.close()


def test_combat_state_and_history_rollback_together_if_event_insert_fails():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        data = prepare_combat(gm, player, "atomicity")

        def fail_domain_event_insert(_mapper, _connection, _target):
            raise RuntimeError("forced combat DomainEvent insert failure")

        event.listen(DomainEvent, "before_insert", fail_domain_event_insert)
        try:
            with SessionLocal() as db:
                with pytest.raises(RuntimeError, match="forced combat DomainEvent"):
                    player_escape(
                        db,
                        uuid.UUID(data["player"]["id"]),
                        uuid.UUID(data["campaign"]["id"]),
                        uuid.UUID(data["encounter"]["encounter_id"]),
                        1,
                    )
                db.rollback()
        finally:
            event.remove(DomainEvent, "before_insert", fail_domain_event_insert)

        with SessionLocal() as db:
            encounter = db.get(CombatEncounter, uuid.UUID(data["encounter"]["encounter_id"]))
            assert encounter.escape_progress == 0
            assert encounter.current_actor == "PLAYER"
            assert db.scalar(select(func.count()).select_from(DomainEvent)) == 0


def test_database_invariants_reject_out_of_range_vitality():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        data = prepare_combat(gm, player, "db-invariant")
        with SessionLocal() as db:
            encounter = db.get(CombatEncounter, uuid.UUID(data["encounter"]["encounter_id"]))
            encounter.player_vitality = 5
            with pytest.raises(IntegrityError):
                db.commit()
            db.rollback()
