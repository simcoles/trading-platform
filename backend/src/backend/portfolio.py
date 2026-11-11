from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from backend.orm import Order

STARTING_CASH = Decimal("100000.00")

# Buys spend cash and add shares; sells do the opposite
_cash_change = case((Order.side == "buy", -Order.total), else_=Order.total)
_share_change = case((Order.side == "buy", Order.quantity), else_=-Order.quantity)


def get_cash(session: Session, owner_sub: str) -> Decimal:
    query = select(func.coalesce(func.sum(_cash_change), 0)).where(
        Order.owner_sub == owner_sub
    )
    return STARTING_CASH + session.execute(query).scalar_one()


def get_position(session: Session, owner_sub: str, symbol: str) -> int:
    query = select(func.coalesce(func.sum(_share_change), 0)).where(
        Order.symbol == symbol, Order.owner_sub == owner_sub
    )
    return session.execute(query).scalar_one()


def get_positions(session: Session, owner_sub: str) -> dict[str, int]:
    held = func.sum(_share_change)
    query = (
        select(Order.symbol, held)
        .where(Order.owner_sub == owner_sub)
        .group_by(Order.symbol)
        .having(held != 0)
        .order_by(Order.symbol)
    )
    rows = session.execute(query)
    return {symbol: quantity for symbol, quantity in rows}
