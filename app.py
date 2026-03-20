import os
import time
from datetime import datetime

import streamlit as st

from executar_pipeline import iniciar_pipeline
from ingestion.load_bcb import SERIES, download_bcb
from rag.Etapa_06_Cadeias import criar_cadeia_consulta

st.set_page_config(
    page_title="Chat Análise Financeira BCB",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS Profissional Moderno
st.markdown(
    """
<style>
    /* Global Styles */
    html, body {
        overflow-x: hidden !important;
        max-width: 100vw !important;
    }

    [data-testid="stApp"] {
        overflow-x: hidden !important;
        max-width: 100vw !important;
    }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
        overflow-x: hidden !important;
        max-width: 100vw !important;
    }

    .main {
        overflow-x: hidden !important;
        max-width: 100% !important;
    }

    .main .block-container {
        max-width: 1200px;
        width: 100%;
        padding: 2rem 1rem 1rem 1rem;
        overflow-x: hidden !important;
    }

    [data-testid="stAppViewBlockContainer"] {
        max-width: 1200px;
        width: 100%;
        padding-left: 1rem;
        padding-right: 1rem;
        overflow-x: hidden !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #161b22;
        border-right: 1px solid #30363d;
        overflow-x: hidden !important;
        overflow-y: auto !important;
        max-width: 100% !important;
        height: 100vh !important;
    }

    section[data-testid="stSidebar"] > div {
        padding: 1.5rem 1rem !important;
        overflow-x: hidden !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        height: auto !important;
    }

    section[data-testid="stSidebar"] * {
        max-width: 100% !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
    }

    section[data-testid="stSidebar"] h2 {
        font-size: 1rem !important;
        margin-bottom: 1rem !important;
    }

    section[data-testid="stSidebar"] h3 {
        font-size: 0.9rem !important;
        margin: 1rem 0 0.5rem 0 !important;
    }

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] li {
        font-size: 0.85rem !important;
        line-height: 1.5 !important;
        margin-bottom: 0.4rem !important;
    }

    section[data-testid="stSidebar"] ul {
        padding-left: 1.2rem !important;
        margin: 0.5rem 0 !important;
    }

    /* Header */
    .chat-header {
        text-align: center;
        padding: 1.5rem 1rem 2rem 1rem;
        border-bottom: 1px solid #30363d;
        margin-bottom: 2rem;
        width: 100%;
        overflow-wrap: anywhere;
    }

    .chat-header h1 {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0 0 0.75rem 0;
        letter-spacing: -0.02em;
    }

    .chat-header p {
        color: #8b949e;
        font-size: 0.95rem;
        margin: 0.5rem auto;
        max-width: min(700px, 100%);
        line-height: 1.6;
    }

    .chat-header a {
        color: #58a6ff;
        text-decoration: none;
    }

    .chat-header a:hover {
        text-decoration: underline;
    }

    /* Chat Messages - Usando componentes nativos do Streamlit */
    .stChatMessage {
        padding: 1rem !important;
        margin-bottom: 1rem !important;
        border-radius: 12px !important;
        box-shadow: none !important;
        width: 100% !important;
        max-width: 100% !important;
        overflow-wrap: anywhere !important;
        word-wrap: break-word !important;
        overflow-x: hidden !important;
    }

    [data-testid="stChatMessageContent"] {
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
        width: 100% !important;
        max-width: 100% !important;
        overflow-wrap: anywhere !important;
        word-wrap: break-word !important;
        overflow-x: hidden !important;
    }

    [data-testid="stChatMessageContent"] * {
        max-width: 100% !important;
        overflow-wrap: break-word !important;
        word-wrap: break-word !important;
    }

    /* User messages */
    .stChatMessage[data-testid*="user"] {
        background: linear-gradient(135deg, #1f6feb 0%, #58a6ff 100%) !important;
        box-shadow: none !important;
    }

    .stChatMessage[data-testid*="user"] p {
        color: #ffffff !important;
    }

    /* Assistant messages */
    .stChatMessage[data-testid*="assistant"] {
        background: #21262d !important;
        border: 1px solid #30363d !important;
        box-shadow: none !important;
    }

    .stChatMessage[data-testid*="assistant"] p {
        color: #e6edf3 !important;
    }

    /* Remover qualquer sombra residual */
    .stChatMessage::after,
    .stChatMessage::before {
        display: none !important;
    }

    /* Chat Input */
    .stChatInputContainer {
        border-top: 1px solid #30363d !important;
        background: #0d1117 !important;
        padding: 1rem 0 !important;
    }

    .stChatInput {
        max-width: 900px !important;
        width: 100% !important;
        margin: 0 auto !important;
    }

    .stChatInput > div {
        background: #161b22 !important;
        border: 1.5px solid #30363d !important;
        border-radius: 12px !important;
        width: 100% !important;
    }

    .stChatInput input {
        color: #ffffff !important;
        font-size: 0.95rem !important;
    }

    .stChatInput input::placeholder {
        color: #6e7681 !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #1f6feb 0%, #58a6ff 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(88, 166, 255, 0.3);
    }

    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #1f6feb 0%, #58a6ff 100%);
    }

    /* Divider */
    hr {
        border-color: #30363d !important;
        margin: 1.5rem 0 !important;
    }

    /* Empty state */
    .empty-chat-state {
        text-align: center;
        padding: 4rem 2rem;
        color: #8b949e;
    }

    .empty-chat-state h3 {
        color: #c9d1d9;
        margin-bottom: 1rem;
    }

    /* Responsive */
    @media (max-width: 1100px) {
        .main .block-container,
        [data-testid="stAppViewBlockContainer"] {
            max-width: 100% !important;
            padding-left: 0.875rem;
            padding-right: 0.875rem;
        }

        .chat-header {
            padding: 1.25rem 0.75rem 1.5rem 0.75rem;
            margin-bottom: 1.5rem;
        }
    }

    @media (max-width: 900px) {
        .main .block-container,
        [data-testid="stAppViewBlockContainer"] {
            max-width: 100% !important;
            padding-left: 0.75rem;
            padding-right: 0.75rem;
        }

        .chat-header h1 {
            font-size: 1.65rem;
        }

        .chat-header p {
            font-size: 0.9rem;
        }
    }

    @media (max-width: 768px) {
        .chat-header h1 {
            font-size: 1.5rem;
        }

        .main .block-container {
            max-width: 100% !important;
            padding: 1rem 0.5rem;
        }

        [data-testid="stAppViewBlockContainer"] {
            max-width: 100% !important;
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }

        .chat-header {
            padding: 1rem 0.25rem 1.25rem 0.25rem;
        }

        .stChatMessage {
            padding: 0.875rem !important;
        }

        section[data-testid="stSidebar"] {
            max-width: 280px !important;
        }
    }

    @media (max-width: 480px) {
        .chat-header h1 {
            font-size: 1.25rem;
        }

        .chat-header p,
        [data-testid="stChatMessageContent"] {
            font-size: 0.88rem !important;
        }

        .main .block-container,
        [data-testid="stAppViewBlockContainer"] {
            max-width: 100% !important;
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }

        section[data-testid="stSidebar"] {
            max-width: 240px !important;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)


def preparar_ambiente():
    """Inicializa o sistema: baixa dados do BCB e prepara pipeline RAG"""
    container_loader = st.empty()
    logs: list[str] = []

    with container_loader.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 🔄 Sincronizando com Banco Central")
            st.markdown(
                "<p style='text-align: center; color: #8b949e;'>"
                "Carregando dados mais recentes para sua consulta..."
                "</p>",
                unsafe_allow_html=True,
            )

            status_texto = st.empty()
            barra_progresso = st.progress(0)
            percentual_texto = st.empty()
            logs_placeholder = st.empty()

            def atualizar_progresso(valor: int):
                valor = max(0, min(100, int(valor)))
                barra_progresso.progress(valor)
                percentual_texto.markdown(
                    f"<p style='text-align: center; font-weight: 600; color: #58a6ff;'>{valor}%</p>",
                    unsafe_allow_html=True,
                )

            def adicionar_log(msg: str):
                if (msg.startswith("-> Passo") or msg.startswith("---")) and logs:
                    logs.append("")
                logs.append(msg)
                logs_placeholder.code("\n".join(logs[-20:]), language="text")
                time.sleep(0.2)

            # Passo 1: Dados BCB
            status_texto.markdown(
                "**Passo 1/3:** Coletando indicadores econômicos...",
                unsafe_allow_html=True,
            )
            adicionar_log("-> Iniciando download de séries do BCB")

            total_series = len(SERIES)
            houve_atualizacao = False
            datas_min = []
            datas_max = []

            for i, (nome, codigo) in enumerate(SERIES.items()):
                try:
                    resumo = download_bcb(nome, codigo)
                    houve_atualizacao = houve_atualizacao or bool(resumo.get("atualizado"))
                    if resumo.get("data_min"):
                        datas_min.append(resumo["data_min"])
                    if resumo.get("data_max"):
                        datas_max.append(resumo["data_max"])
                except Exception as e:
                    adicionar_log(f"[ERRO] {nome}: {e}")

                progresso = int(((i + 1) / total_series) * 40)
                atualizar_progresso(progresso)

            datas_min_dt = [
                datetime.strptime(d, "%d/%m/%Y") for d in datas_min if d
            ]
            datas_max_dt = [
                datetime.strptime(d, "%d/%m/%Y") for d in datas_max if d
            ]
            data_inicial = (
                min(datas_min_dt).strftime("%d/%m/%Y") if datas_min_dt else "-"
            )
            data_final = (
                max(datas_max_dt).strftime("%d/%m/%Y") if datas_max_dt else "-"
            )
            adicionar_log(
                f"-> {total_series} séries carregadas ({data_inicial} a {data_final})"
            )

            # Passo 2: Pipeline
            status_texto.markdown(
                "**Passo 2/3:** Processando base vetorial...",
                unsafe_allow_html=True,
            )
            adicionar_log("-> Verificando atualizações no banco de dados")

            if houve_atualizacao:
                adicionar_log("-> Atualizando pipeline RAG")
            else:
                adicionar_log("-> Reutilizando base vetorial existente")

            try:
                iniciar_pipeline(
                    log_callback=adicionar_log,
                    progress_callback=atualizar_progresso,
                    validate_chain=False,
                )
            except Exception as e:
                adicionar_log(f"[ERRO] Pipeline: {e}")
                if not os.path.exists(os.path.join("data", "vector_db", "chroma.sqlite3")):
                    raise

            # Passo 3: Cadeia
            status_texto.markdown(
                "**Passo 3/3:** Conectando modelo de linguagem...",
                unsafe_allow_html=True,
            )
            atualizar_progresso(95)
            cadeia_final = criar_cadeia_consulta()
            atualizar_progresso(100)
            adicionar_log("✅ Sistema pronto!")
            time.sleep(0.5)

    container_loader.empty()
    return cadeia_final


# Inicialização do sistema
try:
    if "sistema_pronto" not in st.session_state:
        st.session_state.cadeia = preparar_ambiente()
        st.session_state.sistema_pronto = True
    cadeia = st.session_state.cadeia
except Exception as e:
    st.error(f"❌ Erro ao carregar sistema: {e}")
    st.stop()

# Sidebar
with st.sidebar:
    st.markdown(
        """
<div style="text-align: center; margin-bottom: 1.5rem;">
    <h2 style="font-size: 1.1rem; letter-spacing: 0.05em;">SOBRE O SISTEMA</h2>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
Sistema de consulta baseado em **RAG (Retrieval-Augmented Generation)**
com dados oficiais do Banco Central do Brasil.

### Pipeline de Processamento
1. **Ingestão** - Download automático via API BCB
2. **Processamento** - Últimos 24 meses
3. **Chunking** - Segmentação semântica
4. **Embeddings** - multilingual-e5-small
5. **Vetorização** - ChromaDB
6. **Consulta** - LangChain + Groq

### Séries Disponíveis
- **IPCA** - Inflação oficial
- **SELIC** - Taxa básica de juros
- **Câmbio** - Dólar (USD/BRL)
- **Euro** - EUR/BRL
"""
    )

    st.divider()

    if st.button("Exemplos de perguntas", use_container_width=True):
        import random

        perguntas = [
            "O que você pode me ajudar?",
            "Qual o valor atual do IPCA?",
            "Como está a SELIC hoje?",
            "Qual a cotação do dólar mais recente?",
            "Mostre a variação do euro no último mês",
            "Qual foi a inflação nos últimos 12 meses?",
            "Compare o câmbio de hoje com o mês passado",
            "Qual a tendência da SELIC no trimestre?",
            "O IPCA está subindo ou descendo?",
            "Mostre os valores mais recentes de todas as séries",
        ]
        st.session_state.pending_prompt = random.choice(perguntas)
        st.rerun()

    st.divider()

    st.markdown(
        """
<div style="font-size: 0.85rem; color: #8b949e; text-align: center; line-height: 1.6;">
    Desenvolvido por <strong>Caio Barroso</strong><br>
    <a href="https://www.linkedin.com/in/caio-barroso-ia-datascience" target="_blank" style="color: #58a6ff; text-decoration: none;">LinkedIn</a><br>
    <span style="font-size: 0.75rem;">RAG • LangChain • Groq • ChromaDB</span>
</div>
""",
        unsafe_allow_html=True,
    )

# Header
st.markdown(
    """
<div class="chat-header">
    <h1>Consulta API Banco Central</h1>
    <p style="font-size: 0.9rem; color: #8b949e; margin-top: 0.75rem; line-height: 1.6;">
        Sistema de consulta a dados macroeconômicos do Banco Central do Brasil via
        <a href="https://api.bcb.gov.br" target="_blank" style="color: #58a6ff; text-decoration: none;">API SGS</a>
        <br>
        <span style="font-size: 0.85rem; color: #6e7681;">
            Séries disponíveis: IPCA, SELIC, Câmbio (USD/BRL) e Euro (EUR/BRL)
        </span>
    </p>
</div>
""",
    unsafe_allow_html=True,
)

# Inicializar histórico
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = ""


def montar_contexto_memoria(pergunta_atual: str, limite: int = 8) -> str:
    """Monta contexto com histórico recente para continuidade da conversa"""
    historico = st.session_state.get("messages", [])
    pares = []
    pergunta_aberta = None

    for msg in historico:
        role = msg.get("role")
        content = (msg.get("content") or "").strip()
        if not content:
            continue

        if role == "user":
            if pergunta_aberta is not None:
                pares.append((pergunta_aberta, ""))
            pergunta_aberta = content
        elif role == "assistant" and pergunta_aberta is not None:
            pares.append((pergunta_aberta, content))
            pergunta_aberta = None

    if pergunta_aberta is not None:
        pares.append((pergunta_aberta, ""))

    pares = pares[-limite:]
    if not pares:
        return pergunta_atual

    linhas = []
    for i, (q, a) in enumerate(pares, start=1):
        linhas.append(f"Q{i}: {q}")
        if a:
            linhas.append(f"A{i}: {a}")

    return (
        "Histórico da conversa:\n"
        + "\n".join(linhas)
        + f"\n\nPergunta atual: {pergunta_atual}"
    )


# Renderizar mensagens do histórico
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input do usuário
prompt = st.chat_input("Faça sua consulta sobre IPCA, SELIC, câmbio ou euro...")

# Processar prompt pendente do botão
if not prompt:
    prompt = st.session_state.pop("pending_prompt", "")

if prompt:
    prompt = prompt.strip()
    if prompt:
        # Mostrar mensagem do usuário com efeito de digitação
        with st.chat_message("user"):
            def gerar_stream_user():
                for char in prompt:
                    yield char
                    time.sleep(0.005)

            st.write_stream(gerar_stream_user())

        # Adicionar ao histórico após renderizar
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Processar resposta com efeito de digitação
        with st.chat_message("assistant"):
            try:
                pergunta_ctx = montar_contexto_memoria(prompt, limite=8)
                resposta_raw = cadeia(pergunta_ctx)
                resposta_texto = resposta_raw.get("result", "Sem resposta disponível")

                # Efeito de digitação humanizado
                def gerar_stream():
                    for char in resposta_texto:
                        yield char
                        time.sleep(0.01)

                st.write_stream(gerar_stream())
                resposta_completa = resposta_texto

            except Exception as e:
                resposta_completa = f"Erro ao processar consulta: {str(e)}"
                st.markdown(resposta_completa)

        # Adicionar resposta ao histórico após renderizar
        st.session_state.messages.append(
            {"role": "assistant", "content": resposta_completa}
        )
