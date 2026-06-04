import pytest
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.checks.anomaly_detection import RegionalAnomalyDetector, Anomaly


@pytest.fixture
def normal_regional_df():
    """Regions with similar metrics — no anomalies expected."""
    return pd.DataFrame({
        "region":           ["North", "South", "East", "West", "Central"],
        "total_revenue":    [10000.0, 10500.0, 9800.0, 10200.0, 9900.0],
        "total_orders":     [100, 105, 98, 102, 99],
        "unique_customers": [50, 52, 49, 51, 50],
    })


@pytest.fixture
def anomalous_regional_df():
    """One region (North) has a huge revenue spike — should be flagged."""
    return pd.DataFrame({
        "region":           ["North", "South", "East", "West", "Central"],
        "total_revenue":    [99000.0, 10500.0, 9800.0, 10200.0, 9900.0],
        "total_orders":     [100, 105, 98, 102, 99],
        "unique_customers": [50, 52, 49, 51, 50],
    })


# ── No anomalies on normal data ───────────────────────────────────────────────

def test_no_anomalies_on_normal_data(normal_regional_df):
    detector = RegionalAnomalyDetector(z_threshold=2.0)
    anomalies = detector.detect(normal_regional_df)
    assert anomalies == []


# ── Detects a clear spike ─────────────────────────────────────────────────────

def test_detects_revenue_spike(anomalous_regional_df):
    detector = RegionalAnomalyDetector(z_threshold=1.5)
    anomalies = detector.detect(anomalous_regional_df)
    assert len(anomalies) > 0
    revenue_anomalies = [a for a in anomalies if a.metric == "total_revenue"]
    assert len(revenue_anomalies) == 1
    assert revenue_anomalies[0].region == "North"
    assert revenue_anomalies[0].direction == "HIGH"


# ── Detects a low outlier ─────────────────────────────────────────────────────

def test_detects_low_outlier():
    df = pd.DataFrame({
        "region":           ["North", "South", "East", "West", "Central"],
        "total_revenue":    [10000.0, 10500.0, 9800.0, 10200.0, 100.0],  # Central drops
        "total_orders":     [100, 105, 98, 102, 99],
        "unique_customers": [50, 52, 49, 51, 50],
    })
    detector = RegionalAnomalyDetector(z_threshold=1.5)
    anomalies = detector.detect(df)
    low = [a for a in anomalies if a.direction == "LOW" and a.region == "Central"]
    assert len(low) == 1


# ── Threshold sensitivity ─────────────────────────────────────────────────────

def test_higher_threshold_detects_fewer_anomalies(anomalous_regional_df):
    strict = RegionalAnomalyDetector(z_threshold=3.0)
    loose = RegionalAnomalyDetector(z_threshold=1.0)
    assert len(loose.detect(anomalous_regional_df)) >= len(strict.detect(anomalous_regional_df))


# ── Edge cases ────────────────────────────────────────────────────────────────

def test_returns_empty_with_too_few_regions():
    df = pd.DataFrame({
        "region":           ["North", "South"],
        "total_revenue":    [10000.0, 10500.0],
        "total_orders":     [100, 105],
        "unique_customers": [50, 52],
    })
    detector = RegionalAnomalyDetector()
    assert detector.detect(df) == []


def test_handles_identical_values_without_crashing():
    df = pd.DataFrame({
        "region":           ["North", "South", "East", "West"],
        "total_revenue":    [10000.0, 10000.0, 10000.0, 10000.0],  # all identical
        "total_orders":     [100, 100, 100, 100],
        "unique_customers": [50, 50, 50, 50],
    })
    detector = RegionalAnomalyDetector()
    anomalies = detector.detect(df)
    assert anomalies == []  # no deviation possible


def test_anomaly_has_correct_structure(anomalous_regional_df):
    detector = RegionalAnomalyDetector(z_threshold=1.5)
    anomalies = detector.detect(anomalous_regional_df)
    a = anomalies[0]
    assert isinstance(a, Anomaly)
    assert hasattr(a, "region")
    assert hasattr(a, "metric")
    assert hasattr(a, "z_score")
    assert hasattr(a, "direction")


def test_report_runs_without_error(anomalous_regional_df):
    detector = RegionalAnomalyDetector(z_threshold=1.5)
    anomalies = detector.detect(anomalous_regional_df)
    detector.report(anomalies)        # with anomalies
    detector.report([])               # without anomalies