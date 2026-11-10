from decimal import Decimal

import pytest

from backend.exceptions import UnknownSymbolError
from backend.pricing import calculate_total, convert_price, look_up_price


def test_convert_price_rounds_usd():
    # No conversion for USD
    assert convert_price(Decimal("100.323"), "USD") == Decimal("100.32")


def test_convert_price_rounds_gbp():
    # 100.323 * 0.79 = 79.25517 -> rounded to 79.26
    assert convert_price(Decimal("100.323"), "GBP") == Decimal("79.26")


def test_calculate_total():
    assert calculate_total(Decimal("100.00"), 5) == Decimal("500.0")
    assert calculate_total(Decimal("99.99"), 3) == Decimal("299.97")
    assert calculate_total(Decimal("0.00"), 10) == Decimal("0.0")


def test_look_up_price_unknown_symbol_raises():
    with pytest.raises(UnknownSymbolError):
        look_up_price("INVALID")


def test_look_up_price_known_symbols():
    assert look_up_price("AAPL") == Decimal("150.0")
    assert look_up_price("GOOGL") == Decimal("2800.0")
    assert look_up_price("AMZN") == Decimal("3400.0")


def test_convert_price_rounds_half_up():
    # 6.50 * 0.79 = 5.135 exactly; with floats this rounded down to 5.13
    assert convert_price(Decimal("6.50"), "GBP") == Decimal("5.14")
