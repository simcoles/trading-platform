from fastapi import APIRouter

from backend.models import WatchlistItem
from backend.watchlist import add_to_watchlist, get_watchlist, remove_from_watchlist

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


@router.get("", response_model=list[str])
async def retrieve_watchlist():
    return get_watchlist()


@router.post("", response_model=WatchlistItem, status_code=201)
async def add_symbol(item: WatchlistItem):
    added_symbol = add_to_watchlist(item.symbol)
    return WatchlistItem(symbol=added_symbol)


@router.delete("/{symbol}", status_code=204)
async def remove(symbol: str) -> None:
    remove_from_watchlist(symbol=symbol)
