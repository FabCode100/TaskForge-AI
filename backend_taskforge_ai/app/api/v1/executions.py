from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from ...db import session as db_session
from ...db import models
from ...schemas.execution import ExecutionCreate, ExecutionOut
from ...services.executor import enqueue_execution

router = APIRouter()


@router.post("/", response_model=ExecutionOut)
def create_execution(payload: ExecutionCreate, background_tasks: BackgroundTasks, db: Session = Depends(db_session.get_db)):
    # user_id is scaffolded as 1 for now
    user_id = 1
    exe = models.Execution(agent_id=payload.agent_id, user_id=user_id, input=str(payload.input), status="queued")
    db.add(exe)
    db.commit()
    db.refresh(exe)
    enqueue_execution(background_tasks, exe.id, db)
    return exe


@router.get("/{execution_id}", response_model=ExecutionOut)
def get_execution(execution_id: int, db: Session = Depends(db_session.get_db)):
    exe = db.query(models.Execution).get(execution_id)
    if not exe:
        raise HTTPException(status_code=404, detail="Execution not found")
    return exe
