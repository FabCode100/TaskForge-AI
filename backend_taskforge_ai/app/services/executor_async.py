# executor_async.py
import asyncio
import json
import logging
from datetime import datetime
import anyio
import httpx

from ..db import models
from ..core.config import settings
from ..db.session import SessionLocal

logger = logging.getLogger("executor_async")

# IN-MEMORY pub/sub: maps execution_id -> asyncio.Queue[str]
# (cada item da queue será um fragmento de texto que chegamos do LLM)
QUEUES: dict[int, asyncio.Queue] = {}
QUEUES_LOCK = asyncio.Lock()  # protege criação/remoção da fila

def _get_db():
    return SessionLocal()

# ---- sync DB helpers (executados em thread pool) ----
def _fetch_execution_sync(execution_id: int):
    db = _get_db()
    try:
        return db.query(models.Execution).filter(models.Execution.id == execution_id).first()
    finally:
        db.close()

def _commit_sync(exe):
    db = _get_db()
    try:
        db.merge(exe)
        db.commit()
    finally:
        db.close()

def _update_status_sync(execution_id: int, **fields):
    """Atualiza campos simples do registro (rodado em thread)."""
    db = _get_db()
    try:
        exe = db.query(models.Execution).filter(models.Execution.id == execution_id).first()
        if not exe:
            return None
        for k, v in fields.items():
            setattr(exe, k, v)
        db.commit()
        db.refresh(exe)
        return exe
    finally:
        db.close()

# ---- core async worker ----
async def process_execution(execution_id: int):
    """Coroutine que chama o Gemini (streaming) e publica fragmentos na QUEUE correspondente."""
    # cria fila se necessário
    async with QUEUES_LOCK:
        q = QUEUES.get(execution_id)
        if q is None:
            q = asyncio.Queue()
            QUEUES[execution_id] = q

    # busca execução (sync em thread)
    exe = await anyio.to_thread.run_sync(_fetch_execution_sync, execution_id)
    if not exe:
        logger.warning("[executor] Execution %s not found", execution_id)
        # assegura remoção da fila se ninguém usar
        async with QUEUES_LOCK:
            QUEUES.pop(execution_id, None)
        return

    # marca como running
    exe.started_at = exe.started_at or datetime.utcnow()
    exe.status = "running"
    await anyio.to_thread.run_sync(_commit_sync, exe)

    user_input = (exe.input or "").strip()
    if not user_input:
        exe.result = json.dumps({"error": "no input provided"})
        exe.status = "failed"
        exe.finished_at = datetime.utcnow()
        await anyio.to_thread.run_sync(_commit_sync, exe)
        # publica um evento final para quem ouvir
        await q.put(json.dumps({"type": "error", "text": "no input provided"}))
        await q.put("__DONE__")
        async with QUEUES_LOCK:
            QUEUES.pop(execution_id, None)
        return

    # --- Preferência: Gemini streaming (usando streamGenerateContent / generateContentStream endpoints) ---
    # NOTE: endpoint/exact payload pode variar por versão da API. Ajuste se necessário.
    GEMINI_KEY = settings.gemini_api_key
    GEMINI_MODEL = settings.gemini_model or "gemini-2.5"  # substitua conforme config

    if GEMINI_KEY:
        # Exemplo: usar endpoint "streamGenerateContent" (Vertex / GenAI streaming)
        # URL e headers podem variar: aqui usamos o endpoint público de GenAI (ajuste conforme tua conta)
        url = f"https://generativelanguage.googleapis.com/v1/models/{GEMINI_MODEL}:generateContent?key={GEMINI_KEY}"
        # Alguns endpoints de streaming usam /streamGenerateContent ou streamGenerateContent RPC;
        # Se for o caso, ajuste a URL de acordo com a doc da sua versão.
        payload = {
            "contents": [{"text": user_input}],
            # parâmetros típicos
            "temperature": 0.2,
            "maxOutputTokens": 1024,
            # "streaming": True  # dependendo da versão; nem sempre necessário
        }

        try:
            # Usando AsyncClient e stream para iterar por linhas/chunks
            async with httpx.AsyncClient(timeout=120.0) as client:
                # Se a API fornece endpoint de streaming específico (ex: streamGenerateContent),
                # use-o; aqui demonstramos leitura incremental do response.iter_text().
                async with client.stream("POST", url, json=payload) as resp:
                    if resp.status_code not in (200, 201):
                        text = await resp.aread()
                        err = f"Gemini HTTP {resp.status_code}: {text!r}"
                        logger.error(err)
                        await q.put(json.dumps({"type":"error","text": err}))
                        exe.result = json.dumps({"error": "Gemini HTTP error", "detail": str(resp.status_code)})
                        exe.status = "failed"
                        exe.finished_at = datetime.utcnow()
                        await anyio.to_thread.run_sync(_commit_sync, exe)
                        await q.put("__DONE__")
                        async with QUEUES_LOCK:
                            QUEUES.pop(execution_id, None)
                        return

                    # processa streaming incremental
                    buffer = []
                    async for chunk in resp.aiter_text():
                        if not chunk:
                            continue
                        # chunk pode conter JSON parts or plain text depending on API
                        # Tentar extrair texto simples; se for json-lines, parsear
                        text_piece = chunk
                        # limpa prefixos tipo "data: " (se provider usar SSE style)
                        for line in text_piece.splitlines():
                            if not line.strip():
                                continue
                            # se for "data: {...}" ou json, tenta extrair
                            if line.startswith("data:"):
                                content = line[len("data:"):].strip()
                                # some providers send "[DONE]"
                                if content == "[DONE]":
                                    break
                                try:
                                    js = json.loads(content)
                                except Exception:
                                    js = content
                                piece = js if isinstance(js, str) else js.get("text") if isinstance(js, dict) else str(js)
                                if piece:
                                    await q.put(piece)
                                    buffer.append(piece)
                            else:
                                # fallback: envia a linha como texto
                                await q.put(line)
                                buffer.append(line)

                    # fim do stream
                    # junta tudo para salvar no DB
                    full_text = "".join(buffer).strip()
                    exe.result = full_text or json.dumps({"error": "empty response"})
                    exe.status = "completed" if full_text else "failed"

        except Exception as e:
            logger.exception("Gemini streaming failed")
            await q.put(json.dumps({"type":"error","text": f"exception calling Gemini: {str(e)}"}))
            exe.result = json.dumps({"error": "exception calling Gemini", "detail": str(e)})
            exe.status = "failed"

    else:
        # --- Fallback HuggingFace (simples, não-streaming) ---
        hf_token = settings.huggingfacehub_api_token
        hf_model = settings.hf_model
        if not hf_token or not hf_model:
            msg = "No LLM provider configured"
            await q.put(json.dumps({"type":"error","text": msg}))
            exe.result = json.dumps({"error": msg})
            exe.status = "failed"
            exe.finished_at = datetime.utcnow()
            await anyio.to_thread.run_sync(_commit_sync, exe)
            await q.put("__DONE__")
            async with QUEUES_LOCK:
                QUEUES.pop(execution_id, None)
            return

        hf_url = f"https://api-inference.huggingface.co/models/{hf_model}"
        headers = {"Authorization": f"Bearer {hf_token}"}
        payload = {"inputs": user_input, "parameters": {"max_new_tokens": 200, "temperature": 0.7}}
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(hf_url, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    if isinstance(data, list) and data and "generated_text" in data[0]:
                        text = data[0]["generated_text"]
                        await q.put(text)
                        exe.result = text
                        exe.status = "completed"
                    else:
                        text = f"unexpected HF response: {data!r}"
                        await q.put(json.dumps({"type":"error","text": text}))
                        exe.result = json.dumps({"error": "unexpected HF response", "detail": data})
                        exe.status = "failed"
                else:
                    text = f"HF request failed ({resp.status_code})"
                    await q.put(json.dumps({"type":"error","text": text}))
                    exe.result = json.dumps({"error": "HF http error", "status": resp.status_code, "detail": resp.text})
                    exe.status = "failed"
        except Exception as e:
            logger.exception("HF call failed")
            await q.put(json.dumps({"type":"error","text": f"exception calling HF: {str(e)}"}))
            exe.result = json.dumps({"error":"exception calling HF", "detail": str(e)})
            exe.status = "failed"

    exe.finished_at = datetime.utcnow()
    # commit final (sync)
    await anyio.to_thread.run_sync(_commit_sync, exe)

    # sinaliza finalização para listeners
    await q.put("__DONE__")

    # opcional: Retira a fila para liberar memória depois de um tempo
    async def _cleanup():
        await asyncio.sleep(2.0)
        async with QUEUES_LOCK:
            QUEUES.pop(execution_id, None)

    asyncio.create_task(_cleanup())


# helper para enfileirar (usado no router)
def enqueue_execution(background_tasks, execution_id: int):
    background_tasks.add_task(process_execution, execution_id)
