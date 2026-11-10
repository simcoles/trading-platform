from decimal import ROUND_HALF_UP, Decimal

from backend.exceptions import UnknownSymbolError
from backend.models import Currency

prices = {
    "AAPL": Decimal("150.00"),
    "GOOGL": Decimal("2800.00"),
    "AMZN": Decimal("3400.00"),
}

USD_TO_GBP_RATE = Decimal("0.79")  # Example conversion rate from USD to GBP
CENT = Decimal("0.01")


def round_money(amount: Decimal) -> Decimal:
    rounded = amount.quantize(CENT, rounding=ROUND_HALF_UP)
    return rounded


def convert_price(price: Decimal, currency: Currency) -> Decimal:
    if currency == "GBP":
        price = price * USD_TO_GBP_RATE
    return round_money(price)


def look_up_price(symbol: str) -> Decimal:
    price = prices.get(symbol)
    if price is None:
        raise UnknownSymbolError(symbol)
    return price


def calculate_total(price: Decimal, quantity: int) -> Decimal:
    return round_money(price * quantity)
