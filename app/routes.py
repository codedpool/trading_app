from fastapi import APIRouter, HTTPException
from typing import List
from app.models import TickerDataSchema, StrategyPerformance
from app.services import get_all_data, create_record, calculate_strategy_performance

router = APIRouter()

@router.get("/data", response_model=List[TickerDataSchema])
async def read_data():
    """Fetch all stock data records."""
    return await get_all_data()

@router.post("/data", response_model=TickerDataSchema)
async def add_data(record: TickerDataSchema):
    """Add a new stock data record."""
    try:
        new_record = await create_record(record)
        return new_record
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/strategy/performance", response_model=StrategyPerformance)
async def get_strategy_performance():
    """Calculate and return the performance of the MA Crossover Strategy."""
    try:
        performance = await calculate_strategy_performance()
        return performance
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
