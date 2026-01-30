## Método usado para criar o RAG Agentic

Este documento descreve a abordagem adotada para montar um agente RAG (Retrieval-Augmented Generation) neste projeto. O foco é explicar como a Knowledge Base é construída, como indexamos diferentes formatos de documento e como o agente é configurado para sempre consultar essa base antes de responder.

### Visão geral

1. Usamos um vector database (Qdrant) para armazenar vetores de embeddings representando trechos de texto.
2. As embeddings são geradas pelo `FastEmbedEmbedder` e indexadas no Qdrant.
3. Criamos métodos assíncronos para adicionar conteúdo (URLs, JSON, PDF) à knowledge base, chunking controlado e busca semântica.
4. O Agent é configurado para consultar a knowledge base antes de gerar respostas (RAG agentic).

### Vector DB e embedder

- Serviço: Qdrant (rodando via Docker Compose; ver `compose.yml`).
- Embedder: `FastEmbedEmbedder` (configurado em `utils/vector_db.py`).

Observações:
- O Qdrant em si é um banco de vetores. A geração das embeddings pode requerer modelos hospedados no HuggingFace — portanto, nem todo fluxo é 100% offline. Na primeira execução alguns modelos podem precisar ser baixados.
- Para evitar problemas com rate limits do HuggingFace é recomendado criar uma conta gratuita e configurar `HF_TOKEN` no `.env`.

### Por que o Qdrant é o serviço central da Knowledge

O Qdrant armazena todos os vetores que representam o conteúdo processado. Ele é o ponto central que alimenta o comportamento RAG do agente: quando o agente precisa responder, ele primeiro consulta (retrieves) a knowledge base para obter trechos relevantes e, então, gera a resposta com fundamento nas informações retornadas.

### Ingestão de conteúdo

Para manter a base de conhecimento atualizada criamos um controller específico com métodos para diferentes fontes:

- `WebsiteReader` — para páginas e sites (URLs). Permite definir profundidade e número de links.
- `JSONReader` — para arquivos JSON estruturados.
- `PDFReader` — para arquivos PDF.

Esses readers são usados junto com a função `knowledge.add_content_async(...)`, que realiza a ingestão de maneira assíncrona e segura para projetos web baseados em FastAPI.

Exemplos de uso no controller:

- Adicionar URL: usamos `WebsiteReader` com `RecursiveChunking(chunk_size=1000, overlap=100)` (configurável).
- Adicionar JSON: usamos `JSONReader` com chunk sizes menores, adequados para dados estruturados.
- Adicionar PDF: usamos `PDFReader` com chunking recursivo padrão.

### Chunking: por que usamos RecursiveChunking

Usamos `RecursiveChunking` para garantir que os textos sejam divididos em trechos bem formados e otimizados para busca semântica. Isso traz dois benefícios principais:

1. Evita dependência implícita de serviços externos (por exemplo, uma implementação padrão que poderia usar OpenAI por baixo dos panos quando nenhum chunking é passado).
2. Permite controle fino sobre `chunk_size` e `overlap`, melhorando relevância da recuperação para documentos grandes.

Configurar chunking explicitamente é importante quando lidamos com documentos muito grandes: ajustar `chunk_size` e `overlap` melhora precisão e evita perder contexto.

### Processamento assíncrono com add_content_async

Como a aplicação usa FastAPI (assíncrono), utilizamos `add_content_async` para inserir conteúdo na knowledge base sem bloquear o loop de eventos. Isso permite subir arquivos grandes ou rastrear sites sem travar o servidor.

### Como o Agent é criado e configurado

O Agent é criado usando a Knowledge Base (instância singleton) e o modelo LLM desejado. É crucial forçar o agente a usar a knowledge base como fonte primária:

```
Agent(
    model=llm,
    knowledge=knowledge,
    search_knowledge=True,
    read_chat_history=True,
    debug_mode=settings.debug_mode,
    ...
)
```

Pontos importantes na configuração do agente:

- `knowledge=knowledge`: injeta a instância da knowledge base (Qdrant) no agent.
- `search_knowledge=True`: habilita explicitamente que o agent use a função de busca na knowledge antes de gerar qualquer resposta (comportamento RAG agentic).
- `read_chat_history=True`: mantém contexto da conversa quando necessário.
- `debug_mode=True` (opcional): útil para verificar `tool_calls` e confirmar que a busca está sendo usada.

Além disso, nas instruções do agent incluímos regras explícitas para forçar a busca na knowledge (por exemplo: "NUNCA responda sem antes buscar na base de conhecimento"), o que reforça o comportamento desejado.

### Boas práticas e recomendações

- Sempre crie um token do HuggingFace (`HF_TOKEN`) se estiver usando embedders que dependem de modelos hospedados lá — isso reduz problemas com rate limits.
- Para documentos grandes, comece com `chunk_size=500` a `1000` e `overlap=50` a `100` e ajuste conforme a qualidade dos resultados.
- Reprocessar documentos depois de ajustar `chunk_size` é recomendado para melhorar recuperação.
- Monitorar `points_count` na coleção do Qdrant para garantir que os documentos foram indexados corretamente.

### Resumo

Em resumo, a arquitetura adotada consiste em:

1. Qdrant como serviço de knowledge (rodando via Docker Compose).
2. `FastEmbedEmbedder` para gerar embeddings que alimentam o Qdrant.
3. Controllers para ingestão (URL / JSON / PDF) usando readers apropriados e `add_content_async`.
4. Chunking controlado com `RecursiveChunking` para evitar dependências indesejadas e melhorar a qualidade da recuperação.
5. Agent configurado com `knowledge=knowledge` e `search_knowledge=True` para garantir que o comportamento do agente seja RAG-first.
