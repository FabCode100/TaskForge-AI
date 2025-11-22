from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
import datetime

from ...core.config import settings
from ...db import session as db_session
from ...db import models
from ...schemas.user import UserCreate, UserOut
from ...schemas.auth import Token

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(subject: str):
    data = {"sub": str(subject), "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.access_token_expire_minutes)}
    encoded = jwt.encode(data, settings.secret_key, algorithm="HS256")
    return encoded


@router.post("/register", response_model=Token)
def register(user_in: UserCreate, db: Session = Depends(db_session.get_db)):
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = models.User(email=user_in.email, display_name=user_in.display_name or "", hashed_password=get_password_hash(user_in.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
def login(form_data: UserCreate, db: Session = Depends(db_session.get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.email).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}
