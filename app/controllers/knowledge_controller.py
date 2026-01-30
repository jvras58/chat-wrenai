"""
Controllers para operações de knowledge base
"""

import os
import tempfile

from agno.knowledge.chunking.recursive import RecursiveChunking
from agno.knowledge.reader.json_reader import JSONReader
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.knowledge.reader.website_reader import WebsiteReader
from fastapi import UploadFile

from app.schamas.document_schemas import (
    AddContentResponse,
    AddURLRequest,
    DocumentItem,
    KnowledgeStatusResponse,
    ListDocumentsResponse,
)
from utils.knowledge import knowledge
from utils.settings import settings
from utils.vector_db import vector_db


async def add_url_to_knowledge(request: AddURLRequest) -> AddContentResponse:
    """
    Adiciona conteúdo de uma URL à base de conhecimento
    
    Args:
        request: Requisição com URL e configurações
        
    Returns:
        AddContentResponse com status da operação
    """
    reader = WebsiteReader(
        max_depth=request.max_depth,
        max_links=request.max_links,
        chunking_strategy=RecursiveChunking(chunk_size=1000, overlap=100)
    )

    await knowledge.add_content_async(
        url=str(request.url),
        reader=reader
        
    )
    
    return AddContentResponse(
        success=True,
        message="URL adicionada com sucesso",
        content_type="url",
        details={
            "url": str(request.url),
            "max_depth": request.max_depth,
            "max_links": request.max_links
        }
    )


async def add_json_to_knowledge(file: UploadFile) -> AddContentResponse:
    """
    Adiciona conteúdo de um arquivo JSON à base de conhecimento
    
    Args:
        file: Arquivo JSON enviado
        
    Returns:
        AddContentResponse com status da operação
    """
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Configuração otimizada para chunks menores e mais focados
        reader = JSONReader(
            chunking_strategy=RecursiveChunking(
                chunk_size=settings.json_chunk_size,  # Chunks menores para dados estruturados
                overlap=settings.json_overlap,  # Overlap menor
            )
        )
        await knowledge.add_content_async(
            path=tmp_path,
            reader=reader
        )
        
        
        return AddContentResponse(
            success=True,
            message="Arquivo JSON adicionado com sucesso",
            content_type="json",
            details={"filename": file.filename}
        )
    
    finally:
        # Remove arquivo temporário
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


async def add_pdf_to_knowledge(file: UploadFile) -> AddContentResponse:
    """
    Adiciona conteúdo de um arquivo PDF à base de conhecimento
    
    Args:
        file: Arquivo PDF enviado
        
    Returns:
        AddContentResponse com status da operação
    """
    tmp_path = None
    try:
        # Salva arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Adiciona ao knowledge
        reader = PDFReader(
        chunking_strategy=RecursiveChunking()     
        )

        await knowledge.add_content_async(
            path=tmp_path,
            reader=reader
        )
        
        return AddContentResponse(
            success=True,
            message="Arquivo PDF adicionado com sucesso",
            content_type="pdf",
            details={"filename": file.filename}
        )
    
    finally:
        # Remove arquivo temporário
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


def get_knowledge_status() -> KnowledgeStatusResponse:
    """
    Retorna status da base de conhecimento
    
    Returns:
        KnowledgeStatusResponse com informações da base
    """
    # Tenta obter informações do vector DB
    collection_info = vector_db.client.get_collection(vector_db.collection)
    # print(collection_info)
    print(vector_db.collection)
    
    return KnowledgeStatusResponse(
        total_documents=collection_info.points_count,
        collection_name=vector_db.collection,
        embedder_model=settings.embedder_model,
    )


def clear_knowledge_base() -> dict:
    """
    Limpa toda a base de conhecimento
    
    Returns:
        Dict com status da operação
    """
    vector_db.client.delete_collection(vector_db.collection)
    
    # Recria a coleção
    vector_db.client.create_collection(
        collection_name=vector_db.collection,
        vectors_config={"size": 384, "distance": "Cosine"}
    )
    
    return {"success": True, "message": "Base de conhecimento limpa"}


def list_documents(limit: int = 10, offset: int = 0) -> ListDocumentsResponse:
    """
    Lista documentos armazenados na base de conhecimento
    
    Args:
        limit: Número máximo de documentos a retornar
        offset: Número de documentos a pular
        
    Returns:
        ListDocumentsResponse com lista de documentos
    """
    # Obtém informações da coleção
    collection_info = vector_db.client.get_collection(vector_db.collection)
    total = collection_info.points_count
    
    # Busca documentos
    scroll_result = vector_db.client.scroll(
        collection_name=vector_db.collection,
        limit=limit,
        offset=offset,
        with_payload=True,
        with_vectors=False
    )
    
    points = scroll_result[0]  # scroll retorna (points, next_page_offset)
    
    documents = []
    for point in points:
        doc = DocumentItem(
            id=str(point.id),
            content=point.payload.get("content", ""),
            metadata={k: v for k, v in point.payload.items() if k != "content"}
        )
        documents.append(doc)
    
    return ListDocumentsResponse(
        total=total,
        limit=limit,
        offset=offset,
        documents=documents
    )


def search_documents(query: str, limit: int = 5) -> ListDocumentsResponse:
    """
    Busca documentos por similaridade semântica
    
    Args:
        query: Texto de busca
        limit: Número máximo de resultados
        
    Returns:
        ListDocumentsResponse com documentos mais similares
    """
    # Usa o knowledge para buscar (max_results é o parâmetro correto)
    results = knowledge.search(query=query, max_results=limit)
    
    documents = []
    for result in results:
        # Gera um ID baseado no hash do conteúdo se não houver ID
        doc_id = result.id if hasattr(result, 'id') and result.id else str(abs(hash(result.content)))
        
        doc = DocumentItem(
            id=doc_id,
            content=result.content,
            metadata=result.meta_data if hasattr(result, 'meta_data') else {},
            score=result.score if hasattr(result, 'score') else None
        )
        documents.append(doc)
    
    return ListDocumentsResponse(
        total=len(documents),
        limit=limit,
        offset=0,
        documents=documents
    )
