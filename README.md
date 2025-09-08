# AI Trading MVP

Minimal end-to-end system for portfolio analysis and trading insights.
Built with **Python (FastAPI, pipelines, vectorbtpro, YAML model registry)** and **React (Vite, TypeScript)**.
Runs without Docker (Mode A: conda + local files).

---

## 🚀 Environment Setup

1. **Conda**
   ```bash
   conda create -n vectorbtpro python=3.11
   conda activate vectorbtpro
   conda env update -f environment.yml
   ```
   > Also install your private `vectorbtpro` package into this env.

2. **.env**
   ```ini
   ENV=dev
   DATABASE_URL=sqlite:///./data/app.db
   REDIS_URL=disabled
   NORGATE_DB_PATH=/path/to/Norgate/Database   # leave blank until subscribed
   ```

3. **VS Code**
   - Select interpreter: `vectorbtpro`
   - Use `.vscode/settings.json` (ruff, pytest on save)
   - Uvicorn launch config in `.vscode/launch.json`

---

## 📂 Directory Structure

```
/Users/kevin/projects/AIT/
├─ .env
├─ Makefile
├─ environment.yml
├─ pyproject.toml
├─ scripts/
│  └─ dev.sh               # one-command dev runner (backend+frontend)
├─ apps/
│  ├─ backend/              # FastAPI app
│  │  ├─ main.py
│  │  └─ services/
│  │     ├─ analysis_svc/api.py
│  │     ├─ marketdata_svc/api.py  # includes bars_from_silver
│  │     └─ portfolio_svc/stubs.py
│  └─ frontend/             # React + Vite
│     ├─ index.html
│     ├─ vite.config.mts
│     ├─ package.json       # includes "type": "module"
│     └─ src/
│        ├─ main.tsx
│        ├─ pages/Insights.tsx
│        ├─ components/{InsightBadge.tsx,InsightCard.tsx,Sparkline.tsx}
│        └─ types.ts
├─ libs/                    # shared libraries
│  └─ md/norgate/client.py
├─ ml/                      # models + registry
│  ├─ strategies/{momo_trend.py,holdings_review.py}
│  └─ registry/{loader.py,momo_trend.yaml}
├─ pipelines/               # ETL + scoring
│  ├─ mock_ingest.py        # synthetic OHLCV generator
│  ├─ ingest_norgate.py     # real Norgate ingest (later)
│  ├─ build_features.py
│  ├─ daily_scores.py
│  └─ backtest_job.py       # placeholder
├─ tests/
│  ├─ data/
│  ├─ prepare_golden.py
│  └─ test_momo_trend_golden.py
└─ data/                    # runtime artifacts
   ├─ silver/ohlcv.parquet
   └─ gold/scores_latest.parquet
```

---

## 🛠️ Runbook

### One-command dev (recommended)
We added a helper script and Makefile targets to spin up everything:

```bash
# default: mock ingest → backend :8000 + frontend :5173
make dev

# real ingest (requires NORGATE_DB_PATH in .env)
make dev-real

# mock ingest but skip auto-opening Swagger UI
make dev-no-open
```

### Backend only
```bash
conda activate vectorbtpro
make install
make mock-ingest       # synthetic OHLCV
make features
make scores
make api               # FastAPI → http://localhost:8000
```

Test:
```bash
curl -X POST http://localhost:8000/v1/analysis/portfolio/keep_or_replace   -H "Content-Type: application/json"   -d '{"account_id":"demo","symbols":["AAPL","MSFT","AMZN","TSLA"],"benchmark":"SPY","strategy":"momo_trend@0.1.0"}'
```

### Frontend only
```bash
cd apps/frontend
npm install        # first time only
npm run dev        # Vite → http://localhost:5173
```

Then open the app, type tickers like:
```
AAPL,MSFT,AMZN,TSLA
```
Click **Analyze** → you’ll see Keep/Watch/Replace + sparklines.

---

## ✅ Features in MVP

- **YAML model registry** (`ml/registry/*.yaml`)
- **Momentum + trend strategy** (`momo_trend`)
- **Holdings review heuristic**
- **Synthetic OHLCV ingestion** (mock data, no Norgate needed)
- **FastAPI backend** with:
  - `/v1/analysis/portfolio/keep_or_replace`
  - `/v1/md/bars_from_silver` (sparklines from parquet)
- **Frontend** with Insights page, cards, and sparklines (via proxy to API)

---

## ⚠️ Gotchas (and fixes)

- **Conda vs. venv**:
  Makefile is conda-friendly. No `.venv` needed.
- **Python imports**:
  Added `__init__.py` and use `python -m pipelines.mock_ingest` so `libs`/`ml` resolve.
- **YAML vs. Python**:
  Keep YAML config in `.yaml` files, not in `.py`.
- **Frontend entry**:
  `index.html` must live in `apps/frontend/` root.
- **Vite proxy**:
  Config is `vite.config.mts` with `"type": "module"` in `package.json`.
  Ensures `/v1/...` fetches go to FastAPI (`:8000`).
- **Sparklines before Norgate**:
  Use `/v1/md/bars_from_silver` endpoint reading your parquet.

---

## 🩺 Health & Status

Two lightweight endpoints are provided for monitoring and dev scripts:

- **GET `/healthz`** → returns 200 when API is up (liveness).
- **GET `/readyz`** → checks that required files exist (e.g., `data/silver/` and `data/gold/`) and returns 200 when ready.

These help `scripts/dev.sh` (and future deploys) wait for the backend before opening the UI.

---

## 🔮 Next Steps

- Swap mock ingest with **real Norgate** (`make ingest` or `make dev-real`).
- Wire up **E*TRADE positions** (replace stub with OAuth 1.0a).
- Add **backtest endpoint** using vectorbtpro.
- Add **constituents_from_silver** for a symbol dropdown.
- Persist results/users (SQLite now, Postgres later).

---

## 🧰 Troubleshooting

| Symptom                                   | Likely cause                                | Fix                                  |
|-------------------------------------------|---------------------------------------------|--------------------------------------|
| `ModuleNotFoundError: libs`               | missing `__init__.py` or wrong run style    | run modules with `-m`, add `__init__`|
| `SyntaxError: version: 0.1.0`             | YAML pasted into `.py`                      | keep YAML in `.yaml` only            |
| Frontend 404 on `/v1/...`                 | no proxy, hitting Vite server instead       | add `vite.config.mts` or use abs URL |
| Vite error about ESM plugin               | `vite.config.ts` using CJS                  | rename → `vite.config.mts`, set `"type": "module"` |
| Sparklines blank                          | no Norgate, no fallback                     | use `/v1/md/bars_from_silver`        |

---

## 📜 License

Private MVP, © you.
