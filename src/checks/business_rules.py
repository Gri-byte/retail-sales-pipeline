import pandas as pd
from loguru import logger
from dataclasses import dataclass, field
from typing import List
from src.utils.validator import VALID_REGIONS


@dataclass
class RuleViolation:
    rule: str
    severity: str        # "ERROR" | "WARNING"
    count: int
    details: str


def check_business_rules(df: pd.DataFrame) -> List[RuleViolation]:
    """
    Validates core business rules on the cleaned dataset.
    Returns a list of violations — caller decides whether to fail or warn.

    Rules:
      ERROR   - negative revenue         → data is fundamentally wrong
      ERROR   - zero or negative qty     → impossible in a real order
      WARNING - future order dates       → likely a data entry mistake
      WARNING - unknown region values    → mapping issue upstream
      WARNING - unit_price outliers      → possible data entry error
    """
    violations: List[RuleViolation] = []

    # ── ERROR: Zero or negative quantity ────────────────────────────────────
    zero_qty = df[df["quantity"] <= 0]
    if len(zero_qty):
        violations.append(RuleViolation(
            rule="positive_quantity",
            severity="ERROR",
            count=len(zero_qty),
            details=f"{len(zero_qty)} orders have quantity <= 0",
        ))

    # ── ERROR: Negative unit price ───────────────────────────────────────────
    neg_price = df[df["unit_price"] < 0]
    if len(neg_price):
        violations.append(RuleViolation(
            rule="no_negative_price",
            severity="ERROR",
            count=len(neg_price),
            details=f"{len(neg_price)} products have unit_price < 0",
        ))

    # ── WARNING: Future order dates ──────────────────────────────────────────
    future = df[df["order_date"] > pd.Timestamp.today()]
    if len(future):
        violations.append(RuleViolation(
            rule="no_future_dates",
            severity="WARNING",
            count=len(future),
            details=f"{len(future)} orders have future order_date (max: {df['order_date'].max().date()})",
        ))

    # ── WARNING: Unknown region values ───────────────────────────────────────
    unknown_regions = df[~df["region"].isin(VALID_REGIONS)]
    if len(unknown_regions):
        found = unknown_regions["region"].unique().tolist()
        violations.append(RuleViolation(
            rule="valid_region_values",
            severity="WARNING",
            count=len(unknown_regions),
            details=f"{len(unknown_regions)} rows with unknown region: {found}",
        ))

    # ── WARNING: Unit price statistical outliers (IQR method) ────────────────
    q1 = df["unit_price"].quantile(0.25)
    q3 = df["unit_price"].quantile(0.75)
    iqr = q3 - q1
    outliers = df[(df["unit_price"] < q1 - 3 * iqr) | (df["unit_price"] > q3 + 3 * iqr)]
    if len(outliers):
        violations.append(RuleViolation(
            rule="unit_price_outliers",
            severity="WARNING",
            count=len(outliers),
            details=f"{len(outliers)} extreme price outliers detected (IQR method, 3×)",
        ))

    return violations


def log_violations(violations: List[RuleViolation]) -> None:
    """Logs violations and raises if any ERROR-level violations exist."""
    if not violations:
        logger.success("✅ All business rules passed")
        return

    errors = [v for v in violations if v.severity == "ERROR"]
    warnings = [v for v in violations if v.severity == "WARNING"]

    for v in warnings:
        logger.warning(f"⚠️  [{v.rule}] {v.details}")

    for v in errors:
        logger.error(f"❌ [{v.rule}] {v.details}")

    if errors:
        raise ValueError(
            f"Business rules FAILED — {len(errors)} ERROR(s) found. "
            f"Pipeline halted to prevent loading corrupt data."
        )