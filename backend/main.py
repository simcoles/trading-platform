from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Trading Platform API")

prices = {
    "AAPL": 150.0,
    "GOOGL": 2800.0,
    "AMZN": 3400.0,
}

USD_TO_GBP_RATE = 0.79  # Example conversion rate from USD to GBP

Currency = Literal["USD", "GBP"]
Side = Literal["buy", "sell"]


def convert_price(price: float, currency: Currency) -> float:
    if currency == "GBP":
        price = price * USD_TO_GBP_RATE
    return round(price, 2)


def get_price_or_404(symbol: str) -> float:
    price = prices.get(symbol)
    if price is None:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
    return price


def calculate_total(price: float, quantity: int) -> float:
    return round(price * quantity, 2)


class PriceResponse(BaseModel):
    symbol: str
    price: float
    currency: Currency


class OrderRequest(BaseModel):
    symbol: str
    quantity: int = Field(gt=0)
    side: Side


class OrderResponse(BaseModel):
    symbol: str
    quantity: int
    side: Side
    price: float
    total: float


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
