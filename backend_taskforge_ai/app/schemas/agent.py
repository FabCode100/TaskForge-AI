from pydantic import BaseModel
from typing import Optional
import datetime


class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None


class AgentCreate(AgentBase):
    pass


class AgentOut(AgentBase):
    id: int
    owner_id: int
    created_at: datetime.datetime

    class Config:
        orm_mode = True
