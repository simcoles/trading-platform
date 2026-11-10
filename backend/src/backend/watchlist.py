from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.exceptions import SymbolAlreadyInWatchlistError, SymbolNotInWatchlistError
from backend.orm import WatchlistEntry
from backend.pricing import look_up_price


def get_watchlist(session: Session) -> list[str]:
    build = select(WatchlistEntry.symbol).order_by(WatchlistEntry.symbol)
    symbols = session.scalars(build)
    return list(symbols)


def add_to_watchlist(session: Session, symbol: str) -> str:
    symbol = symbol.upper()
    look_up_price(symbol)  # raises UnknownSymbolError if symbol is not found

    session.add(WatchlistEntry(symbol=symbol))

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise SymbolAlreadyInWatchlistError(symbol) from None

    return symbol


def remove_from_watchlist(session: Session, symbol: str) -> None:
    symbol = symbol.upper()
    entry = session.scalar(
        select(WatchlistEntry).where(WatchlistEntry.symbol == symbol)
    )

    if entry is None:
        raise SymbolNotInWatchlistError(symbol)

    session.delete(entry)
    session.commit()
