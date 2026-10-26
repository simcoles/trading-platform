import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.watchlist import clear_watchlist


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_watchlist():
    clear_watchlist()
