from datetime import date, timedelta
from pathlib import Path
from libs.md.norgate.client import NorgateClient

OUT = Path("tests/data/ohlcv_small.parquet"); OUT.parent.mkdir(parents=True, exist_ok=True)
SYMS = ["AAPL","MSFT","AMZN","TSLA","SPY"]
END = date.today().replace(day=1) - timedelta(days=1)
START = END.replace(year=END.year-3)

def main():
    nc = NorgateClient()
    df = nc.bars_eod(SYMS, start=str(START), end=str(END), adjust="CASHDIVIDENDS")
    df = df.iloc[-700:]
    df.to_parquet(OUT)
    print("Wrote", OUT, "rows:", len(df))

if __name__ == "__main__":
    main()
