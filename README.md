# Estrutura do Projeto

Este projeto foi reorganizado seguindo o padrão MVC (Model-View-Controller) adaptado para FastAPI.

## 📁 Estrutura de Arquivos

```
ChatRag/
├── main.py                          # Ponto de entrada da aplicação
├── compose.yml                      # Serviços Docker (Qdrant)
├── controllers/                     # Lógica de negócio
│   ├── __init__.py
│   ├── chat_controller.py          # Lógica de chat e agents
│   └── knowledge_controller.py     # Lógica de knowledge base
├── routers/                        # Definições de rotas
│   ├── __init__.py
│   ├── chat_router.py             # Rotas de chat
│   └── knowledge_router.py        # Rotas de knowledge base
├── schama/                         # Modelos Pydantic
│   ├── chat_schemas.py            # Schemas de chat
│   └── document_schemas.py        # Schemas de documentos
└── utils/                         # Utilitários
    ├── llm.py                     # Configuração de LLMs
    ├── settings.py                # Configurações da aplicação
    ├── vector_db.py               # Configuração do Qdrant
    └── knowledge.py               # Configuração da Knowledge Base
```

## 🏗️ Arquitetura

### **Utils**

#### **settings.py**
- Configurações gerais carregadas do `.env`
- API keys e modelos padrão
- Usa Pydantic Settings

#### **vector_db.py**
- Configuração do Qdrant Vector Database
- Singleton do vector_db
- Configuração do embedder (FastEmbed)

#### **knowledge.py**
- Configuração da Knowledge Base
- Singleton da knowledge base
- Conecta ao vector_db

#### **llm.py**
- Configuração dos modelos LLM (Groq)
- Gerenciamento de modelos disponíveis
- Factory para criação de instâncias

### **Controllers**
Contém a lógica de negócio separada das rotas:

#### **chat_controller.py**
- `get_agent()`: Cria/retorna agent com modelo especificado
- `chat_with_agent()`: Processa mensagens de chat
- `chat_stream_generator()`: Gera streaming de respostas

#### **knowledge_controller.py**
- `add_url_to_knowledge()`: Adiciona URLs à base
- `add_json_to_knowledge()`: Processa arquivos JSON
- `add_pdf_to_knowledge()`: Processa arquivos PDF
- `get_knowledge_status()`: Retorna status da base
- `clear_knowledge_base()`: Limpa toda a base
- `list_documents()`: Lista documentos armazenados
- `search_documents()`: Busca por similaridade

### **Routers**
Define os endpoints da API:

#### **chat_router.py**
- `POST /chat`: Chat normal
- `POST /chat/stream`: Chat com streaming

#### **knowledge_router.py**
- `POST /knowledge/add/url`: Adiciona URL
- `POST /knowledge/add/json`: Upload JSON
- `POST /knowledge/add/pdf`: Upload PDF
- `GET /knowledge/status`: Status da base
- `GET /knowledge/documents`: Lista documentos
- `POST /knowledge/search`: Busca documentos
- `DELETE /knowledge/clear`: Limpa base

## 🚀 Como Executar

```bash
# Subir o Qdrant com Docker Compose
docker compose up -d

# Instalar dependências
uv sync

# Executar aplicação
python main.py

# Ou com uvicorn diretamente
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🧪 Testes e Validação

### Verificar se os dados estão indexados

Para confirmar que seus documentos foram processados e estão disponíveis no Qdrant:

```bash
# Verificar status da coleção
curl http://localhost:6333/collections/agno-rag-api

# Procure por "points_count" - deve ser > 0 se houver documentos indexados
```

**Resposta esperada:**
```json
{
  "result": {
    "status": "green",
    "points_count": 38,  // ← Este número deve ser maior que 0
    "indexed_vectors_count": 0,
    ...
  }
}
```

### Testando o Chat com Perguntas Específicas

Para garantir que o Agent está consultando a base de conhecimento, faça perguntas **específicas** que contenham palavras exatas do seu documento:

✅ **Boas perguntas** (com palavras-chave do conteúdo):
- "O que está na aba Saiba Mais?"
- "Quais são as opções do usuário no Redu?"
- "Como editar meu perfil no Redu?"
- "Como funciona a central de ajuda?"
- "Onde encontro o meu perfil?"

❌ **Perguntas genéricas** (podem não acionar a busca):
- "O que é isso?"
- "Me fale sobre o sistema"
- "Como funciona?"

### Verificando os Logs

Quando o chat está funcionando corretamente, você deve ver nos logs:

```bash
DEBUG ===================================== tool_calls =====================================
DEBUG search_knowledge_base(query='...', num_documents=5)
DEBUG ======================================= tool =========================================
DEBUG search_knowledge_base: [resultados encontrados]
```

Se **NÃO** ver `tool_calls`, significa que o Agent não está buscando na base de conhecimento.

## ⚠️ Problemas Conhecidos e Soluções

### 1. Rate Limit do HuggingFace

**Erro:**
```bash
ERROR | Could not download model from HuggingFace: 429 Client Error: Too Many Requests
We had to rate limit your IP (187.40.216.239)
```

**Causa:** O modelo de embeddings `all-MiniLM-L6-v2-onnx` precisa ser baixado do HuggingFace na primeira execução.

**Solução:**
1. Criar uma conta gratuita em [HuggingFace](https://huggingface.co/join)
2. Gerar um token de acesso em [Settings > Access Tokens](https://huggingface.co/settings/tokens)
3. Adicionar ao `.env`:
   ```bash
   HF_TOKEN=seu_token_aqui
   ```
4. Ou aguardar alguns minutos e tentar novamente (fallback automático)

### 2. Agent não está usando a base de conhecimento

**Sintomas:**
- Respostas genéricas sem citar documentos
- Ausência de `tool_calls` nos logs
- Agent responde sem buscar

**Soluções:**
1. **Verificar se há documentos indexados** (ver seção de testes acima)
2. **Fazer perguntas mais específicas** com palavras-chave exatas do conteúdo
3. **Reprocessar documentos** com chunks menores:
   ```python
   # Em knowledge_controller.py
   RecursiveChunking(chunk_size=500, overlap=50)
   ```
4. **Verificar configuração do Agent** em `chat_controller.py`:
   ```python
   search_knowledge=True,
   debug_mode=True
   ```

### 3. Qdrant não está acessível

**Erro:**
```bash
Connection refused - localhost:6333
```

**Solução:**
```bash
# Verificar se o container está rodando
docker ps

# Se não estiver, iniciar:
docker compose up -d

# Verificar logs:
docker compose logs -f qdrant
```

## 📝 Próximos Passos

- [ ] Adicionar testes unitários para controllers
- [ ] Adicionar testes de integração para routers
- [ ] Implementar logging estruturado
- [ ] Adicionar middleware de autenticação
- [ ] Criar serviços para operações complexas
- [ ] Adicionar health checks para dependências externas
