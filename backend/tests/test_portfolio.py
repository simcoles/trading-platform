from decimal import Decimal

from backend.orders import place_order
from backend.portfolio import STARTING_CASH, get_cash, get_position, get_positions


def test_new_portfolio_has_starting_cash_and_no_positions(session):
    assert get_cash(session) == STARTING_CASH
    assert get_positions(session) == {}
    assert get_position(session, "AAPL") == 0


def test_buy_and_sell_update_cash_and_positions(session):
    place_order(session, "AAPL", "buy", 10)  # -1500
    place_order(session, "AAPL", "sell", 4)  # +600.00
    assert get_cash(session) == STARTING_CASH - Decimal("900.00")
    assert get_position(session, "AAPL") == 6


def test_sold_out_positions_are_hidden(session):
    place_order(session, "AAPL", "buy", 2)
    place_order(session, "AAPL", "sell", 2)
    place_order(session, "GOOGL", "buy", 1)

    assert get_positions(session) == {"GOOGL": 1}


def test_get_portfolio(client):
    client.post("/orders", json={"symbol": "AAPL", "side": "buy", "quantity": 10})
    response = client.get("/portfolio")
    assert response.status_code == 200

    body = response.json()
    assert body == {"cash": 98500.0, "positions": [{"symbol": "AAPL", "quantity": 10}]}
