"""
Controllers para operações de chat
"""

from agno.agent import Agent

from schamas.chat_schemas import ChatRequest, ChatResponse
from utils.knowledge import knowledge
from utils.llm import LLMConfig
from utils.settings import settings

# Agent global
_agent = None


def get_agent(model_name: str = "llama-3.3-70b") -> Agent:
    """Retorna ou cria agent com modelo especificado"""
    global _agent
    
    llm = LLMConfig.get_model(model_name)
    
    _agent = Agent(
        model=llm,
        knowledge=knowledge,
        description="Você é um assistente que SEMPRE consulta a base de conhecimento sobre a plataforma Redu antes de responder.",
        instructions=[
            "OBRIGATÓRIO: Use a função search_knowledge_base para buscar informações antes de qualquer resposta",
            "NUNCA responda sem antes buscar na base de conhecimento",
            "Baseie suas respostas APENAS nas informações encontradas na busca",
            "Se a busca não retornar resultados relevantes, informe que não encontrou informações sobre o assunto",
            "Cite as fontes encontradas na sua resposta",
        ],
        markdown=True,
        search_knowledge=True,
        read_chat_history=True,  # Mantém contexto da conversa
        debug_mode=settings.debug_mode,
    )
    
    return _agent


async def chat_with_agent(request: ChatRequest) -> ChatResponse:
    """
    Processa mensagem de chat com o agent
    
    Args:
        request: Requisição com mensagem e configurações
        
    Returns:
        ChatResponse com resposta do agent
    """
    agent = get_agent(request.model)
    
    if request.stream:
        # TODO: Implementar streaming adequado
        response = agent.run(request.message)
    else:
        response = agent.run(request.message)
    
    return ChatResponse(
        response=response.content if hasattr(response, 'content') else str(response),
        model=request.model
    )


def chat_stream_generator(request: ChatRequest):
    """
    Gera chunks de resposta para streaming
    
    Args:
        request: Requisição com mensagem e configurações
        
    Yields:
        Chunks de resposta do agent
    """
    agent = get_agent(request.model)
    
    for chunk in agent.run(request.message, stream=True):
        if hasattr(chunk, 'content'):
            yield chunk.content
        else:
            yield str(chunk)
