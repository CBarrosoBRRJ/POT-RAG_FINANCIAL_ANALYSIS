import os
import sys

import pandas as pd
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

from rag.Etapa_04_VectoreStore import carregar_banco_vetores
from rag.Etapa_05_Prompts import obter_prompt_financeiro

# Adiciona o diretorio raiz do projeto ao PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()

PASTA_RAW = os.path.join("data", "raw")
SERIES_MAP = {
    "ipca": "IPCA",
    "selic": "SELIC",
    "cambio": "CAMBIO",
    "euro": "EURO",
}


def _resumo_mais_recente_series() -> str:
    linhas = []
    for nome_arquivo, rotulo in SERIES_MAP.items():
        caminho = os.path.join(PASTA_RAW, f"{nome_arquivo}.csv")
        if not os.path.exists(caminho):
            continue
        try:
            df = pd.read_csv(caminho)
            if df.empty or "data" not in df.columns or "valor" not in df.columns:
                continue
            df["data"] = pd.to_datetime(df["data"], errors="coerce")
            df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
            df = df.dropna(subset=["data", "valor"]).sort_values("data")
            if df.empty:
                continue
            ultima_linha = df.iloc[-1]
            data_txt = ultima_linha["data"].strftime("%d/%m/%Y")
            valor_txt = f"{float(ultima_linha['valor']):.2f}".replace(".", ",")
            linhas.append(f"- {rotulo}: ultimo valor {valor_txt} em {data_txt}")
        except Exception:
            continue

    if not linhas:
        return "Resumo de ultimos valores indisponivel."
    return "Resumo de ultimos valores por serie:\n" + "\n".join(linhas)


def criar_cadeia_consulta():
    """
    Configura a chain usando LCEL com contexto recuperado do vetor + resumo recente dos CSVs.
    """
    api_key = os.getenv("GROQ_API_KEY")
    modelo_nome = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    if not api_key:
        print("AVISO: GROQ_API_KEY nao encontrada no arquivo .env.")

    llm = ChatGroq(
        groq_api_key=api_key,
        model_name=modelo_nome,
        temperature=0.35,
    )

    banco = carregar_banco_vetores()
    retriever = banco.as_retriever(search_kwargs={"k": 35})
    prompt_template = obter_prompt_financeiro()

    def formatar_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def buscar_com_fontes(pergunta):
        docs = retriever.invoke(pergunta)
        contexto_rag = formatar_docs(docs)
        contexto_recente = _resumo_mais_recente_series()
        contexto_final = f"{contexto_recente}\n\nContexto recuperado do RAG:\n{contexto_rag}"

        resposta = (prompt_template | llm | StrOutputParser()).invoke(
            {"context": contexto_final, "question": pergunta}
        )

        return {"result": resposta, "source_documents": docs}

    return buscar_com_fontes


if __name__ == "__main__":
    try:
        criar_cadeia_consulta()
        print("--- Cadeia de Consulta configurada com sucesso! ---")
        print(f"Modelo LLM: {os.getenv('GROQ_MODEL')}")
    except Exception as e:
        print(f"Erro ao configurar a Chain: {e}")
