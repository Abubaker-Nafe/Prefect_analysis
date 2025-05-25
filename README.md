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

                   ┌────────────┐      insert       ┌─────────────┐
                   │  MongoDB   │ ───────────────▶ │ Prefect Flow│
                   └────────────┘                  │ (Python)    │
                          ▲                        └─────┬───────┘
                          │ watch()                        │ upserts
                          │                                ▼
                   ┌────────────┐                  ┌─────────────┐
                   │ FastAPI    │  ←―――― queries ― │   MySQL     │
                   │ (uvicorn)  │                  │ analytics DB│
                   └────────────┘                  └─────────────┘

---




