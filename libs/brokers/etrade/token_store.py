

"""Simple JSON token store for E*TRADE OAuth tokens.
Stored locally at secrets/etrade_token.json (git-ignored).
"""
from __future__ import annotations
import json
import os
import threading
from typing import Optional, Dict

_LOCK = threading.RLock()
_DEFAULT_PATH = os.path.join("secrets", "etrade_token.json")

def _ensure_dir(path: str) -> None:
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)

def load(path: str = _DEFAULT_PATH) -> Optional[Dict[str, str]]:
    with _LOCK:
        if not os.path.isfile(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                return None
            return {
                k: v for k, v in data.items()
                if k in {"oauth_token", "oauth_token_secret", "access_token", "access_token_secret"}
            }
        except Exception:
            return None

def save(tokens: Dict[str, str], path: str = _DEFAULT_PATH) -> None:
    with _LOCK:
        _ensure_dir(path)
        safe = {
            k: tokens.get(k, "")
            for k in ["oauth_token", "oauth_token_secret", "access_token", "access_token_secret"]
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(safe, f, indent=2)

def clear(path: str = _DEFAULT_PATH) -> None:
    with _LOCK:
        try:
            if os.path.isfile(path):
                os.remove(path)
        except Exception:
            pass
