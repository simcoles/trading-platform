import random

MAX_MOVE = 0.01  # prices move at most ±1% per tick


def next_price(price: float, rng: random.Random) -> float:
    change = rng.uniform(-MAX_MOVE, MAX_MOVE)
    return round(price * (1 + change), 2)


def simulate_tick(current: dict[str, float], rng: random.Random) -> dict[str, float]:
    return {symbol: next_price(price, rng) for symbol, price in current.items()}
