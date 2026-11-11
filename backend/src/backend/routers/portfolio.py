from fastapi import APIRouter

from backend.auth import CurrentUser
from backend.db import SessionDep
from backend.models import PortfolioResponse, Position
from backend.portfolio import get_cash, get_positions

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("", response_model=PortfolioResponse)
def retrieve_portfolio(session: SessionDep, user: CurrentUser):
    return PortfolioResponse(
        cash=get_cash(session, user.sub),
        positions=[
            Position(symbol=symbol, quantity=quantity)
            for symbol, quantity in get_positions(session, user.sub).items()
        ],
    )
