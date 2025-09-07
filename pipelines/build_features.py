import pandas as pd
from pathlib import Path

SILVER = Path("data/silver")
GOLD = Path("data/gold"); GOLD.mkdir(parents=True, exist_ok=True)

def main():
    ohlcv = pd.read_parquet(SILVER / "ohlcv.parquet")
    close = ohlcv.xs("Close", axis=1, level=1)
    feats = {
        "ret_21": close.pct_change(21),
        "ret_63": close.pct_change(63),
        "ret_126": close.pct_change(126),
        "ma50_gt_ma200": (close.rolling(50).mean() > close.rolling(200).mean()).astype(int),
        "vol14": close.pct_change().rolling(14).std(),
    }
    feat_df = pd.concat(feats, axis=1).dropna(how="all")
    feat_df.to_parquet(GOLD / "features_daily.parquet")
    print("features written:", GOLD / "features_daily.parquet")

if __name__ == "__main__":
    main()
