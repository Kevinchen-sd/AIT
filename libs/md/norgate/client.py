import os
import pandas as pd
from functools import lru_cache

def _require(pkg):
    try: return __import__(pkg)
    except ImportError as e: raise RuntimeError(f"Missing dependency: {pkg}") from e

class NorgateClient:
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or os.getenv("NORGATE_DB_PATH")

    @lru_cache(maxsize=1)
    def _api(self):
        norgatedata = _require("norgatedata")
        if self.db_path:
            norgatedata.set_db_path(self.db_path)
        return norgatedata

    def bars_eod(self, symbols: list[str], start: str | None = None, end: str | None = None,
                 adjust: str = "CASHDIVIDENDS"):
        nd = self._api()
        df = nd.price_timeseries(
            symbols, start_date=start, end_date=end,
            fields=["Open","High","Low","Close","Volume"],
            adjust=adjust, include_delisted=True, dataframe=True
        )
        df.index = pd.DatetimeIndex(df.index).tz_localize(None)
        return df.sort_index()

    def constituents(self, index_symbol: str, date: str):
        nd = self._api()
        members = nd.members(index_symbol, asof=date, include_delisted=True)
        return list(members)
