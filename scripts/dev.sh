#!/usr/bin/env bash
# scripts/dev.sh - one-command dev runner (backend + frontend)
# Usage:
#   ./scripts/dev.sh          # mock ingest (default)
#   ./scripts/dev.sh --real   # real Norgate ingest (needs NORGATE_DB_PATH)
#
# Flags:
#   --real        Use real ingest (pipelines/ingest_norgate.py) instead of mock
#   --no-open     Do not auto-open Swagger UI
#   --api-port N  Override API port (default 8000)
#   --ui-port N   Override Vite port (default 5173)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
BACKEND_DIR="$REPO_ROOT/apps/backend"
FRONTEND_DIR="$REPO_ROOT/apps/frontend"
ENV_NAME="vectorbtpro"
API_PORT=8000
UI_PORT=5173
OPEN_DOCS=true
USE_REAL=false

# ---- parse args ----
while [[ $# -gt 0 ]]; do
  case "$1" in
    --real) USE_REAL=true; shift ;;
    --no-open) OPEN_DOCS=false; shift ;;
    --api-port) API_PORT="${2:-8000}"; shift 2 ;;
    --ui-port) UI_PORT="${2:-5173}"; shift 2 ;;
    *) echo "[dev] Unknown arg: $1"; exit 1 ;;
  esac
done

log() { printf "\033[1;36m[dev]\033[0m %s\n" "$*"; }
err() { printf "\033[1;31m[dev]\033[0m %s\n" "$*" >&2; }

# ---- conda env handling ----
need_activate=true
if [[ "${CONDA_DEFAULT_ENV-}" == "$ENV_NAME" ]]; then
  need_activate=false
fi

if $need_activate; then
  if command -v conda >/dev/null 2>&1; then
    # shellcheck disable=SC1091
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate "$ENV_NAME" || {
      err "Conda env '$ENV_NAME' not found. Create it first: conda env create -f environment.yml"
      exit 1
    }
    log "Activated conda env: $ENV_NAME"
  else
    err "conda not found on PATH. Open a shell where 'conda' is available or activate the env manually."
    exit 1
  fi
else
  log "Conda env already active: $ENV_NAME"
fi

# ---- sanity checks ----
command -v uvicorn >/dev/null || { err "uvicorn not found. Run: pip install -e '.[app]'"; exit 1; }
command -v npm >/dev/null || { err "npm not found. Install Node.js (>=18)."; exit 1; }

# ---- ensure data ----
if $USE_REAL; then
  if [[ -z "${NORGATE_DB_PATH-}" ]]; then
    err "--real requested but NORGATE_DB_PATH is not set in environment (see .env)."
    exit 1
  fi
  log "Using REAL ingest (Norgate)."
  ( cd "$REPO_ROOT" && make ingest features scores )
else
  log "Using MOCK ingest."
  ( cd "$REPO_ROOT" && make mock-ingest features scores )
fi

# ---- start backend ----
log "Starting backend (FastAPI on :$API_PORT)"
( cd "$REPO_ROOT" && python -m uvicorn apps.backend.main:app --reload --host 0.0.0.0 --port "$API_PORT" ) &
BACK_PID=$!

cleanup() {
  log "Stopping backend (pid $BACK_PID)"
  kill "$BACK_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Optional: open docs after backend warms up
if $OPEN_DOCS; then
  ( sleep 1; if command -v open >/dev/null; then open "http://localhost:${API_PORT}/docs"; fi ) &
fi

# ---- start frontend ----
log "Starting frontend (Vite on :$UI_PORT)"
cd "$FRONTEND_DIR"
if [[ ! -d node_modules ]]; then
  log "Installing frontend deps (npm install)"
  npm install
fi

# Pass the desired port to Vite (works with vite >=3)
npm run dev -- --port "$UI_PORT"
