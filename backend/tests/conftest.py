import pytest
from fastapi.testclient import TestClient

from backend.db import SessionLocal
from backend.main import app
from backend.watchlist import clear_watchlist


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(autouse=True)
def reset_watchlist():
    with SessionLocal() as session:
        clear_watchlist(session)
