"""Generate synthetic retail sales data for testing."""
import pandas as pd
import numpy as np
from pathlib import Path

np.random.seed(42)
n = 500

df = pd.DataFrame({
    "order_id": [f"ORD-{i:05d}" for i in range(1, n + 1)],
    "customer_id": [f"CUST-{np.random.randint(1, 100):04d}" for _ in range(n)],
    "product_id": [f"PROD-{np.random.randint(1, 50):03d}" for _ in range(n)],
    "quantity": np.random.randint(1, 20, n),
    "unit_price": np.round(np.random.uniform(5.0, 500.0, n), 2),
    "order_date": pd.date_range("2024-01-01", periods=n, freq="12h"),
    "region": np.random.choice(["North", "South", "East", "West", "Central"], n),
})

# Introduce realistic dirty data
df.loc[5, "quantity"] = None
df.loc[10, "unit_price"] = None
df = pd.concat([df, df.iloc[[0, 1]]], ignore_index=True)  # duplicate rows

output = Path(__file__).parent / "raw" / "sales_2024.csv"
output.parent.mkdir(exist_ok=True)
df.to_csv(output, index=False)
print(f"Generated {len(df)} rows -> {output}")
