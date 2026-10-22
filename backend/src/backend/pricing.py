from fastapi import HTTPException

from backend.models import Currency

prices = {
    "AAPL": 150.0,
    "GOOGL": 2800.0,
    "AMZN": 3400.0,
}

USD_TO_GBP_RATE = 0.79  # Example conversion rate from USD to GBP


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
