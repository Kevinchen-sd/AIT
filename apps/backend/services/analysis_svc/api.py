from fastapi import APIRouter
from pydantic import BaseModel
from pathlib import Path
import pandas as pd
from ml.registry.loader import load_model
from ml.strategies.holdings_review import review_holdings

router = APIRouter(prefix="/v1/analysis", tags=["analysis"])
SILVER = Path("data/silver")
GOLD = Path("data/gold")

class KeepReplaceReq(BaseModel):
    account_id: str
    evaluation_date: str | None = None
    benchmark: str = "SPY"
    strategy: str = "momo_trend@0.1.0"
    symbols: list[str]

@router.post("/portfolio/keep_or_replace")
def keep_or_replace(req: KeepReplaceReq):
    ohlcv = pd.read_parquet(SILVER / "ohlcv.parquet")
    scores_path = GOLD / "scores_latest.parquet"
    if scores_path.exists():
        scores = pd.read_parquet(scores_path)
    else:
        name, _, ver = req.strategy.partition("@")
        model, _ = load_model(name, ver or None)
        scores = model.score(ohlcv)["scores"].to_frame(name=name)

    review = review_holdings(ohlcv, req.symbols, benchmark=req.benchmark)

    name = req.strategy.split("@")[0]
    top = scores[name].sort_values(ascending=False)
    candidates = [s for s in top.index if s not in set(req.symbols)][:3]
    for r in review:
        r["replacements"] = candidates if r["action"] == "REPLACE" else []
    return {"as_of": str(ohlcv.index[-1].date()), "items": review}
