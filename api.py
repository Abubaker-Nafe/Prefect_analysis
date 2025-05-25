from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from datetime import date
from sqlalchemy import MetaData, Table, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Database DSN (async)
ASYNC_SQL_DSN = "mysql+aiomysql://root:0597785625nafe@localhost:3306/analysis"

# Async engine & session factory
async_engine = create_async_engine(ASYNC_SQL_DSN, echo=True)
async_session = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

metadata = MetaData()
# Declare empty Table objects (no autoload yet)
receipts_summary = None
store_monthly    = None
item_performance = None
store_peak_hours = None

app = FastAPI(
    title="Coffeeshop Analytics API",
    description="Explore receipts summary and analytics via FastAPI endpoints.",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    global receipts_summary, store_monthly, item_performance, store_peak_hours

    # Reflect all tables into metadata
    async with async_engine.begin() as conn:
        await conn.run_sync(metadata.reflect)

    # Now grab the reflected Table objects
    receipts_summary    = metadata.tables["receipts_summary"]
    store_monthly       = metadata.tables["store_monthly"]
    item_performance    = metadata.tables["item_performance"]
    store_peak_hours    = metadata.tables["store_peak_hours"]

@app.on_event("shutdown")
async def shutdown_event():
    await async_engine.dispose()

# Pydantic models
class ReceiptSummary(BaseModel):
    as_of: date
    spend_per_rcpt: float
    items_per_rcpt: float
    this_week_sales: float
    last_week_sales: float

class StoreMonthly(BaseModel):
    month: str
    store_id: int
    sales: float

class ItemPerformance(BaseModel):
    item_name: str
    total_sold: int

class StorePeakHour(BaseModel):
    store_id: int
    peak_hour: int
    tx_count: int

@app.get("/receipts_summary", response_model=List[ReceiptSummary])
async def get_receipts_summary():
    async with async_session() as session:
        result = await session.execute(select(receipts_summary))
        rows = result.mappings().all()
    return [ReceiptSummary(**row) for row in rows]

@app.get("/store_monthly", response_model=List[StoreMonthly])
async def get_store_monthly():
    async with async_session() as session:
        result = await session.execute(select(store_monthly))
        rows = result.mappings().all()
    return [StoreMonthly(**row) for row in rows]

@app.get("/item_performance", response_model=List[ItemPerformance])
async def get_item_performance():
    async with async_session() as session:
        result = await session.execute(select(item_performance))
        rows = result.mappings().all()
    return [ItemPerformance(**row) for row in rows]

@app.get("/store_peak_hours", response_model=List[StorePeakHour])
async def get_store_peak_hours():
    async with async_session() as session:
        result = await session.execute(select(store_peak_hours))
        rows = result.mappings().all()
    return [StorePeakHour(**row) for row in rows]