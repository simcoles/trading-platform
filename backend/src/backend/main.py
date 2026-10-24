from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.exceptions import UnknownSymbolError
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


@app.exception_handler(UnknownSymbolError)
async def unknown_symbol_handler(request: Request, exc: UnknownSymbolError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})
