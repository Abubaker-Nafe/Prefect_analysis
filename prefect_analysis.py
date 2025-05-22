from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.engine import Row

# ——————————————  
# Configuration  
# ——————————————
SQL_DSN = "mysql+pymysql://root:0597785625nafe@localhost:3306/analysis"
engine = create_engine(SQL_DSN)
metadata = MetaData()
metadata.reflect(bind=engine, only=[
    "receipts_summary",
    "store_monthly",
    "item_performance",
    "store_peak_hours",
])

receipts_summary_table   = metadata.tables["receipts_summary"]
store_monthly_table      = metadata.tables["store_monthly"]
item_performance_table   = metadata.tables["item_performance"]
store_peak_hours_table   = metadata.tables["store_peak_hours"]

app = FastAPI(title="Coffeeshop Analytics API", version="1.0")

# ——————————————  
# Pydantic models for responses  
# ——————————————
class ReceiptSummary(BaseModel):
    as_of: str            # YYYY-MM-DD
    spend_per_rcpt: float
    items_per_rcpt: float
    this_week_sales: float
    last_week_sales: float

class StoreMonthly(BaseModel):
    month: str            # YYYY-MM
    store_id: int
    sales: float

class ItemPerformance(BaseModel):
    item_name: str
    total_sold: int

class StorePeakHour(BaseModel):
    store_id: int
    peak_hour: int
    tx_count: int

# ——————————————  
# Helper to convert a Row to dict then to Pydantic  
# ——————————————
def rows_to_pydantic(rows: List[Row], model):
    return [model(**dict(r)) for r in rows]

# ——————————————  
# Endpoints  
# ——————————————
@app.get("/receipts_summary/", response_model=List[ReceiptSummary])
def get_receipts_summary():
    with engine.connect() as conn:
        rows = conn.execute(select(receipts_summary_table)).all()
    return rows_to_pydantic(rows, ReceiptSummary)

@app.get("/store_monthly/", response_model=List[StoreMonthly])
def get_store_monthly():
    with engine.connect() as conn:
        rows = conn.execute(select(store_monthly_table)).all()
    return rows_to_pydantic(rows, StoreMonthly)

@app.get("/item_performance/", response_model=List[ItemPerformance])
def get_item_performance():
    with engine.connect() as conn:
        rows = conn.execute(select(item_performance_table)).all()
    return rows_to_pydantic(rows, ItemPerformance)

@app.get("/store_peak_hours/", response_model=List[StorePeakHour])
def get_store_peak_hours():
    with engine.connect() as conn:
        rows = conn.execute(select(store_peak_hours_table)).all()
    return rows_to_pydantic(rows, StorePeakHour)