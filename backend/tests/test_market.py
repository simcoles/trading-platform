import random

from backend.market import next_price, simulate_tick


def test_next_price_stays_within_one_percent():
    rng = random.Random(42)
    for _ in range(1000):
        result = next_price(100.0, rng)
        assert 99.0 <= result <= 101.0


def test_next_price_is_rounded_to_two_decimals():
    rng = random.Random(42)
    for _ in range(1000):
        result = next_price(123.45, rng)
        assert result == round(result, 2)


def test_next_price_is_deterministic_with_same_seed():
    rng1 = random.Random(42)
    rng2 = random.Random(42)
    result1 = next_price(100.0, rng1)
    result2 = next_price(100.0, rng2)
    assert result1 == result2


def test_simulate_tick_returns_new_dict_without_mutating_input():
    original = {"AAPL": 150.0, "GOOGL": 2800.0}
    snapshot = dict(original)  # a copy to compare against later
    rng = random.Random(42)

    result = simulate_tick(original, rng)

    assert set(result.keys()) == set(original.keys())
    assert original == snapshot
    assert result is not original
