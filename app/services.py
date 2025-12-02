from app.database import db
from app.models import TickerDataSchema
import pandas as pd

async def get_all_data():
    """Fetch all records from the database ordered by date."""
    records = await db.tickerdata.find_many(order={'datetime': 'asc'})
    return records

async def create_record(data: TickerDataSchema):
    """Create a new ticker record."""
    record = await db.tickerdata.create(
        data={
            'datetime': data.datetime,
            'open': data.open,
            'high': data.high,
            'low': data.low,
            'close': data.close,
            'volume': data.volume
        }
    )
    return record

async def calculate_strategy_performance():
    """
    Implements a simple Moving Average Crossover Strategy.
    Short Window: 10 days
    Long Window: 50 days
    """
    # 1. Fetch data
    records = await get_all_data()
    if not records:
        return {"error": "No data available"}

    # 2. Convert to DataFrame for easier calculation
    data = [
        {
            "datetime": r.datetime, 
            "close": float(r.close)
        } for r in records
    ]
    df = pd.DataFrame(data)
    df.set_index('datetime', inplace=True)

    # 3. Calculate Moving Averages
    short_window = 10
    long_window = 50

    df['short_mavg'] = df['close'].rolling(window=short_window, min_periods=1).mean()
    df['long_mavg'] = df['close'].rolling(window=long_window, min_periods=1).mean()

    # 4. Generate Signals
    # 1.0 when short > long (Bullish/Buy), 0.0 otherwise
    df['signal'] = 0.0
    df.loc[df.index[short_window:], 'signal'] = np_where(
        df['short_mavg'][short_window:] > df['long_mavg'][short_window:], 1.0, 0.0
    )
    
    # Generate 'positions' (diff of signal) -> 1 (Buy), -1 (Sell)
    df['positions'] = df['signal'].diff()

    # 5. Backtest / Calculate Performance
    initial_capital = 10000.0
    positions = pd.DataFrame(index=df.index).fillna(0.0)
    positions['stock'] = 100 * df['signal']   # Buy 100 shares on signal
    
    # Portfolio value
    portfolio = positions.multiply(df['close'], axis=0)
    difference_in_shares = positions.diff()
    
    # Simplified Logic:
    # We will track specific trades for the requested JSON output
    trades = []
    position = None # None, 'LONG'
    entry_price = 0
    
    total_trades = 0
    winning_trades = 0
    losing_trades = 0
    total_pnl = 0

    for index, row in df.iterrows():
        current_price = row['close']
        signal_val = row['positions'] # 1.0 buy, -1.0 sell

        if signal_val == 1.0: # Buy Signal
            if position is None:
                position = 'LONG'
                entry_price = current_price
        
        elif signal_val == -1.0: # Sell Signal
            if position == 'LONG':
                position = None
                exit_price = current_price
                pnl = exit_price - entry_price
                total_pnl += pnl
                total_trades += 1
                if pnl > 0:
                    winning_trades += 1
                else:
                    losing_trades += 1
    
    # Calculate metrics
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    total_return_pct = (total_pnl / initial_capital) * 100 # Hypothetical return on base capital

    return {
        "strategy_name": "Moving Average Crossover (10/50)",
        "total_return_percentage": round(total_return_pct, 2),
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "losing_trades": losing_trades,
        "win_rate": round(win_rate, 2)
    }

# Helper for numpy-like 'where' logic without heavy numpy dependency if preferred, 
# but pandas uses numpy under the hood anyway.
import numpy as np
def np_where(condition, x, y):
    return np.where(condition, x, y)
