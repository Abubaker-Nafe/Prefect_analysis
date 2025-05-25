# ☕ Coffeeshop Analytics

Real-time analytics pipeline that streams **MongoDB** receipt inserts into **MySQL** summary tables with **Prefect 2.0**, then exposes aggregated insights through a **FastAPI** REST service.

*From raw transactions to live dashboards in seconds, all in plain Python.*

---

## ✨ Features

| Layer | Tech | What It Does |
|-------|------|--------------|
| **Ingestion & Orchestration** | Prefect 2.0 | Watches MongoDB’s `receipt` collection and triggers a flow for every new insert. |
| **Storage** | MongoDB Atlas | Raw receipts (one document per transaction). |
|  | MySQL (analysis DB) | Four analytic tables automatically **upserted** by the flow. |
| **Analytics** | SQLAlchemy Core | Computes KPIs (spend per receipt, item performance, etc.) and writes them idempotently. |
| **API** | FastAPI + SQLAlchemy Async | Zero-copy selects from MySQL and JSON-serialises with Pydantic models. |


- **ETL Flow** (Prefect)
  - Loads all receipts from MongoDB.
  - Computes overall metrics (average spend/items per receipt, week-over-week sales).
  - Computes per‐store monthly sales.
  - Computes item‐level performance (total quantity sold).
  - Identifies each store’s peak transaction hour.
  - Upserts results into MySQL tables via “INSERT … ON DUPLICATE KEY UPDATE”.

- **REST API** (FastAPI)
  - `/receipts_summary` – All-time snapshots of overall metrics.
  - `/store_monthly` – Monthly sales per store.
  - `/item_performance` – Total units sold per product.
  - `/store_peak_hours` – Hour of day with highest tx count per store.

## 🚀 Quick Start

> **Prerequisites**  
> • Python ≥ 3.10  
> • MySQL 8.x (or MariaDB ≥ 10.5)  
> • MongoDB Atlas cluster (or local replica set)  
> • [Poetry](https://python-poetry.org/) *or* `pip`

1. **Clone & install**

   ```bash
   git clone https://github.com/<you>/coffeeshop-analytics.git
   cd coffeeshop-analytics
   pip install -r requirements.txt

2. Create .env
   # MongoDB
   MONGO_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net
   # MySQL sync
   SQL_DSN=mysql+pymysql://<user>:<password>@localhost:3306/analysis
   # MySQL async
   ASYNC_SQL_DSN=mysql+aiomysql://<user>:<password>@localhost:3306/analysis

3. Bootstrap the schema
  The first run of prefect_analysis.py creates all four tables via metadata.create_all(engine).

4. Run the services
   # ETL listener
   python prefect_analysis.py
   # API (separate terminal)
   uvicorn api:app --reload


## 🛠️ Configuration
| Variable | Default | code	Purpose |
|----------|---------|--------------|
| **SQL_DSN** | mysql+pymysql://root:…@localhost:3306/analysis | Sync engine for upserts. |
| **ASYNC_SQL_DSN** | 	mysql+aiomysql://root:…@localhost:3306/analysis | analysis	Async engine for API. |
| **MONGO_URI** | mongodb+srv://nafe:…@coffeeshop.mongodb.net | Source cluster. |

## 📊 Analytics Tables
| Table | Primary Key(s)	 | What’s Inside |
|-------|------------------|---------------|
| **receipts_summary** | 	as_of DATE | Daily KPIs: avg spend/receipt, items/receipt, this-week vs last-week sales. |
| **store_monthly** | 		(month, store_id) | Monthly sales per store (YYYY-MM). |
| **item_performance** | item_name	 |Lifetime units sold per menu item. |
| **store_peak_hours** | **store_id** | Peak hour (0-23) and transaction count. |            

