from typing import Literal

from pydantic import BaseModel, Field

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
