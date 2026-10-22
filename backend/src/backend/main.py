from fastapi import FastAPI

from backend.models import Currency, OrderRequest, OrderResponse, PriceResponse
from backend.pricing import calculate_total, convert_price, get_price_or_404, prices

app = FastAPI(title="Trading Platform API")


@app.get("/")
async def root():
    return {"message": "Trading Platform API is running"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/prices/{symbol}", response_model=PriceResponse)
async def get_price(symbol: str, currency: Currency = "USD"):
    symbol = symbol.upper()
    price = get_price_or_404(symbol)
    price = convert_price(price, currency)
    return PriceResponse(symbol=symbol, price=price, currency=currency)


@app.get("/prices", response_model=list[PriceResponse])
async def get_prices(currency: Currency = "USD"):
    return [
        PriceResponse(
            symbol=symbol, price=convert_price(price, currency), currency=currency
        )
        for symbol, price in prices.items()
    ]


@app.post("/orders", response_model=OrderResponse, status_code=201)
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
