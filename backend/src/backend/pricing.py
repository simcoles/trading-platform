from decimal import ROUND_HALF_UP, Decimal

from backend.exceptions import UnknownSymbolError
from backend.models import Currency, Side

# Starting mid prices for the simulation; live prices come from the broadcaster
prices = {
    "AAPL": Decimal("150.00"),
    "GOOGL": Decimal("2800.00"),
    "AMZN": Decimal("3400.00"),
    "MSFT": Decimal("420.00"),
    "NVDA": Decimal("180.00"),
    "TSLA": Decimal("250.00"),
    "META": Decimal("600.00"),
    "JPM": Decimal("240.00"),
}

USD_TO_GBP_RATE = Decimal("0.79")  # Example conversion rate from USD to GBP
CENT = Decimal("0.01")
# Bid and ask sit 0.1% either side of the mid, so the spread is 0.2%
HALF_SPREAD = Decimal("0.001")


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


def bid_ask(mid: Decimal) -> tuple[Decimal, Decimal]:
    return round_money(mid * (1 - HALF_SPREAD)), round_money(mid * (1 + HALF_SPREAD))


def fill_price(mid: Decimal, side: Side) -> Decimal:
    """Buyers pay the ask, sellers receive the bid."""
    bid, ask = bid_ask(mid)
    return ask if side == "buy" else bid
