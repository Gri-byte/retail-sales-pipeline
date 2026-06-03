import pytest
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.checks.business_rules import check_business_rules, log_violations


@pytest.fixture
def clean_df():
    return pd.DataFrame({
        "order_id":    [f"ORD-{i:03d}" for i in range(10)],
        "customer_id": [f"C{i:03d}" for i in range(10)],
        "product_id":  [f"P{i:03d}" for i in range(10)],
        "quantity":    [1, 2, 3, 1, 2, 4, 1, 2, 3, 5],
        "unit_price":  [10.0, 25.0, 50.0, 15.0, 30.0, 20.0, 10.0, 25.0, 50.0, 10.0],
        "order_date":  pd.date_range("2024-01-01", periods=10, freq="D"),
        "region":      ["North", "South", "East", "West", "Central"] * 2,
    })


# ── No violations on clean data ───────────────────────────────────────────────

def test_no_violations_on_clean_data(clean_df):
    violations = check_business_rules(clean_df)
    errors = [v for v in violations if v.severity == "ERROR"]
    assert len(errors) == 0


# ── Negative revenue ──────────────────────────────────────────────────────────

def test_detects_negative_revenue(clean_df):
    df = clean_df.copy()
    df.loc[0, "unit_price"] = -10.0
    violations = check_business_rules(df)
    rules = [v.rule for v in violations]
    assert "no_negative_revenue" in rules or "no_negative_price" in rules


# ── Zero quantity ─────────────────────────────────────────────────────────────

def test_detects_zero_quantity(clean_df):
    df = clean_df.copy()
    df.loc[2, "quantity"] = 0
    violations = check_business_rules(df)
    rules = [v.rule for v in violations]
    assert "positive_quantity" in rules


def test_detects_negative_quantity(clean_df):
    df = clean_df.copy()
    df.loc[3, "quantity"] = -5
    violations = check_business_rules(df)
    rules = [v.rule for v in violations]
    assert "positive_quantity" in rules


# ── Future dates ──────────────────────────────────────────────────────────────

def test_detects_future_order_dates(clean_df):
    df = clean_df.copy()
    df.loc[0, "order_date"] = pd.Timestamp("2099-12-31")
    violations = check_business_rules(df)
    rules = [v.rule for v in violations]
    assert "no_future_dates" in rules


# ── Unknown regions ───────────────────────────────────────────────────────────

def test_detects_unknown_region(clean_df):
    df = clean_df.copy()
    df.loc[1, "region"] = "UNKNOWN_REGION"
    violations = check_business_rules(df)
    rules = [v.rule for v in violations]
    assert "valid_region_values" in rules


# ── log_violations raises on ERROR ────────────────────────────────────────────

def test_log_violations_raises_on_error_severity(clean_df):
    df = clean_df.copy()
    df.loc[0, "quantity"] = 0   # triggers ERROR
    violations = check_business_rules(df)
    errors = [v for v in violations if v.severity == "ERROR"]
    assert len(errors) > 0
    with pytest.raises(ValueError, match="Business rules FAILED"):
        log_violations(violations)


def test_log_violations_no_raise_on_warnings_only(clean_df):
    df = clean_df.copy()
    df.loc[0, "order_date"] = pd.Timestamp("2099-01-01")  # WARNING only
    violations = check_business_rules(df)
    warnings = [v for v in violations if v.severity == "WARNING"]
    errors   = [v for v in violations if v.severity == "ERROR"]
    assert len(warnings) > 0
    assert len(errors) == 0
    log_violations(violations)  # should NOT raise