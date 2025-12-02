from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

class TickerDataSchema(BaseModel):
    datetime: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int

    class Config:
        from_attributes = True

class StrategyPerformance(BaseModel):
    strategy_name: str
    total_return_percentage: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float

class Signal(BaseModel):
    datetime: datetime
    signal: str  # "BUY" or "SELL"
    price: Decimal
