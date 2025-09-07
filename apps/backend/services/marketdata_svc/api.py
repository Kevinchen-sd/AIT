from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Literal, List
import pandas as pd
from libs.md.norgate.client import NorgateClient

router = APIRouter(prefix="/v1/md", tags=["marketdata"])

class Bar(BaseModel):
    ts: str; o: float; h: float; l: float; c: float; v: float

class BarsResp(BaseModel):
    symbol: str
    adjust: Literal["CASHDIVIDENDS","TOTALRETURN","CAPITAL"]
    bars: List[Bar]

@router.get("/bars", response_model=BarsResp)
def get_bars(
    symbol: str = Query(...),
    start: str | None = Query(None, description="YYYY-MM-DD"),
    end: str | None = Query(None, description="YYYY-MM-DD"),
    adjust: Literal["CASHDIVIDENDS","TOTALRETURN","CAPITAL"] = "CASHDIVIDENDS",
):
    try:
        nc = NorgateClient()
        df: pd.DataFrame = nc.bars_eod([symbol], start=start, end=end, adjust=adjust)
        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")
        ohlcv = df[symbol].reset_index().rename(columns={
            "index": "ts", "Open":"o","High":"h","Low":"l","Close":"c","Volume":"v"
        })
        rows = [Bar(ts=r["ts"].strftime("%Y-%m-%d"), o=r["o"], h=r["h"], l=r["l"], c=r["c"], v=r["v"])
                for _, r in ohlcv.iterrows()]
        return BarsResp(symbol=symbol, adjust=adjust, bars=rows)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
