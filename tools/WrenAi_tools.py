"""
Ferramenta Wren AI para Agno Agent
- Wrapper para chamar Wren dentro do agent
- Tratamento de erros e logging
- Formatação de resultados
"""

import logging

from agno.tools import tool

logger = logging.getLogger(__name__)


@tool
async def bi_query_tool(intent: str, db_source: str = "default") -> str:
    """
    Ferramenta de Query BI usando Wren AI Engine

    Use esta ferramenta quando o usuário fizer perguntas sobre:
    - Vendas, receita, lucro
    - Métricas de negócio
    - Dados de clientes
    - Comparações entre períodos/regiões
    - Qualquer análise quantitativa do banco de dados

    Args:
        intent: Pergunta em linguagem natural sobre dados
                Exemplo: "Qual foi a receita total do último trimestre?"
                         "Top 5 produtos mais vendidos por região"
                         "Crescimento de clientes mes a mes"

        db_source: Base de dados a consultar (padrão: "default")
                   Pode ser: "sales", "crm", "analytics", etc.

    Returns:
        String com:
        - SQL gerado
        - Resultado dos dados
        - Sugestão de visualização

    Examples:
        >>> bi_query_tool("Vendas por região", db_source="sales")
        >>> bi_query_tool("Top 10 clientes por volume")
    """

    try:
        # Importar aqui para evitar circular imports
        from app.schemas.bi_schemas import BIRequest

        from app.controllers.wrenai_controller import bi_query

        logger.info(f"🔍 Processando query BI: {intent[:60]}...")

        # Criar request
        request = BIRequest(message=intent, db_source=db_source)

        # Executar query
        result = await bi_query(request)

        # Formatar resposta
        response = _format_response(result)
        logger.info("✓ Query processada com sucesso")

        return response

    except ValueError as e:
        error_msg = f"❌ Erro ao processar query BI:\n{str(e)}"
        logger.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"❌ Erro inesperado em bi_query_tool:\n{str(e)}"
        logger.error(error_msg)
        return error_msg


@tool
async def check_bi_health() -> str:
    """
    Verificar saúde do Wren BI Engine

    Use quando o usuário pedir para testar conectividade
    ou diagnosticar problemas com queries.

    Returns:
        Status de saúde do Wren Engine
    """
    try:
        from app.controllers.wrenai_controller import health_check

        is_healthy = await health_check()

        if is_healthy:
            return "✅ Wren BI Engine está operacional e pronto para consultas"
        else:
            return "❌ Wren BI Engine indisponível. Tente novamente em alguns momentos."

    except Exception as e:
        return f"❌ Erro ao verificar saúde: {e}"


@tool
async def get_bi_cache_stats() -> str:
    """
    Obter estatísticas de cache de queries

    Útil para monitoramento e otimização de performance.
    Mostra quantas queries foram reutilizadas do cache.

    Returns:
        Estatísticas de cache formatadas
    """
    try:
        from app.controllers.wrenai_controller import get_cache_statistics

        stats = await get_cache_statistics()

        return f"""
            📊 Estatísticas de Cache:
            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            • Cache Hits: {stats["hits"]}
            • Cache Misses: {stats["misses"]}
            • Total de Consultas: {stats["total"]}
            • Taxa de Acerto: {stats["hit_rate"]}
            • Queries em Cache: {stats["cached_queries"]}
            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """

    except Exception as e:
        return f"❌ Erro ao obter estatísticas: {e}"


def _format_response(bi_response) -> str:
    """
    Formatar resposta do Wren em markdown legível

    Args:
        bi_response: BIResponse object

    Returns:
        String formatada para apresentação ao usuário
    """

    try:
        # Extrair dados
        sql = bi_response.sql
        result = bi_response.result
        chart_prompt = bi_response.chart_prompt

        # Formatar SQL
        sql_block = f"""
                    ```sql
                    {sql}
                    ```"""

        # Formatar dados
        if isinstance(result, list) and len(result) > 0:
            # Converter para tabela markdown
            if isinstance(result[0], dict):
                headers = list(result[0].keys())
                rows = [[row.get(h, "") for h in headers] for row in result]

                # Limitar a 10 linhas para não sobrecarregar
                display_rows = rows[:10]

                table = _create_markdown_table(headers, display_rows)

                # Aviso se houver mais linhas
                more_rows = len(rows) - 10
                if more_rows > 0:
                    table += f"\n\n*... e mais {more_rows} linhas*"
            else:
                table = f"```\n{str(result)}\n```"
        else:
            table = "_Nenhum resultado encontrado_"

        # Montar resposta final
        formatted = f"""
                    ## 📊 Resultado da Consulta BI

                    **SQL Gerado:**
                    {sql_block}

                    **Resultado:**
                    {table}

                    **Visualização Sugerida:**
                    {chart_prompt}

                    ---
                    *Query processada pelo Wren AI Engine*
                    """

        return formatted.strip()

    except Exception as e:
        logger.error(f"Erro ao formatar resposta: {e}")
        return f"Erro ao formatar resultado: {e}"


def _create_markdown_table(headers: list, rows: list) -> str:
    """
    Criar tabela markdown a partir de headers e linhas

    Args:
        headers: Lista de nomes de colunas
        rows: Lista de listas com dados

    Returns:
        String com tabela markdown
    """
    # Header
    table = "| " + " | ".join(str(h) for h in headers) + " |\n"

    # Separador
    table += "| " + " | ".join("---" for _ in headers) + " |\n"

    # Linhas
    for row in rows:
        table += "| " + " | ".join(str(v) for v in row) + " |\n"

    return table.rstrip()


# Tools para incluir no Agent
BI_TOOLS = [bi_query_tool, check_bi_health, get_bi_cache_stats]
