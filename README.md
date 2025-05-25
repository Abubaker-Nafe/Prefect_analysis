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



