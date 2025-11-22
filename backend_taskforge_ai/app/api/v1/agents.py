from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from ...db import session as db_session
from ...db import models
from ...schemas.agent import AgentCreate, AgentOut
from ...services import storage

router = APIRouter()


@router.get("/", response_model=list[AgentOut])
def list_agents(db: Session = Depends(db_session.get_db)):
    agents = db.query(models.Agent).all()
    return agents


@router.post("/", response_model=AgentOut)
def create_agent(agent_in: AgentCreate, db: Session = Depends(db_session.get_db)):
    # For scaffold, owner_id is fixed to 1 or should be extracted from auth
    owner_id = 1
    agent = models.Agent(name=agent_in.name, description=agent_in.description, owner_id=owner_id)
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


@router.post("/upload")
def upload_file(file: UploadFile = File(...)):
    data = file.file.read()
    filename, url = storage.save_file(file.filename, data)
    return {"filename": filename, "url": url}


@router.get("/{agent_id}", response_model=AgentOut)
def get_agent(agent_id: int, db: Session = Depends(db_session.get_db)):
    agent = db.query(models.Agent).get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent
