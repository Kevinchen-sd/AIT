import pandas as pd
from pathlib import Path
from ml.registry.loader import load_model

SILVER = Path("data/silver"); GOLD = Path("data/gold"); GOLD.mkdir(parents=True, exist_ok=True)

def run_strategy(name: str, version: str | None = None) -> pd.DataFrame:
    model, _ = load_model(name, version)
    ohlcv = pd.read_parquet(SILVER / "ohlcv.parquet")
    result = model.score(ohlcv)
    return result["scores"].to_frame(name=f"{name}")

def main():
    registry_dir = Path("ml/registry")
    strategies = [p.stem for p in registry_dir.glob("*.yaml")]
    frames = [run_strategy(name) for name in strategies]
    df = pd.concat(frames, axis=1)
    out = GOLD / "scores_latest.parquet"; df.to_parquet(out)
    print("scores written:", out)

if __name__ == "__main__":
    main()
