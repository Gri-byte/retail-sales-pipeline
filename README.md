# 🛒 Retail Sales ETL Pipeline

![CI/CD](https://github.com/Gri-byte/retail-sales-pipeline/actions/workflows/pipeline.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue?style=flat-square&logo=python)
![Coverage](https://img.shields.io/badge/coverage-98%25-brightgreen?style=flat-square)
![Tests](https://img.shields.io/badge/tests-47%20passing-brightgreen?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square)

Production-style ETL pipeline that processes daily retail sales data — extracts from CSV, validates & cleans, aggregates KPIs, and loads results. Includes 5 layers of automated bug detection before any data reaches the output.

---

## 🏗️ Architecture

```
data/raw/sales_2024.csv
        │
        ▼
[CSVExtractor]
        │
        ▼  Gate 1: Schema check
        │  Gate 2: Volume check
        ▼
[DataCleaner]
        │
        ▼  Gate 3: Drop rate check (<15%)
        ▼
[BusinessRules]
        │
        ▼  Gate 4: No negative prices, zero qty, future dates, unknown regions
        ▼
[SalesAggregator]
        │
        ▼  Gate 5: Revenue & order count reconciliation
        ▼
[CSVLoader] → data/processed/
               ├── daily_sales.csv
               ├── sales_by_region.csv
               └── top_products.csv
```

---

## 🛡️ Bug Detection Gates

| Gate | Module | What it catches |
|---|---|---|
| 1 — Schema | `src/utils/validator.py` | Missing or renamed columns in input |
| 2 — Volume | `src/utils/validator.py` | Empty or near-empty files |
| 3 — Drop rate | `src/utils/validator.py` | Cleaner discarded >15% of rows silently |
| 4 — Business rules | `src/checks/business_rules.py` | Negative prices, zero qty, future dates, unknown regions, outliers |
| 5 — Reconciliation | `src/checks/reconciliation.py` | Aggregated totals don't match raw source |

If any ERROR-level gate fails, the pipeline halts immediately and exits with code 1 — no corrupt data reaches the output.

---

## 🚀 Quick Start

```bash
git clone https://github.com/Gri-byte/retail-sales-pipeline
cd retail-sales-pipeline
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python data/generate_sample_data.py    # creates synthetic test data
pytest tests/ -v                       # run all 47 tests
python pipeline.py                     # run full pipeline
```

---

## ✅ Test Coverage — 98%

| Module | Coverage |
|---|---|
| `src/extract/csv_extractor.py` | 100% |
| `src/transform/cleaner.py` | 100% |
| `src/transform/aggregator.py` | 100% |
| `src/load/csv_loader.py` | 100% |
| `src/utils/validator.py` | 100% |
| `src/checks/reconciliation.py` | 100% |
| `src/checks/business_rules.py` | 94% |

---

## 📊 Output Files

| File | Description |
|---|---|
| `daily_sales.csv` | Revenue and order count per day |
| `sales_by_region.csv` | KPIs broken down by region |
| `top_products.csv` | Top 10 products by revenue |

---

## ⚙️ CI/CD — GitHub Actions

The pipeline runs automatically:
- On every push to `main` or `develop`
- On every pull request to `main`
- Scheduled Monday–Friday at 6am Argentina time (UTC-3)
- Manually via **Actions → Run workflow** button

Jobs run in sequence: tests must pass before the pipeline executes. Processed data is saved as a downloadable artifact for 30 days after each run.

---

## 🛠️ Stack

`Python 3.11` · `Pandas` · `loguru` · `pytest` · `pytest-cov` · `python-dotenv` · `GitHub Actions`