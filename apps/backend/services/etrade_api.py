from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query
from starlette.responses import RedirectResponse
import os
from fastapi import Body

from libs.brokers.etrade.client import ETradeClient
from libs.brokers.etrade.token_store import clear as token_clear

from typing import Optional

router = APIRouter(prefix="/v1/brokers/etrade", tags=["etrade"])

@router.get("/auth/start")
def auth_start():
    """Begin OAuth 1.0a. If ETRADE_CALLBACK_URL == 'oob', return authorize_url + oauth_token for manual flow."""
    try:
        client = ETradeClient()
        oauth_token, _ = client.get_request_token()
        authorize_url = client.get_authorize_url(oauth_token)
        callback = os.environ.get("ETRADE_CALLBACK_URL", "").strip().lower()
        if callback == "oob":
            # In OOB mode, E*TRADE will display an oauth_verifier that the user must paste back.
            return {"mode": "oob", "authorize_url": authorize_url, "oauth_token": oauth_token}
        return RedirectResponse(authorize_url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/callback")
def auth_callback(oauth_token: str = Query(...), oauth_verifier: str = Query(...)):
    """Callback endpoint E*TRADE redirects to with oauth_verifier; exchanges for access token."""
    try:
        client = ETradeClient()
        access_token, _ = client.get_access_token(oauth_token, oauth_verifier)
        return {"ok": True, "access_token_set": bool(access_token)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# OOB/manual auth completion endpoint
@router.post("/auth/complete")
def auth_complete(payload: dict = Body(...)):
    """Complete OAuth for OOB/manual flows by exchanging oauth_verifier for access token.
    Expected JSON:
    {
      "oauth_token": "...",
      "oauth_verifier": "..."
    }
    """
    try:
        oauth_token = payload.get("oauth_token")
        oauth_verifier = payload.get("oauth_verifier")
        if not oauth_token or not oauth_verifier:
            raise HTTPException(status_code=422, detail="oauth_token and oauth_verifier are required")
        client = ETradeClient()
        access_token, _ = client.get_access_token(oauth_token, oauth_verifier)
        return {"ok": True, "access_token_set": bool(access_token)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/tokens")
def logout():
    """Clear locally stored E*TRADE OAuth tokens (sign out locally)."""
    try:
        token_clear()
        return {"ok": True, "tokens_cleared": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/accounts")
def accounts():
    try:
        client = ETradeClient()
        data = client.list_accounts()
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/portfolio")
def portfolio(
    accountIdKey: str = Query(...),
    view: Optional[str] = Query(None),
    count: Optional[int] = Query(None),
    totalsRequired: Optional[bool] = Query(None),
    lotsRequired: Optional[bool] = Query(None),
    marketSession: Optional[str] = Query(None),
):
    try:
        client = ETradeClient()
        data = client.get_portfolio(
            account_id_key=accountIdKey,
            view=view,
            count=count,
            totals_required=totalsRequired,
            lots_required=lotsRequired,
            market_session=marketSession,
        )
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
