from fastapi.testclient import TestClient

from main import app

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
    print(response.json())
    assert response.json()["detail"][0]["loc"] == ["query", "currency"]
