from pydantic import BaseModel

class BIRequest(BaseModel):
    """Pedido de consulta BI. """
    message: str  # "Vendas Q4 por região"
    db_source: str  # "postgres_sales"

class BIResponse(BaseModel):
    """Resposta da consulta BI."""
    sql: str
    result: dict
    chart_prompt: str  # Para LLM gerar tabela
