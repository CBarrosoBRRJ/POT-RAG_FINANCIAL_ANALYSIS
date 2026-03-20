import os
from datetime import datetime, timedelta
from typing import Dict

import pandas as pd
import requests

# CONFIGURACAO DAS SERIES (SGS - Banco Central)
SERIES = {
    "ipca": 433,
    "selic": 1178,
    "cambio": 1,
    "euro": 21619,
}

PASTA_RAW = os.path.join("data", "raw")
JANELA_MESES = 24
TIMEOUT_SEGUNDOS = 30


def _data_inicial_janela() -> datetime:
    return datetime.now() - timedelta(days=JANELA_MESES * 30)


def _url_serie(codigo: int) -> str:
    data_inicial = _data_inicial_janela().strftime("%d/%m/%Y")
    return (
        f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"
        f"?dataInicial={data_inicial}&formato=json"
    )


def _normalizar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["data", "valor"])

    df = df.copy()
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    datas = df["data"].astype(str).str.strip()
    mascara_br = datas.str.contains("/", regex=False)
    data_br = pd.to_datetime(
        datas.where(mascara_br), format="%d/%m/%Y", errors="coerce"
    )
    data_iso = pd.to_datetime(
        datas.where(~mascara_br), format="%Y-%m-%d", errors="coerce"
    )
    df["data"] = data_br.fillna(data_iso)
    df = df.dropna(subset=["data", "valor"])
    df = df.drop_duplicates(subset=["data"], keep="last")
    df = df.sort_values("data")
    return df[["data", "valor"]]


def _carregar_existente(caminho: str) -> pd.DataFrame:
    if not os.path.exists(caminho):
        return pd.DataFrame(columns=["data", "valor"])

    existente = pd.read_csv(caminho)
    return _normalizar_dataframe(existente)


def download_bcb(nome: str, codigo: int) -> Dict[str, object]:
    """
    Baixa os dados recentes do BCB e atualiza incrementalmente o CSV local.
    Mantem somente os ultimos 24 meses para manter performance.
    """
    os.makedirs(PASTA_RAW, exist_ok=True)
    save_path = os.path.join(PASTA_RAW, f"{nome}.csv")
    inicio_janela = _data_inicial_janela()

    print(f"Baixando serie: {nome.upper()} (SGS {codigo})...")

    response = requests.get(_url_serie(codigo), timeout=TIMEOUT_SEGUNDOS)
    response.raise_for_status()

    remoto_df = _normalizar_dataframe(pd.DataFrame(response.json()))
    existente_df = _carregar_existente(save_path)

    if not existente_df.empty:
        existente_df = existente_df[existente_df["data"] >= inicio_janela]

    datas_antes = set(existente_df["data"].tolist())
    combinado = pd.concat([existente_df, remoto_df], ignore_index=True)
    combinado = _normalizar_dataframe(combinado)
    combinado = combinado[combinado["data"] >= inicio_janela]

    existente_ordenado = existente_df.sort_values("data").reset_index(drop=True)
    combinado_ordenado = combinado.sort_values("data").reset_index(drop=True)
    sem_mudancas = existente_ordenado.equals(combinado_ordenado)

    datas_depois = set(combinado_ordenado["data"].tolist())
    novos_registros = len(datas_depois - datas_antes)
    atualizado = not sem_mudancas

    if atualizado:
        combinado_ordenado.to_csv(save_path, index=False)
        print(f"Sucesso! Arquivo atualizado em: {save_path}")
    else:
        print(f"Sem novidades para {nome.upper()}. Arquivo local mantido.")

    return {
        "serie": nome,
        "arquivo": save_path,
        "registros_totais": int(len(combinado_ordenado)),
        "novos_registros": int(novos_registros),
        "atualizado": bool(atualizado),
        "data_min": (
            combinado_ordenado["data"].min().strftime("%d/%m/%Y")
            if not combinado_ordenado.empty
            else None
        ),
        "data_max": (
            combinado_ordenado["data"].max().strftime("%d/%m/%Y")
            if not combinado_ordenado.empty
            else None
        ),
    }


if __name__ == "__main__":
    for nome, codigo in SERIES.items():
        try:
            resumo = download_bcb(nome, codigo)
            print(
                f"{resumo['serie'].upper()}: {resumo['registros_totais']} registros "
                f"({resumo['novos_registros']} novos)."
            )
        except Exception as e:
            print(f"Erro ao processar {nome}: {e}")
