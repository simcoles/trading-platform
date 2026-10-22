from backend.pricing import calculate_total, convert_price


def test_convert_price_rounds_usd():
    # No conversion for USD
    assert convert_price(100.323, "USD") == 100.32


def test_convert_price_rounds_gbp():
    # 100.323 * 0.79 = 79.25517 -> rounded to 79.26
    assert convert_price(100.323, "GBP") == 79.26


def test_calculate_total():
    assert calculate_total(100.0, 5) == 500.0
    assert calculate_total(99.99, 3) == 299.97
    assert calculate_total(0.0, 10) == 0.0
