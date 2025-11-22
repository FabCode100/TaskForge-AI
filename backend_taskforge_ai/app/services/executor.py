import time
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from ..db import models


def process_execution(execution_id: int, db: Session):
    # Very basic simulated executor: sleep then write result
    exe = db.query(models.Execution).filter(models.Execution.id == execution_id).first()
    if not exe:
        return
    exe.status = "running"
    db.commit()
    exe.started_at = exe.started_at or __import__("datetime").datetime.utcnow()
    db.commit()
    # simulate work
    time.sleep(2)
    exe.result = "{\"message\": \"Execution completed (simulated)\"}"
    exe.status = "completed"
    exe.finished_at = __import__("datetime").datetime.utcnow()
    db.commit()


def enqueue_execution(background_tasks: BackgroundTasks, execution_id: int, db: Session):
    background_tasks.add_task(process_execution, execution_id, db)
