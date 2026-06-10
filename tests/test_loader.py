import pytest
import pandas as pd
from src.load.csv_loader import CSVLoader


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "order_date":    pd.to_datetime(["2024-01-01", "2024-01-02"]),
        "total_orders":  [10, 15],
        "total_revenue": [1500.00, 2250.00],
    })


def test_loader_creates_output_file(tmp_path, sample_df):
    loader = CSVLoader(str(tmp_path))
    loader.load(sample_df, "daily_sales.csv")
    assert (tmp_path / "daily_sales.csv").exists()


def test_loader_returns_output_path(tmp_path, sample_df):
    loader = CSVLoader(str(tmp_path))
    result = loader.load(sample_df, "daily_sales.csv")
    assert "daily_sales.csv" in result


def test_loader_saved_content_matches_input(tmp_path, sample_df):
    loader = CSVLoader(str(tmp_path))
    loader.load(sample_df, "daily_sales.csv")
    loaded = pd.read_csv(tmp_path / "daily_sales.csv")
    assert len(loaded) == len(sample_df)
    assert list(loaded.columns) == list(sample_df.columns)


def test_loader_creates_output_dir_if_not_exists(tmp_path, sample_df):
    nested_path = tmp_path / "a" / "b" / "c"
    loader = CSVLoader(str(nested_path))
    loader.load(sample_df, "output.csv")
    assert (nested_path / "output.csv").exists()


def test_loader_overwrites_existing_file(tmp_path, sample_df):
    loader = CSVLoader(str(tmp_path))
    loader.load(sample_df, "daily_sales.csv")

    new_df = sample_df.head(1)
    loader.load(new_df, "daily_sales.csv")

    loaded = pd.read_csv(tmp_path / "daily_sales.csv")
    assert len(loaded) == 1
