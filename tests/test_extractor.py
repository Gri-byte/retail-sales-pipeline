import pytest
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.extract.csv_extractor import CSVExtractor


@pytest.fixture
def sample_csv(tmp_path):
    """Creates a temporary CSV file for testing."""
    df = pd.DataFrame({
        "order_id":    ["ORD-001", "ORD-002", "ORD-003"],
        "customer_id": ["C001", "C002", "C003"],
        "product_id":  ["P001", "P002", "P003"],
        "quantity":    [2, 1, 3],
        "unit_price":  [10.0, 25.0, 50.0],
        "order_date":  pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
        "region":      ["North", "South", "East"],
    })
    csv_file = tmp_path / "sales_2024.csv"
    df.to_csv(csv_file, index=False)
    return tmp_path, df


def test_extract_returns_dataframe(sample_csv):
    tmp_path, original = sample_csv
    extractor = CSVExtractor(str(tmp_path))
    result = extractor.extract("sales_2024.csv")
    assert isinstance(result, pd.DataFrame)


def test_extract_returns_correct_row_count(sample_csv):
    tmp_path, original = sample_csv
    extractor = CSVExtractor(str(tmp_path))
    result = extractor.extract("sales_2024.csv")
    assert len(result) == len(original)


def test_extract_returns_correct_columns(sample_csv):
    tmp_path, original = sample_csv
    extractor = CSVExtractor(str(tmp_path))
    result = extractor.extract("sales_2024.csv")
    assert list(result.columns) == list(original.columns)


def test_extract_parses_order_date_as_datetime(sample_csv):
    tmp_path, _ = sample_csv
    extractor = CSVExtractor(str(tmp_path))
    result = extractor.extract("sales_2024.csv")
    assert str(result["order_date"].dtype).startswith("datetime64")


def test_extract_raises_if_file_not_found(tmp_path):
    extractor = CSVExtractor(str(tmp_path))
    with pytest.raises(FileNotFoundError):
        extractor.extract("nonexistent.csv")


def test_extract_all_combines_multiple_files(tmp_path):
    """extract_all should concatenate all CSV files in the directory."""
    for i in range(1, 3):
        df = pd.DataFrame({
            "order_id":    [f"ORD-{i:03d}"],
            "customer_id": [f"C{i:03d}"],
            "product_id":  [f"P{i:03d}"],
            "quantity":    [i],
            "unit_price":  [float(i * 10)],
            "order_date":  ["2024-01-01"],
            "region":      ["North"],
        })
        df.to_csv(tmp_path / f"sales_0{i}.csv", index=False)

    extractor = CSVExtractor(str(tmp_path))
    result = extractor.extract_all()
    assert len(result) == 2


def test_extract_all_raises_if_no_csv_files(tmp_path):
    extractor = CSVExtractor(str(tmp_path))
    with pytest.raises(ValueError, match="No CSV files found"):
        extractor.extract_all()