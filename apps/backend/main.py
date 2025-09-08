# apps/backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.backend.services.analysis_svc.api import router as analysis_router
from apps.backend.services.marketdata_svc.api import router as marketdata_router
from apps.backend.services.portfolio_svc.stubs import router as portfolio_router
from apps.backend.services.etrade_api import router as etrade_router
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="AI Trading MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

app.include_router(analysis_router)
app.include_router(marketdata_router)
app.include_router(portfolio_router)
app.include_router(etrade_router)

@app.get("/health")
def health():
    return {"ok": True}
