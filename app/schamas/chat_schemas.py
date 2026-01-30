"""
Modelos Pydantic para validação de dados da API - Chat
"""

from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request para chat"""
    message: str = Field(..., description="Mensagem do usuário", min_length=1)
    model: Optional[str] = Field(
        default="llama-3.3-70b",
        description="Modelo a ser usado"
    )
    stream: bool = Field(default=False, description="Retornar resposta em streaming")


class ChatResponse(BaseModel):
    """Response do chat"""
    response: str
    model: str
