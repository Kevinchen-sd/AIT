import pandas as pd
from pathlib import Path
from ml.registry.loader import load_model

DATA = Path("tests/data/ohlcv_small.parquet")

def test_scores_are_stable():
    assert DATA.exists(), "Run `make prepare-golden` first"
    ohlcv = pd.read_parquet(DATA)
    model, _ = load_model("momo_trend", "0.1.0")
    res = model.score(ohlcv)
    scores = res["scores"]
    assert not scores.empty
    assert float(scores.iloc[0]) > float(scores.iloc[-1])
    res2 = model.score(ohlcv)
    pd.testing.assert_series_equal(scores, res2["scores"], check_names=False)

def test_signals_topk_subset():
    ohlcv = pd.read_parquet(DATA)
    model, _ = load_model("momo_trend", "0.1.0")
    res = model.score(ohlcv)
    top_syms = res["signals"]["buy"]
    close_cols = ohlcv.xs("Close", axis=1, level=1).columns
    assert set(top_syms).issubset(set(close_cols))
