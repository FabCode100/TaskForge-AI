from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt

from ...core.config import settings
from ...db import session as db_session
from ...db import models
from ...schemas.user import UserOut

router = APIRouter()


def get_current_user(token: str = Depends(lambda: None), db: Session = Depends(db_session.get_db)):
    # Minimal token-based user lookup from Authorization header handled by FastAPI security in production.
    # For this scaffold, accept a raw token via dependency if provided.
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.get("/me", response_model=UserOut)
def read_me(current_user: models.User = Depends(get_current_user)):
    return current_user
