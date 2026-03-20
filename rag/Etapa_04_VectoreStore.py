import os
import shutil
import sys

from langchain_community.vectorstores import Chroma

from rag.Etapa_02_Embeddings import carregar_modelo_embeddings

# Adiciona o diretorio raiz do projeto ao PYTHONPATH para permitir importacoes do pacote 'rag'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

DIRETORIO_BANCO = "data/vector_db"
NOME_COLECAO = "rag_financial"
TAMANHO_LOTE = 128


def _recriar_diretorio_banco() -> None:
    if os.path.exists(DIRETORIO_BANCO):
        shutil.rmtree(DIRETORIO_BANCO)
    os.makedirs(DIRETORIO_BANCO, exist_ok=True)


def criar_banco_vetores(pedacos_de_texto):
    """
    Recebe os pedaços de texto, transforma em vetores em lotes e salva no disco.
    """
    if not pedacos_de_texto:
        raise ValueError("Nenhum pedaço de texto foi fornecido para vetorização.")

    modelo_embeddings = carregar_modelo_embeddings()
    _recriar_diretorio_banco()

    banco = Chroma(
        persist_directory=DIRETORIO_BANCO,
        embedding_function=modelo_embeddings,
        collection_name=NOME_COLECAO,
    )

    total = len(pedacos_de_texto)
    for inicio in range(0, total, TAMANHO_LOTE):
        fim = min(inicio + TAMANHO_LOTE, total)
        lote = pedacos_de_texto[inicio:fim]
        ids = [f"doc-{i}" for i in range(inicio, fim)]
        banco.add_documents(documents=lote, ids=ids)

    return banco


def carregar_banco_vetores():
    """
    Carrega o banco persistido anteriormente.
    """
    modelo_embeddings = carregar_modelo_embeddings()
    return Chroma(
        persist_directory=DIRETORIO_BANCO,
        embedding_function=modelo_embeddings,
        collection_name=NOME_COLECAO,
    )


if __name__ == "__main__":
    print(f"--- Inicializando o Banco de Vetores em {DIRETORIO_BANCO} ---")
    if not os.path.exists(DIRETORIO_BANCO):
        print(
            f"O banco ainda nao existe em {DIRETORIO_BANCO}. "
            "Ele sera criado quando rodarmos o pipeline completo."
        )
    else:
        print(f"Banco de vetores localizado em {DIRETORIO_BANCO}")
