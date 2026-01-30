from httpx import AsyncClient
from utils.settings import settings
from app.schamas.bi_schemas import BIRequest, BIResponse


wren_client: AsyncClient = None

async def bi_query(request: BIRequest) -> BIResponse:
    """Wren Engine: intent → SQL → executa no DB"""
    global wren_client
    if wren_client is None:
        wren_client = AsyncClient(base_url=settings.wren_url)
    resp = await wren_client.post("/mcp/sql", json={"intent": request.message})
    data = resp.json()
    return BIResponse(
        sql=data["sql"],
        result=data["result"],
        chart_prompt=f"Formate estes dados BI: {data['result']}"
    )
