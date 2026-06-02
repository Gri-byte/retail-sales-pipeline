import pandas as pd
from pathlib import Path
from loguru import logger


class CSVExtractor:
    """Extracts raw sales data from CSV files."""

    def __init__(self, data_path: str):
        self.data_path = Path(data_path)

    def extract(self, filename: str) -> pd.DataFrame:
        filepath = self.data_path / filename
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        logger.info(f"Extracting data from {filepath}")
        df = pd.read_csv(filepath, parse_dates=["order_date"])
        logger.info(f"Extracted {len(df)} rows from {filename}")
        return df

    def extract_all(self) -> pd.DataFrame:
        files = list(self.data_path.glob("*.csv"))
        if not files:
            raise ValueError(f"No CSV files found in {self.data_path}")
        frames = [pd.read_csv(f, parse_dates=["order_date"]) for f in files]
        combined = pd.concat(frames, ignore_index=True)
        logger.info(f"Extracted {len(combined)} total rows from {len(files)} files")
        return combined
