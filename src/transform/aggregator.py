import pandas as pd
from loguru import logger


class SalesAggregator:
    """Aggregates cleaned sales data into business metrics."""

    def add_revenue(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["revenue"] = df["quantity"] * df["unit_price"]
        return df

    def daily_sales(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self.add_revenue(df)
        daily = (
            df.groupby("order_date")
            .agg(
                total_orders=("order_id", "nunique"),
                total_revenue=("revenue", "sum"),
                avg_order_value=("revenue", "mean"),
            )
            .reset_index()
            .sort_values("order_date")
        )
        logger.info(f"Daily aggregation: {len(daily)} days")
        return daily

    def sales_by_region(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self.add_revenue(df)
        regional = (
            df.groupby("region")
            .agg(
                total_orders=("order_id", "nunique"),
                total_revenue=("revenue", "sum"),
                unique_customers=("customer_id", "nunique"),
            )
            .reset_index()
            .sort_values("total_revenue", ascending=False)
        )
        return regional

    def top_products(self, df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        df = self.add_revenue(df)
        products = (
            df.groupby("product_id")
            .agg(
                units_sold=("quantity", "sum"),
                total_revenue=("revenue", "sum"),
            )
            .reset_index()
            .sort_values("total_revenue", ascending=False)
            .head(top_n)
        )
        return products
