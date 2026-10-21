from fastapi import FastAPI, HTTPException

app = FastAPI(title="Trading Platform API")

prices = {
    "AAPL": 150.0,
    "GOOGL": 2800.0,
    "AMZN": 3400.0,
}


@app.get("/")
async def root():
    return {"message": "Trading Platform API is running"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/prices/{symbol}")
async def get_price(symbol: str):
    symbol = symbol.upper()
    price = prices.get(symbol)

    if price is None:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
    return {"symbol": symbol, "price": price}
