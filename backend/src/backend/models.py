from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Currency = Literal["USD", "GBP"]
Side = Literal["buy", "sell"]


class PriceResponse(BaseModel):
    symbol: str
    price: float
    currency: Currency


class OrderRequest(BaseModel):
    symbol: str
    quantity: int = Field(gt=0)
    side: Side


class OrderResponse(BaseModel):
    symbol: str
    quantity: int
    side: Side
    price: float
    total: float


class WatchlistItem(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    symbol: str = Field(min_length=1, max_length=10)
