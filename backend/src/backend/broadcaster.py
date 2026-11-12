import asyncio
import random
from decimal import Decimal

from backend.exceptions import UnknownSymbolError
from backend.market import simulate_tick
from backend.pricing import bid_ask, prices

TICK_SECONDS = 1.0

Prices = dict[str, float]  # symbol -> mid price
Quotes = dict[str, dict[str, float]]  # symbol -> {"bid", "mid", "ask"}


def to_quotes(mids: Prices) -> Quotes:
    quotes: Quotes = {}
    for symbol, mid in mids.items():
        # str() first, so Decimal gets 150.42 rather than the float's binary value
        bid, ask = bid_ask(Decimal(str(mid)))
        quotes[symbol] = {"bid": float(bid), "mid": mid, "ask": float(ask)}
    return quotes


class PriceBroadcaster:
    def __init__(self, rng: random.Random) -> None:
        self.current_prices: Prices = {
            symbol: float(price) for symbol, price in prices.items()
        }
        # Computed once per tick, not once per client
        self.current_quotes: Quotes = to_quotes(self.current_prices)
        self._rng = rng
        self._subscribers: set[asyncio.Queue[Quotes]] = set()

    def subscribe(self) -> asyncio.Queue[Quotes]:
        queue = asyncio.Queue[Quotes](maxsize=1)
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[Quotes]) -> None:
        self._subscribers.discard(queue)

    def mid_price(self, symbol: str) -> Decimal:
        """The live mid price, as an exact Decimal for filling orders."""
        mid = self.current_prices.get(symbol)
        if mid is None:
            raise UnknownSymbolError(symbol)
        return Decimal(str(mid))

    def tick(self) -> Quotes:
        self.current_prices = simulate_tick(self.current_prices, self._rng)
        self.current_quotes = to_quotes(self.current_prices)
        for queue in self._subscribers:
            if queue.full():
                queue.get_nowait()
            queue.put_nowait(self.current_quotes)
        return self.current_quotes

    async def run(self) -> None:
        while True:
            await asyncio.sleep(TICK_SECONDS)
            self.tick()


broadcaster = PriceBroadcaster(random.Random())
