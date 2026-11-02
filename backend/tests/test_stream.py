import time

from backend.pricing import prices
from backend.routers import stream


def test_first_message_has_all_symbols(client):
    with client.websocket_connect("/ws/prices") as ws:
        data = ws.receive_json()

    assert set(data.keys()) == set(prices.keys())
    for symbol, price in data.items():
        one_percent_of_price = prices[symbol] * 0.01
        assert abs(prices[symbol] - price) <= one_percent_of_price


def test_streams_multiple_updates(client, monkeypatch):
    monkeypatch.setattr(stream, "TICK_SECONDS", 0)
    start = time.perf_counter()
    with client.websocket_connect("/ws/prices") as ws:
        messages = [ws.receive_json() for _ in range(5)]
    stop = time.perf_counter()
    assert len(messages) == 5
    assert all(set(m.keys()) == set(prices.keys()) for m in messages)
    assert messages[0] != messages[-1]  # prices actually moved
    assert stop - start <= 0.5


def test_does_not_change_shared_prices(client):
    snapshot = dict(prices)
    with client.websocket_connect("/ws/prices") as ws:
        ws.receive_json()
    assert prices == snapshot
