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


def test_get_price_valid_symbol():
    response = client.get("/prices/AAPL")
    assert response.status_code == 200
    assert response.json() == {"symbol": "AAPL", "price": 150.0}


def test_get_price_invalid_symbol():
    response = client.get("/prices/INVALID")
    assert response.status_code == 404
    assert response.json() == {"detail": "Symbol INVALID not found"}


def test_get_price_case_insensitivity():
    response = client.get("/prices/aapl")
    assert response.status_code == 200
    assert response.json() == {"symbol": "AAPL", "price": 150.0}
