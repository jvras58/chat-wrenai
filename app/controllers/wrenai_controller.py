"""
Controlador Wren AI para Consultas BI
- Gerencia conexão com Wren Engine
- Executa e cach queries
- Tratamento robusto de erros
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from httpx import AsyncClient, HTTPError, TimeoutException
from functools import lru_cache
import hashlib

from utils.settings import settings
from app.schemas.bi_schemas import BIRequest, BIResponse

logger = logging.getLogger(__name__)

class WrenAIClient:
    """Cliente Wren AI com cache e retry logic"""
    
    def __init__(self, base_url: str = None, timeout: int = 60):
        self.base_url = base_url or settings.wren_url
        self.timeout = timeout
        self.client: Optional[AsyncClient] = None
        self._query_cache: Dict[str, BIResponse] = {}
        self._cache_hits = 0
        self._cache_misses = 0
    
    async def __aenter__(self):
        """Context manager setup"""
        self.client = AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        if self.client:
            await self.client.aclose()
    
    async def init(self):
        """Inicializar cliente"""
        if not self.client:
            self.client = AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout
            )
    
    async def close(self):
        """Fechar cliente"""
        if self.client:
            await self.client.aclose()
    
    def _get_cache_key(self, intent: str, db_source: str) -> str:
        """Gerar chave de cache para query"""
        key_str = f"{intent}_{db_source}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    async def health_check(self) -> bool:
        """Verificar saúde do Wren Engine"""
        try:
            await self.init()
            response = await self.client.get("/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check falhou: {e}")
            return False
    
    async def query_to_sql(
        self,
        intent: str,
        db_source: str = "default",
        use_cache: bool = True
    ) -> Optional[str]:
        """
        Converter intent em SQL usando Wren
        
        Args:
            intent: Pergunta em linguagem natural
            db_source: Fonte de dados
            use_cache: Usar cache de queries
        
        Returns:
            SQL gerado ou None se falhar
        """
        # Verificar cache
        cache_key = self._get_cache_key(intent, db_source)
        if use_cache and cache_key in self._query_cache:
            self._cache_hits += 1
            logger.info(f"✓ Cache HIT para: {intent[:50]}...")
            return self._query_cache[cache_key].sql
        
        self._cache_misses += 1
        
        try:
            await self.init()
            
            payload = {
                "intent": intent,
                "db_source": db_source,
                "model": "gpt-4"  # Wren usa seu próprio modelo
            }
            
            logger.info(f"🔄 Consultando Wren para: {intent[:50]}...")
            response = await self.client.post(
                "/mcp/sql",
                json=payload
            )
            
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"✓ SQL gerado com sucesso")
            return data.get("sql")
            
        except TimeoutException:
            logger.error(f"⏱️ Timeout ao conectar Wren: {self.base_url}")
            return None
        except HTTPError as e:
            logger.error(f"❌ Erro HTTP Wren: {e.response.status_code}")
            logger.error(f"   Resposta: {e.response.text[:200]}")
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao converter intent: {e}")
            return None
    
    async def execute_sql(
        self,
        sql: str,
        db_source: str = "default"
    ) -> Optional[Dict[str, Any]]:
        """
        Executar SQL no banco de dados
        
        Args:
            sql: Comando SQL
            db_source: Fonte de dados
        
        Returns:
            Resultado da query ou None
        """
        try:
            await self.init()
            
            payload = {
                "sql": sql,
                "db_source": db_source
            }
            
            logger.info(f"📊 Executando SQL...")
            response = await self.client.post(
                "/mcp/query",
                json=payload
            )
            
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"✓ Query executada, {len(data.get('data', []))} linhas retornadas")
            return data
            
        except Exception as e:
            logger.error(f"❌ Erro ao executar SQL: {e}")
            return None
    
    async def full_query(
        self,
        intent: str,
        db_source: str = "default"
    ) -> Optional[BIResponse]:
        """
        Pipeline completo: intent -> SQL -> execução -> resultado
        
        Args:
            intent: Pergunta do usuário
            db_source: Fonte de dados
        
        Returns:
            BIResponse com SQL e dados
        """
        # Passo 1: Converter intent em SQL
        sql = await self.query_to_sql(intent, db_source)
        if not sql:
            return None
        
        # Passo 2: Executar SQL
        result = await self.execute_sql(sql, db_source)
        if not result:
            return None
        
        # Passo 3: Formatar resposta
        response = BIResponse(
            sql=sql,
            result=result.get("data", []),
            chart_prompt=self._generate_chart_suggestion(intent)
        )
        
        # Cachear resultado
        cache_key = self._get_cache_key(intent, db_source)
        self._query_cache[cache_key] = response
        
        return response
    
    def _generate_chart_suggestion(self, intent: str) -> str:
        """Sugerir tipo de visualização baseado na pergunta"""
        intent_lower = intent.lower()
        
        if any(x in intent_lower for x in ["por", "cada", "comparar"]):
            return "Gráfico de barras para comparação por categoria"
        elif any(x in intent_lower for x in ["tendência", "evolução", "tempo"]):
            return "Gráfico de linhas para tendência temporal"
        elif any(x in intent_lower for x in ["percentual", "proporção", "distribuição"]):
            return "Gráfico de pizza para distribuição"
        else:
            return "Tabela com os resultados"
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Estatísticas de cache"""
        total = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total * 100) if total > 0 else 0
        
        return {
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "total": total,
            "hit_rate": f"{hit_rate:.1f}%",
            "cached_queries": len(self._query_cache)
        }
    
    def clear_cache(self):
        """Limpar cache de queries"""
        self._query_cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        logger.info("✓ Cache limpo")


# Instância global
_wren_client: Optional[WrenAIClient] = None


async def get_wren_client() -> WrenAIClient:
    """Obter cliente Wren singleton"""
    global _wren_client
    if _wren_client is None:
        _wren_client = WrenAIClient()
    return _wren_client


async def bi_query(request: BIRequest) -> BIResponse:
    """
    Controlador principal para queries BI
    
    Args:
        request: BIRequest com intent e db_source
    
    Returns:
        BIResponse com SQL e resultado
    """
    client = await get_wren_client()
    
    response = await client.full_query(
        intent=request.message,
        db_source=request.db_source
    )
    
    if not response:
        raise ValueError(
            f"Não foi possível processar query: {request.message}"
        )
    
    return response


async def get_cache_statistics() -> Dict[str, Any]:
    """Obter estatísticas de cache"""
    client = await get_wren_client()
    return client.get_cache_stats()


async def health_check() -> bool:
    """Verificar saúde do Wren Engine"""
    client = await get_wren_client()
    return await client.health_check()
