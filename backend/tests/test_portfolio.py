from decimal import Decimal

from backend.orders import place_order
from backend.portfolio import STARTING_CASH, get_cash, get_position, get_positions

OWNER = "user-a"


def test_new_portfolio_has_starting_cash_and_no_positions(session):
    assert get_cash(session, OWNER) == STARTING_CASH
    assert get_positions(session, OWNER) == {}
    assert get_position(session, OWNER, "AAPL") == 0


def test_buy_and_sell_update_cash_and_positions(session):
    place_order(session, OWNER, "AAPL", "buy", 10)  # -1500
    place_order(session, OWNER, "AAPL", "sell", 4)  # +600.00
    assert get_cash(session, OWNER) == STARTING_CASH - Decimal("900.00")
    assert get_position(session, OWNER, "AAPL") == 6


def test_sold_out_positions_are_hidden(session):
    place_order(session, OWNER, "AAPL", "buy", 2)
    place_order(session, OWNER, "AAPL", "sell", 2)
    place_order(session, OWNER, "GOOGL", "buy", 1)

    assert get_positions(session, OWNER) == {"GOOGL": 1}


def test_get_portfolio(client):
    client.post(
        "/orders",
        json={"symbol": "AAPL", "side": "buy", "quantity": 10},
    )
    response = client.get("/portfolio")
    assert response.status_code == 200

    body = response.json()
    assert body == {"cash": 98500.0, "positions": [{"symbol": "AAPL", "quantity": 10}]}


def test_users_only_see_their_own_orders(session):
    place_order(session, OWNER, "AAPL", "buy", 10)
    place_order(session, "user-b", "GOOGL", "buy", 1)
    assert get_positions(session, OWNER) == {"AAPL": 10}
    assert get_positions(session, "user-b") == {"GOOGL": 1}
    assert get_cash(session, "user-b") == STARTING_CASH - Decimal("2800.00")
