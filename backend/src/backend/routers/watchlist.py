from fastapi import APIRouter

from backend.db import SessionDep
from backend.models import WatchlistItem
from backend.watchlist import add_to_watchlist, get_watchlist, remove_from_watchlist

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


@router.get("", response_model=list[str])
def retrieve_watchlist(session: SessionDep):
    return get_watchlist(session)


@router.post("", response_model=WatchlistItem, status_code=201)
def add_symbol(item: WatchlistItem, session: SessionDep):
    added_symbol = add_to_watchlist(session, item.symbol)
    return WatchlistItem(symbol=added_symbol)


@router.delete("/{symbol}", status_code=204)
def remove(session: SessionDep, symbol: str) -> None:
    remove_from_watchlist(session, symbol=symbol)
