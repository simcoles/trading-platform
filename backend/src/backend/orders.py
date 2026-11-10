from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import Side
from backend.orm import Order
from backend.pricing import calculate_total, look_up_price


def place_order(session: Session, symbol: str, side: Side, quantity: int) -> Order:
    symbol = symbol.upper()
    # raises UnknownSymbolError if symbol is not found
    price = look_up_price(symbol)
    total = calculate_total(price, quantity)

    order = Order(symbol=symbol, side=side, quantity=quantity, price=price, total=total)

    session.add(order)
    session.commit()
    return order


def list_orders(session: Session) -> list[Order]:
    query = select(Order).order_by(Order.id.desc())
    orders = session.scalars(query)
    return list(orders)
