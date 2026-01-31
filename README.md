# Chat com Wren AI - Sistema RAG Integrado

Este projeto implementa um sistema de chat com Retrieval-Augmented Generation (RAG) integrado ao Wren AI, uma plataforma de SQL generation e business intelligence.

## 📁 Estrutura de Arquivos

```
chat-wrenai/
├── compose.yml                      # Serviços Docker (PostgreSQL, Qdrant, Wren AI)
├── pyproject.toml                   # Dependências Python
├── makefile                         # Comandos de automação
├── README.md                        # Este arquivo
├── app/                             # Aplicação FastAPI
│   ├── main.py                      # Ponto de entrada da aplicação
│   ├── controllers/                 # Lógica de negócio
│   │   ├── __init__.py
│   │   ├── chat_controller.py       # Lógica de chat e agents
│   │   ├── knowledge_controller.py  # Lógica de knowledge base
│   │   └── wrenai_controller.py     # Integração com Wren AI
│   ├── routers/                     # Definições de rotas
│   │   ├── __init__.py
│   │   ├── chat_router.py          # Rotas de chat
│   │   ├── knowledge_router.py     # Rotas de knowledge base
│   │   └── wrenai_router.py        # Rotas de integração Wren AI
│   ├── schemas/                     # Modelos Pydantic
│   │   ├── bi_schemas.py           # Schemas para BI/Wren
│   │   ├── chat_schemas.py         # Schemas de chat
│   │   └── document_schemas.py     # Schemas de documentos
│   └── utils/                       # Utilitários
│       ├── knowledge.py            # Configuração da Knowledge Base
│       ├── llm.py                  # Configuração de LLMs
│       ├── settings.py             # Configurações da aplicação
│       └── vector_db.py            # Configuração do Qdrant
├── docs/                            # Documentação
│   └── RAG_AGENT_METHOD.md         # Método do agente RAG
├── etc/                             # Configurações Wren Engine
│   ├── config.properties           # Configuração do Wren Engine
│   ├── mdl/
│   │   └── wrenmdl.json           # Manifesto do modelo Wren
│   └── scripts/                    # Scripts auxiliares
├── scripts/                         # Scripts do projeto
│   └── dbsample.py                 # Amostra de dados
└── tools/                           # Ferramentas
    └── WrenAi_tools.py             # Ferramentas para Wren AI
```

## 🏗️ Arquitetura

### **Serviços Docker (Compose)**

O sistema utiliza múltiplos serviços containerizados:

- **PostgreSQL**: Banco de dados relacional para dados reais
- **Qdrant**: Vector database para embeddings e RAG
- **Wren Engine**: Core de geração de SQL e processamento de queries
- **Wren Ibis**: API layer para integração com Wren Engine
- **Wren UI**: Interface web para exploração de dados

### **Configurações Wren Engine (etc/)**

A pasta `etc/` contém as configurações essenciais para o Wren Engine, que define a semântica e estrutura dos dados para geração de SQL e business intelligence:

#### **config.properties**
Arquivo de propriedades Java-style que configura o comportamento do Wren Engine:
```properties
wren.directory=etc/mdl                    # Diretório do manifesto MDL
wren.datasource.type=DUCKDB              # Tipo de datasource (DUCKDB/PostgreSQL)
wren.experimental-enable-dynamic-fields=true  # Habilita campos dinâmicos
node.environment=production              # Ambiente de execução
```

**Como atualizar:**
- Edite diretamente o arquivo `etc/config.properties`
- Reinicie o container: `docker compose restart wren-engine`

#### **mdl/wrenmdl.json**
Manifesto MDL (Model Definition Language) que define semanticamente os modelos de dados, relacionamentos e métricas:
```json
{
  "catalog": "wren",
  "schema": "test",
  "models": [
    {
      "name": "Orders",
      "tableReference": {
        "catalog": "postgres",
        "schema": "public",
        "table": "orders"
      },
      "columns": [
        {
          "name": "orderkey",
          "expression": "order_id",
          "type": "integer"
        }
      ],
      "primaryKey": "orderkey"
    }
  ],
  "relationships": [],
  "views": [],
  "metrics": []
}
```

**Como atualizar:**
1. **Adicionar modelos:** Defina novas tabelas com suas colunas e tipos
2. **Configurar relacionamentos:** Especifique foreign keys entre modelos
3. **Definir métricas:** Adicione cálculos agregados (somas, médias, etc.)
4. **Criar views:** Defina views virtuais para consultas complexas
5. **Reiniciar serviços:** `docker compose restart wren-engine wren-ibis`

**Estrutura dos modelos:**
- `name`: Nome semântico do modelo
- `tableReference`: Referência à tabela física no banco
- `columns`: Mapeamento de colunas com expressões SQL
- `primaryKey`: Chave primária para relacionamentos
- `relationships`: Conexões entre modelos
- `metrics`: Definições de métricas calculadas

#### **scripts/**
Pasta auxiliar com scripts de configuração:
- `dbsample.py`: Script para popular dados de exemplo

**Como usar:**
```bash
# Executar script de exemplo que sobe um banco de dados de sample 
python etc/scripts/dbsample.py
```

#### **Utils**

##### **settings.py**
- Configurações gerais carregadas do `.env`
- API keys (Groq, HuggingFace) e modelos padrão
- Usa Pydantic Settings

##### **vector_db.py**
- Configuração do Qdrant Vector Database
- Singleton do vector_db
- Configuração do embedder (FastEmbed)

##### **knowledge.py**
- Configuração da Knowledge Base RAG
- Singleton da knowledge base
- Conecta ao vector_db para busca semântica

##### **llm.py**
- Configuração dos modelos LLM (Groq)
- Gerenciamento de modelos disponíveis
- Factory para criação de instâncias

#### **Controllers**
Contém a lógica de negócio separada das rotas:

##### **chat_controller.py**
- `get_agent()`: Cria/retorna agent com modelo especificado
- `chat_with_agent()`: Processa mensagens de chat
- `chat_stream_generator()`: Gera streaming de respostas

##### **knowledge_controller.py**
- `add_url_to_knowledge()`: Adiciona URLs à base
- `add_json_to_knowledge()`: Processa arquivos JSON
- `add_pdf_to_knowledge()`: Processa arquivos PDF
- `get_knowledge_status()`: Retorna status da base
- `clear_knowledge_base()`: Limpa toda a base
- `list_documents()`: Lista documentos armazenados
- `search_documents()`: Busca por similaridade

##### **wrenai_controller.py**
- Integração com Wren AI para queries SQL
- Processamento de dados de business intelligence
- Conexão com PostgreSQL via Wren Ibis

#### **Routers**
Define os endpoints da API:

##### **chat_router.py**
- `POST /chat`: Chat normal
- `POST /chat/stream`: Chat com streaming

##### **knowledge_router.py**
- `POST /knowledge/add/url`: Adiciona URL
- `POST /knowledge/add/json`: Upload JSON
- `POST /knowledge/add/pdf`: Upload PDF
- `GET /knowledge/status`: Status da base
- `GET /knowledge/documents`: Lista documentos
- `POST /knowledge/search`: Busca documentos
- `DELETE /knowledge/clear`: Limpa base

##### **wrenai_router.py**
- `POST /wrenai/query`: Executa queries SQL via Wren
- `GET /wrenai/models`: Lista modelos disponíveis
- `POST /wrenai/analyze`: Análise de dados

## 🚀 Como Executar

### **Pré-requisitos**
- Docker e Docker Compose
- Python 3.11+
- Conta Groq (para LLMs)
- Token HuggingFace (opcional, para evitar rate limits)

### **Passos de Instalação**

```bash
# 1. Clonar o repositório
git clone <repo-url>
cd chat-wrenai

# 2. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas chaves API

# 3. Subir todos os serviços
docker compose up -d

# 4. Instalar dependências Python
pip install -r requirements.txt
# ou se usar uv:
uv sync

# 5. Executar aplicação
python app/main.py

# Ou com uvicorn diretamente
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **Acesso aos Serviços**

Após iniciar, os serviços estarão disponíveis em:
- **API FastAPI**: http://localhost:8000
- **Wren UI**: http://localhost:3000
- **Wren Ibis API**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Qdrant**: http://localhost:6333

## 🧪 Testes e Validação

### **Verificar Serviços**

```bash
# Status de todos os containers
docker compose ps

# Logs de um serviço específico
docker compose logs wren-engine
```

### **Testar RAG**

Para confirmar que seus documentos foram processados:

```bash
# Verificar coleção Qdrant
curl http://localhost:6333/collections/agno-rag-api

# Deve retornar points_count > 0
```

### **Testar Wren AI**

```bash
# Verificar Wren Engine
curl http://localhost:8080/api/status

# Testar query via Wren Ibis
curl -X POST http://localhost:8000/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM your_table LIMIT 5"}'
```

### **Configurar Modelo de Dados (MDL)**

Para que o Wren AI entenda sua estrutura de dados:

1. **Editar `etc/mdl/wrenmdl.json`** com seus modelos
2. **Reiniciar serviços:**
   ```bash
   docker compose restart wren-engine wren-ibis
   ```
3. **Testar queries semânticas:**
   ```bash
   # Em vez de SQL físico
   "mostre vendas por cliente"
   
   # Wren converte para SQL usando o MDL
   SELECT customer.name, SUM(orders.total) 
   FROM orders JOIN customer ON orders.customer_id = customer.id
   GROUP BY customer.name
   ```

### **Popular Dados de Exemplo**

```bash
# Executar script de exemplo
make dbsample

# Ou diretamente
python etc/scripts/dbsample.py
```

## ⚠️ Problemas Conhecidos e Soluções

### **1. Rate Limit do HuggingFace**
**Solução:** Adicionar `HF_TOKEN` ao `.env`

### **2. Agent não usa knowledge base**
**Sintomas:** Respostas genéricas, sem `tool_calls` nos logs
**Solução:** Verificar documentos indexados e fazer perguntas específicas

### **3. Wren Engine não inicia**
**Sintomas:** Container sai com erro
**Solução:** Verificar arquivos em `etc/config.properties` e `etc/mdl/wrenmdl.json`

### **4. Dependências entre serviços**
**Sintomas:** Containers não iniciam na ordem correta
**Solução:** Usar `docker compose up -d` para iniciar todos simultaneamente

### **5. MDL não configurado corretamente**
**Sintomas:** Queries Wren retornam erros ou resultados incorretos
**Solução:** 
1. Verificar `etc/mdl/wrenmdl.json` tem modelos corretos
2. Garantir que `tableReference` aponta para tabelas existentes
3. Reiniciar `wren-engine` e `wren-ibis` após mudanças
4. Testar queries simples primeiro

### **6. Dados não populados**
**Sintomas:** Queries retornam tabelas vazias
**Solução:**
```bash
# Popular dados de exemplo
make dbsample

# Ou verificar PostgreSQL
docker exec -it postgres_db psql -U postgres -d postgres -c "SELECT * FROM your_table LIMIT 5;"
```

## 📝 Próximos Passos

- [ ] Documentar integração completa com Wren AI
- [ ] Criar ferramenta para auto-gerar MDL a partir do schema PostgreSQL
- [ ] Implementar validação automática do `wrenmdl.json`
- [ ] Adicionar exemplos de MDL para diferentes tipos de dados
- [ ] Criar interface web para editar configurações MDL
- [ ] Adicionar testes unitários para controllers
- [ ] Implementar autenticação e autorização
- [ ] Criar dashboard unificado
- [ ] Adicionar monitoramento e métricas
- [ ] Otimizar performance de queries RAG
- [ ] Implementar cache para resultados frequentes
