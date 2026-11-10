import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.broadcaster import broadcaster
from backend.config import FRONTEND_ORIGIN
from backend.exceptions import (
    SymbolAlreadyInWatchlistError,
    SymbolNotInWatchlistError,
    UnknownSymbolError,
)
from backend.routers import health, orders, prices, stream, watchlist


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    task = asyncio.create_task(broadcaster.run())
    yield
    task.cancel()
    with suppress(asyncio.CancelledError):
        await task


app = FastAPI(title="Trading Platform API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)
app.include_router(orders.router)
app.include_router(prices.router)
app.include_router(watchlist.router)
app.include_router(stream.router)
app.include_router(health.router)


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
