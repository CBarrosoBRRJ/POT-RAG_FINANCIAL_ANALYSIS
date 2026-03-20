import sys
import os

# Adiciona o diretório raiz do projeto ao PYTHONPATH para permitir importações do pacote 'rag'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_huggingface import HuggingFaceEmbeddings

# --- ETAPA 1: ESCOLHA DO MODELO DE EMBEDDING ---
# O modelo 'multilingual-e5-small' é superior ao MiniLM para o português (multilíngue).
# Ele é leve, rápido e foi treinado especificamente para busca semântica em diversos idiomas.
# Diferença: Enquanto o MiniLM é focado em inglês, o E5-Small entende muito melhor o contexto brasileiro.
MODELO = "intfloat/multilingual-e5-small"

def carregar_modelo_embeddings():
    """
    Inicializa e retorna o modelo que transforma texto em vetores numéricos.
    """
    modelo = HuggingFaceEmbeddings(
        model_name=MODELO,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"batch_size": 32},
    )
    return modelo

# --- ETAPA 2: TESTE PRÁTICO ---
if __name__ == "__main__":
    print(f"--- Carregando modelo de embeddings: {MODELO} ---")
    modelo_teste = carregar_modelo_embeddings()
    texto_exemplo = "A taxa Selic subiu para 13.75% ao ano."
    vetor_gerado = modelo_teste.embed_query(texto_exemplo)
    
    print("\n--- Teste de Conversão Concluído ---")
    print(f"Texto Original: '{texto_exemplo}'")
    print(f"Tamanho do Vetor Gerado: {len(vetor_gerado)} números")
