import pandas as pd
from loguru import logger
from dataclasses import dataclass
from typing import List


@dataclass
class Anomaly:
    region: str
    metric: str
    value: float
    z_score: float
    direction: str   # "HIGH" | "LOW"
    details: str


class RegionalAnomalyDetector:
    """
    Detects regions whose metrics deviate significantly from the average
    using the Z-score method (number of standard deviations from the mean).

    A region is flagged as anomalous when |z_score| > threshold.
    This is the same statistical approach used in production data
    observability tools to catch unusual spikes or drops.
    """

    def __init__(self, z_threshold: float = 2.0):
        self.z_threshold = z_threshold

    def _zscore(self, series: pd.Series) -> pd.Series:
        mean = series.mean()
        std = series.std(ddof=0)
        if std == 0:
            # All values identical — no deviation possible
            return pd.Series([0.0] * len(series), index=series.index)
        return (series - mean) / std

    def detect(self, regional_df: pd.DataFrame) -> List[Anomaly]:
        """
        Analyzes a regional aggregation dataframe and returns a list of
        anomalies found across revenue, orders, and customers.

        Expects columns: region, total_revenue, total_orders, unique_customers
        """
        if len(regional_df) < 3:
            logger.warning(
                f"Anomaly detection needs at least 3 regions to be meaningful "
                f"(got {len(regional_df)}). Skipping."
            )
            return []

        anomalies: List[Anomaly] = []
        metrics = ["total_revenue", "total_orders", "unique_customers"]

        for metric in metrics:
            if metric not in regional_df.columns:
                continue

            z_scores = self._zscore(regional_df[metric])

            for idx, z in z_scores.items():
                if abs(z) > self.z_threshold:
                    region = regional_df.loc[idx, "region"]
                    value = regional_df.loc[idx, metric]
                    direction = "HIGH" if z > 0 else "LOW"
                    anomalies.append(Anomaly(
                        region=str(region),
                        metric=metric,
                        value=float(value),
                        z_score=round(float(z), 2),
                        direction=direction,
                        details=(
                            f"Region '{region}' has {direction} {metric}: "
                            f"{value:,.2f} (z-score: {z:.2f}, "
                            f"threshold: ±{self.z_threshold})"
                        ),
                    ))

        return anomalies

    def report(self, anomalies: List[Anomaly]) -> None:
        """Logs a summary of detected anomalies."""
        if not anomalies:
            logger.success("✅ No regional anomalies detected — all regions within normal range")
            return

        logger.warning(f"🔍 {len(anomalies)} regional anomalies detected:")
        for a in anomalies:
            icon = "📈" if a.direction == "HIGH" else "📉"
            logger.warning(f"   {icon} {a.details}")
