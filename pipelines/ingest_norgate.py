import os, json
from datetime import date
from pathlib import Path
from libs.md.norgate.client import NorgateClient

DATA = Path("data"); SILVER = DATA / "silver"; SILVER.mkdir(parents=True, exist_ok=True)
INDEX = os.getenv("UNIVERSE_INDEX", "^SPX")
START = os.getenv("HIST_START", "2015-01-01")

def main(eod_date: str | None = None):
    eod_date = eod_date or str(date.today())
    nc = NorgateClient()
    members = nc.constituents(INDEX, eod_date)
    bars = nc.bars_eod(members, start=START, end=eod_date, adjust="CASHDIVIDENDS")
    out = SILVER / "ohlcv.parquet"
    bars.to_parquet(out)
    (SILVER / "universe.json").write_text(json.dumps({"index": INDEX, "asof": eod_date, "count": len(members)}))
    print(f"written {out}, universe size {len(members)}")

if __name__ == "__main__":
    main()
