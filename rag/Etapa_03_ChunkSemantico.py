import sys
import os

# Adiciona o diretório raiz do projeto ao PYTHONPATH para permitir importações do pacote 'rag'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_experimental.text_splitter import SemanticChunker
from rag.Etapa_01_LoaderDados import realizar_carregamento
from rag.Etapa_02_Embeddings import carregar_modelo_embeddings

# --- ETAPA 3: DIVISÃO SEMÂNTICA (SEMANTIC CHUNKING) ---
# O SemanticChunker usa IA para entender o contexto do texto.
# Ele decide onde cortar baseando-se no significado das frases, mantendo a coerência.

def realizar_chunking_semantico(documentos):
    """
    Divide os documentos usando inteligência semântica para manter o contexto.
    """
    # Carregamos o 'motor' de embeddings da Etapa 2
    modelo_embeddings = carregar_modelo_embeddings()
    
    # Inicializamos o divisor semântico
    divisor = SemanticChunker(modelo_embeddings)
    
    # Realizamos a divisão
    chunks = divisor.split_documents(documentos)
    return chunks

if __name__ == "__main__":
    print("--- Iniciando a divisão SEMÂNTICA dos documentos ---")
    
    # 1. Carrega os dados (Etapa 1)
    docs, _ = realizar_carregamento()
    
    # 2. Divide semânticamente (Etapa 3)
    chunks = realizar_chunking_semantico(docs)
    
    print(f"--- Divisão concluída! {len(chunks)} pedaços inteligentes gerados. ---\n")
    if chunks:
        print("Exemplo de um pedaço gerado semânticamente:")
        print(chunks[0].page_content)
