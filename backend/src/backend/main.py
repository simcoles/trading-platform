from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.exceptions import (
    SymbolAlreadyInWatchlistError,
    SymbolNotInWatchlistError,
    UnknownSymbolError,
)
from backend.routers import orders, prices, stream, watchlist

app = FastAPI(title="Trading Platform API")

app.include_router(orders.router)
app.include_router(prices.router)
app.include_router(watchlist.router)
app.include_router(stream.router)


@app.get("/")
async def root():
    return {"message": "Trading Platform API is running"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.exception_handler(UnknownSymbolError)
async def unknown_symbol_handler(request: Request, exc: UnknownSymbolError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(SymbolAlreadyInWatchlistError)
async def symbol_already_in_watchlist_handler(
    request: Request, exc: SymbolAlreadyInWatchlistError
):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(SymbolNotInWatchlistError)
async def symbol_not_in_watchlist_handler(
    request: Request, exc: SymbolNotInWatchlistError
):
    return JSONResponse(status_code=404, content={"detail": str(exc)})
