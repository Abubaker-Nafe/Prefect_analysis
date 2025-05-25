CoffeeShop Analytics
A lightweight data pipeline and API for summarizing and exploring coffee shop receipt data. This project uses Prefect to extract, transform, and load (ETL) MongoDB “receipt” documents into a MySQL analytics schema, and FastAPI to expose key metrics via REST endpoints.

Features
ETL Flow (Prefect)

Loads all receipts from MongoDB.

Computes overall metrics (average spend/items per receipt, week‐over‐week sales).

Computes per‐store monthly sales.

Computes item‐level performance (total quantity sold).

Identifies each store’s peak transaction hour.

Upserts results into MySQL tables via “INSERT … ON DUPLICATE KEY UPDATE”.

REST API (FastAPI)

/receipts_summary – All‐time snapshots of overall metrics.

/store_monthly – Monthly sales per store.

/item_performance – Total units sold per product.

/store_peak_hours – Hour of day with highest tx count per store.

Prerequisites
Python 3.9+

MongoDB (Atlas or local) with a coffeeshop.receipt collection.

MySQL 5.7+ (or compatible) for the analytics database.

(Optional) Prefect for orchestration.

(Optional) FastAPI for API.

pip or poetry for dependency management.

Setup & Installation
Clone the repo

bash
Copy
Edit
git clone https://github.com/<your-username>/coffeeshop-analytics.git
cd coffeeshop-analytics
Create a virtual environment & install dependencies

bash
Copy
Edit
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
Configure connection strings

In prefect_analysis.py:

python
Copy
Edit
SQL_DSN   = "mysql+pymysql://<user>:<pass>@<host>:<port>/analysis"
MONGO_URI = "mongodb+srv://<user>:<pass>@<cluster>.mongodb.net"
In api.py:

python
Copy
Edit
ASYNC_SQL_DSN = "mysql+aiomysql://<user>:<pass>@<host>:<port>/analysis"
Initialize MySQL schema
Running the ETL flow will auto-create these tables if they don’t exist:

receipts_summary

store_monthly

item_performance

store_peak_hours

Ensure MongoDB has receipt documents
Example receipt structure:

json
Copy
Edit
{
  "Store_ID": 1,
  "transactionDate": "2025-05-20",
  "transactionTime": "14:23:00",
  "total_price": 12.50,
  "items": [
    { "product_name": "Latte",  "product_quantity": 2 },
    { "product_name": "Muffin", "product_quantity": 1 }
  ]
}
Running the ETL Flow
bash
Copy
Edit
python prefect_analysis.py
Listens for inserts on the MongoDB receipt collection.

On each new receipt, recomputes metrics and upserts into MySQL.

Tip: Integrate with Prefect Cloud/Server to schedule, monitor, and manage your flows.

Starting the API Server
bash
Copy
Edit
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
Visit the interactive docs at:
http://localhost:8000/docs

API Endpoints
Path	Method	Description
/receipts_summary	GET	List all snapshot records of overall metrics.
/store_monthly	GET	List monthly sales totals per store.
/item_performance	GET	List total units sold per product.
/store_peak_hours	GET	List peak transaction hour and count per store.

Example Request
bash
Copy
Edit
curl http://localhost:8000/store_monthly
json
Copy
Edit
[
  { "month": "2025-05", "store_id": 1, "sales": 12345.67 },
  { "month": "2025-05", "store_id": 2, "sales":  9876.54 }
]
