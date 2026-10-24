from fastapi import APIRouter

from backend.models import Currency, PriceResponse
from backend.pricing import convert_price, look_up_price, prices

router = APIRouter(prefix="/prices", tags=["prices"])


@router.get("/{symbol}", response_model=PriceResponse)
async def get_price(symbol: str, currency: Currency = "USD"):
    symbol = symbol.upper()
    price = look_up_price(symbol)
    price = convert_price(price, currency)
    return PriceResponse(symbol=symbol, price=price, currency=currency)


@router.get("", response_model=list[PriceResponse])
async def get_prices(currency: Currency = "USD"):
    return [
        PriceResponse(
            symbol=symbol, price=convert_price(price, currency), currency=currency
        )
        for symbol, price in prices.items()
    ]
