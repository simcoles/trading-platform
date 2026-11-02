import pytest

from backend.main import FRONTEND_ORIGIN

OTHER_ORIGIN = "http://evil.example"


def test_allowed_origin_gets_cors_header(client):
    response = client.get(
        "/prices",
        headers={"Origin": FRONTEND_ORIGIN},
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == FRONTEND_ORIGIN


def test_other_origin_gets_no_cors_header(client):
    response = client.get(
        "/prices",
        headers={"Origin": OTHER_ORIGIN},
    )

    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


def test_preflight_for_watchlist_post(client):
    response = client.options(
        "/watchlist",
        headers={
            "Origin": FRONTEND_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == FRONTEND_ORIGIN


@pytest.mark.parametrize(
    "origin,method,expected_text",
    [
        (FRONTEND_ORIGIN, "PUT", "Disallowed CORS method"),
        (OTHER_ORIGIN, "POST", "Disallowed CORS origin"),
    ],
    ids=[
        "disallowed_method",
        "disallowed_origin",
    ],
)
def test_disallowed_cors_requests(origin, method, expected_text, client):
    response = client.options(
        "/watchlist",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": method,
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 400
    assert expected_text == response.text
