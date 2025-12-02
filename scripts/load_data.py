import pandas as pd
import asyncio
from prisma import Prisma
from decimal import Decimal
import os

# Ensure we can find the file relative to the script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_PATH = os.path.join(BASE_DIR, "HINDALCO_1D.xlsx")

async def main():
    print("Reading Excel file...")
    try:
        df = pd.read_excel(FILE_PATH)
    except FileNotFoundError:
        print(f"Error: File not found at {FILE_PATH}")
        return

    # Standardize column names
    df.columns = [c.lower() for c in df.columns]
    
    # Ensure datetime format
    df['datetime'] = pd.to_datetime(df['datetime'])

    print("Connecting to database...")
    db = Prisma()
    await db.connect()

    print("Preparing data for insertion...")
    records = []
    for _, row in df.iterrows():
        records.append({
            'datetime': row['datetime'],
            'open': Decimal(str(row['open'])),
            'high': Decimal(str(row['high'])),
            'low': Decimal(str(row['low'])),
            'close': Decimal(str(row['close'])),
            'volume': int(row['volume'])
        })

    print(f"Inserting {len(records)} records...")
    
    # Batch insert for performance
    batch_size = 500
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        await db.tickerdata.create_many(data=batch, skip_duplicates=True)
        print(f"Inserted batch {i // batch_size + 1}")

    await db.disconnect()
    print("Data loading complete!")

if __name__ == "__main__":
    asyncio.run(main())
