from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Trading Platform API")

prices = {
    "AAPL": 150.0,
    "GOOGL": 2800.0,
    "AMZN": 3400.0,
}

USD_TO_GBP_RATE = 0.79  # Example conversion rate from USD to GBP

Currency = Literal["USD", "GBP"]


def convert_price(price: float, currency: Currency) -> float:
    if currency == "GBP":
        price = price * USD_TO_GBP_RATE
    return round(price, 2)


class PriceResponse(BaseModel):
    symbol: str
    price: float
    currency: Currency


@app.get("/")
async def root():
    return {"message": "Trading Platform API is running"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/prices/{symbol}", response_model=PriceResponse)
async def get_price(symbol: str, currency: Currency = "USD"):
    symbol = symbol.upper()
    price = prices.get(symbol)

    if price is None:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")

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
