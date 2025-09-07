from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/v1/portfolio", tags=["portfolio"])

class PositionsResp(BaseModel):
    positions: list[dict]

@router.get("/positions", response_model=PositionsResp)
def positions(account_id: str):
    return {"positions": [{"symbol": "AAPL", "qty": 10}, {"symbol": "MSFT", "qty": 5}]}
