import pytest
from fastapi import WebSocketDisconnect, status

from backend.config import FRONTEND_ORIGIN
from backend.pricing import prices

ALLOWED_HEADERS = {"Origin": FRONTEND_ORIGIN}


def test_first_message_has_all_symbols(client):
    with client.websocket_connect("/ws/prices", headers=ALLOWED_HEADERS) as ws:
        data = ws.receive_json()
    assert set(data.keys()) == set(prices.keys())
    for quote in data.values():
        assert set(quote) == {"bid", "mid", "ask"}
        assert 0 < quote["bid"] < quote["mid"] < quote["ask"]


@pytest.mark.parametrize(
    "headers",
    [
        {},  # no Origin header
        {"Origin": "http://evil.example"},  # disallowed Origin
    ],
    ids=["no_origin", "disallowed_origin"],
)
def test_rejects_disallowed_origins(client, headers):
    with (
        pytest.raises(WebSocketDisconnect) as exc_info,
        client.websocket_connect("/ws/prices", headers=headers),
    ):
        pass
    assert exc_info.value.code == status.WS_1008_POLICY_VIOLATION


def test_two_clients_receive_the_same_prices(client):
    with (
        client.websocket_connect("/ws/prices", headers=ALLOWED_HEADERS) as ws_a,
        client.websocket_connect("/ws/prices", headers=ALLOWED_HEADERS) as ws_b,
    ):
        data_a = ws_a.receive_json()
        data_b = ws_b.receive_json()
    assert data_a == data_b
