import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.pricing import calculate_total, convert_price

client = TestClient(app)


def test_root_returns_running_message():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Trading Platform API is running"}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_price_invalid_symbol():
    response = client.get("/prices/INVALID")
    assert response.status_code == 404
    assert response.json() == {"detail": "Symbol INVALID not found"}


def test_get_price_case_insensitivity():
    response = client.get("/prices/aapl")
    assert response.status_code == 200
    assert response.json() == {"symbol": "AAPL", "price": 150.0, "currency": "USD"}


def test_get_price_with_no_currency_parameter():
    response = client.get("/prices/AAPL")
    assert response.status_code == 200
    assert response.json() == {"symbol": "AAPL", "price": 150.0, "currency": "USD"}


def test_get_price_with_currency_parameter_usd():
    response = client.get("/prices/AAPL?currency=USD")
    assert response.status_code == 200
    assert response.json() == {"symbol": "AAPL", "price": 150.0, "currency": "USD"}


def test_get_price_with_currency_parameter_gbp():
    response = client.get("/prices/AAPL?currency=GBP")
    assert response.status_code == 200
    # 1 USD = 0.79 GBP
    assert response.json() == {"symbol": "AAPL", "price": 118.50, "currency": "GBP"}


def test_get_price_with_invalid_currency_parameter_jpy():
    response = client.get("/prices/AAPL?currency=JPY")
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "currency"]


def test_list_prices_defaults_to_usd():
    response = client.get("/prices")
    assert response.status_code == 200
    prices = response.json()
    assert len(prices) == 3
    assert prices[0]["symbol"] == "AAPL"
    assert prices[0]["currency"] == "USD"
    assert prices[0]["price"] == 150.0  # AAPL price in USD


def test_list_prices_in_gbp():
    response = client.get("/prices?currency=GBP")
    assert response.status_code == 200
    prices = response.json()
    assert all(price["currency"] == "GBP" for price in prices)
    assert prices[0]["price"] == 118.5  # AAPL price in GBP


def test_list_prices_invalid_currency_returns_422():
    response = client.get("/prices?currency=JPY")
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "currency"]


def test_convert_price_rounds_usd():
    # No conversion for USD
    assert convert_price(100.323, "USD") == 100.32


def test_convert_price_rounds_gbp():
    # 100.323 * 0.79 = 79.25517 -> rounded to 79.26
    assert convert_price(100.323, "GBP") == 79.26


def test_create_order_buy():
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


def test_create_order_sell():
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


def test_create_order_unknown_symbol_returns_404():
    response = client.post(
        "/orders", json={"symbol": "INVALID", "quantity": 10, "side": "buy"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Symbol INVALID not found"}


@pytest.mark.parametrize("quantity", [0, -5])
def test_create_order_invalid_quantity_returns_422(quantity):
    response = client.post(
        "/orders", json={"symbol": "AAPL", "quantity": quantity, "side": "buy"}
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "quantity"]


def test_create_order_invalid_side_returns_422():
    response = client.post(
        "/orders", json={"symbol": "AAPL", "quantity": 10, "side": "hold"}
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "side"]


def test_calculate_total():
    assert calculate_total(100.0, 5) == 500.0
    assert calculate_total(99.99, 3) == 299.97
    assert calculate_total(0.0, 10) == 0.0
