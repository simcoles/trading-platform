import time
from collections.abc import Iterator
from typing import Any

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from backend import auth
from backend.auth import get_current_user
from backend.config import settings
from backend.main import app

# A throwaway key pair standing in for Keycloak's signing key
PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
OTHER_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)

ORDER = {"symbol": "AAPL", "side": "buy", "quantity": 1}


def make_token(key: Any = PRIVATE_KEY, **overrides: Any) -> str:
    now = int(time.time())
    claims = {
        "iss": settings.keycloak_issuer,
        "aud": ["trading-api", "account"],
        "sub": "user-123",
        "preferred_username": "alice",
        "realm_access": {"roles": ["trader"]},
        "iat": now,
        "exp": now + 300,
    } | overrides
    return jwt.encode(claims, key, algorithm="RS256")


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def auth_client(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> Iterator[TestClient]:
    """Real token checking: undo conftest's fake user, verify with the test key."""
    del app.dependency_overrides[get_current_user]
    monkeypatch.setattr(auth, "signing_key", lambda token: PRIVATE_KEY.public_key())
    yield client


def test_missing_token_returns_401(auth_client: TestClient):
    response = auth_client.get("/orders")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
    assert response.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.parametrize(
    "token",
    [
        "not-a-jwt",
        make_token(key=OTHER_KEY),  # signed by someone else
        make_token(exp=int(time.time()) - 60),  # expired
        make_token(aud="some-other-api"),  # meant for a different API
        make_token(iss="http://evil.example/realms/trading"),
    ],
    ids=["garbage", "wrong-key", "expired", "wrong-audience", "wrong-issuer"],
)
def test_bad_token_returns_401(auth_client: TestClient, token: str):
    response = auth_client.get("/orders", headers=bearer(token))
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired token"}


def test_valid_token_reads_orders(auth_client: TestClient):
    response = auth_client.get("/orders", headers=bearer(make_token()))
    assert response.status_code == 200


def test_viewer_cannot_place_orders(auth_client: TestClient):
    token = make_token(realm_access={"roles": ["viewer"]})
    response = auth_client.post("/orders", json=ORDER, headers=bearer(token))
    assert response.status_code == 403
    assert response.json() == {"detail": "Requires the trader role"}


def test_trader_can_place_orders(auth_client: TestClient):
    response = auth_client.post("/orders", json=ORDER, headers=bearer(make_token()))
    assert response.status_code == 201
