import json
from typing import Any, Dict, Optional

class EtradeClient:
    def __init__(self, base: str, sess):
        self.base = base
        self.sess = sess

    def _signed_get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Any:
        headers = {"Accept": "application/json"}
        response = self.sess.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_portfolio(
        self,
        account_id_key: str,
        view: Optional[str] = None,
        count: Optional[int] = None,
        totals_required: Optional[bool] = None,
        lots_required: Optional[bool] = None,
        market_session: Optional[str] = None,
    ) -> Any:
        url = f"{self.base}/v1/accounts/{account_id_key}/portfolio.json"

        params: Dict[str, Any] = {}
        # Default/normalize view to allowed uppercase values
        if view is None:
            view_norm = "QUICK"
        else:
            v = (view or "").strip().lower()
            view_map = {
                "quick": "QUICK",
                "complete": "COMPLETE",
                "performance": "PERFORMANCE",
                "fundamental": "FUNDAMENTAL",
                "optionswatch": "OPTIONSWATCH",
            }
            view_norm = view_map.get(v, (view or "QUICK").upper())
        params["view"] = view_norm

        if count is not None:
            params["count"] = int(count)
        if totals_required is not None:
            params["totalsRequired"] = str(bool(totals_required)).lower()
        if lots_required is not None:
            params["lotsRequired"] = str(bool(lots_required)).lower()
        if market_session:
            params["marketSession"] = market_session

        return self._signed_get(url, params=params)
