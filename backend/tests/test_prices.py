def test_get_price_invalid_symbol(client):
    response = client.get("/prices/INVALID")
    assert response.status_code == 404
    assert response.json() == {"detail": "Symbol INVALID not found"}


def test_get_price_case_insensitivity(client):
    response = client.get("/prices/aapl")
    assert response.status_code == 200
    assert response.json() == {"symbol": "AAPL", "price": 150.0, "currency": "USD"}


def test_get_price_with_no_currency_parameter(client):
    response = client.get("/prices/AAPL")
    assert response.status_code == 200
    assert response.json() == {"symbol": "AAPL", "price": 150.0, "currency": "USD"}


def test_get_price_with_currency_parameter_usd(client):
    response = client.get("/prices/AAPL?currency=USD")
    assert response.status_code == 200
    assert response.json() == {"symbol": "AAPL", "price": 150.0, "currency": "USD"}


def test_get_price_with_currency_parameter_gbp(client):
    response = client.get("/prices/AAPL?currency=GBP")
    assert response.status_code == 200
    # 1 USD = 0.79 GBP
    assert response.json() == {"symbol": "AAPL", "price": 118.50, "currency": "GBP"}


def test_get_price_with_invalid_currency_parameter_jpy(client):
    response = client.get("/prices/AAPL?currency=JPY")
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "currency"]


def test_list_prices_defaults_to_usd(client):
    response = client.get("/prices")
    assert response.status_code == 200
    prices = response.json()
    assert len(prices) == 3
    assert prices[0]["symbol"] == "AAPL"
    assert prices[0]["currency"] == "USD"
    assert prices[0]["price"] == 150.0  # AAPL price in USD


def test_list_prices_in_gbp(client):
    response = client.get("/prices?currency=GBP")
    assert response.status_code == 200
    prices = response.json()
    assert all(price["currency"] == "GBP" for price in prices)
    assert prices[0]["price"] == 118.5  # AAPL price in GBP


def test_list_prices_invalid_currency_returns_422(client):
    response = client.get("/prices?currency=JPY")
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "currency"]
