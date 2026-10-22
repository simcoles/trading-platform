import pytest


def test_create_order_buy(client):
    response = client.post(
        "/orders", json={"symbol": "aapl", "quantity": 10, "side": "buy"}
    )
    assert response.status_code == 201
    assert response.json() == {
        "symbol": "AAPL",
        "quantity": 10,
        "side": "buy",
        "price": 150.0,
        "total": 1500.0,
    }


def test_create_order_sell(client):
    response = client.post(
        "/orders", json={"symbol": "googl", "quantity": 10, "side": "sell"}
    )
    assert response.status_code == 201
    assert response.json() == {
        "symbol": "GOOGL",
        "quantity": 10,
        "side": "sell",
        "price": 2800.0,
        "total": 28000.0,
    }


def test_create_order_unknown_symbol_returns_404(client):
    response = client.post(
        "/orders", json={"symbol": "INVALID", "quantity": 10, "side": "buy"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Symbol INVALID not found"}


@pytest.mark.parametrize("quantity", [0, -5])
def test_create_order_invalid_quantity_returns_422(client, quantity):
    response = client.post(
        "/orders", json={"symbol": "AAPL", "quantity": quantity, "side": "buy"}
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "quantity"]


def test_create_order_invalid_side_returns_422(client):
    response = client.post(
        "/orders", json={"symbol": "AAPL", "quantity": 10, "side": "hold"}
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "side"]
