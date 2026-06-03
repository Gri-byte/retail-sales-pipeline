import pandas as pd
from loguru import logger


def assert_revenue_reconciliation(
    raw_df: pd.DataFrame,
    daily_df: pd.DataFrame,
    tolerance: float = 0.01,
) -> None:
    """
    Verifies that the sum of revenue in the aggregated output matches
    the sum calculated directly from the raw cleaned data.

    This catches bugs where a filter, join, or groupby silently
    drops or duplicates rows during aggregation.

    tolerance: max allowed difference in dollars (default: $0.01 for float rounding)
    """
    raw_total = (raw_df["quantity"] * raw_df["unit_price"]).sum()
    aggregated_total = daily_df["total_revenue"].sum()
    diff = abs(raw_total - aggregated_total)

    if diff > tolerance:
        raise ValueError(
            f"Revenue reconciliation FAILED!\n"
            f"  Raw total      : ${raw_total:>12,.2f}\n"
            f"  Aggregated total: ${aggregated_total:>12,.2f}\n"
            f"  Difference      : ${diff:>12,.2f}  (tolerance: ${tolerance:.2f})\n"
            f"  → A filter or groupby is dropping/duplicating rows. Investigate aggregator."
        )

    logger.success(
        f"✅ Revenue reconciliation OK — "
        f"${aggregated_total:,.2f} matches across raw and aggregated datasets"
    )


def assert_order_count_reconciliation(
    raw_df: pd.DataFrame,
    daily_df: pd.DataFrame,
) -> None:
    """
    Verifies total unique orders in raw data matches sum in daily aggregation.
    Catches fan-out bugs (row duplication during joins).
    """
    raw_count = raw_df["order_id"].nunique()
    aggregated_count = daily_df["total_orders"].sum()

    if raw_count != aggregated_count:
        raise ValueError(
            f"Order count reconciliation FAILED!\n"
            f"  Unique orders (raw)       : {raw_count}\n"
            f"  Sum of daily total_orders : {int(aggregated_count)}\n"
            f"  → Possible fan-out or missing orders in aggregation."
        )

    logger.success(f"✅ Order count reconciliation OK — {raw_count} orders")