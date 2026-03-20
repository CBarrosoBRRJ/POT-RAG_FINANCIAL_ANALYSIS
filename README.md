# POT-RAG Financial Analysis

Aplicacao de analise financeira com RAG sobre series macroeconomicas do Banco Central do Brasil. O projeto baixa dados oficiais da API SGS, normaliza os CSVs localmente, gera embeddings, persiste uma base vetorial com ChromaDB e expõe uma interface conversacional em Streamlit para consultas sobre IPCA, SELIC, cambio e euro.

## Objetivo

Construir um chatbot de portfolio que responda perguntas financeiras com base em dados reais do BCB, combinando:

- ingestao automatica das series via API oficial;
- processamento incremental dos dados dos ultimos 24 meses;
- recuperacao semantica com LangChain + ChromaDB;
- respostas geradas por LLM via Groq;
- interface web simples para demonstracao e exploracao.

## O que foi implementado

- Download incremental das series `IPCA`, `SELIC`, `cambio` e `euro` via API SGS do Banco Central.
- Normalizacao dos dados e manutencao de janela de 24 meses para manter o projeto leve.
- Pipeline RAG com:
  - carregamento dos CSVs;
  - semantic chunking;
  - embeddings com `intfloat/multilingual-e5-small`;
  - armazenamento vetorial com ChromaDB.
- Rebuild incremental do banco vetorial, evitando reprocessar embeddings quando os CSVs nao mudam.
- Chat em Streamlit com historico de conversa e inicializacao automatica do ambiente.
- Resumo dos ultimos valores das series injetado no contexto para melhorar respostas objetivas.
- Ajuste operacional para uso de modelo Groq mais leve, reduzindo impacto de rate limit.

## Arquitetura

### Fluxo de dados

1. `ingestion/load_bcb.py` baixa e atualiza os CSVs em `data/raw/`.
2. `executar_pipeline.py` calcula fingerprint dos arquivos e decide se precisa reconstruir o vetor.
3. `rag/Etapa_01_LoaderDados.py` transforma linhas dos CSVs em documentos.
4. `rag/Etapa_03_ChunkSemantico.py` cria chunks semanticos.
5. `rag/Etapa_04_VectoreStore.py` persiste embeddings no Chroma em `data/vector_db/`.
6. `rag/Etapa_06_Cadeias.py` monta a cadeia de consulta com retriever + prompt + Groq.
7. `app.py` inicializa tudo e expõe a interface em Streamlit.

### Estrutura do projeto

```text
.
|-- app.py
|-- executar_pipeline.py
|-- ingestion/
|   `-- load_bcb.py
|-- rag/
|   |-- Etapa_01_LoaderDados.py
|   |-- Etapa_02_Embeddings.py
|   |-- Etapa_03_ChunkSemantico.py
|   |-- Etapa_04_VectoreStore.py
|   |-- Etapa_05_Prompts.py
|   `-- Etapa_06_Cadeias.py
|-- data/
|   |-- raw/
|   `-- vector_db/
|-- SOLUCAO_RATE_LIMIT.md
|-- Dockerfile
`-- docker-compose.yml
```

## Stack

- Python
- Streamlit
- LangChain
- LangChain Community / HuggingFace / Groq
- ChromaDB
- Sentence Transformers
- Pandas
- API SGS do Banco Central do Brasil

## Requisitos

- Python 3.10 ou superior
- Chave da Groq
- Acesso a internet para baixar as series do BCB e o modelo de embeddings na primeira execucao

## Configuracao local

1. Crie e ative um ambiente virtual.
2. Instale as dependencias:

```bash
pip install -r requirements.txt
```

3. Crie o arquivo `.env` a partir de `.env.example`.

Exemplo:

```env
GROQ_API_KEY=sua_chave_aqui
GROQ_MODEL=llama-3.1-8b-instant
```

## Como executar

### Subir a aplicacao

```bash
streamlit run app.py
```

A aplicacao:

- sincroniza os dados do BCB ao iniciar;
- reaproveita o banco vetorial quando nao ha mudancas;
- reconstrui embeddings apenas quando os CSVs sao atualizados.

### Rodar apenas o pipeline

```bash
python executar_pipeline.py
```

## Docker

Criar `Dockerfile` e `docker-compose.yml` faz sentido neste projeto. O ambiente usa dependencias de NLP, embeddings, banco vetorial local e uma interface Streamlit; containerizar isso reduz variacao de ambiente e facilita demonstracao, onboarding e execucao futura.

### Build e execucao com Docker Compose

```bash
docker compose up --build
```

A aplicacao ficara disponivel em `http://localhost:8501`.

Os volumes configurados mantem persistentes:

- `data/raw` com os CSVs baixados;
- `data/vector_db` com a base vetorial do Chroma.

### Variaveis de ambiente no Docker

O `docker-compose.yml` usa o arquivo `.env` do projeto. Garanta que ele exista antes de subir os containers.

## Decisoes tecnicas

### Embeddings

Foi escolhido `intfloat/multilingual-e5-small` por equilibrar:

- suporte melhor a portugues;
- custo computacional menor;
- desempenho suficiente para um caso de portfolio com base pequena e estruturada.

### Modelo LLM

Foi mantido `llama-3.1-8b-instant` como recomendacao principal porque:

- responde mais rapido;
- consome menos tokens;
- reduz o risco de rate limit em contas gratuitas da Groq;
- atende bem consultas financeiras curtas e objetivas.

Detalhes adicionais estao em [SOLUCAO_RATE_LIMIT.md](/E:/desenvolvimento/pot-rag_financial_analysis/SOLUCAO_RATE_LIMIT.md).

### Rebuild incremental

O pipeline salva um fingerprint dos CSVs em `data/vector_db/pipeline_state.json`. Se os dados nao mudarem, o projeto reaproveita a base vetorial existente e evita recomputar embeddings desnecessariamente.

## Exemplos de perguntas

- `Qual o valor atual do IPCA?`
- `Como esta a SELIC hoje?`
- `Qual a cotacao do dolar mais recente?`
- `Mostre a variacao do euro no ultimo mes`
- `Qual foi a inflacao nos ultimos 12 meses?`
- `Compare o cambio de hoje com o mes passado`
- `Qual a tendencia da SELIC no trimestre?`

## Limitacoes atuais

- O projeto depende de um provedor externo de LLM.
- A primeira execucao pode ser mais lenta por causa do download do modelo de embeddings.
- O conjunto de dados esta restrito a quatro series economicas.
- Ainda nao ha suite automatizada de testes.

## Melhorias futuras

- adicionar cache de respostas;
- adicionar fallback entre provedores de LLM;
- ampliar o conjunto de series economicas;
- incluir observabilidade e logs estruturados;
- criar testes automatizados para ingestao e pipeline.

## Autor

Desenvolvido por Caio Barroso.
