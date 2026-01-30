"""
Controllers para operações de chat
"""

from agno.agent import Agent

from app.schamas.chat_schemas import ChatRequest, ChatResponse
from utils.knowledge import knowledge
from utils.llm import LLMConfig
from utils.settings import settings
from tools.WrenAi_tools import bi_query_tool

# Agent global
_agent = None


def get_agent(model_name: str = "llama-3.3-70b") -> Agent:
    """Agent que usa Wren Engine + seu RAG atual"""
    global _agent
    
    llm = LLMConfig.get_model(model_name)
    
    _agent = Agent(
        model=llm,
        knowledge=knowledge,
        description="Assistente BI que usa Wren para SQL + RAG para docs",
        instructions="""
        Para perguntas BI (vendas, relatórios, métricas):
        1. Use tool 'bi_query' com Wren Engine
        2. Peça ao LLM para formatar resultado como tabela/markdown
        
        Para docs/processos: use knowledge base (RAG atual)
        """,
        tools=[bi_query_tool],
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
        response = await agent.arun(request.message)
    else:
        response = await agent.arun(request.message)
    
    return ChatResponse(
        response=response.content if hasattr(response, 'content') else str(response),
        model=request.model
    )


async def chat_stream_generator(request: ChatRequest):
    """
    Gera chunks de resposta para streaming
    
    Args:
        request: Requisição com mensagem e configurações
        
    Yields:
        Chunks de resposta do agent
    """
    agent = get_agent(request.model)
    
    async for chunk in agent.arun(request.message, stream=True):
        if hasattr(chunk, 'content'):
            yield chunk.content
        else:
            yield str(chunk)
