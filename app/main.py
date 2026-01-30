"""
API REST para RAG com Agno, Groq e Qdrant
"""

from fastapi import FastAPI

from routers import chat_router, knowledge_router
from utils.llm import LLMConfig
from utils.vector_db import vector_db

app = FastAPI(
    title="Agno RAG API",
    description="API para chat com RAG usando Agno, Groq e Qdrant",
    version="1.0.0"
)

app.include_router(chat_router.router)
app.include_router(knowledge_router.router)


@app.get("/models")
async def list_models():
    """
    Lista modelos disponíveis
    """
    return {
        "models": LLMConfig.list_models(),
        "default": "llama-3.3-70b"
    }


@app.get("/")
async def health_check():
    """
    Health check da API
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "knowledge_base": "ready"
    }

@app.on_event("startup")
async def startup_event():
    """
    Inicializa a aplicação
    """
    print("🚀 Iniciando Agno RAG API...")
    print(f"📚 Collection: {vector_db.collection}")
    print(f"🤖 Modelos disponíveis: {list(LLMConfig.MODELS.keys())}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
