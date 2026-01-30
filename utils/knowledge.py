"""
Configuração da Knowledge Base
"""

from agno.knowledge.knowledge import Knowledge

from utils.vector_db import vector_db


def get_knowledge() -> Knowledge:
    """
    Retorna instância configurada da Knowledge Base
    
    Returns:
        Instância de Knowledge conectada ao vector_db
    """
    return Knowledge(vector_db=vector_db)


# Instância singleton da knowledge base
knowledge = get_knowledge()
