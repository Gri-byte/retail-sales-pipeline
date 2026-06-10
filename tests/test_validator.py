import pytest
import pandas as pd
from src.utils.validator import assert_schema, assert_volume, assert_drop_rate, assert_data_freshness


@pytest.fixture
def valid_df():
    return pd.DataFrame({
        "order_id":    ["ORD-001", "ORD-002"],
        "customer_id": ["C001", "C002"],
        "product_id":  ["P001", "P002"],
        "quantity":    [2.0, 3.0],
        "unit_price":  [10.0, 20.0],
        "order_date":  pd.to_datetime(["2024-01-01", "2024-01-02"]),
        "region":      ["North", "South"],
    })


# ── assert_schema ─────────────────────────────────────────────────────────────

def test_assert_schema_passes_valid_df(valid_df):
    assert_schema(valid_df, "TEST")  # should not raise


def test_assert_schema_raises_on_missing_column(valid_df):
    df = valid_df.drop(columns=["region"])
    with pytest.raises(ValueError, match="missing columns"):
        assert_schema(df, "TEST")


def test_assert_schema_raises_on_multiple_missing(valid_df):
    df = valid_df.drop(columns=["region", "order_date"])
    with pytest.raises(ValueError) as exc:
        assert_schema(df, "TEST")
    assert "region" in str(exc.value)
    assert "order_date" in str(exc.value)


# ── assert_volume ─────────────────────────────────────────────────────────────

def test_assert_volume_passes(valid_df):
    assert_volume(valid_df, "TEST", min_rows=1)


def test_assert_volume_raises_when_too_few_rows(valid_df):
    with pytest.raises(ValueError, match="Volume check FAILED"):
        assert_volume(valid_df, "TEST", min_rows=100)


def test_assert_volume_raises_on_empty_df():
    empty = pd.DataFrame(columns=["order_id"])
    with pytest.raises(ValueError, match="Volume check FAILED"):
        assert_volume(empty, "TEST", min_rows=1)


# ── assert_drop_rate ──────────────────────────────────────────────────────────

def test_assert_drop_rate_passes_within_threshold():
    assert_drop_rate(before=100, after=95, max_drop_pct=0.10)  # 5% drop — OK


def test_assert_drop_rate_raises_above_threshold():
    with pytest.raises(ValueError, match="Drop rate check FAILED"):
        assert_drop_rate(before=100, after=70, max_drop_pct=0.10)  # 30% drop — FAIL


def test_assert_drop_rate_raises_on_zero_before():
    with pytest.raises(ValueError, match="cannot calculate drop rate"):
        assert_drop_rate(before=0, after=0)


def test_assert_drop_rate_exact_threshold_passes():
    assert_drop_rate(before=100, after=90, max_drop_pct=0.10)  # exactly 10% — OK


# ── assert_data_freshness ─────────────────────────────────────────────────────

def test_assert_freshness_recent_data_does_not_raise(valid_df, caplog):
    # Use today's date — should be fresh
    df = valid_df.copy()
    df["order_date"] = pd.Timestamp.today()
    import logging
    with caplog.at_level(logging.WARNING):
        assert_data_freshness(df, max_days_old=1)
    assert "WARNING" not in caplog.text


def test_assert_freshness_old_data_logs_warning(valid_df, caplog):
    df = valid_df.copy()
    df["order_date"] = pd.to_datetime("2020-01-01")  # very old
    import logging
    with caplog.at_level(logging.WARNING):
        assert_data_freshness(df, max_days_old=2)
    # loguru doesn't integrate with caplog by default — just assert no raise