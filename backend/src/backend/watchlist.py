from backend.exceptions import SymbolAlreadyInWatchlistError, SymbolNotInWatchlistError
from backend.pricing import look_up_price

_watchlist: set[str] = set()


def clear_watchlist() -> None:
    _watchlist.clear()


def get_watchlist() -> list[str]:
    return sorted(_watchlist)


def add_to_watchlist(symbol: str) -> str:
    symbol = symbol.upper()
    look_up_price(symbol)  # raises UnknownSymbolError if symbol is not found
    if symbol in _watchlist:
        raise SymbolAlreadyInWatchlistError(symbol)
    _watchlist.add(symbol)
    return symbol


def remove_from_watchlist(symbol: str) -> None:
    symbol = symbol.upper()
    if symbol not in _watchlist:
        raise SymbolNotInWatchlistError(symbol)
    _watchlist.remove(symbol)
