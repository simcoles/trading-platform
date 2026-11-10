from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer

Currency = Literal["USD", "GBP"]
Side = Literal["buy", "sell"]

# Exact in Python, a plain number in JSON
Money = Annotated[Decimal, PlainSerializer(float, return_type=float, when_used="json")]


class PriceResponse(BaseModel):
    symbol: str
    price: Money
    currency: Currency


class OrderRequest(BaseModel):
    symbol: str
    quantity: int = Field(gt=0)
    side: Side


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    symbol: str
    quantity: int
    side: Side
    price: Money
    total: Money
    created_at: datetime


class WatchlistItem(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    symbol: str = Field(min_length=1, max_length=10)


class Position(BaseModel):
    symbol: str
    quantity: int


class PortfolioResponse(BaseModel):
    cash: Money
    positions: list[Position]
