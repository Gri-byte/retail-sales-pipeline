"""
Retail Sales ETL Pipeline
=========================
Real-world pipeline with 5 layers of bug detection:

  Gate 1 — Schema validation     (columns present and named correctly)
  Gate 2 — Volume check          (file is not empty or near-empty)
  Gate 3 — Drop rate check       (cleaner didn't silently discard too many rows)
  Gate 4 — Business rules        (no negative prices, zero qty, future dates, etc.)
  Gate 5 — Revenue reconciliation (aggregated totals match raw source)
"""

import sys
from loguru import logger
from config.settings import RAW_DATA_PATH, PROCESSED_DATA_PATH
from src.extract.csv_extractor import CSVExtractor
from src.transform.cleaner import DataCleaner
from src.transform.aggregator import SalesAggregator
from src.load.csv_loader import CSVLoader
from src.utils.validator import (
    assert_schema,
    assert_volume,
    assert_drop_rate,
    assert_data_freshness,
)
from src.checks.business_rules import check_business_rules, log_violations
from src.checks.reconciliation import (
    assert_revenue_reconciliation,
    assert_order_count_reconciliation,
)
from src.checks.anomaly_detection import RegionalAnomalyDetector

logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | {message}")
logger.add("pipeline.log", rotation="1 week", retention="4 weeks")


def run_pipeline():
    logger.info("=" * 60)
    logger.info("   RETAIL SALES PIPELINE — START")
    logger.info("=" * 60)

    # ── EXTRACT ───────────────────────────────────────────────────────────────
    logger.info("📥 [EXTRACT] Loading raw data...")
    extractor = CSVExtractor(RAW_DATA_PATH)
    raw_df = extractor.extract("sales_2024.csv")

    # Gate 1 — Schema
    assert_schema(raw_df, stage="EXTRACT")
    # Gate 2 — Volume
    assert_volume(raw_df, stage="EXTRACT", min_rows=10)

    rows_before = len(raw_df)
    logger.info(f"📥 [EXTRACT] {rows_before} rows loaded")

    # ── TRANSFORM ─────────────────────────────────────────────────────────────
    logger.info("🔧 [TRANSFORM] Cleaning data...")
    cleaner = DataCleaner()
    clean_df = cleaner.clean(raw_df)

    # Gate 3 — Drop rate
    assert_drop_rate(before=rows_before, after=len(clean_df), max_drop_pct=0.15)

    # Gate 4 — Business rules
    logger.info("🔍 [VALIDATE] Checking business rules...")
    violations = check_business_rules(clean_df)
    log_violations(violations)  # raises if any ERROR-level violation found

    # Freshness check (warning only, doesn't stop pipeline)
    assert_data_freshness(clean_df, max_days_old=400)  # relaxed for sample data

    # ── AGGREGATE ─────────────────────────────────────────────────────────────
    logger.info("📊 [AGGREGATE] Building KPIs...")
    aggregator = SalesAggregator()
    daily_df      = aggregator.daily_sales(clean_df)
    regional_df   = aggregator.sales_by_region(clean_df)
    top_products_df = aggregator.top_products(clean_df)

    # Gate 5 — Reconciliation
    logger.info("🔁 [RECONCILE] Verifying totals match source data...")
    assert_revenue_reconciliation(clean_df, daily_df)
    assert_order_count_reconciliation(clean_df, daily_df)

    # ── ANOMALY DETECTION ───────────────────────────────────────────────────────
    logger.info("🔍 [ANOMALY] Scanning regions for statistical outliers...")
    detector = RegionalAnomalyDetector(z_threshold=2.0)
    anomalies = detector.detect(regional_df)
    detector.report(anomalies)  # warns but does not halt the pipeline

    # ── LOAD ──────────────────────────────────────────────────────────────────
    logger.info("💾 [LOAD] Writing output files...")
    loader = CSVLoader(PROCESSED_DATA_PATH)
    loader.load(daily_df,        "daily_sales.csv")
    loader.load(regional_df,     "sales_by_region.csv")
    loader.load(top_products_df, "top_products.csv")

    logger.info("=" * 60)
    logger.success("   PIPELINE COMPLETED SUCCESSFULLY ✅")
    logger.info(f"   Rows processed : {len(clean_df)}")
    logger.info(f"   Days covered   : {len(daily_df)}")
    logger.info(f"   Regions        : {len(regional_df)}")
    logger.info("=" * 60)


if __name__ == "__main__":
    try:
        run_pipeline()
    except ValueError as e:
        logger.error(f"Pipeline HALTED — bug detected:\n{e}")
        sys.exit(1)