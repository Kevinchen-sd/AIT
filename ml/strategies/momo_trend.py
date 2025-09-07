from dataclasses import dataclass
import pandas as pd
import numpy as np

@dataclass
class MomoTrendCfg:
    lookbacks: tuple[int,int,int] = (21, 63, 126)
    ma_fast: int = 50
    ma_slow: int = 200
    vol_norm_window: int = 14
    top_frac: float = 0.05

class MomoTrend:
    def __init__(self, params: dict | None = None):
        self.cfg = MomoTrendCfg(**params) if params else MomoTrendCfg()

    def score(self, ohlcv: pd.DataFrame) -> dict:
        close = ohlcv.xs("Close", axis=1, level=1).copy()
        ret = close.pct_change()

        rels = [(close / close.shift(lb) - 1.0) for lb in self.cfg.lookbacks]
        rel = sum(rels) / len(rels)

        ma_f = close.rolling(self.cfg.ma_fast).mean()
        ma_s = close.rolling(self.cfg.ma_slow).mean()
        trend_ok = (ma_f > ma_s).astype(float)

        vol = ret.rolling(self.cfg.vol_norm_window).std()
        voladj = (ret.rolling(21).sum() / (vol.replace(0, np.nan))).clip(-5,5)

        composite = (0.5 * rel + 0.3 * trend_ok + 0.2 * voladj)
        score = composite.iloc[-1].dropna().sort_values(ascending=False)

        top_n = max(1, int(self.cfg.top_frac * max(1, score.size)))
        buy_syms = score.index[:top_n].tolist()

        explain = {
            "rel_momentum": rel.iloc[-1].to_dict(),
            "trend_ok": trend_ok.iloc[-1].to_dict(),
            "voladj": voladj.iloc[-1].to_dict()
        }
        return {"scores": score, "signals": {"buy": buy_syms}, "explain": explain}
