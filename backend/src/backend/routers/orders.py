from fastapi import APIRouter

from backend.models import OrderRequest, OrderResponse
from backend.pricing import calculate_total, get_price_or_404

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(order: OrderRequest):
    symbol = order.symbol.upper()
    price = get_price_or_404(symbol)
    total = calculate_total(price, order.quantity)
    return OrderResponse(
        symbol=symbol,
        quantity=order.quantity,
        side=order.side,
        price=price,
        total=total,
    )
