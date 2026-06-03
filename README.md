# 🛒 Retail Sales ETL Pipeline

Production-style ETL pipeline that processes daily retail sales data — extracts from CSV, validates & cleans, aggregates KPIs, and loads results. Simulates a real retail analytics use case.

## 🏗️ Architecture

```
data/raw/sales_2024.csv
        │
        ▼
[CSVExtractor] → [DataCleaner] → [SalesAggregator] → [CSVLoader]
                  - Duplicates     - Daily KPIs         data/processed/
                  - Nulls          - By Region
                  - Types          - Top Products
```

## 🚀 Quick Start

```bash
git clone https://github.com/Gri-byte/retail-sales-pipeline
cd retail-sales-pipeline
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python data/generate_sample_data.py    # creates synthetic test data
pytest tests/ -v                       # run all tests
python pipeline.py                     # run full pipeline
```

## 📊 Output Files

| File | Description |
|---|---|
| `daily_sales.csv` | Revenue and order count per day |
| `sales_by_region.csv` | KPIs broken down by region |
| `top_products.csv` | Top 10 products by revenue |

## ✅ Test Coverage

- Schema validation (missing columns)
- Duplicate order_id detection & removal
- Null handling in critical fields
- Data type coercion
- Revenue aggregation accuracy

## 🛠️ Stack

`Python 3.12` · `Pandas` · `python-dotenv` · `pytest` · `pytest-cov` · `loguru` · `GitHub Actions`
