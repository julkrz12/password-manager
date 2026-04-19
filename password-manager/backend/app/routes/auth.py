import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db, engine
from ..models import User
from ..schemas import RegisterRequest, LoginRequest, SessionResponse
from ..core.crypto import hash_master_password, verify_master_password, derive_key
from ..core.session_store import create_session, delete_session
from ..core.config import settings

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/register', response_model=SessionResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=409, detail='Użytkownik już istnieje')

    kdf_salt = os.urandom(16)
    pw_hash = hash_master_password(payload.master_password)

    u = User(username=payload.username, password_hash=pw_hash, kdf_salt=kdf_salt)
    db.add(u)
    db.commit()
    db.refresh(u)

    key = derive_key(payload.master_password, u.kdf_salt)
    token = create_session(u.id, key)
    return SessionResponse(token=token, ttl_minutes=settings.session_ttl_minutes)


@router.post('/login', response_model=SessionResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.username == payload.username).first()
    if not u:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Błędny login lub hasło')

    if not verify_master_password(u.password_hash, payload.master_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Błędny login lub hasło')

    key = derive_key(payload.master_password, u.kdf_salt)
    token = create_session(u.id, key)
    return SessionResponse(token=token, ttl_minutes=settings.session_ttl_minutes)


@router.post('/logout')
def logout(token: str):
    delete_session(token)
    return {'ok': True}
