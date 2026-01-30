"""
Rotas para operações de knowledge base
"""

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from controllers.knowledge_controller import (
    add_json_to_knowledge,
    add_pdf_to_knowledge,
    add_url_to_knowledge,
    clear_knowledge_base,
    list_documents,
    search_documents,
)
from controllers.knowledge_controller import get_knowledge_status as get_status
from schamas.document_schemas import (
    AddContentResponse,
    AddURLRequest,
    KnowledgeStatusResponse,
    ListDocumentsResponse,
    SearchRequest,
)

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.post("/add/url", response_model=AddContentResponse)
async def add_url_content(request: AddURLRequest):
    """
    Adiciona conteúdo de uma URL à base de conhecimento
    """
    try:
        return await add_url_to_knowledge(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar URL: {str(e)}")


@router.post("/add/json", response_model=AddContentResponse)
async def add_json_content(file: UploadFile = File(...)):
    """
    Adiciona conteúdo de um arquivo JSON à base de conhecimento
    """
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser JSON")
    
    try:
        return await add_json_to_knowledge(file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar JSON: {str(e)}")


@router.post("/add/pdf", response_model=AddContentResponse)
async def add_pdf_content(file: UploadFile = File(...)):
    """
    Adiciona conteúdo de um arquivo PDF à base de conhecimento
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser PDF")
    
    try:
        return await add_pdf_to_knowledge(file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar PDF: {str(e)}")


@router.get("/status", response_model=KnowledgeStatusResponse)
async def get_knowledge_status():
    """
    Retorna status da base de conhecimento
    """
    try:
        return get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter status: {str(e)}")


@router.delete("/clear")
async def clear_knowledge():
    """
    Limpa toda a base de conhecimento
    """
    try:
        return clear_knowledge_base()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao limpar knowledge: {str(e)}")


@router.get("/documents", response_model=ListDocumentsResponse)
async def get_documents(
    limit: int = Query(default=10, ge=1, le=100, description="Número de documentos a retornar"),
    offset: int = Query(default=0, ge=0, description="Número de documentos a pular")
):
    """
    Lista os documentos armazenados na base de conhecimento
    """
    try:
        return list_documents(limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar documentos: {str(e)}")


@router.post("/search", response_model=ListDocumentsResponse)
async def search_knowledge(request: SearchRequest):
    """
    Busca documentos por similaridade semântica
    """
    try:
        return search_documents(query=request.query, limit=request.limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar documentos: {str(e)}")
