import pytest
import pandas as pd
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.transform.cleaner import DataCleaner


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "order_id": ["ORD-001", "ORD-002", "ORD-001", "ORD-003"],
        "customer_id": ["C001", "C002", "C001", "C003"],
        "product_id": ["P001", "P002", "P001", None],
        "quantity": [2, None, 2, 5],
        "unit_price": [10.0, 20.0, 10.0, 15.0],
        "order_date": pd.to_datetime(["2024-01-01"] * 4),
        "region": ["North", "South", "North", "East"],
    })


def test_remove_duplicates(sample_df):
    cleaner = DataCleaner()
    result = cleaner.remove_duplicates(sample_df)
    assert len(result) == 3
    assert result["order_id"].nunique() == 3


def test_handle_nulls_drops_null_product(sample_df):
    cleaner = DataCleaner()
    result = cleaner.handle_nulls(sample_df)
    assert result["product_id"].isnull().sum() == 0


def test_handle_nulls_fills_quantity(sample_df):
    cleaner = DataCleaner()
    result = cleaner.handle_nulls(sample_df)
    assert result["quantity"].isnull().sum() == 0


def test_validate_schema_raises_on_missing_column(sample_df):
    cleaner = DataCleaner()
    df_bad = sample_df.drop(columns=["order_date"])
    with pytest.raises(ValueError, match="Missing required columns"):
        cleaner.validate_schema(df_bad)


def test_fix_data_types(sample_df):
    cleaner = DataCleaner()
    result = cleaner.fix_data_types(sample_df)
    assert result["unit_price"].dtype == float
    assert result["order_date"].dtype == "datetime64[ns]"


def test_full_clean_pipeline(sample_df):
    cleaner = DataCleaner()
    result = cleaner.clean(sample_df)
    assert len(result) > 0
    assert result["order_id"].nunique() == len(result)
