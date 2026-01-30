"""
utils/llm.py - Configuração do LLM com Groq
"""

from agno.models.groq import Groq
from utils.settings import settings


def get_groq_llm(model_id: str = None) -> Groq:
    """
    Retorna uma instância configurada do modelo Groq

    Args:
        model_id: ID do modelo (usa default_model de settings se não especificado)

    Returns:
        Instância configurada de Groq
    """
    model = model_id or settings.default_model

    return Groq(id=model, api_key=settings.groq_api_key)


class LLMConfig:
    """
    Classe de configuração centralizada para LLM
    """

    # Modelos disponíveis
    MODELS = {
        "llama-3.3-70b": "llama-3.3-70b-versatile",
        "llama-3.1-70b": "llama-3.1-70b-versatile",
        "llama-3.1-8b": "llama-3.1-8b-instant",
        "mixtral-8x7b": "mixtral-8x7b-32768",
    }

    @staticmethod
    def get_model(model_name: str = "llama-3.3-70b") -> Groq:
        """
        Retorna modelo pelo nome amigável

        Args:
            model_name: Nome amigável do modelo

        Returns:
            Instância de Groq configurada
        """
        model_id = LLMConfig.MODELS.get(model_name, settings.default_model)
        return get_groq_llm(model_id)

    @staticmethod
    def list_models() -> dict:
        """
        Lista modelos disponíveis

        Returns:
            Dicionário com modelos disponíveis
        """
        return LLMConfig.MODELS
