from pydantic import BaseModel
from typing import Optional, Any
import datetime


class ExecutionCreate(BaseModel):
    agent_id: int
    input: Optional[Any] = None


class ExecutionOut(BaseModel):
    id: int
    agent_id: int
    user_id: int
    status: str
    input: Optional[Any]
    result: Optional[Any]
    created_at: datetime.datetime
    started_at: Optional[datetime.datetime]
    finished_at: Optional[datetime.datetime]

    class Config:
        orm_mode = True
