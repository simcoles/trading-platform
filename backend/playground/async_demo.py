import asyncio
import time


async def fetch_price(symbol: str) -> str:
    await asyncio.sleep(1)
    return f"{symbol}: 150.0"


async def main() -> None:
    symbols = ["AAPL", "GOOGL", "AMZN"]

    # 1. Sequential: await each one in turn
    start = time.perf_counter()
    for symbol in symbols:
        result = await fetch_price(symbol)
        print(result)
    print(f"Sequential: {time.perf_counter() - start:.2f}s")

    # 2. Concurrent: run all three at once
    start = time.perf_counter()
    results = await asyncio.gather(*(fetch_price(symbol) for symbol in symbols))
    for result in results:
        print(result)
    print(f"Concurrent: {time.perf_counter() - start:.2f}s")


asyncio.run(main())
