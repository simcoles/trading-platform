import pytest


def test_create_order_buy(client):
    response = client.post(
        "/orders", json={"symbol": "aapl", "quantity": 10, "side": "buy"}
    )
    assert response.status_code == 201

    body = response.json()

    assert isinstance(body.pop("id"), int)
    assert isinstance(body.pop("created_at"), str)

    # Everything left must match exactly, as before
    assert body == {
        "symbol": "AAPL",
        "quantity": 10,
        "side": "buy",
        "price": 150.0,
        "total": 1500.0,
    }


def test_create_order_sell(client):
    client.post("/orders", json={"symbol": "GOOGL", "quantity": 10, "side": "buy"})
    response = client.post(
        "/orders", json={"symbol": "googl", "quantity": 10, "side": "sell"}
    )
    assert response.status_code == 201
    body = response.json()

    body.pop("id")
    body.pop("created_at")

    assert body == {
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


def test_list_orders_empty(client):
    response = client.get("/orders")
    assert response.status_code == 200
    assert response.json() == []


def test_list_orders_newest_first(client):
    client.post("/orders", json={"symbol": "AAPL", "quantity": 1, "side": "buy"})
    client.post("/orders", json={"symbol": "AMZN", "quantity": 2, "side": "buy"})
    client.post("/orders", json={"symbol": "GOOGL", "quantity": 5, "side": "buy"})
    response = client.get("/orders")
    symbols = [order["symbol"] for order in response.json()]
    assert response.status_code == 200

    assert symbols == ["GOOGL", "AMZN", "AAPL"]


def test_buy_beyond_cash_returns_409(client):
    response = client.post(
        "/orders", json={"symbol": "GOOGL", "quantity": 40, "side": "buy"}
    )
    assert response.status_code == 409
    assert response.json() == {
        "detail": "Insufficient cash: order costs 112000.00 but only 100000.00 is available"
    }


def test_sell_more_than_held_returns_409(client):
    response = client.post(
        "/orders", json={"symbol": "GOOGL", "quantity": 10, "side": "sell"}
    )
    assert response.status_code == 409
    assert response.json() == {
        "detail": "Insufficient shares: cannot sell 10 GOOGL, only 0 held"
    }


def test_sell_more_than_partly_held_returns_409(client):
    client.post("/orders", json={"symbol": "AAPL", "quantity": 5, "side": "buy"})
    response = client.post(
        "/orders", json={"symbol": "AAPL", "quantity": 6, "side": "sell"}
    )
    assert response.status_code == 409
    assert response.json() == {
        "detail": "Insufficient shares: cannot sell 6 AAPL, only 5 held"
    }


def test_rejected_order_is_not_saved(client):
    client.post("/orders", json={"symbol": "GOOGL", "quantity": 40, "side": "buy"})
    client.post("/orders", json={"symbol": "AAPL", "quantity": 1, "side": "sell"})
    response = client.get("/orders")
    assert response.json() == []
