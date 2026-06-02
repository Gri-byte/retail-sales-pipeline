import pandas as pd
from loguru import logger
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import REQUIRED_COLUMNS


class DataCleaner:
    """Cleans and validates raw retail sales data."""

    def validate_schema(self, df: pd.DataFrame) -> None:
        missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        before = len(df)
        df = df.drop_duplicates(subset=["order_id"])
        removed = before - len(df)
        if removed > 0:
            logger.warning(f"Removed {removed} duplicate order_ids")
        return df

    def handle_nulls(self, df: pd.DataFrame) -> pd.DataFrame:
        critical_cols = ["order_id", "customer_id", "product_id", "unit_price"]
        null_counts = df[critical_cols].isnull().sum()
        if null_counts.any():
            logger.warning(f"Null values found:\n{null_counts[null_counts > 0]}")
        df = df.dropna(subset=critical_cols)
        df = df.copy()
        df["quantity"] = df["quantity"].fillna(1).astype(int)
        return df

    def fix_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(1).astype(int)
        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
        return df

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Starting data cleaning pipeline")
        self.validate_schema(df)
        df = self.remove_duplicates(df)
        df = self.handle_nulls(df)
        df = self.fix_data_types(df)
        logger.info(f"Cleaning complete. {len(df)} rows ready for transformation.")
        return df
