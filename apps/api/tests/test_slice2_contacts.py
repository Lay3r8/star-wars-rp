import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event, func, select

from conftest import register_and_login
from star_wars_rp.application.contacts import create_contact, reveal_prepared_information
from star_wars_rp.db import SessionLocal
from star_wars_rp.modules.contacts.models import Contact
from star_wars_rp.modules.entities.models import Entity
from star_wars_rp.modules.history.models import DomainEvent
from star_wars_rp.modules.knowledge.models import CharacterKnowledge, KnowledgeFragment
from star_wars_rp.modules.resolutions.models import ActionResolution


def setup_campaign(gm: TestClient, player: TestClient, suffix: str) -> dict:
    player_info = register_and_login(player, f"player-s2-{suffix}")
    gm_info = register_and_login(gm, f"gm-s2-{suffix}")

    campaign = gm.post("/api/campaigns", json={"name": f"Slice 2 {suffix}"}).json()
    campaign_id = campaign["id"]
    assert gm.post(
        f"/api/campaigns/{campaign_id}/members",
        json={"username": f"player-s2-{suffix}"},
    ).status_code == 201

    character = gm.post(
        f"/api/campaigns/{campaign_id}/characters",
        json={"name": "Ryn Tal", "slicing_modifier": 1},
    ).json()
    location = gm.post(
        f"/api/campaigns/{campaign_id}/locations",
        json={"name": "Dock 47"},
    ).json()
    assert gm.put(
        f"/api/campaigns/{campaign_id}/player-assignment",
        json={
            "player_principal_id": player_info["id"],
            "character_id": character["id"],
        },
    ).status_code == 204

    return {
        "gm": gm_info,
        "player": player_info,
        "campaign": campaign,
        "character": character,
        "location": location,
    }


def contact_payload(location_id: str, *, name: str = "Nira Voss", role: str = "Imperial dock clerk and discreet informant") -> dict:
    return {
        "name": name,
        "role": role,
        "location_id": location_id,
        "gm_note": "Keeps a low profile around customs officers.",
        "prepared_information": {
            "claim_text": "A customs audit is scheduled for Dock 47 tomorrow at 06:00.",
            "gm_veracity": "TRUE",
        },
    }


def create_contact_api(gm: TestClient, data: dict, **overrides) -> dict:
    payload = contact_payload(data["location"]["id"])
    payload.update(overrides)
    response = gm.post(
        f"/api/campaigns/{data['campaign']['id']}/contacts",
        json=payload,
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_create_is_atomic_and_rejects_blank_domain_text():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        data = setup_campaign(gm, player, "atomic")
        campaign_id = uuid.UUID(data["campaign"]["id"])
        gm_id = uuid.UUID(data["gm"]["id"])
        location_id = uuid.UUID(data["location"]["id"])

        with SessionLocal() as db:
            before_entities = db.scalar(select(func.count()).select_from(Entity))
            before_fragments = db.scalar(select(func.count()).select_from(KnowledgeFragment))

        def fail_contact_insert(_mapper, _connection, _target):
            raise RuntimeError("forced Contact insert failure")

        event.listen(Contact, "before_insert", fail_contact_insert)
        try:
            with SessionLocal() as db:
                with pytest.raises(RuntimeError, match="forced Contact"):
                    create_contact(
                        db,
                        gm_id,
                        campaign_id,
                        name="Nira Voss",
                        role="Dock clerk",
                        location_id=location_id,
                        gm_note=None,
                        claim_text="Customs audit tomorrow.",
                        gm_veracity="TRUE",
                    )
                db.rollback()
        finally:
            event.remove(Contact, "before_insert", fail_contact_insert)

        with SessionLocal() as db:
            assert db.scalar(select(func.count()).select_from(Contact)) == 0
            assert db.scalar(select(func.count()).select_from(Entity)) == before_entities
            assert db.scalar(select(func.count()).select_from(KnowledgeFragment)) == before_fragments

        blank = contact_payload(data["location"]["id"])
        blank["name"] = "   "
        response = gm.post(f"/api/campaigns/{data['campaign']['id']}/contacts", json=blank)
        assert response.status_code == 422
        assert "blank" in response.json()["detail"].lower()


def test_search_is_campaign_scoped_partial_and_deterministic():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        first = setup_campaign(gm, player, "search")
        c1 = create_contact_api(gm, first, name="Zed Voss", role="Dock clerk")
        c2 = create_contact_api(gm, first, name="Nira Voss", role="Dock clerk")
        c3 = create_contact_api(gm, first, name="Dockmaster Nira", role="Logistics officer")
        create_contact_api(gm, first, name="Nira Voss", role="Customs liaison")

        by_name = gm.get(f"/api/campaigns/{first['campaign']['id']}/contacts/search", params={"q": "NIRA"})
        assert by_name.status_code == 200
        assert [item["name"] for item in by_name.json()] == ["Dockmaster Nira", "Nira Voss", "Nira Voss"]
        assert all(set(item) == {"contact_id", "name", "role", "location_name"} for item in by_name.json())

        mixed = gm.get(f"/api/campaigns/{first['campaign']['id']}/contacts/search", params={"q": "dock"})
        assert mixed.status_code == 200
        names = [item["name"] for item in mixed.json()]
        assert names[0] == "Dockmaster Nira"
        assert names[1:] == ["Nira Voss", "Zed Voss"]

        second_campaign = gm.post("/api/campaigns", json={"name": "Other campaign"}).json()
        second_location = gm.post(
            f"/api/campaigns/{second_campaign['id']}/locations",
            json={"name": "Dock 47"},
        ).json()
        other = gm.post(
            f"/api/campaigns/{second_campaign['id']}/contacts",
            json=contact_payload(second_location["id"], name="Nira Other"),
        )
        assert other.status_code == 201
        scoped = gm.get(f"/api/campaigns/{first['campaign']['id']}/contacts/search", params={"q": "Other"})
        assert scoped.json() == []

        # Existing IDs do not authorize cross-campaign retrieval.
        cross = gm.get(
            f"/api/campaigns/{second_campaign['id']}/contacts/{c1['contact_id']}"
        )
        assert cross.status_code == 404


def test_player_cannot_access_contact_gm_surfaces():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        data = setup_campaign(gm, player, "authz")
        contact = create_contact_api(gm, data)
        base = f"/api/campaigns/{data['campaign']['id']}/contacts"

        assert player.get(f"{base}/search", params={"q": "Nira"}).status_code == 403
        assert player.get(f"{base}/{contact['contact_id']}").status_code == 403
        assert player.post(base, json=contact_payload(data["location"]["id"])).status_code == 403
        assert player.patch(
            f"{base}/{contact['contact_id']}",
            json=contact_payload(data["location"]["id"]),
        ).status_code == 403
        assert player.post(
            f"{base}/{contact['contact_id']}/reveal",
            json={"recipient_character_id": data["character"]["id"]},
        ).status_code == 403


def test_edit_replaces_fragment_without_rewriting_previously_revealed_knowledge():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        data = setup_campaign(gm, player, "edit")
        contact = create_contact_api(gm, data)
        campaign_id = data["campaign"]["id"]
        contact_id = contact["contact_id"]

        before = player.get(f"/api/player/campaigns/{campaign_id}/character")
        assert before.json()["knowledge"] == []

        revealed = gm.post(
            f"/api/campaigns/{campaign_id}/contacts/{contact_id}/reveal",
            json={"recipient_character_id": data["character"]["id"]},
        )
        assert revealed.status_code == 200, revealed.text
        old_claim = revealed.json()["claim_text"]

        with SessionLocal() as db:
            old_fragment_id = db.get(Contact, uuid.UUID(contact_id)).prepared_fragment_id

        updated_payload = contact_payload(
            data["location"]["id"],
            role="Senior Imperial dock clerk",
        )
        updated_payload["gm_note"] = "Now watching the customs office."
        updated_payload["prepared_information"] = {
            "claim_text": "The audit was moved to 08:00.",
            "gm_veracity": "UNKNOWN",
        }
        updated = gm.patch(
            f"/api/campaigns/{campaign_id}/contacts/{contact_id}",
            json=updated_payload,
        )
        assert updated.status_code == 200, updated.text
        assert updated.json()["role"] == "Senior Imperial dock clerk"
        assert updated.json()["prepared_information"]["claim_text"] == "The audit was moved to 08:00."

        after = player.get(f"/api/player/campaigns/{campaign_id}/character").json()
        assert [item["claim_text"] for item in after["knowledge"]] == [old_claim]

        with SessionLocal() as db:
            fragments = db.scalars(
                select(KnowledgeFragment).where(KnowledgeFragment.campaign_id == uuid.UUID(campaign_id))
            ).all()
            assert len(fragments) == 2
            knowledge = db.scalars(
                select(CharacterKnowledge).where(CharacterKnowledge.campaign_id == uuid.UUID(campaign_id))
            ).all()
            assert len(knowledge) == 1
            assert knowledge[0].fragment_id == old_fragment_id
            current_contact = db.get(Contact, uuid.UUID(contact_id))
            assert current_contact.prepared_fragment_id != old_fragment_id


def test_reveal_is_atomic_idempotent_and_does_not_use_action_resolution():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        data = setup_campaign(gm, player, "reveal")
        contact = create_contact_api(gm, data)
        campaign_id = data["campaign"]["id"]
        contact_id = contact["contact_id"]
        endpoint = f"/api/campaigns/{campaign_id}/contacts/{contact_id}/reveal"
        body = {"recipient_character_id": data["character"]["id"]}

        assert player.get(f"/api/player/campaigns/{campaign_id}/character").json()["knowledge"] == []

        first = gm.post(endpoint, json=body)
        second = gm.post(endpoint, json=body)
        assert first.status_code == 200, first.text
        assert first.json()["already_revealed"] is False
        assert second.status_code == 200, second.text
        assert second.json()["already_revealed"] is True

        with SessionLocal() as db:
            assert db.scalar(select(func.count()).select_from(CharacterKnowledge)) == 1
            assert db.scalar(
                select(func.count()).select_from(DomainEvent).where(
                    DomainEvent.event_type == "contact.information_revealed"
                )
            ) == 1
            assert db.scalar(select(func.count()).select_from(ActionResolution)) == 0

        projection = player.get(f"/api/player/campaigns/{campaign_id}/character")
        assert projection.status_code == 200
        assert projection.json()["knowledge"][0]["claim_text"] == contact["prepared_information"]["claim_text"]
        assert "gm_veracity" not in projection.text
        assert "gm_note" not in projection.text

        def fail_event_insert(_mapper, _connection, _target):
            raise RuntimeError("forced DomainEvent failure")

        # A second Contact gives a fresh fragment so the atomicity path can be exercised.
        other = create_contact_api(gm, data, name="Kara Nox", role="Cargo analyst")
        event.listen(DomainEvent, "before_insert", fail_event_insert)
        try:
            with SessionLocal() as db:
                with pytest.raises(RuntimeError, match="forced DomainEvent"):
                    reveal_prepared_information(
                        db,
                        uuid.UUID(data["gm"]["id"]),
                        uuid.UUID(campaign_id),
                        uuid.UUID(other["contact_id"]),
                        uuid.UUID(data["character"]["id"]),
                    )
                db.rollback()
        finally:
            event.remove(DomainEvent, "before_insert", fail_event_insert)

        with SessionLocal() as db:
            other_contact = db.get(Contact, uuid.UUID(other["contact_id"]))
            assert db.get(
                CharacterKnowledge,
                {
                    "campaign_id": uuid.UUID(campaign_id),
                    "character_id": uuid.UUID(data["character"]["id"]),
                    "fragment_id": other_contact.prepared_fragment_id,
                },
            ) is None


def test_cross_campaign_location_and_recipient_are_rejected():
    with TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app) as gm, TestClient(
        __import__("star_wars_rp.main", fromlist=["app"]).app
    ) as player:
        first = setup_campaign(gm, player, "cross")

        second_player = TestClient(__import__("star_wars_rp.main", fromlist=["app"]).app)
        try:
            second_player_info = register_and_login(second_player, "player-s2-other")
            second = gm.post("/api/campaigns", json={"name": "Other"}).json()
            gm.post(f"/api/campaigns/{second['id']}/members", json={"username": "player-s2-other"})
            second_character = gm.post(
                f"/api/campaigns/{second['id']}/characters",
                json={"name": "Other PC", "slicing_modifier": 0},
            ).json()
            second_location = gm.post(
                f"/api/campaigns/{second['id']}/locations",
                json={"name": "Other dock"},
            ).json()
            gm.put(
                f"/api/campaigns/{second['id']}/player-assignment",
                json={
                    "player_principal_id": second_player_info["id"],
                    "character_id": second_character["id"],
                },
            )

            bad_create = gm.post(
                f"/api/campaigns/{first['campaign']['id']}/contacts",
                json=contact_payload(second_location["id"]),
            )
            assert bad_create.status_code == 404

            contact = create_contact_api(gm, first)
            bad_reveal = gm.post(
                f"/api/campaigns/{first['campaign']['id']}/contacts/{contact['contact_id']}/reveal",
                json={"recipient_character_id": second_character["id"]},
            )
            assert bad_reveal.status_code == 404
        finally:
            second_player.close()
