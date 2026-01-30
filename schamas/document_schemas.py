"""
Modelos Pydantic para validação de dados da API - Documentos e Knowledge Base
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class ContentTypeEnum(str, Enum):
    """Tipos de conteúdo suportados"""
    URL = "url"
    JSON = "json"
    PDF = "pdf"


class AddURLRequest(BaseModel):
    """Request para adicionar URL"""
    url: HttpUrl = Field(..., description="URL do website")
    max_depth: int = Field(default=1, ge=0, le=5, description="Profundidade máxima de crawling")
    max_links: int = Field(default=10, ge=1, le=100, description="Número máximo de links")


class AddContentResponse(BaseModel):
    """Response padrão para adição de conteúdo"""
    success: bool
    message: str
    content_type: str
    details: Optional[dict] = None


class KnowledgeStatusResponse(BaseModel):
    """Status da base de conhecimento"""
    total_documents: int
    collection_name: str
    embedder_model: str


class DocumentItem(BaseModel):
    """Item de documento retornado"""
    id: str = Field(..., description="ID do documento")
    content: str = Field(..., description="Conteúdo do documento")
    metadata: dict = Field(default_factory=dict, description="Metadados do documento")
    score: Optional[float] = Field(None, description="Score de similaridade (se aplicável)")


class ListDocumentsResponse(BaseModel):
    """Response para listagem de documentos"""
    total: int
    limit: int
    offset: int
    documents: list[DocumentItem]


class SearchRequest(BaseModel):
    """Request para busca no knowledge base"""
    query: str = Field(..., description="Texto de busca", min_length=1)
    limit: int = Field(default=5, ge=1, le=50, description="Número máximo de resultados")
