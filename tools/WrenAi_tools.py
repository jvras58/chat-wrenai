from agno.tools import tool
from app.controllers.wrenai_controller import bi_query
from app.schamas.bi_schemas import BIRequest

@tool
async def bi_query_tool(intent: str, db_source: str = "default") -> str:
    """Gera/executa SQL BI via Wren Engine"""
    result = await bi_query(BIRequest(message=intent, db_source=db_source))
    return f"SQL: {result.sql}\nResultado: {result.result}"
