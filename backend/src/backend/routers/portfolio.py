from fastapi import APIRouter

from backend.db import SessionDep
from backend.models import PortfolioResponse, Position
from backend.portfolio import get_cash, get_positions

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("", response_model=PortfolioResponse)
def retrieve_portfolio(session: SessionDep):
    return PortfolioResponse(
        cash=get_cash(session),
        positions=[
            Position(symbol=symbol, quantity=quantity)
            for symbol, quantity in get_positions(session).items()
        ],
    )
