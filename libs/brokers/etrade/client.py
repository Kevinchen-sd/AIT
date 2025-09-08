from __future__ import annotations
import os
import urllib.parse as urlparse
from typing import Dict, Tuple, Optional, Any

from requests_oauthlib import OAuth1Session

from .token_store import load as token_load, save as token_save


class ETradeClient:
    """Minimal E*TRADE API client (OAuth 1.0a)."""

    def __init__(self) -> None:
        self.consumer_key = os.environ.get("ETRADE_CONSUMER_KEY", "").strip()
        self.consumer_secret = os.environ.get("ETRADE_CONSUMER_SECRET", "").strip()
        self.callback_url = os.environ.get(
            "ETRADE_CALLBACK_URL", "http://localhost:8000/v1/brokers/etrade/callback"
        ).strip()
        self.sandbox = os.environ.get("ETRADE_SANDBOX", "true").lower() == "true"

        if not self.consumer_key or not self.consumer_secret:
            raise RuntimeError("Missing ETRADE_CONSUMER_KEY/ETRADE_CONSUMER_SECRET in environment.")

        self.base = "https://apisb.etrade.com" if self.sandbox else "https://api.etrade.com"
        self.authorize_base = "https://us.etrade.com"

    def get_request_token(self) -> Tuple[str, str]:
        oauth = OAuth1Session(
            self.consumer_key, client_secret=self.consumer_secret, callback_uri=self.callback_url
        )
        resp = oauth.fetch_request_token(f"{self.base}/oauth/request_token")
        token_save(resp)
        return resp["oauth_token"], resp["oauth_token_secret"]

    def get_authorize_url(self, oauth_token: str) -> str:
        params = {"key": self.consumer_key, "token": oauth_token}
        return f"{self.authorize_base}/e/t/etws/authorize?{urlparse.urlencode(params)}"

    def get_access_token(self, oauth_token: str, oauth_verifier: str) -> Tuple[str, str]:
        stored = token_load() or {}
        resource_owner_secret = stored.get("oauth_token_secret", "")
        oauth = OAuth1Session(
            self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=oauth_token,
            resource_owner_secret=resource_owner_secret,
            verifier=oauth_verifier,
        )
        resp = oauth.fetch_access_token(f"{self.base}/oauth/access_token")
        token_save(
            {
                "oauth_token": stored.get("oauth_token", ""),
                "oauth_token_secret": resource_owner_secret,
                "access_token": resp.get("oauth_token", ""),
                "access_token_secret": resp.get("oauth_token_secret", ""),
            }
        )
        return resp["oauth_token"], resp["oauth_token_secret"]

    def _signed(self) -> OAuth1Session:
        t = token_load() or {}
        at = t.get("access_token", "")
        ats = t.get("access_token_secret", "")
        if not at or not ats:
            raise RuntimeError("No E*TRADE access token found. Complete OAuth flow first.")
        return OAuth1Session(
            self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=at,
            resource_owner_secret=ats,
        )

    def _signed_get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict:
        sess = self._signed()
        r = sess.get(url, params=params or None, headers={"Accept": "application/json"})
        try:
            r.raise_for_status()
        except Exception as e:
            body = r.text[:2000] if hasattr(r, "text") else ""
            raise RuntimeError(f"E*TRADE API error {r.status_code}: {body}") from e
        try:
            return r.json()
        except Exception:
            return {"raw": r.text}

    def list_accounts(self) -> Dict:
        url = f"{self.base}/v1/accounts/list.json"
        return self._signed_get(url)

    def get_portfolio(
        self,
        account_id_key: str,
        view: Optional[str] = None,
        count: Optional[int] = None,
        totals_required: Optional[bool] = None,
        lots_required: Optional[bool] = None,
        market_session: Optional[str] = None,
    ) -> Dict:
        url = f"{self.base}/v1/accounts/{account_id_key}/portfolio.json"
        params: Dict[str, Any] = {}

        # Normalize/ensure view matches one of E*TRADE's allowed values
        # Allowed: QUICK, COMPLETE, PERFORMANCE, FUNDAMENTAL, OPTIONSWATCH
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
