import asyncio
import random

from backend.market import simulate_tick
from backend.pricing import prices

TICK_SECONDS = 1.0

Prices = dict[str, float]


class PriceBroadcaster:
    def __init__(self, rng: random.Random) -> None:
        self.current_prices: Prices = {
            symbol: float(price) for symbol, price in prices.items()
        }
        self._rng = rng
        self._subscribers: set[asyncio.Queue[Prices]] = set()

    def subscribe(self) -> asyncio.Queue[Prices]:
        queue = asyncio.Queue[Prices](maxsize=1)
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[Prices]) -> None:
        self._subscribers.discard(queue)

    def tick(self) -> Prices:
        self.current_prices = simulate_tick(self.current_prices, self._rng)
        for queue in self._subscribers:
            if queue.full():
                queue.get_nowait()
            queue.put_nowait(self.current_prices)
        return self.current_prices

    async def run(self) -> None:
        while True:
            await asyncio.sleep(TICK_SECONDS)
            self.tick()


broadcaster = PriceBroadcaster(random.Random())
