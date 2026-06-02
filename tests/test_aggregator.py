import pytest
import pandas as pd
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.transform.aggregator import SalesAggregator


@pytest.fixture
def clean_df():
    return pd.DataFrame({
        "order_id": [f"ORD-{i:03d}" for i in range(10)],
        "customer_id": ["C001", "C002", "C001", "C003", "C002", "C001", "C004", "C003", "C002", "C001"],
        "product_id": ["P001", "P002", "P001", "P003", "P002", "P003", "P001", "P002", "P003", "P001"],
        "quantity": [2, 1, 3, 2, 1, 4, 1, 2, 3, 2],
        "unit_price": [10.0, 25.0, 10.0, 50.0, 25.0, 50.0, 10.0, 25.0, 50.0, 10.0],
        "order_date": pd.to_datetime(["2024-01-01"] * 5 + ["2024-01-02"] * 5),
        "region": ["North", "South", "North", "East", "South", "West", "North", "East", "South", "West"],
    })


def test_add_revenue(clean_df):
    agg = SalesAggregator()
    result = agg.add_revenue(clean_df)
    assert "revenue" in result.columns
    assert result["revenue"].iloc[0] == 20.0


def test_daily_sales_shape(clean_df):
    agg = SalesAggregator()
    result = agg.daily_sales(clean_df)
    assert len(result) == 2
    assert "total_revenue" in result.columns


def test_sales_by_region(clean_df):
    agg = SalesAggregator()
    result = agg.sales_by_region(clean_df)
    assert set(result["region"]) == {"North", "South", "East", "West"}
    assert result["total_revenue"].iloc[0] >= result["total_revenue"].iloc[-1]


def test_top_products_limit(clean_df):
    agg = SalesAggregator()
    result = agg.top_products(clean_df, top_n=2)
    assert len(result) == 2
