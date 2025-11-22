from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1 import auth, users, agents, executions
from .core.config import settings
from .db import session as db_session
from .db import base as db_base
from .db import models as db_models
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="TaskForge-AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


def include_routers(application: FastAPI):
    application.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
    application.include_router(users.router, prefix="/api/v1/users", tags=["users"])
    application.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
    application.include_router(executions.router, prefix="/api/v1/executions", tags=["executions"])


include_routers(app)


@app.on_event("startup")
def on_startup():
    # Create DB tables for dev if they don't exist
    db_base.Base.metadata.create_all(bind=db_session.engine)
    logger.info("Database tables ensured.")


@app.on_event("shutdown")
def on_shutdown():
    logger.info("Shutting down application")
