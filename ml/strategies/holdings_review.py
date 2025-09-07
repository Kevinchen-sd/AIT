import pandas as pd

def review_holdings(ohlcv: pd.DataFrame, portfolio_symbols: list[str], benchmark: str = "SPY") -> list[dict]:
    close = ohlcv.xs("Close", axis=1, level=1)
    syms = [s for s in portfolio_symbols if s in close.columns]
    out = []

    ma50 = close.rolling(50).mean()
    ma200 = close.rolling(200).mean()
    r3m = close.pct_change(63)
    r6m = close.pct_change(126)
    dd = (close / close.cummax() - 1.0)

    last = close.index[-1]
    for s in syms:
        ok_trend = bool(ma50[s].iloc[-1] > ma200[s].iloc[-1])
        r3, r6 = float(r3m[s].iloc[-1]), float(r6m[s].iloc[-1])
        ddown = float(dd[s].iloc[-1])
        score = (ok_trend) + (r3 > 0) + (r6 > 0)
        if score == 3 and ddown > -0.2: action = "KEEP"
        elif score >= 1:                 action = "WATCH"
        else:                            action = "REPLACE"
        out.append({
            "symbol": s,
            "as_of": str(last.date()),
            "action": action,
            "metrics": {"trend_ok": ok_trend, "r3m": r3, "r6m": r6, "drawdown": ddown}
        })
    return out
