import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event, func, select, text
from sqlalchemy.exc import IntegrityError

from conftest import register_and_login
from star_wars_rp.application.resolutions import correct_resolution
from star_wars_rp.db import SessionLocal
from star_wars_rp.modules.history.models import DomainEvent
from star_wars_rp.modules.knowledge.models import CharacterKnowledge
from star_wars_rp.modules.resolutions.models import ActionResolution
from test_slice1_integration import setup_campaign


def _roll(gm: TestClient, data: dict) -> dict:
    response = gm.post(
        f"/api/campaigns/{data['campaign']['id']}/resolutions/{data['resolution']['id']}/roll"
    )
    assert response.status_code == 200, response.text
    return response.json()


def _finalize(
    gm: TestClient,
    data: dict,
    final_outcome: str,
    *,
    failure_adjudication: str | None = None,
    reason: str | None = None,
) -> dict:
    payload = {"final_outcome": final_outcome}
    if failure_adjudication is not None:
        payload["failure_adjudication"] = failure_adjudication
    if reason is not None:
        payload["reason"] = reason
    response = gm.post(
        f"/api/campaigns/{data['campaign']['id']}/resolutions/{data['resolution']['id']}/finalize",
        json=payload,
    )
    assert response.status_code == 200, response.text
    return response.json()


def _correct(
    gm: TestClient,
    data: dict,
    revision: int,
    final_outcome: str,
    reason: str,
    *,
    failure_adjudication: str | None = None,
) -> dict:
    payload = {
        "expected_adjudication_revision": revision,
        "final_outcome": final_outcome,
        "correction_reason": reason,
    }
    if failure_adjudication is not None:
        payload["failure_adjudication"] = failure_adjudication
    response = gm.post(
        f"/api/campaigns/{data['campaign']['id']}/resolutions/{data['resolution']['id']}/correct",
        json=payload,
    )
    assert response.status_code == 200, response.text
    return response.json()


def _mechanical_evidence(value: dict) -> tuple:
    return (
        value["natural_roll"],
        value["resolved_modifier"],
        value["total"],
        value["dc"],
        value["mechanical_result"],
    )


def test_roll_is_idempotent_and_mechanical_evidence_is_immutable():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        data = setup_campaign(gm, player, "s3-immutable", dc=1)
        first = _roll(gm, data)
        second = _roll(gm, data)
        assert _mechanical_evidence(second) == _mechanical_evidence(first)
        assert second["state"] == "AWAITING_ADJUDICATION"
        assert second["final_outcome"] is None

        finalized = _finalize(gm, data, "SUCCESS")
        assert _mechanical_evidence(finalized) == _mechanical_evidence(first)

        corrected = _correct(
            gm,
            data,
            1,
            "FAILURE",
            "The terminal result was adjudicated against the fiction.",
            failure_adjudication="Only the local security log records the intrusion.",
        )
        assert _mechanical_evidence(corrected) == _mechanical_evidence(first)
        assert corrected["state"] == "FINALIZED"
        assert corrected["adjudication_revision"] == 2

        with SessionLocal() as db:
            with pytest.raises(IntegrityError):
                db.execute(
                    text(
                        "UPDATE action_resolution SET total = total + 1 WHERE id = :id"
                    ),
                    {"id": uuid.UUID(data["resolution"]["id"])},
                )
                db.commit()
            db.rollback()


def test_both_override_directions_preserve_mechanical_result():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        failure = setup_campaign(gm, player, "s3-override-fs", dc=100)
        rolled_failure = _roll(gm, failure)
        assert rolled_failure["mechanical_result"] == "FAILURE"
        overridden_success = _finalize(
            gm,
            failure,
            "SUCCESS",
            reason="The cached transfer record is still readable.",
        )
        assert overridden_success["mechanical_result"] == "FAILURE"
        assert overridden_success["final_outcome"] == "SUCCESS"
        assert overridden_success["is_overridden"] is True
        assert player.get(
            f"/api/player/campaigns/{failure['campaign']['id']}/character"
        ).json()["knowledge"]

    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm2, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player2:
        success = setup_campaign(gm2, player2, "s3-override-sf", dc=1)
        rolled_success = _roll(gm2, success)
        assert rolled_success["mechanical_result"] == "SUCCESS"
        overridden_failure = _finalize(
            gm2,
            success,
            "FAILURE",
            failure_adjudication="Imperial security notices the intrusion.",
            reason="The access token was a decoy.",
        )
        assert overridden_failure["mechanical_result"] == "SUCCESS"
        assert overridden_failure["final_outcome"] == "FAILURE"
        assert overridden_failure["is_overridden"] is True
        assert player2.get(
            f"/api/player/campaigns/{success['campaign']['id']}/character"
        ).json()["knowledge"] == []


def test_failure_to_success_correction_adds_knowledge_and_preserves_history():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        data = setup_campaign(gm, player, "s3-correct-fs", dc=100)
        _roll(gm, data)
        finalized = _finalize(gm, data, "FAILURE")
        evidence = _mechanical_evidence(finalized)
        assert player.get(
            f"/api/player/campaigns/{data['campaign']['id']}/character"
        ).json()["knowledge"] == []

        corrected = _correct(
            gm,
            data,
            1,
            "SUCCESS",
            "The GM corrected the adjudication after reviewing the fiction.",
        )
        assert corrected["final_outcome"] == "SUCCESS"
        assert corrected["adjudication_revision"] == 2
        assert corrected["is_corrected"] is True
        assert corrected["previous_final_outcome"] == "FAILURE"
        assert _mechanical_evidence(corrected) == evidence

        projection = player.get(
            f"/api/player/campaigns/{data['campaign']['id']}/character"
        ).json()
        assert projection["knowledge"][0]["claim_text"] == data["fragment"]["claim_text"]

        with SessionLocal() as db:
            events = db.scalars(
                select(DomainEvent)
                .where(DomainEvent.subject_id == uuid.UUID(data["resolution"]["id"]))
                .order_by(DomainEvent.occurred_at)
            ).all()
            assert [e.event_type for e in events] == [
                "resolution.adjudication_finalized",
                "resolution.adjudication_corrected",
            ]
            assert events[-1].payload["previous_final_outcome"] == "FAILURE"
            assert events[-1].payload["success_disclosure_applied_now"] is True


def test_success_to_failure_correction_retains_irreversible_knowledge():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        data = setup_campaign(gm, player, "s3-correct-sf", dc=1)
        _roll(gm, data)
        _finalize(gm, data, "SUCCESS")
        before = player.get(
            f"/api/player/campaigns/{data['campaign']['id']}/character"
        ).json()
        assert before["knowledge"][0]["claim_text"] == data["fragment"]["claim_text"]

        corrected = _correct(
            gm,
            data,
            1,
            "FAILURE",
            "The GM corrected the adjudication but cannot erase disclosure.",
            failure_adjudication="Imperial security notices the intrusion.",
        )
        assert corrected["final_outcome"] == "FAILURE"
        assert corrected["mechanical_result"] == "SUCCESS"
        assert corrected["adjudication_revision"] == 2

        after = player.get(
            f"/api/player/campaigns/{data['campaign']['id']}/character"
        ).json()
        assert after["knowledge"] == before["knowledge"]

        summary = player.get(
            f"/api/player/campaigns/{data['campaign']['id']}/resolutions/latest"
        )
        assert summary.status_code == 200
        assert summary.json()["mechanical_result"] == "SUCCESS"
        assert summary.json()["final_outcome"] == "FAILURE"
        assert summary.json()["is_corrected"] is True
        assert summary.json()["previous_final_outcome"] == "SUCCESS"
        player_summary = summary.json()
        for forbidden in [
            "dc",
            "adjudication_reason",
            "correction_reason",
            "failure_adjudication",
            "gm_veracity",
            "risk",
        ]:
            assert forbidden not in player_summary

        with SessionLocal() as db:
            knowledge_count = db.scalar(
                select(func.count())
                .select_from(CharacterKnowledge)
                .where(
                    CharacterKnowledge.campaign_id == uuid.UUID(data["campaign"]["id"]),
                    CharacterKnowledge.character_id == uuid.UUID(data["character"]["id"]),
                    CharacterKnowledge.fragment_id == uuid.UUID(data["fragment"]["id"]),
                )
            )
            assert knowledge_count == 1
            correction = db.scalar(
                select(DomainEvent)
                .where(
                    DomainEvent.subject_id == uuid.UUID(data["resolution"]["id"]),
                    DomainEvent.event_type == "resolution.adjudication_corrected",
                )
            )
            assert correction.payload["prior_success_disclosure_retained"] is True


def test_failure_text_correction_noop_and_stale_revision():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        data = setup_campaign(gm, player, "s3-failure-text", dc=100)
        _roll(gm, data)
        finalized = _finalize(gm, data, "FAILURE")
        old_text = finalized["failure_adjudication"]

        noop = gm.post(
            f"/api/campaigns/{data['campaign']['id']}/resolutions/{data['resolution']['id']}/correct",
            json={
                "expected_adjudication_revision": 1,
                "final_outcome": "FAILURE",
                "failure_adjudication": old_text,
                "correction_reason": "This must still be rejected as a no-op.",
            },
        )
        assert noop.status_code == 422

        changed = _correct(
            gm,
            data,
            1,
            "FAILURE",
            "Narrow the failure consequence.",
            failure_adjudication="Only the terminal's local security log records the intrusion.",
        )
        assert changed["adjudication_revision"] == 2
        assert changed["failure_adjudication"] != old_text

        stale = gm.post(
            f"/api/campaigns/{data['campaign']['id']}/resolutions/{data['resolution']['id']}/correct",
            json={
                "expected_adjudication_revision": 1,
                "final_outcome": "SUCCESS",
                "correction_reason": "Stale request.",
            },
        )
        assert stale.status_code == 409

        with SessionLocal() as db:
            assert db.scalar(
                select(func.count())
                .select_from(DomainEvent)
                .where(
                    DomainEvent.subject_id == uuid.UUID(data["resolution"]["id"]),
                    DomainEvent.event_type == "resolution.adjudication_corrected",
                )
            ) == 1


def test_correction_rolls_back_if_event_insert_fails():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        data = setup_campaign(gm, player, "s3-correct-rollback", dc=100)
        _roll(gm, data)
        _finalize(gm, data, "FAILURE")

        def fail_domain_event_insert(_mapper, _connection, _target):
            raise RuntimeError("forced correction event failure")

        event.listen(DomainEvent, "before_insert", fail_domain_event_insert)
        try:
            with SessionLocal() as db:
                with pytest.raises(RuntimeError, match="forced correction event"):
                    correct_resolution(
                        db,
                        uuid.UUID(data["gm"]["id"]),
                        uuid.UUID(data["campaign"]["id"]),
                        uuid.UUID(data["resolution"]["id"]),
                        1,
                        "SUCCESS",
                        "Corrected after review.",
                    )
                db.rollback()
        finally:
            event.remove(DomainEvent, "before_insert", fail_domain_event_insert)

        with SessionLocal() as db:
            resolution = db.get(ActionResolution, uuid.UUID(data["resolution"]["id"]))
            assert resolution.final_outcome == "FAILURE"
            assert resolution.adjudication_revision == 1
            assert db.scalar(select(func.count()).select_from(CharacterKnowledge)) == 0
            assert db.scalar(
                select(func.count())
                .select_from(DomainEvent)
                .where(
                    DomainEvent.subject_id == uuid.UUID(data["resolution"]["id"]),
                    DomainEvent.event_type == "resolution.adjudication_corrected",
                )
            ) == 0


def test_player_projection_is_finalized_assigned_character_only():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        data = setup_campaign(gm, player, "s3-player", dc=1)
        _roll(gm, data)
        pending = player.get(
            f"/api/player/campaigns/{data['campaign']['id']}/resolutions/latest"
        )
        assert pending.status_code == 200
        assert pending.json() is None

        _finalize(gm, data, "SUCCESS")
        visible = player.get(
            f"/api/player/campaigns/{data['campaign']['id']}/resolutions/latest"
        )
        assert visible.status_code == 200
        assert visible.json()["final_outcome"] == "SUCCESS"

        outsider = TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app)
        try:
            register_and_login(outsider, "s3-player-outsider")
            assert outsider.get(
                f"/api/player/campaigns/{data['campaign']['id']}/resolutions/latest"
            ).status_code == 403
        finally:
            outsider.close()
