
from fastapi import APIRouter
from app.controllers.wrenai_controller import bi_query
from app.schamas.bi_schemas import BIRequest, BIResponse

router = APIRouter(prefix="/bi", tags=["bi"])

@router.post("/query", response_model=BIResponse)
async def wren_query(request: BIRequest):
    """Consulta BI via Wren AI Engine"""
    return await bi_query(request)
