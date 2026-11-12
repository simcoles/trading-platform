from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.exceptions import InsufficientCashError, InsufficientSharesError
from backend.models import Side
from backend.orm import Order
from backend.portfolio import get_cash, get_position
from backend.pricing import calculate_total, look_up_price


def place_order(
    session: Session, owner_sub: str, symbol: str, side: Side, quantity: int
) -> Order:
    symbol = symbol.upper()
    # raises UnknownSymbolError if symbol is not found
    price = look_up_price(symbol)
    total = calculate_total(price, quantity)

    # Check the rules before saving, so a rejected order is never written.
    # Check-then-insert: fine for a simulator, but two orders arriving at the
    # same moment could both pass. A real system would lock the account row.
    if side == "buy":
        cash = get_cash(session, owner_sub)
        if total > cash:
            raise InsufficientCashError(total, cash)
    else:
        held = get_position(session, owner_sub, symbol)
        if quantity > held:
            raise InsufficientSharesError(symbol, quantity, held)

    order = Order(
        owner_sub=owner_sub,
        symbol=symbol,
        side=side,
        quantity=quantity,
        price=price,
        total=total,
    )

    session.add(order)
    session.commit()
    return order


def list_orders(session: Session, owner_sub: str) -> list[Order]:
    query = select(Order).where(Order.owner_sub == owner_sub).order_by(Order.id.desc())
    orders = session.scalars(query)
    return list(orders)
