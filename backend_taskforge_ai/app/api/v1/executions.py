# routes/executions.py
import asyncio
import json
from datetime import datetime
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, Request
from fastapi.responses import StreamingResponse

from ...db import session as db_session
from ...db import models
from ...schemas.execution import ExecutionCreate, ExecutionOut
from ...services.executor_async import enqueue_execution, QUEUES, QUEUES_LOCK

router = APIRouter()

@router.post("/", response_model=ExecutionOut)
def create_execution(
    payload: ExecutionCreate,
    background_tasks: BackgroundTasks,
    db = Depends(db_session.get_db),
):
    user_id = 1  # fixo por enquanto
    exe = models.Execution(
        agent_id=payload.agent_id,
        user_id=user_id,
        input=str(payload.input),
        status="queued",
    )
    db.add(exe)
    db.commit()
    db.refresh(exe)

    # garante fila para streaming
    import asyncio
    from ..executor_async import QUEUES, QUEUES_LOCK
    async def _ensure_queue(eid: int):
        async with QUEUES_LOCK:
            if eid not in QUEUES:
                QUEUES[eid] = asyncio.Queue()
    # nota: background_tasks aceita coroutine functions; chamar aqui para criar fila imediatamente:
    background_tasks.add_task(_ensure_queue, exe.id)

    enqueue_execution(background_tasks, exe.id)
    return exe

@router.get("/{execution_id}", response_model=ExecutionOut)
def get_execution(execution_id: int, db = Depends(db_session.get_db)):
    exe = db.query(models.Execution).filter(models.Execution.id == execution_id).first()
    if not exe:
        raise HTTPException(status_code=404, detail="Execution not found")
    return exe

# SSE streaming endpoint
@router.get("/{execution_id}/stream")
async def stream_execution(request: Request, execution_id: int):
    """Server-Sent Events endpoint. Client should connect with EventSource."""
    # cria fila se não existir
    async with QUEUES_LOCK:
        q = QUEUES.get(execution_id)
        if q is None:
            q = asyncio.Queue()
            QUEUES[execution_id] = q

    async def event_generator():
        try:
            while True:
                # se cliente desconectar, exit
                if await request.is_disconnected():
                    break
                try:
                    item = await asyncio.wait_for(q.get(), timeout=25.0)
                except asyncio.TimeoutError:
                    # enviar um keep-alive para evitar timeouts intermediários
                    yield ":\n\n"
                    continue

                if item == "__DONE__":
                    # optional: envia evento final e fecha stream
                    yield f"event: done\ndata: {json.dumps({'finished': True})}\n\n"
                    break

                # se item for string JSON já, envia como data
                # escape novas linhas conforme SSE
                for chunk_line in str(item).splitlines():
                    yield f"data: {chunk_line}\n"
                yield "\n"

            # fim
        finally:
            # cleanup: remove fila se vazia (não estritamente necessário)
            async with QUEUES_LOCK:
                q2 = QUEUES.get(execution_id)
                if q2 is q:
                    # se fila vazia, remove
                    try:
                        q2.get_nowait()
                    except Exception:
                        pass
                    # não remover imediatamente, executor remove após timeout
                    # QUEUES.pop(execution_id, None)
                    pass

    return StreamingResponse(event_generator(), media_type="text/event-stream")
