import os

os.environ.setdefault(
    "DATABASE_URL",
    os.getenv(
        "TEST_DATABASE_URL",
        "postgresql+psycopg://starwars:starwars@localhost:5432/star_wars_rp_test",
    ),
)
os.environ.setdefault("AUTH_SECRET", "test-secret-that-is-at-least-thirty-two-characters")

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text

from star_wars_rp.db import SessionLocal
from star_wars_rp.main import app


@pytest.fixture(scope="session", autouse=True)
def migrated_database():
    config = Config("alembic.ini")
    command.upgrade(config, "head")
    yield


@pytest.fixture(autouse=True)
def clean_database(migrated_database):
    yield
    with SessionLocal() as db:
        db.execute(
            text(
                """
                TRUNCATE TABLE
                    domain_event,
                    action_resolution,
                    player_character_assignment,
                    character_knowledge,
                    knowledge_fragment,
                    location,
                    custom_d20_character_profile,
                    character,
                    entity,
                    campaign_membership,
                    campaign,
                    principal
                RESTART IDENTITY CASCADE
                """
            )
        )
        db.commit()


@pytest.fixture
def client():
    with TestClient(app) as value:
        yield value


def register_and_login(client: TestClient, username: str, password: str = "password123"):
    response = client.post("/api/auth/register", json={"username": username, "password": password})
    assert response.status_code == 201, response.text
    principal = response.json()
    response = client.post("/api/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200, response.text
    return principal
