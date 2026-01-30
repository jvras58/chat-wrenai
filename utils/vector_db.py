"""
Configuração do Vector Database (Qdrant)
"""

from agno.knowledge.embedder.fastembed import FastEmbedEmbedder
from agno.vectordb.qdrant import Qdrant

from utils.settings import settings


def get_vector_db() -> Qdrant:
    """
    Retorna instância configurada do Qdrant Vector DB
    
    Returns:
        Instância configurada de Qdrant
    """
    return Qdrant(
        collection=settings.vector_db_collection,
        url=settings.vector_db_url,
        embedder=FastEmbedEmbedder(
            id=settings.embedder_model,
            dimensions=settings.embedder_dimensions,
        ),
    )


# Instância singleton do vector DB
vector_db = get_vector_db()
