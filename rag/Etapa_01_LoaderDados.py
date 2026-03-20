from langchain_community.document_loaders import CSVLoader
import os

# --- ETAPA 1: LOCALIZAR OS ARQUIVOS NA PASTA DE DADOS BRUTOS ---
## Local da pasta de dados brutos
PASTA_DADOS = "data/raw"


# --- ETAPA 2: FUNÇÃO PARA CARREGAR ARQUIVOS CSV ---
def realizar_carregamento():
    """
    Lista e carrega todos os arquivos CSV da pasta de dados brutos.
    """
    # Identifica os arquivos disponíveis
    arquivos = [f for f in os.listdir(PASTA_DADOS) if f.endswith('.csv')]
    
    documentos_completos = []
    
    # Percorre cada arquivo e carrega seu conteúdo
    for arquivo in arquivos:
        caminho_arquivo = os.path.join(PASTA_DADOS, arquivo)
        
        # Extrai o nome da série do nome do arquivo (ex: 'selic.csv' -> 'selic')
        nome_serie = arquivo.replace('.csv', '').upper()
        
        # O CSVLoader por padrão coloca cada linha como um documento.
        # Vamos configurar para que o conteúdo inclua o nome da série para facilitar a busca.
        carregador = CSVLoader(
            file_path=caminho_arquivo,
            source_column="data", # Usa a data como fonte principal no metadado
            content_columns=["data", "valor"],
            metadata_columns=["data"]
        )
        documentos_temporarios = carregador.load()
        
        # Adiciona o nome da série ao conteúdo de cada documento para melhorar a recuperação
        for doc in documentos_temporarios:
            # Pegamos o valor e a data do conteúdo para formatar melhor
            linhas = doc.page_content.split('\n')
            data_valor = {l.split(': ')[0]: l.split(': ')[1] for l in linhas if ': ' in l}
            
            data_str = data_valor.get('data', 'N/A')
            valor_str = data_valor.get('valor', 'N/A')
            
            doc.page_content = f"Série: {nome_serie} | Data: {data_str} | Valor: {valor_str}"
            
        documentos_completos.extend(documentos_temporarios)

    return documentos_completos, arquivos


# --- CHAMANDO A FUNÇÃO DE CARREGAMENTO ---
if __name__ == "__main__":

    print('Iniciando o carregamento dos dados...')
    print('')

    # Executa a função e recebe os documentos e a lista de arquivos
    documentos, lista_arquivos = realizar_carregamento()
    
    print(f"-> Localizados {len(lista_arquivos)} arquivos CSV na pasta '{PASTA_DADOS}': {lista_arquivos}")
    print('Dados carregados com sucesso!')
    print('--- RESUMO ---')
    print(f"Total de arquivos processados: {len(lista_arquivos)}")
    print(f"Total de linhas (documentos) carregadas: {len(documentos)}")
    print('---')
    print('Finalizado o carregamento dos dados. Próxima etapa: Chunking (divisão em pedaços).')