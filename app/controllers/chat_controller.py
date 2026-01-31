"""
Chat Controller com Agno Agent
- Combina RAG (Knowledge Base) + Wren BI
- Agent decide quando usar cada ferramenta
- Mantém contexto da conversa
"""

import logging
from agno.agent import Agent
from app.schemas.chat_schemas import ChatRequest, ChatResponse
from utils.knowledge import knowledge
from utils.llm import LLMConfig
from utils.settings import settings
from wren_tools_improved import BI_TOOLS

logger = logging.getLogger(__name__)

# Agent global (singleton)
_agent: Agent = None


def get_agent(model_name: str = "llama-3.3-70b") -> Agent:
    """
    Obter ou criar agent que combina RAG + Wren BI
    
    Args:
        model_name: Nome do modelo LLM
    
    Returns:
        Agent configurado
    """
    global _agent
    
    # Reutilizar agent se já existe
    if _agent is not None:
        return _agent
    
    logger.info(f"🚀 Criando Agent com modelo: {model_name}")
    
    # Obter LLM
    llm = LLMConfig.get_model(model_name)
    
    # Criar agent
    _agent = Agent(
        name="BI Intelligence Assistant",
        model=llm,
        knowledge=knowledge,  # RAG para buscar em documentos
        
        description="""
        Assistente inteligente de Business Intelligence.
        Combina análise de documentos com consultas de dados.
        """,
        
        instructions="""
        Você é um assistente de BI especializado que ajuda usuários a entender dados e documentos.
        
        COMPORTAMENTO:
        
        1. Para PERGUNTAS SOBRE DADOS (vendas, métricas, números):
           ✓ SEMPRE use a ferramenta 'bi_query_tool' para consultar o banco
           ✓ Explique o SQL que será gerado
           ✓ Analise os resultados e forneça insights
           ✓ Sugira visualizações apropriadas
        
        2. Para PERGUNTAS SOBRE DOCUMENTOS/PROCESSOS:
           ✓ Use a knowledge base (RAG) para buscar informações
           ✓ Cite os documentos relevantes
           ✓ Resuma as informações importantes
        
        3. Para PERGUNTAS COMBINADAS (dados + documentos):
           ✓ Primeiro busque em documentos relevantes
           ✓ Depois consulte dados com as ferramentas BI
           ✓ Combine as respostas para conclusão completa
        
        NUNCA adivinhe resultados de dados - sempre use as ferramentas!
        Seja preciso, cite fontes, e ofereça insights além dos números.
        
        CONTEXTO:
        - Base de dados disponível: {db_sources}
        - Modelos LLM disponíveis: {available_models}
        - Modo debug: {debug_mode}
        """.format(
            db_sources="sales, crm, analytics",
            available_models=list(LLMConfig.list_models().keys()),
            debug_mode=settings.debug_mode
        ),
        
        # Tools disponíveis
        tools=BI_TOOLS,
        
        # Configurações
        markdown=True,
        search_knowledge=True,  # Habilitar RAG
        read_chat_history=True,  # Manter contexto
        debug_mode=settings.debug_mode,
        
        # Limites
        max_iterations=10,  # Máximo de tool calls
        max_tokens=2000,  # Máximo de tokens na resposta
    )
    
    logger.info("✓ Agent criado com sucesso")
    return _agent


async def chat_with_agent(request: ChatRequest) -> ChatResponse:
    """
    Processar mensagem do usuário com o Agent
    
    Args:
        request: ChatRequest com mensagem e configurações
    
    Returns:
        ChatResponse com resposta do agent
    """
    try:
        logger.info(f"💬 Nova mensagem: {request.message[:60]}...")
        
        # Obter agent
        agent = get_agent(request.model)
        
        # Executar agent
        logger.debug(f"Model: {request.model}")
        logger.debug(f"Stream: {request.stream}")
        
        response = await agent.arun(request.message)
        
        # Extrair texto da resposta
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        logger.info(f"✓ Resposta gerada ({len(response_text)} caracteres)")
        
        return ChatResponse(
            response=response_text,
            model=request.model
        )
        
    except Exception as e:
        logger.error(f"❌ Erro no chat: {e}", exc_info=True)
        raise


async def chat_stream_generator(request: ChatRequest):
    """
    Gerar resposta em streaming
    
    Args:
        request: ChatRequest
    
    Yields:
        Chunks de texto da resposta
    """
    try:
        logger.info(f"🎬 Iniciando stream para: {request.message[:60]}...")
        
        agent = get_agent(request.model)
        
        # Streaming não é natively suportado em agno,
        # então fazemos "fake streaming" enviando chunks
        response = await agent.arun(request.message)
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        # Dividir em chunks e enviar
        chunk_size = 100
        for i in range(0, len(response_text), chunk_size):
            chunk = response_text[i:i + chunk_size]
            yield chunk
            
        logger.info("✓ Stream finalizado")
        
    except Exception as e:
        logger.error(f"❌ Erro no stream: {e}")
        yield f"Erro: {e}"


def reset_agent():
    """Resetar agent (útil para testes ou mudança de modelo)"""
    global _agent
    _agent = None
    logger.info("✓ Agent resetado")


async def get_agent_info() -> dict:
    """Obter informações sobre o agent atual"""
    agent = get_agent()
    
    return {
        "name": agent.name,
        "description": agent.description,
        "model": agent.model.id if hasattr(agent.model, 'id') else str(agent.model),
        "tools_count": len(agent.tools) if agent.tools else 0,
        "has_knowledge_base": agent.knowledge is not None,
        "debug_mode": agent.debug_mode,
    }
