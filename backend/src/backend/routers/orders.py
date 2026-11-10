from fastapi import APIRouter

from backend.db import SessionDep
from backend.models import OrderRequest, OrderResponse
from backend.orders import list_orders, place_order

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=201)
def create_order(order: OrderRequest, session: SessionDep):
    return place_order(session, order.symbol, order.side, order.quantity)


@router.get("", response_model=list[OrderResponse])
def retrieve_orders(session: SessionDep):
    return list_orders(session)
