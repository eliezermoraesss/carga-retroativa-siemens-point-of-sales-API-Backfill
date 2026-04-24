"""
siemens_api.py — Integração com a API Siemens Point of Sales.
Envia batches de até 3000 registros via POST com retry e delay entre requisições.
"""
import time
import logging
import requests
import json
from config import SIEMENS_API_URL, SIEMENS_API_TOKEN, RETRY_MAX, RETRY_BACKOFF

logger = logging.getLogger(__name__)

# Delay seguro entre o envio de BATCHES (em segundos)
BATCH_DELAY = 2.0 

def _build_headers() -> dict:
    """Monta os headers HTTP para a requisição."""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "x-api-key": SIEMENS_API_TOKEN
    }
    return headers


def send_batch(records: list, batch_index: int = 0, dry_run: bool = False) -> dict:
    """
    Envia um batch de registros para a API Siemens.

    Args:
        records:      Lista de dicionários (até 3000 registros).
        batch_index:  Índice do batch (para logging).
        dry_run:      Se True, simula o envio sem fazer requisição real.

    Returns:
        dict com keys: success (bool), status_code (int|None),
                        response_body (dict|str|None), error (str|None).
    """
    if not dry_run and batch_index > 1:
        time.sleep(BATCH_DELAY)

    # Conforme solicitado, o payload é diretamente a lista (array de objetos JSON)
    payload = records
    headers = _build_headers()

    if dry_run:
        logger.info(f"[DRY-RUN] Batch {batch_index} ({len(records)} registros) — Pronto para envio.")
        if len(records) > 1:
            preview = json.dumps(payload[:2], indent=2, ensure_ascii=False, default=str)
            # Remove o último colchete e adiciona a indicação de que há mais registros
            preview = preview[:-1] + f"  ... (e mais {len(records)-2} registros JSON) ...\n]"
            logger.info(f"[DRY-RUN] Estrutura do Array JSON Payload que será enviado:\n{preview}")
        return {"success": True, "status_code": 201, "response_body": {"dry_run": True}, "error": None}

    last_error = None
    for attempt in range(1, RETRY_MAX + 1):
        try:
            logger.info(f"Enviando Batch {batch_index} com {len(records)} registros (tentativa {attempt}/{RETRY_MAX})…")
            
            if len(records) > 1:
                preview = json.dumps(payload[:2], indent=2, ensure_ascii=False, default=str)
                preview = preview[:-1] + f"  ... (e mais {len(records)-2} registros JSON) ...\n]"
                logger.info(f"Estrutura do Array JSON Payload:\n{preview}")
            
            resp = requests.post(
                SIEMENS_API_URL,
                json=payload,
                headers=headers,
                timeout=120, # Timeout estendido para 120s por ser um batch grande
            )

            if resp.status_code == 201:
                logger.info(f"✅ Batch {batch_index} aceito (201 Created).")
                try:
                    body = resp.json()
                except Exception:
                    body = resp.text
                return {"success": True, "status_code": 201, "response_body": body, "error": None}

            logger.warning(f"⚠️ Batch {batch_index} retornou status {resp.status_code}: {resp.text[:500]}")
            last_error = f"HTTP {resp.status_code}: {resp.text[:300]}"

        except Exception as exc:
            last_error = str(exc)
            logger.warning(f"❌ Erro no Batch {batch_index} (tentativa {attempt}): {exc}")

        if attempt < RETRY_MAX:
            time.sleep(RETRY_BACKOFF ** attempt)

    return {"success": False, "status_code": None, "response_body": None, "error": last_error}
