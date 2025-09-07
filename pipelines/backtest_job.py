from pathlib import Path
import pandas as pd
from ml.registry.loader import load_model

def backtest(strategy: str, start: str, end: str, cash: float = 100_000.0):
    name, _, ver = strategy.partition("@")
    model, _ = load_model(name, ver or None)
    ohlcv = pd.read_parquet(Path("data/silver/ohlcv.parquet"))
    top = model.score(ohlcv)["signals"]["buy"]
    return {"symbols": top, "note": "placeholder backtest"}
