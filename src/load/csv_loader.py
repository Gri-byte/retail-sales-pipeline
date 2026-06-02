import pandas as pd
from pathlib import Path
from loguru import logger


class CSVLoader:
    """Loads processed data to the output directory."""

    def __init__(self, output_path: str):
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)

    def load(self, df: pd.DataFrame, filename: str) -> str:
        output_file = self.output_path / filename
        df.to_csv(output_file, index=False)
        logger.info(f"Saved {len(df)} rows to {output_file}")
        return str(output_file)
