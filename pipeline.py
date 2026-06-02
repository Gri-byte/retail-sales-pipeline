"""
Retail Sales ETL Pipeline
Simulates a real-world daily sales data pipeline for a retail company.
"""
from loguru import logger
from config.settings import RAW_DATA_PATH, PROCESSED_DATA_PATH
from src.extract.csv_extractor import CSVExtractor
from src.transform.cleaner import DataCleaner
from src.transform.aggregator import SalesAggregator
from src.load.csv_loader import CSVLoader


def run_pipeline():
    logger.info("=== Retail Sales Pipeline START ===")

    # Extract
    extractor = CSVExtractor(RAW_DATA_PATH)
    raw_df = extractor.extract("sales_2024.csv")

    # Transform
    cleaner = DataCleaner()
    clean_df = cleaner.clean(raw_df)

    aggregator = SalesAggregator()
    daily_df = aggregator.daily_sales(clean_df)
    regional_df = aggregator.sales_by_region(clean_df)
    top_products_df = aggregator.top_products(clean_df)

    # Load
    loader = CSVLoader(PROCESSED_DATA_PATH)
    loader.load(daily_df, "daily_sales.csv")
    loader.load(regional_df, "sales_by_region.csv")
    loader.load(top_products_df, "top_products.csv")

    logger.info("=== Retail Sales Pipeline END ===")


if __name__ == "__main__":
    run_pipeline()
