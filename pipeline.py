name: Retail Sales Pipeline CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: "0 9 * * 1-5"   # lunes a viernes 6am Argentina (UTC-3)
  workflow_dispatch:          # permite correrlo manualmente desde GitHub

jobs:
  test:
    name: 🧪 Run Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Generate sample data
        run: python data/generate_sample_data.py
      - name: Run tests with coverage
        run: pytest tests/ -v --cov=src --cov-report=term-missing

  run-pipeline:
    name: 🚀 Run Full Pipeline
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Generate sample data
        run: python data/generate_sample_data.py
      - name: Execute pipeline
        run: python pipeline.py
      - name: Upload processed data as artifact
        uses: actions/upload-artifact@v4
        with:
          name: processed-data-${{ github.run_number }}
          path: data/processed/
          retention-days: 30