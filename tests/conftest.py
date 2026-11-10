import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app  # noqa: E402
from seed_data import DEMO_PASSWORD, seed  # noqa: E402


@pytest.fixture
def app(tmp_path):
    """Fresh app with its own seeded database for every test."""
    db_path = tmp_path / "test.db"
    seed(db_path, accounts=10, views_count=60, favourites_count=10, sessions_count=30)
    app = create_app({"TESTING": True, "DATABASE": str(db_path), "SECRET_KEY": "test"})
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def ctx(app):
    """App context for calling controllers/entities directly (unit tests)."""
    with app.app_context():
        yield


def login(client, username, password=DEMO_PASSWORD):
    return client.post("/login", data={"username": username, "password": password})


@pytest.fixture
def admin_client(client):
    login(client, "admin")
    return client
