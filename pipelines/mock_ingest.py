# pipelines/mock_ingest.py
import numpy as np
import pandas as pd
from pathlib import Path

DATA = Path("data"); SILVER = DATA / "silver"; SILVER.mkdir(parents=True, exist_ok=True)

SYMS = ["AAPL", "MSFT", "AMZN", "TSLA", "SPY"]

def main():
    dates = pd.date_range("2023-01-01", periods=300, freq="B")  # 300 business days
    rng = np.random.default_rng(0)

    panels = {}
    for sym in SYMS:
        base = 100 + rng.normal(0, 1)  # starting price
        rets = rng.normal(0, 0.01, size=len(dates))  # daily returns ~1%
        prices = base * np.exp(np.cumsum(rets))
        df = pd.DataFrame({
            "Open": prices * (1 + rng.normal(0, 0.002, size=len(dates))),
            "High": prices * (1 + rng.normal(0, 0.005, size=len(dates))),
            "Low":  prices * (1 - rng.normal(0, 0.005, size=len(dates))),
            "Close": prices,
            "Volume": rng.integers(1e6, 5e6, size=len(dates))
        }, index=dates)
        panels[sym] = df

    # concat into MultiIndex DataFrame: (symbol, field)
    ohlcv = pd.concat(panels, axis=1)
    out = SILVER / "ohlcv.parquet"
    ohlcv.to_parquet(out)
    print("mock OHLCV written:", out, "shape:", ohlcv.shape)

if __name__ == "__main__":
    main()
