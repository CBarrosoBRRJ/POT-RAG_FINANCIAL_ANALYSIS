import hashlib
import json
import os
from datetime import datetime
from typing import Callable, Dict, Optional

from rag.Etapa_01_LoaderDados import realizar_carregamento
from rag.Etapa_03_ChunkSemantico import realizar_chunking_semantico
from rag.Etapa_04_VectoreStore import criar_banco_vetores
from rag.Etapa_06_Cadeias import criar_cadeia_consulta

VECTOR_DIR = os.path.join("data", "vector_db")
STATE_PATH = os.path.join(VECTOR_DIR, "pipeline_state.json")


def _emit_log(log_callback: Optional[Callable[[str], None]], msg: str) -> None:
    print(msg)
    if log_callback:
        log_callback(msg)


def _emit_progress(
    progress_callback: Optional[Callable[[int], None]], value: int
) -> None:
    if progress_callback:
        progress_callback(value)


def _fingerprint_csv_files(arquivos: list[str]) -> str:
    payload = []
    for arquivo in sorted(arquivos):
        caminho = os.path.join("data", "raw", arquivo)
        stat = os.stat(caminho)
        payload.append(
            {"arquivo": arquivo, "size": stat.st_size, "mtime_ns": stat.st_mtime_ns}
        )
    serializado = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(serializado.encode("utf-8")).hexdigest()


def _carregar_estado_anterior() -> Dict[str, object]:
    if not os.path.exists(STATE_PATH):
        return {}
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _salvar_estado(estado: Dict[str, object]) -> None:
    os.makedirs(VECTOR_DIR, exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=2)


def _banco_vetorial_existe() -> bool:
    return os.path.exists(os.path.join(VECTOR_DIR, "chroma.sqlite3"))


def iniciar_pipeline(
    log_callback: Optional[Callable[[str], None]] = None,
    progress_callback: Optional[Callable[[int], None]] = None,
    force_rebuild: bool = False,
    validate_chain: bool = True,
) -> Dict[str, object]:
    """
    Executa o pipeline do RAG com rebuild incremental.
    Reprocessa embeddings somente quando os CSVs mudam ou quando force_rebuild=True.
    """
    _emit_log(log_callback, "--- INICIANDO PIPELINE DE CONSTRUCAO DO RAG ---")
    _emit_progress(progress_callback, 50)

    documentos, arquivos = realizar_carregamento()

    estado_anterior = _carregar_estado_anterior()
    fingerprint_atual = _fingerprint_csv_files(arquivos)

    precisa_rebuild = force_rebuild or not _banco_vetorial_existe()
    if not precisa_rebuild:
        precisa_rebuild = estado_anterior.get("csv_fingerprint") != fingerprint_atual

    total_pedacos = int(estado_anterior.get("total_pedacos", 0))
    reprocessado = False

    _emit_log(log_callback, "-> Passo 3: Embedding")
    if precisa_rebuild:
        _emit_log(
            log_callback,
            "-> Passo 4: Realizando Chunks Semanticos - Overlap",
        )
        _emit_progress(progress_callback, 60)
        pedacos = realizar_chunking_semantico(documentos)
        total_pedacos = len(pedacos)
        _emit_log(log_callback, f"-> {total_pedacos} pedaços inteligentes gerados.")

        _emit_log(
            log_callback,
            "-> Passo 5: Realizando Vetorizacao",
        )
        _emit_progress(progress_callback, 80)
        criar_banco_vetores(pedacos)
        _emit_log(log_callback, f"-> Banco atual com {total_pedacos} pedaços.")
        reprocessado = True

        _salvar_estado(
            {
                "updated_at": datetime.now().isoformat(),
                "csv_fingerprint": fingerprint_atual,
                "total_pedacos": total_pedacos,
                "total_documentos": len(documentos),
                "total_arquivos": len(arquivos),
            }
        )
    else:
        _emit_log(
            log_callback,
            "-> Sem mudancas detectadas para embeddings. Reaproveitando base existente.",
        )
        _emit_log(
            log_callback,
            "-> Passo 4: Realizando Chunks Semanticos - Overlap",
        )
        _emit_log(
            log_callback,
            "-> Etapa pulada (sem mudancas nos dados).",
        )
        _emit_log(
            log_callback,
            "-> Passo 5: Realizando Vetorizacao",
        )
        _emit_log(
            log_callback,
            f"-> Etapa pulada. Banco atual com {total_pedacos} pedaços.",
        )
        _emit_progress(progress_callback, 85)

    if validate_chain:
        _emit_log(log_callback, "-> Passo 6: Validando a configuracao da Cadeia de Consulta...")
        _emit_progress(progress_callback, 95)
        criar_cadeia_consulta()
        _emit_log(log_callback, "-> Cadeia configurada com sucesso.")
    else:
        _emit_log(
            log_callback,
            "-> Passo 6: Validacao da cadeia adiada para a inicializacao final do app.",
        )

    _emit_log(log_callback, "--- PIPELINE CONCLUIDO ---")
    _emit_progress(progress_callback, 95)

    return {
        "reprocessado": reprocessado,
        "total_arquivos": len(arquivos),
        "total_documentos": len(documentos),
        "total_pedacos": total_pedacos,
    }


if __name__ == "__main__":
    iniciar_pipeline()
