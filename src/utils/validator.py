import pandas as pd
from loguru import logger

EXPECTED_SCHEMA = {
    "order_id": "object",
    "customer_id": "object",
    "product_id": "object",
    "quantity": "float64",
    "unit_price": "float64",
    "order_date": "datetime64[ns]",
    "region": "object",
}

VALID_REGIONS = {"North", "South", "East", "West", "Central"}


def assert_schema(df: pd.DataFrame, stage: str) -> None:
    """Checks that all required columns are present."""
    missing = [c for c in EXPECTED_SCHEMA if c not in df.columns]
    if missing:
        raise ValueError(f"[{stage}] Schema check FAILED — missing columns: {missing}")
    logger.info(f"[{stage}] ✅ Schema OK — {len(df.columns)} columns present")


def assert_volume(df: pd.DataFrame, stage: str, min_rows: int = 10) -> None:
    """Checks that the dataframe has enough rows to be meaningful."""
    if len(df) < min_rows:
        raise ValueError(
            f"[{stage}] Volume check FAILED — {len(df)} rows received (min: {min_rows})"
        )
    logger.info(f"[{stage}] ✅ Volume OK — {len(df)} rows")


def assert_drop_rate(before: int, after: int, max_drop_pct: float = 0.10) -> None:
    """
    Checks that the cleaning stage didn't silently discard too many rows.
    A drop rate above 10% usually means a bug in the cleaner or corrupt input.
    """
    if before == 0:
        raise ValueError("assert_drop_rate: 'before' count is 0, cannot calculate drop rate")
    drop_rate = (before - after) / before
    if drop_rate > max_drop_pct:
        raise ValueError(
            f"Drop rate check FAILED — {drop_rate:.1%} rows lost "
            f"({before - after} of {before}). Threshold: {max_drop_pct:.1%}. "
            f"Investigate DataCleaner or input file."
        )
    logger.info(f"✅ Drop rate OK — {drop_rate:.1%} rows cleaned ({before - after} removed)")


def assert_data_freshness(df: pd.DataFrame, max_days_old: int = 2) -> None:
    """
    Warns if the most recent order date is older than expected.
    Catches cases where the pipeline re-processed stale/old data.
    """
    latest = df["order_date"].max()
    days_old = (pd.Timestamp.today() - latest).days
    if days_old > max_days_old:
        logger.warning(
            f"⚠️  Freshness WARNING — latest order is {days_old} days old "
            f"(as of {latest.date()}). Expected data within {max_days_old} days."
        )
    else:
        logger.info(f"✅ Freshness OK — latest order: {latest.date()} ({days_old} days ago)")