from typing import Annotated

from fastapi import APIRouter, Depends

from backend.auth import CurrentUser, TraderUser
from backend.broadcaster import PriceBroadcaster, broadcaster
from backend.db import SessionDep
from backend.models import OrderRequest, OrderResponse
from backend.orders import list_orders, place_order
from backend.pricing import fill_price

router = APIRouter(prefix="/orders", tags=["orders"])


def get_market() -> PriceBroadcaster:
    """The live market. Tests override this with one that doesn't tick."""
    return broadcaster


MarketDep = Annotated[PriceBroadcaster, Depends(get_market)]


@router.post("", response_model=OrderResponse, status_code=201)
def create_order(
    order: OrderRequest, session: SessionDep, user: TraderUser, market: MarketDep
):
    symbol = order.symbol.upper()
    # Fill at the live price when the order arrives: buys at the ask, sells at
    # the bid. It can differ slightly from what the user saw (slippage).
    price = fill_price(market.mid_price(symbol), order.side)
    return place_order(session, user.sub, symbol, order.side, order.quantity, price)


@router.get("", response_model=list[OrderResponse])
def retrieve_orders(session: SessionDep, user: CurrentUser):
    return list_orders(session, user.sub)
