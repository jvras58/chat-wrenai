"""
Rotas para operações de chat
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from controllers.chat_controller import chat_stream_generator, chat_with_agent
from schamas.chat_schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint para chat com o agent
    """
    try:
        return await chat_with_agent(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no chat: {str(e)}")


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    Endpoint para chat com streaming
    """
    try:
        return StreamingResponse(
            chat_stream_generator(request),
            media_type="text/plain"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no streaming: {str(e)}")
