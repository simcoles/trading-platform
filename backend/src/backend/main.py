from fastapi import FastAPI

from backend.routers import orders, prices

app = FastAPI(title="Trading Platform API")

app.include_router(orders.router)
app.include_router(prices.router)


@app.get("/")
async def root():
    return {"message": "Trading Platform API is running"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}
