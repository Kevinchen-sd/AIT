#!/usr/bin/env zsh
# Automate E*TRADE OAuth 1.0a OOB flow against your local API.
# Requirements:
#   - FastAPI running locally (make api)
#   - .env has ETRADE_CALLBACK_URL=oob (and keys)
#   - curl and python available

set -euo pipefail

API_BASE="${API_BASE:-http://localhost:8000}"
AUTH_START_ENDPOINT="$API_BASE/v1/brokers/etrade/auth/start"
AUTH_COMPLETE_ENDPOINT="$API_BASE/v1/brokers/etrade/auth/complete"
ACCOUNTS_ENDPOINT="$API_BASE/v1/brokers/etrade/accounts"

echo "→ Requesting new request token from: $AUTH_START_ENDPOINT"
START_JSON="$(curl -sf "$AUTH_START_ENDPOINT")" || {
  echo "❌ Failed to contact $AUTH_START_ENDPOINT. Is your API running?"; exit 1
}

# Use python to extract fields from JSON (no jq; pass via env)
START_JSON_ESC="$START_JSON"
START_JSON=""  # avoid leaking big JSON via env further down
AUTHORIZE_URL="$(
  START_JSON="$START_JSON_ESC" python - <<'PY' 2>/dev/null || true
import os, json
try:
    data = json.loads(os.environ["START_JSON"])
    print(data.get("authorize_url",""))
except Exception:
    pass
PY
)"
OAUTH_TOKEN="$(
  START_JSON="$START_JSON_ESC" python - <<'PY' 2>/dev/null || true
import os, json
try:
    data = json.loads(os.environ["START_JSON"])
    print(data.get("oauth_token",""))
except Exception:
    pass
PY
)"
unset START_JSON_ESC

if [[ -z "$AUTHORIZE_URL" || -z "$OAUTH_TOKEN" ]]; then
  echo "❌ Could not parse authorize_url or oauth_token from response:"
  echo "$START_JSON"
  exit 1
fi

echo
echo "✅ Received request token."
echo "oauth_token: $OAUTH_TOKEN"
echo
echo "Open this URL to authorize the app (log in, approve, copy the verification code):"
echo "$AUTHORIZE_URL"
# Try to open a browser (macOS 'open', otherwise just print the URL)
if command -v open >/dev/null 2>&1; then
  open "$AUTHORIZE_URL" || true
fi

echo
if [[ ! -t 0 ]]; then
  echo "❌ This script needs an interactive terminal to read the verification code." >&2
  exit 1
fi
read -r "OAUTH_VERIFIER?Paste the verification code (oauth_verifier) here: "

# Build JSON payload safely (export env before python so it can read OT/OV)
PAYLOAD="$(
  OT="$OAUTH_TOKEN" OV="$OAUTH_VERIFIER" python - <<'PY'
import json, os
print(json.dumps({"oauth_token": os.environ["OT"], "oauth_verifier": os.environ["OV"]}))
PY
)"

echo
echo "→ Exchanging verifier for access token at: $AUTH_COMPLETE_ENDPOINT"
COMPLETE_JSON="$(curl -sf -H "Content-Type: application/json" -X POST \
  --data-binary "$PAYLOAD" "$AUTH_COMPLETE_ENDPOINT")" || {
  echo "❌ Exchange failed. Raw response:"
  curl -sv -H "Content-Type: application/json" -X POST --data-binary "$PAYLOAD" "$AUTH_COMPLETE_ENDPOINT" || true
  exit 1
}

echo "✅ Exchange response:"
echo "$COMPLETE_JSON"

# Post-auth: list accounts, prompt, then fetch portfolio
echo
echo "→ Fetching /accounts"
if ACCOUNTS_JSON="$(curl -sf "$ACCOUNTS_ENDPOINT")"; then
  echo "✅ Accounts received."
  echo
  echo "Available accounts:"
  ACC_LIST="$(
    ACCOUNTS_JSON="$ACCOUNTS_JSON" python - <<'PY' 2>/dev/null || true
import os, json
try:
    data = json.loads(os.environ["ACCOUNTS_JSON"]) or {}
    # Try typical E*TRADE accounts JSON shapes
    accounts = []
    # shape 1: {"AccountListResponse": {"Accounts": {"Account": [ ... ]}}}
    acct = (
        data.get("AccountListResponse", {})
            .get("Accounts", {})
            .get("Account", [])
    )
    if isinstance(acct, dict):
        acct = [acct]
    if not acct:
        # shape 2: flatten anything that looks like accounts
        for k, v in data.items():
            if isinstance(v, dict) and "Account" in v:
                item = v["Account"]
                if isinstance(item, list):
                    acct.extend(item)
                elif isinstance(item, dict):
                    acct.append(item)
    idx = 0
    lines = []
    for a in acct:
        key = a.get("accountIdKey") or a.get("accountId") or a.get("accountKey") or ""
        if not key:
            continue
        name = a.get("accountDesc") or a.get("accountName") or a.get("nickname") or ""
        typ = a.get("accountType") or a.get("type") or ""
        lines.append(f"{idx}|{key}|{name or 'Account'}|{typ}")
        idx += 1
    print("\n".join(lines))
except Exception:
    pass
PY
  )"

  if [[ -z "$ACC_LIST" ]]; then
    echo "⚠️  Could not parse account list. Raw response (truncated):"
    echo "$ACCOUNTS_JSON" | python - <<'PY' 2>/dev/null | sed -e 's/[[:cntrl:]]//g'
import sys, json
try:
    data=json.load(sys.stdin)
    out=json.dumps(data)[:800]
    print(out + ('…' if len(json.dumps(data))>800 else ''))
except Exception:
    print(sys.stdin.read()[:800])
PY
    echo "You can still call the portfolio endpoint manually with accountIdKey."
    echo "Done."
    exit 0
  fi

  echo "$ACC_LIST" | nl -ba -w2 -s'. '
  echo
  read -r "ACC_CHOICE?Enter the index number to fetch portfolio (or paste an accountIdKey): "

  # Determine chosen key
  CHOSEN_KEY=""
  if [[ "$ACC_CHOICE" =~ '^[0-9]+$' ]]; then
    # map index to key
    CHOSEN_KEY="$(
      printf '%s\n' "$ACC_LIST" | awk -v idx="$ACC_CHOICE" -F'|' 'NR==idx+1 {print $2}'
    )"
  else
    CHOSEN_KEY="$ACC_CHOICE"
  fi

  if [[ -z "$CHOSEN_KEY" ]]; then
    echo "❌ No accountIdKey selected. Exiting."
    exit 1
  fi

  PORTFOLIO_ENDPOINT="$API_BASE/v1/brokers/etrade/portfolio?accountIdKey=$CHOSEN_KEY"
  echo
  echo "→ Fetching portfolio for accountIdKey=$CHOSEN_KEY"
  if PORT_JSON="$(curl -sf "$PORTFOLIO_ENDPOINT")"; then
    echo "✅ Portfolio (truncated pretty JSON):"
    echo "$PORT_JSON" | python - <<'PY' 2>/dev/null | sed -e 's/[[:cntrl:]]//g'
import sys, json
try:
    data=json.load(sys.stdin)
    out=json.dumps(data, indent=2)
    print(out[:2000] + ('\n…(truncated)…' if len(out)>2000 else ''))
except Exception:
    print(sys.stdin.read()[:2000])
PY
  else
    echo "⚠️  Failed to fetch portfolio at: $PORTFOLIO_ENDPOINT"
  fi
else
  echo "⚠️  /accounts call failed. Tokens may not be stored yet, or E*TRADE sandbox is hiccuping."
fi

echo
echo "Done."
