def test_watchlist_starts_empty(client):
    response = client.get("/watchlist")
    assert response.status_code == 200
    assert response.json() == []


def test_add_symbol_to_watchlist(client):
    response = client.post("/watchlist", json={"symbol": "aapl"})
    assert response.status_code == 201
    assert response.json() == {"symbol": "AAPL"}
    response = client.get("/watchlist")
    assert response.status_code == 200
    assert response.json() == ["AAPL"]


def test_add_duplicate_symbol_returns_409(client):
    response = client.post("/watchlist", json={"symbol": "aapl"})
    assert response.status_code == 201
    response = client.post("/watchlist", json={"symbol": "aapl"})
    assert response.status_code == 409
    assert response.json() == {"detail": "Symbol AAPL is already in the watchlist"}


def test_add_unknown_symbol_returns_404(client):
    response = client.post("/watchlist", json={"symbol": "unknown"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Symbol UNKNOWN not found"}


def test_remove_symbol_from_watchlist(client):
    client.post("/watchlist", json={"symbol": "aapl"})
    response = client.delete("/watchlist/aapl")
    assert response.status_code == 204
    response = client.get("/watchlist")
    assert response.json() == []


def test_remove_symbol_not_in_watchlist_returns_404(client):
    response = client.delete("/watchlist/amzn")
    assert response.status_code == 404
    assert response.json() == {"detail": "Symbol AMZN is not in the watchlist"}
