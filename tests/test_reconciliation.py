import pytest
import pandas as pd
from src.checks.reconciliation import assert_revenue_reconciliation, assert_order_count_reconciliation
from src.transform.aggregator import SalesAggregator


@pytest.fixture
def clean_df():
    return pd.DataFrame({
        "order_id":   [f"ORD-{i:03d}" for i in range(6)],
        "customer_id": [f"C{i:03d}" for i in range(6)],
        "product_id":  [f"P{i:03d}" for i in range(6)],
        "quantity":    [2, 1, 3, 2, 1, 4],
        "unit_price":  [10.0, 25.0, 50.0, 15.0, 30.0, 20.0],
        "order_date":  pd.to_datetime(["2024-01-01"] * 3 + ["2024-01-02"] * 3),
        "region":      ["North", "South", "East", "West", "Central", "North"],
    })


# ── Revenue reconciliation ────────────────────────────────────────────────────

def test_revenue_reconciliation_passes_on_correct_aggregation(clean_df):
    agg = SalesAggregator()
    daily_df = agg.daily_sales(clean_df)
    assert_revenue_reconciliation(clean_df, daily_df)  # should not raise


def test_revenue_reconciliation_fails_when_daily_total_is_wrong(clean_df):
    agg = SalesAggregator()
    daily_df = agg.daily_sales(clean_df)
    # Tamper with the aggregated total to simulate a bug
    daily_df = daily_df.copy()
    daily_df.loc[0, "total_revenue"] = daily_df.loc[0, "total_revenue"] + 999.0
    with pytest.raises(ValueError, match="Revenue reconciliation FAILED"):
        assert_revenue_reconciliation(clean_df, daily_df)


def test_revenue_reconciliation_passes_with_float_tolerance(clean_df):
    agg = SalesAggregator()
    daily_df = agg.daily_sales(clean_df)
    # Tiny float difference — should still pass within tolerance
    daily_df = daily_df.copy()
    daily_df.loc[0, "total_revenue"] = daily_df.loc[0, "total_revenue"] + 0.001
    assert_revenue_reconciliation(clean_df, daily_df, tolerance=0.01)


# ── Order count reconciliation ────────────────────────────────────────────────

def test_order_count_reconciliation_passes(clean_df):
    agg = SalesAggregator()
    daily_df = agg.daily_sales(clean_df)
    assert_order_count_reconciliation(clean_df, daily_df)


def test_order_count_reconciliation_fails_on_dropped_orders(clean_df):
    agg = SalesAggregator()
    daily_df = agg.daily_sales(clean_df)
    # Simulate a bug that dropped one day entirely
    daily_df_short = daily_df.head(1).copy()
    with pytest.raises(ValueError, match="Order count reconciliation FAILED"):
        assert_order_count_reconciliation(clean_df, daily_df_short)