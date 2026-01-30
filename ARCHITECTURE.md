# Estrutura do Projeto

Este projeto foi reorganizado seguindo o padrão MVC (Model-View-Controller) adaptado para FastAPI.

## 📁 Estrutura de Arquivos

```
test_rag/
├── main.py                          # Ponto de entrada da aplicação
├── config.py                        # Configurações globais (vector_db, knowledge)
├── schemas.py                       # Modelos Pydantic para validação
├── controllers/                     # Lógica de negócio
│   ├── __init__.py
│   ├── chat_controller.py          # Lógica de chat e agents
│   └── knowledge_controller.py     # Lógica de knowledge base
├── routers/                        # Definições de rotas
│   ├── __init__.py
│   ├── chat_router.py             # Rotas de chat
│   └── knowledge_router.py        # Rotas de knowledge base
└── utils/                         # Utilitários
    └── llm.py                     # Configuração de LLMs
```

## 🏗️ Arquitetura

### **main.py**
- Ponto de entrada da aplicação
- Configura o FastAPI
- Registra os routers
- Define rotas auxiliares (health, models)
- Gerencia eventos de startup

### **config.py**
- Configurações globais da aplicação
- Instância única do vector_db (Qdrant)
- Knowledge base global
- Configurações compartilhadas

### **schemas.py**
- Todos os modelos Pydantic
- Validação de requests e responses
- Enums e tipos customizados
- Documentação dos dados da API

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
- `DELETE /knowledge/clear`: Limpa base

## 🎯 Vantagens da Nova Estrutura

1. **Separação de Responsabilidades**: Cada arquivo tem uma responsabilidade clara
2. **Testabilidade**: Controllers podem ser testados independentemente
3. **Manutenibilidade**: Código organizado e fácil de encontrar
4. **Escalabilidade**: Fácil adicionar novos endpoints e funcionalidades
5. **Reutilização**: Lógica de negócio pode ser reutilizada
6. **Documentação**: Estrutura autoexplicativa

## 🚀 Como Executar

```bash
# Instalar dependências
uv sync

# Executar aplicação
python main.py

# Ou com uvicorn diretamente
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📝 Próximos Passos

- [ ] Adicionar testes unitários para controllers
- [ ] Adicionar testes de integração para routers
- [ ] Implementar logging estruturado
- [ ] Adicionar middleware de autenticação
- [ ] Criar serviços para operações complexas
