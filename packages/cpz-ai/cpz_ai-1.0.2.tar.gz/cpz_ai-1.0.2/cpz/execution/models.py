from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from .enums import OrderSide, OrderType, TimeInForce


class OrderSubmitRequest(BaseModel):
    symbol: str
    side: OrderSide
    qty: float
    type: OrderType
    time_in_force: TimeInForce
    strategy_id: str  # REQUIRED: Strategy ID for all orders
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    client_order_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))

    @model_validator(mode="after")
    def _validate_limit_price(self) -> "OrderSubmitRequest":
        if self.type == OrderType.LIMIT and self.limit_price is None:
            raise ValueError("limit_price required for limit orders")
        return self


class OrderReplaceRequest(BaseModel):
    qty: Optional[float] = None
    limit_price: Optional[float] = None


class Order(BaseModel):
    id: str
    symbol: str
    side: OrderSide
    qty: float
    type: OrderType
    time_in_force: TimeInForce
    status: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Account(BaseModel):
    id: str
    buying_power: float
    equity: float
    cash: float


class Position(BaseModel):
    symbol: str
    qty: float
    avg_entry_price: float
    market_value: float


class Quote(BaseModel):
    symbol: str
    bid: float
    ask: float
    bid_size: float = 0
    ask_size: float = 0
    ts: datetime = Field(default_factory=datetime.utcnow)

class Bar(BaseModel):
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    ts: datetime = Field(default_factory=datetime.utcnow)
