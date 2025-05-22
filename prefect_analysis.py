from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Any

import prefect
from prefect import flow, task, get_run_logger
from pymongo import MongoClient
from sqlalchemy import create_engine, Table, Column, Integer, Float, String, MetaData, Date, Time
from sqlalchemy.dialects.mysql import insert as mysql_upsert

# DSN
SQL_DSN = "mysql+pymysql://root:0597785625nafe@localhost:3306/analysis"

# Mongo setup
MONGO_URI = "mongodb+srv://nafe:0597785625@coffeeshop.s8duwhp.mongodb.net"
client     = MongoClient(MONGO_URI)
db         = client["coffeeshop"]
collection = db["receipt"]

# Prepare SQL metadata
engine   = create_engine(SQL_DSN)
metadata = MetaData()

receipts_summary_table = Table(
    "receipts_summary", metadata,
    Column("as_of", Date, primary_key=True),
    Column("spend_per_rcpt", Float, nullable=False),
    Column("items_per_rcpt", Float, nullable=False),
    Column("this_week_sales", Float, nullable=False),
    Column("last_week_sales", Float, nullable=False),
)


store_monthly_table = Table(
    "store_monthly", metadata,
    Column("month",    String(7), primary_key=True),  # "YYYY-MM"
    Column("store_id", Integer,   primary_key=True),
    Column("sales",    Float,     nullable=False),
)

item_performance_table = Table(
    "item_performance", metadata,
    Column("item_name", String(100), primary_key=True),
    Column("total_sold", Integer, nullable=False),
)

store_peak_hours_table = Table(
    "store_peak_hours", metadata,
    Column("store_id", Integer, primary_key=True),
    Column("peak_hour", Integer, nullable=False),
    Column("tx_count", Integer, nullable=False),
)

metadata.create_all(engine)

@task
def load_all_receipts() -> List[Dict[str,Any]]:
    return list(collection.find())


@task
def compute_overall_metrics(receipts):
    today = datetime.now()
    # totals
    total_rcpt = len(receipts)
    total_sales = sum(r["total_price"] for r in receipts)
    total_items = sum(
        sum(i["product_quantity"] for i in r.get("items", []))
        for r in receipts
    )
    # averages
    spr = total_sales/total_rcpt if total_rcpt else 0
    ipr = total_items/total_rcpt if total_rcpt else 0

    # week-over-week
    start_this = today - timedelta(days=today.weekday())
    start_last = start_this - timedelta(days=7)
    parse_dt   = lambda r: datetime.fromisoformat(r["transactionDate"])

    tws = sum(r["total_price"] for r in receipts if parse_dt(r) >= start_this)
    lws = sum(r["total_price"] for r in receipts if start_last <= parse_dt(r) < start_this)

    return {
        "as_of": today.date(),
        "spend_per_rcpt": spr,
        "items_per_rcpt": ipr,
        "this_week_sales": tws,
        "last_week_sales": lws,
    }


@task
def compute_store_monthly(receipts):
    today = datetime.now()
    current_month = today.replace(day=1).strftime("%Y-%m")
    sales = defaultdict(float)
    for r in receipts:
        if r["transactionDate"] >= current_month:
            sales[r["Store_ID"]] += r["total_price"]
    return [
        {"month": current_month, "store_id": sid, "sales": val}
        for sid, val in sales.items()
    ]


@task
def compute_item_performance(receipts):
    counts = defaultdict(int)
    for r in receipts:
        for i in r["items"]:
            counts[i["product_name"]] += i["product_quantity"]
    return [{"item_name": k, "total_sold": v} for k,v in counts.items()]


@task
def compute_peak_hours(receipts):
    tx_per_store = defaultdict(lambda: defaultdict(int))
    for r in receipts:
        dt_str = r["transactionDate"] + "T" + r["transactionTime"]
        dt = datetime.fromisoformat(dt_str)
        tx_per_store[r["Store_ID"]][dt.hour] += 1

    result = []
    for sid, hours in tx_per_store.items():
        peak = max(hours, key=hours.get)
        result.append({"store_id": sid, "peak_hour": peak, "tx_count": hours[peak]})
    return result


@task
def write_to_mysql(overall, store_monthly_data, items, peak_hours):
    conn = engine.connect()

    # 1) Upsert overall to receipts_summary
    stmt = mysql_upsert(receipts_summary_table).values(**overall)
    stmt = stmt.on_duplicate_key_update({c.name:c for c in stmt.inserted})
    with engine.begin() as conn:
        conn.execute(stmt)

    # 2) Upsert store_monthly
    for row in store_monthly_data:
        stmt = mysql_upsert(store_monthly_table).values(**row)
        stmt = stmt.on_duplicate_key_update({c.name:c for c in stmt.inserted})
        with engine.begin() as conn:
            conn.execute(stmt)

    # 3) Upsert item_performance
    for row in items:
        stmt = mysql_upsert(item_performance_table).values(**row)
        stmt = stmt.on_duplicate_key_update({c.name:c for c in stmt.inserted})
        with engine.begin() as conn:
            conn.execute(stmt)

    # 4) Upsert store_peak_hours
    for row in peak_hours:
        stmt = mysql_upsert(store_peak_hours_table).values(**row)
        stmt = stmt.on_duplicate_key_update({c.name:c for c in stmt.inserted})
        with engine.begin() as conn:
            conn.execute(stmt)

    conn.close()


@flow
def process_new_receipt(change_event):
    """
    Prefect flow triggered on each MongoDB insert change.
    change_event is the raw change doc, not used here except for logging.
    """
    logger = get_run_logger()
    logger.info("Received MongoDB change: %s", change_event)

    receipts               = load_all_receipts()
    overall                = compute_overall_metrics(receipts)
    store_monthly_data     = compute_store_monthly(receipts)
    items                  = compute_item_performance(receipts)
    peak_hours             = compute_peak_hours(receipts)

    write_to_mysql(overall, store_monthly_data, items, peak_hours)


def watch_changes():
    """
    Run this function as a long-lived process (e.g. on your Prefect agent host).
    It listens for MongoDB inserts and dispatches the Prefect flow.
    """
    # collection.watch is blocking function as it waits for a document to be added
    print("Listening!")
    with collection.watch([{"$match": {"operationType": "insert"}}]) as stream:
        for change in stream:
            # Launch the flow asynchronously for each new insert
            process_new_receipt(change)
            print("done, listening again!!")


if __name__ == "__main__":
    watch_changes()